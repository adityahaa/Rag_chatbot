"""Audit and freeze pilot development/evaluation IDs before running any methods."""
from __future__ import annotations
import ast, csv, hashlib, json, re, sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from decisionlens.documents import parse_document,chunk_documents
RAW=ROOT/'data/raw';DERIVED=ROOT/'data/derived'
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def normalized(value):
    # Labels contain literal escaped \n and \uXXXX sequences; decode these without arbitrary eval.
    value=re.sub(r'\\u([0-9a-fA-F]{4})',lambda m:chr(int(m.group(1),16)),value)
    value=value.replace('\\n','\n').replace('\\"','"').replace('\\t','\t')
    return re.sub(r'[^\w]+','',value.lower())
def snippet(id,product,text,name=None,**extra):
    return dict(id=id,text=text,product=product,name=name or id,doc_id=id,source_url='',source_date=None,
                page=None,section='Attribute record',synthetic=False,**extra)

def aws():
    rows=list(csv.DictReader((RAW/'aws/products.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    groups=defaultdict(list);invalid=[];exact=Counter();reference_cells=0
    for i,row in enumerate(rows):
        try:
            attrs=ast.literal_eval(row['Attribute Names and Values for Products under Consideration'])
            if not isinstance(attrs,dict) or not attrs:raise ValueError('empty or invalid attributes')
            cells=[]
            for key,value in attrs.items():
                match=re.match(r'(.+)_product(\d+)$',key,re.I)
                if not match:raise ValueError('malformed attribute key')
                cells.append((f'Product {match[2]}',match[1],str(value)))
            signature=tuple(sorted(set(x[1] for x in cells)));group=digest(signature)
            item_id=digest(attrs);exact[item_id]+=1;reference_cells+=len(cells)
            groups[group].append((item_id,i,cells))
        except Exception as e:invalid.append({'row':i,'reason':str(e)})
    selected=[]
    for order,group in enumerate(sorted(groups)[:80]):
        item_id,row,cells=sorted(groups[group])[0]
        split='dev' if order<20 else 'eval'
        documents=[snippet(f'aws:{item_id[:12]}:{j}',p,f'{f}: {v}',f'{p} attribute {j}') for j,(p,f,v) in enumerate(cells)]
        # Constant unrelated evidence distractors, shared across methods. Synthetic additions are marked.
        documents += [dict(snippet(f'noise:{j}',f'Distractor {j}',f'Help center: unrelated policy {j}'),synthetic=True) for j in range(3)]
        selected.append(dict(id='aws:'+item_id,group=group,split=split,dataset='aws_real_attributes',
            row=row,query='Compare '+', '.join(dict.fromkeys(p for p,f,v in cells))+' on '+', '.join(dict.fromkeys(f for p,f,v in cells))+'.',
            chunks=documents,gold_ids=[x['id'] for x in documents if x['id'].startswith('aws:')],
            reference=[dict(product=p,field=f,values=[v],status='known') for p,f,v in cells]))
    return selected,dict(rows=len(rows),columns=list(rows[0]),invalid=invalid,attribute_signatures=len(groups),
        exact_attribute_maps=len(exact),duplicate_attribute_rows=sum(v-1 for v in exact.values()),reference_cells=reference_cells,
        dev=sum(x['split']=='dev' for x in selected),eval=sum(x['split']=='eval' for x in selected),
        caveat='IDs are anonymized per row. Human comparative prose is not used as a preference label. Distractors are synthetic neutral text.')

def rag():
    path=RAW/'rag/datasets/Dataset categories - queries_01122025.csv'
    rows=list(csv.DictReader(path.open(encoding='utf-8-sig')))
    docs=sorted((RAW/'rag/datasets').rglob('*.md'))
    docs=[p for p in docs if 'cloud' in str(p).lower()]
    byname={p.name:p for p in docs};normtext={p.name:normalized(p.read_text(encoding='utf-8')) for p in docs}
    corpus=[parse_document(p.name,p.read_bytes(),product='Cloudway 24 (synthetic)',synthetic=True) for p in docs]
    chunks=chunk_documents(corpus)
    cloud=[(i,r) for i,r in enumerate(rows) if 'cloud' in r['Enterprise Name'].lower()]
    eligible=[];issues=[];seen=set()
    for i,row in cloud:
        qnorm=normalized(row['Query'])
        if qnorm in seen:
            issues.append({'row':i,'reason':'duplicate normalized query'});continue
        seen.add(qnorm)
        try:
            supports=json.loads(row['Supporting Facts'])
            if not supports:raise ValueError('empty support')
            names=[]
            for support in supports:
                name=support['filename'].strip()
                # Only surrounding whitespace normalization is allowed for label filenames.
                found=next((f for f in byname if f.strip()==name),None)
                if not found:raise ValueError('missing source: '+name)
                if not normalized(support['text']) in normtext[found]:raise ValueError('support span not found in '+found)
                names.append(found)
            eligible.append(dict(id='rag:'+str(i),row=i,query=row['Query'],query_type=row['Query Type'],
                gold_names=sorted(set(names)),dataset='rag_multi_synthetic'))
        except Exception as e:issues.append({'row':i,'reason':str(e)})
    # Connected components of gold filenames avoid support-document overlap across dev/eval labels.
    parent={name:name for item in eligible for name in item['gold_names']}
    def find(v):
        while parent[v]!=v:v=parent[v]
        return v
    for item in eligible:
        first=find(item['gold_names'][0])
        for name in item['gold_names'][1:]:parent[find(name)]=first
    components=defaultdict(set)
    for name in parent:components[find(name)].add(name)
    groups=sorted((digest(sorted(v)),v) for v in components.values())
    dev_names=set().union(*(v for _,v in groups[:max(1,len(groups)//4)])) if groups else set()
    eval_count=0;cases=[]
    for item in sorted(eligible,key=lambda x:digest(x['query'])):
        split='dev' if item['gold_names'][0] in dev_names else 'eval'
        if split=='eval' and eval_count>=60:continue
        if split=='eval':eval_count+=1
        item.update(split=split,group=digest(sorted(components[find(item['gold_names'][0])])),corpus='rag_cloudway')
        cases.append(item)
    return cases,chunks,dict(all_query_rows=len(rows),cloudway_rows=len(cloud),documents=len(docs),chunks=len(chunks),
        eligible_rows=len(eligible),exclusions=issues,components=len(groups),dev=sum(c['split']=='dev' for c in cases),
        eval=sum(c['split']=='eval' for c in cases),query_types=dict(Counter(r['Query Type'] for i,r in cloud)),
        exact_duplicate_documents=len(docs)-len({hashlib.sha256(p.read_bytes()).hexdigest() for p in docs}),
        caveat='README says Cloud & SaaS and 786 total queries. Actual pinned QA CSV has different counts and Cloudway docs describe an airline. Existence + normalized span checks are mechanical, not semantic validation.')

def synthetic():
    cases=[]
    for i in range(20):
        split='dev' if i<5 else 'eval';group=f'synthetic-seed31-group{i:02d}'
        products=[f'Vendor-{31*i+7}A',f'Vendor-{31*i+7}B']
        base=[(products[0],'SSO','SAML included'),(products[0],'Data residency','EU'),
              (products[1],'SSO','Enterprise only'),(products[1],'Data residency','US')]
        for condition in ('full','missing','conflict','absent'):
            facts=base.copy()
            if condition=='missing':facts.pop(1)
            if condition=='conflict':facts.append((products[0],'SSO','SAML excluded'))
            if condition=='absent':facts=[]
            chunks=[dict(snippet(f'{group}:{condition}:{j}',p,f'{f}: {v}'),synthetic=True) for j,(p,f,v) in enumerate(facts)]
            chunks+=[dict(snippet(f'{group}:noise:{j}',f'Other vendor {j}',f'Support: community forum {j}'),synthetic=True) for j in range(5)]
            ref=[]
            for p,f,v in base:
                values=sorted(set(value for product,field,value in facts if product==p and field==f))
                ref.append(dict(product=p,field=f,values=values,status='conflict' if len(values)>1 else 'known' if values else 'missing'))
            cases.append(dict(id=f'{group}:{condition}',group=group,split=split,dataset='controlled_synthetic',condition=condition,
                query=f'Compare {products[0]} and {products[1]} on SSO and Data residency.',
                chunks=chunks,gold_ids=[c['id'] for c in chunks if ':noise:' not in c['id']],reference=ref))
    return cases

def main():
    DERIVED.mkdir(parents=True,exist_ok=True)
    a,aa=aws();r,corpus,ra=rag();s=synthetic()
    all_cases=a+r+s
    # Check split disjointness as a pre-evaluation invariant.
    assert not {c['group'] for c in all_cases if c['split']=='dev'} & {c['group'] for c in all_cases if c['split']=='eval'}
    (DERIVED/'cases.json').write_text(json.dumps(all_cases,indent=2,ensure_ascii=False),encoding='utf-8')
    (DERIVED/'rag_cloudway.json').write_text(json.dumps(corpus,indent=2,ensure_ascii=False),encoding='utf-8')
    audit={'created':'2026-11-04','aws':aa,'rag_multi':ra,'synthetic':{'groups':20,'conditions':4,'dev':20,'eval':60},
        'case_file_sha256':hashlib.sha256((DERIVED/'cases.json').read_bytes()).hexdigest()}
    (ROOT/'research/data_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    # IDs, not source excerpts, are safe to include in the source package.
    (ROOT/'research/split_manifest.json').write_text(json.dumps([{k:v for k,v in c.items() if k in ('id','group','split','dataset','row','condition','gold_names')} for c in all_cases],indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k!='rag_multi'},indent=2))
    print('RAG audit:',{k:v for k,v in ra.items() if k!='exclusions'},'excluded:',len(ra['exclusions']))
if __name__=='__main__':main()
