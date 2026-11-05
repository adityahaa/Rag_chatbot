from fastapi.testclient import TestClient
from decisionlens.server import app

def test_document_to_review_score_export_and_isolation():
    with TestClient(app) as a,TestClient(app) as b:
        r=a.post('/api/upload',files=[('files',('A.txt',b'SSO: SAML included\nPrice: USD 10','text/plain'))],data={'product':'A','source_date':'2026-10-01'})
        assert r.status_code==200,r.text
        assert b.get('/api/state').json()['documents']==[]
        r=a.post('/api/review',json={'key':'A::SSO','value':'SAML included','confirmed':True,'note':'Verified scope from uploaded A.txt'})
        assert r.status_code==200
        r=a.post('/api/priorities',json={'criteria':[{'field':'SSO','requirement':'SAML required','weight':100}],'ratings':{'A::SSO':100},'notes':'test'})
        assert r.json()['scores'][0]['score']==100
        assert 'A.txt' in a.get('/api/export/brief').text
        assert a.get('/api/export/csv').status_code==200
        assert a.get('/api/export/json').json()['matrix']['products']==['A']
        a.post('/api/brief',json={'text':'# Reviewed decision\nMy decision.'})
        assert a.get('/api/export/brief').text=='# Reviewed decision\nMy decision.'
        assert a.post('/api/ask',json={'query':'SSO','method':'keyword'}).json()['citations'][0]['name']=='A.txt'
        a.post('/api/reset');assert a.get('/api/state').json()['documents']==[]

def test_errors_and_csrf_and_formula_export():
    with TestClient(app) as c:
        assert c.post('/api/demo',headers={'Origin':'https://evil.example'}).status_code==403
        assert c.post('/api/upload',files={'files':('scan.pdf',b'not pdf')}).status_code==400
        c.post('/api/upload',files={'files':('A.txt',b'SSO: =HYPERLINK("evil")')},data={'product':'A'})
        assert "'=HYPERLINK" in c.get('/api/export/csv').text
        assert c.post('/api/review',json={'key':'A::SSO','value':'X','confirmed':True}).status_code==400
        assert c.post('/api/priorities',json={'criteria':[{'field':'SSO','requirement':'x','weight':100}],'ratings':{'A::SSO':101}}).status_code==400
        assert c.get('/').headers['x-content-type-options']=='nosniff'
        assert c.post('/api/ask',json={'query':'x','method':'invented'}).status_code==400

def test_public_case_unknown_dates_and_permitted_note_sources():
    with TestClient(app) as c:
        state=c.post('/api/case').json()
        assert len(state['documents'])==3
        assert all(d['source_date'] is None and d['source_url'].startswith('https://') for d in state['documents'])
        assert set(state['matrix']['products'])=={'GitHub Enterprise Cloud','GitLab.com Premium'}

def test_duplicate_upload_batch_deduplicated_and_edit_not_mislabelled():
    with TestClient(app) as c:
        r=c.post('/api/upload',files=[('files',('same.txt',b'SSO: included')),('files',('same.txt',b'SSO: included'))])
        assert len(r.json()['documents'])==1
        r=c.post('/api/review',json={'key':'same::SSO','value':'changed by user','note':'draft review','confirmed':False})
        cell=next(x for x in r.json()['matrix']['cells'] if x['field']=='SSO')
        assert cell['status']=='edited' and cell['evidence'][0]['value']=='included'
