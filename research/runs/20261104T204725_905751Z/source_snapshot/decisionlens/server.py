"""Loopback-only local application, with isolated expiring in-memory workspaces."""
from __future__ import annotations
import csv, io, json, secrets, threading, time
from pathlib import Path
from fastapi import FastAPI, Request, Response, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from .documents import parse_document, chunk_documents, InputError, MAX_BYTES
from .evidence import extract_facts, matrix, evidence_answer
from .retrieval import Index, MODEL_PATH
from .generation import generate, MODEL_PATH as GENERATOR_PATH
from .decisions import score, brief

ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title='DecisionLens',docs_url=None,redoc_url=None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','testserver'])
_sessions={};_guard=threading.Lock()

def new_session():
    return dict(documents=[],overrides={},criteria=[
        {'field':'SSO','requirement':'SAML SSO on the selected plan','weight':40},
        {'field':'Price','requirement':'Within budget; verify billing period and units','weight':30},
        {'field':'Data residency','requirement':'EU hosting available','weight':30}],ratings={},index=None,
        notes='',brief_text='',touched=time.monotonic(),lock=threading.RLock())

@app.middleware('http')
async def local_security(request,call_next):
    if request.method not in ('GET','HEAD','OPTIONS'):
        origin=request.headers.get('origin')
        if origin and origin != str(request.base_url).rstrip('/'):
            return Response('Cross-origin changes are disabled.',status_code=403)
    if request.headers.get('content-length','').isdigit() and int(request.headers['content-length'])>MAX_BYTES*10+65536:
        return Response('Upload batch too large.',status_code=413)
    token=request.cookies.get('decisionlens_session')
    with _guard:
        now=time.monotonic()
        expired=[k for k,v in _sessions.items() if now-v['touched']>3600]
        for k in expired: _sessions.pop(k,None)
        if token not in _sessions:
            if len(_sessions)>=32:
                return Response('Local session limit reached; restart the app.',status_code=503)
            token=secrets.token_urlsafe(32);_sessions[token]=new_session()
        workspace=_sessions[token];workspace['touched']=now
    request.state.workspace=workspace
    response=await call_next(request)
    response.set_cookie('decisionlens_session',token,httponly=True,samesite='strict',max_age=3600)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    response.headers['Cache-Control']='no-store'
    response.headers['Referrer-Policy']='no-referrer'
    return response

def summary(s):
    m=matrix(s['documents'],extract_facts(s['documents']),s['overrides'])
    return dict(documents=[{k:v for k,v in d.items() if k!='pages'} for d in s['documents']],
        matrix=m,criteria=s['criteria'],ratings=s['ratings'],scores=score(m,s['criteria'],s['ratings']),
        notes=s['notes'],brief_text=s['brief_text'],semantic_ready=(MODEL_PATH/'config.json').exists(),
        generator_ready=(GENERATOR_PATH/'config.json').exists())

@app.get('/api/state')
def state(request:Request):
    with request.state.workspace['lock']:
        return summary(request.state.workspace)

@app.post('/api/demo')
def demo(request:Request):
    s=request.state.workspace
    with s['lock']:
        s.update({k:v for k,v in new_session().items() if k!='lock'});s['documents']=[parse_document(p.name,p.read_bytes(),product=product,
            source_date=day,synthetic=True) for p,product,day in [
            (ROOT/'data/demo/sprintly.md','Sprintly','2026-10-01'),
            (ROOT/'data/demo/forgeflow.md','ForgeFlow','2026-10-01'),
            (ROOT/'data/demo/orbitdesk.md','OrbitDesk','2026-10-01'),
            (ROOT/'data/demo/forgeflow-addendum.md','ForgeFlow','2026-10-15')]]
        return summary(s)

@app.post('/api/reset')
def reset(request:Request):
    s=request.state.workspace
    with s['lock']:
        for key,value in new_session().items():
            if key!='lock': s[key]=value
        return summary(s)

@app.post('/api/upload')
async def upload(request:Request,files:list[UploadFile]=File(...),product:str=Form(''),source_url:str=Form(''),
                 source_date:str=Form(''),synthetic:bool=Form(False)):
    s=request.state.workspace
    if len(files)>10: raise HTTPException(400,'Upload at most 10 files per batch.')
    documents=[]
    try:
        for file in files:
            data=await file.read(MAX_BYTES+1)
            documents.append(parse_document(file.filename or 'upload.txt',data,product,source_url,source_date,synthetic))
    except InputError as e:
        raise HTTPException(400,str(e)) from None
    finally:
        for file in files: await file.close()
    with s['lock']:
        additions=[d for d in documents if d['id'] not in {x['id'] for x in s['documents']}]
        if len(s['documents'])+len(additions)>20:
            raise HTTPException(400,'Workspace limit: 20 documents. Start a new workspace to replace the current set.')
        if sum(len(p['text']) for d in s['documents']+additions for p in d['pages'])>2_000_000:
            raise HTTPException(400,'Workspace text limit reached; use fewer documents.')
        s['documents']+=additions;s['index']=None;s['brief_text']=''
        return summary(s)

