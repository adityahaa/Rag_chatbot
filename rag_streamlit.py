"""Preserved Streamlit launch workflow, repaired for local session-only evidence."""
import json
from pathlib import Path
import streamlit as st
from decisionlens.documents import parse_document,chunk_documents,InputError
from decisionlens.evidence import extract_facts,matrix
from decisionlens.retrieval import Index
from decisionlens.decisions import brief

st.set_page_config(page_title='DecisionLens · Streamlit companion',page_icon='🔎',layout='wide')
st.title('DecisionLens')
st.caption('Streamlit companion · full review and vendor scoring dashboard: run Start.ps1')
st.info('Local only. No API key or paid provider. Synthetic demo values are fictional. Export to keep your work.')
if 'documents' not in st.session_state: st.session_state.documents=[]
with st.sidebar:
    st.header('Sources')
    product=st.text_input('Product name (blank uses filename)')
    files=st.file_uploader('Upload text documents',type=['pdf','txt','md','csv','json','docx'],accept_multiple_files=True)
    if st.button('Process documents'):
        try:
            additions=[parse_document(f.name,f.getvalue(),product=product) for f in files]
            if len(st.session_state.documents)+len(additions)>20: raise InputError('Use at most 20 documents.')
            st.session_state.documents+=additions
        except InputError as e: st.error(str(e))
    if st.button('Load synthetic demo'):
        root=Path(__file__).parent/'data/demo'
        st.session_state.documents=[parse_document(p.name,p.read_bytes(),product=name,synthetic=True,source_date='2026-10-01')
            for p,name in [(root/'sprintly.md','Sprintly'),(root/'forgeflow.md','ForgeFlow'),(root/'orbitdesk.md','OrbitDesk')]]
    method=st.selectbox('Retrieval',['hybrid','semantic','keyword'])
docs=st.session_state.documents
if docs:
    data=matrix(docs,extract_facts(docs))
    st.dataframe([{'Product':c['product'],'Attribute':c['field'],'Value':c['value'],'Status':c['status']} for c in data['cells']],use_container_width=True)
    st.download_button('Export evidence JSON',json.dumps(data,indent=2),'decisionlens-evidence.json','application/json')
    st.download_button('Export working brief',brief(data,[],[]),'decisionlens-brief.md','text/markdown')
    question=st.chat_input('Ask your evidence')
    if question:
        try:
            index=Index(chunk_documents(docs),semantic=method!='keyword')
            for c in index.search(question,3,method):
                st.caption(f"{c['name']} · page {c['page'] or 'n/a'} · {c['source_date'] or 'Date unknown'}")
                st.text(c['text'])
        except RuntimeError as e: st.error(str(e))
else: st.write('Add documents or load the synthetic demonstration to begin.')
