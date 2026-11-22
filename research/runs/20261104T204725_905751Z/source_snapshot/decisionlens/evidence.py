"""Auditable literal extraction. No claim of general semantic correctness."""
import re
from collections import defaultdict

FIELDS={
 'Price': ('price','pricing','cost','monthly price'),
 'SSO': ('sso','single sign-on','single sign on'),
 'Data residency': ('data residency','hosting region','data location'),
 'Support': ('support','support hours'),
 'Intended users': ('intended users','target users','best for','audience'),
 'Limitations': ('limitations','limitation','documented limitations'),
 'SLA': ('sla','uptime','availability'),
 'Integrations': ('integrations','integration'),
 'Contract': ('contract','terms','minimum term'),
}
def norm(v):
    return re.sub(r'\s+',' ',v.strip().lower().rstrip('.'))

def extract_facts(documents):
    facts=[]
    for doc in documents:
        for page in doc['pages']:
            section=page['section']
            for line_num,line in enumerate(page['text'].splitlines(),1):
                if line.startswith('#'):
                    section=line.strip('# ').strip()
                line=line.strip().strip('|').strip()
                match=re.match(r'^(?:[-*]\s*)?(?:\*\*)?([\w /()\-]{2,60})(?:\*\*)?\s*[:|]\s*(.+)$',line)
                if not match:
                    continue
                label,value=match.groups(); key=norm(label)
                if key in ('product','vendor','source','source date','synthetic','document date','date'):
                    continue
                field=next((f for f,aliases in FIELDS.items() if key in aliases),label.strip())
                if not value.strip() or len(value)>1500:
                    continue
                # An explicit unknown is missing information, not a measured zero.
                if norm(value) in ('unknown','not specified','n/a','not documented','missing'):
                    continue
                facts.append(dict(id=f"{doc['id']}:{page['page'] or 0}:L{line_num}",product=doc['product'],
                    field=field,value=value.strip(),excerpt=line,doc_id=doc['id'],name=doc['name'],
                    source_url=doc['source_url'],source_date=doc['source_date'],page=page['page'],
                    section=section,line=line_num,synthetic=doc['synthetic']))
    return facts

def matrix(documents,facts,overrides=None):
    overrides=overrides or {}
    products=list(dict.fromkeys(d['product'] for d in documents))
    fields=list(dict.fromkeys(list(FIELDS)+[f['field'] for f in facts]))
    cells=[]
    for field in fields:
        for product in products:
            evidence=[f for f in facts if f['field']==field and f['product']==product]
            values=list(dict.fromkeys(f['value'] for f in evidence))
            conflict=len({norm(v) for v in values})>1
            key=product+'::'+field
            cell=dict(key=key,product=product,field=field,status='conflict' if conflict else 'documented' if values else 'missing',
                      value=' / '.join(values) if values else None,evidence=evidence,confirmed=False,note='')
            if key in overrides:
                edit=overrides[key]
                cell.update(value=edit['value'],confirmed=bool(edit['confirmed']),note=edit['note'],
                    status='reviewed' if edit['confirmed'] and edit['value'].strip() else cell['status'])
                if not edit['value'].strip():
                    cell.update(value=None,status='missing',confirmed=False)
            cells.append(cell)
    return dict(products=products,fields=fields,cells=cells)

def evidence_answer(query,chunks):
    if not chunks:
        return {'text':'No evidence found. Add a document or change the question.','citations':[], 'mode':'extractive'}
    # Excerpts are not synthesized claims. Relevance is the user's judgment.
    return dict(text='Retrieved evidence is shown below. It may cover only part of your question. '
                     'Check scope, dates and missing fields before deciding.',citations=chunks,mode='extractive')
