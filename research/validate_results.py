"""Independent receipt: reconstruct gold membership and summary rates from saved IDs."""
import json,math
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
def main():
    run=ROOT/'research/runs'/(ROOT/'research/LATEST_RUN.txt').read_text().strip()
    cases=json.loads((ROOT/'data/derived/cases.json').read_text(encoding='utf-8'))
    assert not {c['group'] for c in cases if c['split']=='dev'} & {c['group'] for c in cases if c['split']=='eval'}
    corpus=json.loads((ROOT/'data/derived/rag_cloudway.json').read_text(encoding='utf-8'))
    names={c['id']:c['name'] for c in corpus}
    byid={c['id']:c for c in cases if c['split']=='eval'}
    raw=[json.loads(line) for line in (run/'per_case.jsonl').read_text().splitlines()]
    assert len(raw)==len(byid)*5
    grouped=defaultdict(list)
    for r in raw:
        assert 'failed' not in r
        c=byid[r['id']];gold=set(c.get('gold_ids',c.get('gold_names',[])))
        retrieved={names[k] for k in r['retrieved_ids']} if 'gold_names' in c else set(r['retrieved_ids'])
        recomputed=len(gold&retrieved)/len(gold) if gold else None
        assert (recomputed is None and r['recall_at_3'] is None) or math.isclose(recomputed,r['recall_at_3'])
        grouped[(r['dataset'],r['method'])].append(recomputed)
    summary=json.loads((run/'summary.json').read_text())
    for s in summary:
        vals=[v for v in grouped[(s['dataset'],s['method'])] if v is not None]
        assert len(vals)==s['recall_at_3_n']
        assert math.isclose(sum(vals)/len(vals),s['recall_at_3'])
    receipt={'run':run.name,'validated_method_cases':len(raw),'split_group_overlap':0,
        'checks':['Saved retrieved-ID membership recomputed against gold IDs/names','Recall denominators and means reconstructed','Dev/eval evidence groups disjoint'],
        'limits':'Does not validate semantic relevance labels, factual correctness, independence of source identities, or generalization.'}
    (ROOT/'research/validation_receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
