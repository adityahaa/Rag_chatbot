"""Frozen pilot runner; append-only run directories, same cases and budgets."""
from __future__ import annotations
import argparse, hashlib, json, platform, statistics, sys, time, traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from decisionlens.retrieval import Index,encode,MODEL_ID
from decisionlens.generation import generate
METHODS=['semantic','keyword','hybrid','semantic_diverse','hybrid_diverse']

def retrieve(index,query,method,k=3):
    base=method.replace('_diverse','')
    if not method.endswith('_diverse'):return index.search(query,k,base)
    ranked=index.search(query,len(index.chunks),base)
    chosen=[];seen=set()
    for c in ranked:
        # Corpus QA has one organization; document diversification uses name.
        key=c['name'] if c['product']=='Cloudway 24 (synthetic)' else c['product']
        if key not in seen:
            chosen.append(c);seen.add(key)
            if len(chosen)==k:break
    for c in ranked:
        if len(chosen)==k:break
        if c['id'] not in {v['id'] for v in chosen}:chosen.append(c)
    return chosen

def product_metrics(case,retrieved):
    found=defaultdict(set)
    for chunk in retrieved:
        for line in chunk['text'].splitlines():
            if ': ' in line:
                field,value=line.split(': ',1);found[(chunk['product'],field)].add(value)
    correct=missing_correct=missing_n=conflict_found=conflict_n=known_n=known_correct=0
    for ref in case['reference']:
        actual=found[(ref['product'],ref['field'])];expected=set(ref['values'])
        correct+=actual==expected
        if ref['status']=='missing':missing_n+=1;missing_correct+=not actual
        if ref['status']=='conflict':conflict_n+=1;conflict_found+=len(actual)>1
        if ref['status']=='known':known_n+=1;known_correct+=actual==expected
    return dict(literal_cell_accuracy=correct/len(case['reference']),known_cell_recovery=known_correct/known_n if known_n else None,
        missing_status_accuracy=missing_correct/missing_n if missing_n else None,missing_cells=missing_n,
        conflict_recall=conflict_found/conflict_n if conflict_n else None,conflict_cells=conflict_n)

def code_hash():
    h=hashlib.sha256()
    for p in sorted(list((ROOT/'decisionlens').glob('*.py'))+[Path(__file__),ROOT/'research/prepare_data.py',ROOT/'research/PROTOCOL.md']):
        h.update(p.name.encode());h.update(p.read_bytes())
    return h.hexdigest()

