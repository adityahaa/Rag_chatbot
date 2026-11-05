import io
import pytest
from decisionlens.documents import parse_document,chunk_documents,InputError,safe_url
from decisionlens.evidence import extract_facts,matrix
from decisionlens.decisions import score
from decisionlens.retrieval import Index

def document(text='Price: USD 10 per month\nSSO: Included',**kwargs):
    return parse_document('example.md',text.encode(),product='Example',**kwargs)

def test_page_source_and_chunks():
    d=document(source_date='2026-10-01',source_url='https://example.org/docs')
    c=chunk_documents([d])[0]
    assert c['source_date']=='2026-10-01' and c['name']=='example.md'
    assert c['source_url']=='https://example.org/docs' and c['page'] is None
    assert c['text']==d['pages'][0]['text']

def test_real_text_pdf_and_blank_detection():
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
    writer=PdfWriter();page=writer.add_blank_page(width=612,height=792)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
    stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 50 700 Td (SSO: SAML included) Tj ET')
    page[NameObject('/Contents')]=writer._add_object(stream)
    output=io.BytesIO();writer.write(output)
    doc=parse_document('sample.pdf',output.getvalue(),product='PDF product')
    assert 'SAML included' in doc['pages'][0]['text']
    assert extract_facts([doc])[0]['page']==1
    writer=PdfWriter();writer.add_blank_page(width=612,height=792);output=io.BytesIO();writer.write(output)
    with pytest.raises(InputError,match='No readable text'):parse_document('scan.pdf',output.getvalue())

@pytest.mark.parametrize('name,data',[('a.png',b'image'),('a.pdf',b'broken'),('a.txt',b''),('a.txt',b'\xff')])
def test_reject_bad_documents(name,data):
    with pytest.raises(InputError):parse_document(name,data)

@pytest.mark.parametrize('link',['javascript:alert(1)','file:///C:/private','https://user:password@example.com'])
def test_unsafe_source_links(link):
    with pytest.raises(InputError):safe_url(link)

def test_unknown_is_missing_and_conflict_keeps_both_sources():
    a=document('SSO: Unknown\nPrice: USD 10')
    b=parse_document('new.md',b'Price: USD 12',product='Example')
    m=matrix([a,b],extract_facts([a,b]))
    assert next(c for c in m['cells'] if c['field']=='SSO')['value'] is None
    price=next(c for c in m['cells'] if c['field']=='Price')
    assert price['status']=='conflict' and len(price['evidence'])==2

def test_score_excludes_unknown_and_unconfirmed():
    d=document();facts=extract_facts([d]);criteria=[{'field':'SSO','weight':60,'requirement':'included'},{'field':'Price','weight':40,'requirement':'budget'}]
    m=matrix([d],facts,{'Example::SSO':{'value':'Included','note':'Checked source','confirmed':True}})
    s=score(m,criteria,{'Example::SSO':100,'Example::Price':0})[0]
    assert s['score']==100 and s['coverage']==60 and not s['complete']
    m=matrix([d],facts);assert score(m,criteria,{'Example::SSO':100})[0]['score'] is None

def test_keyword_retrieval_uses_actual_evidence():
    docs=[document('SSO: SAML included'),parse_document('other.txt',b'Gardening: watering flowers',product='Other')]
    index=Index(chunk_documents(docs),semantic=False)
    assert index.search('SAML',1,'keyword')[0]['product']=='Example'
    with pytest.raises(RuntimeError):index.search('SAML',1,'semantic')

def test_json_csv_docx():
    assert extract_facts([parse_document('a.json',b'{"SSO":"Included"}')])[0]['field']=='SSO'
    assert extract_facts([parse_document('a.csv',b'SSO,Support\nIncluded,Email')])[0]['value']=='Included'
    from docx import Document
    doc=Document();doc.add_paragraph('SSO: SAML included');out=io.BytesIO();doc.save(out)
    assert extract_facts([parse_document('a.docx',out.getvalue())])[0]['value']=='SAML included'

def test_json_null_is_unknown_but_zero_is_an_actual_value():
    d=parse_document('data.json',b'{"SSO": null, "Price": 0}')
    facts=extract_facts([d])
    assert not any(f['field']=='SSO' for f in facts)
    assert next(f for f in facts if f['field']=='Price')['value']=='0'