class Review(BaseModel):
    key:str=Field(max_length=300)
    value:str=Field(max_length=3000)
    confirmed:bool=False
    note:str=Field(default='',max_length=3000)

@app.post('/api/review')
def review(body:Review,request:Request):
    s=request.state.workspace
    with s['lock']:
        keys={c['key'] for c in summary(s)['matrix']['cells']}
        if body.key not in keys: raise HTTPException(400,'Unknown comparison cell.')
        if body.confirmed and not body.note.strip():
            raise HTTPException(400,'Add a review note, especially for manual additions or conflict resolution.')
        s['overrides'][body.key]=body.model_dump(exclude={'key'});s['brief_text']=''
        return summary(s)

class Criterion(BaseModel):
    field:str=Field(min_length=1,max_length=100)
    requirement:str=Field(max_length=2000)
    weight:float=Field(gt=0,le=100)
class Priorities(BaseModel):
    criteria:list[Criterion]=Field(min_length=1,max_length=20)
    ratings:dict[str,float|None]
    notes:str=Field(default='',max_length=10000)

@app.post('/api/priorities')
def priorities(body:Priorities,request:Request):
    s=request.state.workspace
    if len({c.field for c in body.criteria})!=len(body.criteria):
        raise HTTPException(400,'Each criterion field must be unique.')
    if any(v is not None and (v<0 or v>100) for v in body.ratings.values()):
        raise HTTPException(400,'Ratings must be between 0 and 100, or unknown.')
    with s['lock']:
        allowed=summary(s)['matrix']['fields']
        if any(c.field not in allowed for c in body.criteria):
            raise HTTPException(400,'Choose criterion fields from the evidence table.')
        s.update(criteria=[c.model_dump() for c in body.criteria],ratings=body.ratings,notes=body.notes,brief_text='')
        return summary(s)

class Question(BaseModel):
    query:str=Field(min_length=1,max_length=2000)
    method:str='hybrid'
    k:int=Field(default=3,ge=1,le=10)
    generation:bool=False

@app.post('/api/ask')
def ask(body:Question,request:Request):
    s=request.state.workspace
    with s['lock']:
        if not s['documents']: raise HTTPException(400,'Add documents before searching.')
        if body.method not in ('semantic','keyword','hybrid'): raise HTTPException(400,'Choose semantic, keyword or hybrid.')
        try:
            needed=body.method!='keyword'
            if s['index'] is None or (needed and s['index'].vectors is None):
                s['index']=Index(chunk_documents(s['documents']),semantic=needed)
            start=time.perf_counter();chunks=s['index'].search(body.query,body.k,body.method)
            result=generate(body.query,chunks) if body.generation else evidence_answer(body.query,chunks)
            result['retrieval_ms']=round((time.perf_counter()-start)*1000,2)
            return result
        except RuntimeError as e:
            raise HTTPException(503,str(e)) from None
        except Exception:
            raise HTTPException(503,'Local model could not run. Use Keyword search; check setup and available memory. No paid fallback was used.') from None

class BriefEdit(BaseModel):
    text:str=Field(max_length=200000)
@app.post('/api/brief')
def save_brief(body:BriefEdit,request:Request):
    request.state.workspace['brief_text']=body.text
    return {'saved':True}

@app.get('/api/brief')
def get_brief(request:Request):
    s=request.state.workspace;data=summary(s)
    return {'text':s['brief_text'] or brief(data['matrix'],s['criteria'],data['scores'],s['notes'])}

@app.get('/api/export/{kind}')
def export(kind:str,request:Request):
    s=request.state.workspace;data=summary(s)
    if kind=='brief':
        content=s['brief_text'] or brief(data['matrix'],s['criteria'],data['scores'],s['notes'])
        mime='text/markdown';name='decisionlens-brief.md'
    elif kind=='json':
        content=json.dumps(data,indent=2,ensure_ascii=False);mime='application/json';name='decisionlens-evidence.json'
    elif kind=='csv':
        stream=io.StringIO();writer=csv.writer(stream)
        writer.writerow(['Product','Attribute','Value','Status','Confirmed','Source files','Source dates'])
        for c in data['matrix']['cells']:
            row=[c['product'],c['field'],c['value'] or '',c['status'],str(c['confirmed']),
                 '; '.join(e['name'] for e in c['evidence']),'; '.join(e['source_date'] or 'unknown' for e in c['evidence'])]
            writer.writerow(["'"+v if v.lstrip().startswith(('=','+','-','@','\t','\r')) else v for v in row])
        content=stream.getvalue();mime='text/csv';name='decisionlens-comparison.csv'
    else: raise HTTPException(404,'Unknown export format.')
    return Response(content,media_type=mime,headers={'Content-Disposition':f'attachment; filename="{name}"'})

app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
@app.get('/')
def home(): return FileResponse(ROOT/'static/index.html')