def main(split='eval',generation=False):
    cases=json.loads((ROOT/'data/derived/cases.json').read_text(encoding='utf-8'))
    cases=[c for c in cases if c['split']==split]
    run=ROOT/'research/runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    run.mkdir(parents=True,exist_ok=False)
    import importlib.metadata
    metadata=dict(started_utc=datetime.now(timezone.utc).isoformat(),split=split,code_hash=code_hash(),k=3,
        methods=METHODS,model=MODEL_ID,model_manifest=json.loads((ROOT/'models_manifest.json').read_text()),
        cases_sha256=hashlib.sha256((ROOT/'data/derived/cases.json').read_bytes()).hexdigest(),
        python=platform.python_version(),platform=platform.platform(),processor=platform.processor(),
        dependencies={n:importlib.metadata.version(n) for n in ('torch','transformers','sentence-transformers','numpy')},
        generator='google/flan-t5-small' if generation else None,
        limitations='Pilot samples, automatic literal and filename checks only; no independent human evaluation.')
    (run/'metadata.json').write_text(json.dumps(metadata,indent=2))
    # Warm encoder once. Record startup separately; query timings are warm.
    t=time.perf_counter();encode(['warmup']);metadata['encoder_startup_ms']=(time.perf_counter()-t)*1000
    records=[];failures=[];indexes={};vectors={};index_times={}
    with (run/'per_case.jsonl').open('w',encoding='utf-8') as output:
        for case_num,case in enumerate(cases):
            corpus_key=case.get('corpus',case['id'])
            if corpus_key not in indexes:
                chunks=case.get('chunks') or json.loads((ROOT/'data/derived'/f'{corpus_key}.json').read_text(encoding='utf-8'))
                t=time.perf_counter();indexes[corpus_key]=Index(chunks,semantic=True);index_times[corpus_key]=(time.perf_counter()-t)*1000
            index=indexes[corpus_key]
            for method in METHODS:
                try:
                    start=time.perf_counter();retrieved=retrieve(index,case['query'],method)
                    latency=(time.perf_counter()-start)*1000
                    gold=set(case.get('gold_names',case.get('gold_ids',[])))
                    keys=[c['name'] if 'gold_names' in case else c['id'] for c in retrieved]
                    relevant=set(keys)&gold
                    recall=len(relevant)/len(gold) if gold else None
                    ranks=[i+1 for i,key in enumerate(keys) if key in gold]
                    record=dict(id=case['id'],dataset=case['dataset'],condition=case.get('condition','natural'),
                        method=method,gold_units=len(gold),retrieved_ids=[c['id'] for c in retrieved],
                        recall_at_3=recall,complete_evidence=float(gold.issubset(set(keys))) if gold else None,
                        mrr=1/min(ranks) if ranks else (0. if gold else None),latency_ms=latency,
                        index_ms=index_times[corpus_key])
                    if 'reference' in case:record.update(product_metrics(case,retrieved))
                    records.append(record);output.write(json.dumps(record)+'\n');output.flush()
                except Exception as e:
                    failure=dict(id=case['id'],method=method,error=type(e).__name__,traceback=traceback.format_exc())
                    failures.append(failure);output.write(json.dumps({'failed':failure})+'\n');output.flush()
            if (case_num+1)%20==0:print(f'Evaluated {case_num+1}/{len(cases)} cases',flush=True)
    aggregate=[]
    for dataset in sorted({r['dataset'] for r in records}):
        for method in METHODS:
            rows=[r for r in records if r['dataset']==dataset and r['method']==method]
            entry=dict(dataset=dataset,method=method,cases=len(rows),retrieval_cases=sum(r['gold_units']>0 for r in rows),
                structural_complete_ceiling=sum(r['gold_units']<=3 for r in rows if r['gold_units'])/sum(r['gold_units']>0 for r in rows) if any(r['gold_units'] for r in rows) else None)
            for metric in ('recall_at_3','complete_evidence','mrr','literal_cell_accuracy','known_cell_recovery','missing_status_accuracy','conflict_recall','latency_ms'):
                values=[r[metric] for r in rows if r.get(metric) is not None]
                entry[metric]=statistics.mean(values) if values else None
                entry[metric+'_n']=len(values)
            aggregate.append(entry)
    (run/'summary.json').write_text(json.dumps(aggregate,indent=2))
    (run/'failures.json').write_text(json.dumps(failures,indent=2))
    if generation:
        synth=[c for c in cases if c['dataset']=='controlled_synthetic']
        groups=sorted({c['group'] for c in synth})[:3]
        generation_results=[]
        for c in synth:
            if c['group'] not in groups or c['condition'] not in ('full','absent'):continue
            product=c['reference'][0]['product'];query=f'What is the SSO availability for {product}?'
            expected=c['reference'][0]['values'][0] if c['reference'][0]['values'] else 'Unknown'
            for method in ('semantic','hybrid','hybrid_diverse'):
                try:
                    chunks=retrieve(indexes[c['id']],query,method)
                    response=generate(query,chunks);response.pop('citations',None)
                    exact=response['text'].strip().rstrip('.').lower()==expected.lower()
                    abstain=any(v in response['text'].lower() for v in ('unknown','not provided','not specified','cannot answer','insufficient'))
                    generation_results.append(dict(id=c['id'],condition=c['condition'],method=method,expected=expected,
                        exact_match=exact,heuristic_abstention=abstain,**response))
                except Exception:
                    generation_results.append(dict(id=c['id'],method=method,failed=traceback.format_exc()))
                (run/'generation.json').write_text(json.dumps(generation_results,indent=2))
    metadata['finished_utc']=datetime.now(timezone.utc).isoformat()
    metadata['successful_method_cases']=len(records);metadata['failed_method_cases']=len(failures)
    (run/'metadata.json').write_text(json.dumps(metadata,indent=2))
    (ROOT/'research/LATEST_RUN.txt').write_text(run.name)
    print('Saved',run);print(json.dumps(aggregate,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--split',choices=['dev','eval'],default='eval');p.add_argument('--generation',action='store_true');a=p.parse_args();main(a.split,a.generation)
