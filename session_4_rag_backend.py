"""Repaired local successor; original backend is preserved in legacy/.

Retains parse -> chunk -> index -> retrieve workflow, with source metadata and
in-memory indexes. The original Chroma/Gemini code remains archived for audit.
"""
from pathlib import Path
from decisionlens.documents import parse_document, chunk_documents
from decisionlens.retrieval import Index
from decisionlens.generation import generate

def parse_pdf(pdf_path):
    doc=parse_document(Path(pdf_path).name,Path(pdf_path).read_bytes())
    return '\n'.join(p['text'] for p in doc['pages'])

def create_document_chunks(text,chunk_size=1000,chunk_overlap=200):
    doc=parse_document('text.txt',text.encode())
    return [c['text'] for c in chunk_documents([doc],chunk_size,chunk_overlap)]

def store_embeddings(embedding_model,text_chunks,collection_name='session',persist_directory=None,metadatas=None):
    if metadatas is None or len(metadatas)!=len(text_chunks):
        raise ValueError('Supply one source-metadata record per chunk.')
    chunks=[dict(metadata,id=f'{collection_name}:{i}',text=text,
                 product=metadata.get('product','Document'),name=metadata.get('source','Document'))
            for i,(text,metadata) in enumerate(zip(text_chunks,metadatas))]
    return Index(chunks,semantic=True)

def get_context_from_chunks(chunks,splitter='\n\n---\n\n'):
    return splitter.join(f"[{i+1}] {c.get('name','Document')} page {c.get('page','n/a')}: {c['text']}" for i,c in enumerate(chunks))

def query_with_full_context(query,vectorstore,model_name='local-extractive',k=3,temperature=0):
    chunks=vectorstore.search(query,k,'semantic')
    answer=generate(query,chunks)['text'] if model_name=='google/flan-t5-small' else 'Retrieved evidence:\n'+get_context_from_chunks(chunks)
    return answer,get_context_from_chunks(chunks),chunks
