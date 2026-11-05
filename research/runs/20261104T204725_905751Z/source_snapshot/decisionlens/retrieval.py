"""Pretrained local embeddings, BM25 and equal-weight reciprocal rank fusion."""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
from pathlib import Path
import math, re, threading
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODEL_PATH=ROOT/'models'/'minilm'
MODEL_ID='sentence-transformers/all-MiniLM-L6-v2'
_MODEL_LOCK=threading.Lock()

def tokens(text):
    return re.findall(r'[\w]+',text.lower())

@lru_cache(maxsize=1)
def encoder():
    if not (MODEL_PATH/'config.json').exists():
        raise RuntimeError('Local semantic model missing. Run Setup.ps1 (or scripts/prepare_models.py). Choose Keyword to work without it.')
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(2)
    return SentenceTransformer(str(MODEL_PATH),device='cpu',local_files_only=True,trust_remote_code=False)

def encode(texts):
    with _MODEL_LOCK:
        return encoder().encode(texts,normalize_embeddings=True,show_progress_bar=False,batch_size=32)

class Index:
    def __init__(self,chunks,semantic=True):
        self.chunks=chunks
        self.terms=[Counter(tokens(c['product']+' '+c['text'])) for c in chunks]
        self.length=np.array([sum(t.values()) for t in self.terms],dtype=float)
        self.avg=float(self.length.mean()) if len(self.length) else 1
        self.df=Counter(t for terms in self.terms for t in terms)
        self.vectors=encode([c['product']+' '+c['text'] for c in chunks]) if semantic and chunks else None

    def keyword_scores(self,query):
        scores=np.zeros(len(self.chunks))
        for term in set(tokens(query)):
            n=self.df.get(term,0)
            idf=math.log(1+(len(self.chunks)-n+.5)/(n+.5))
            tf=np.array([t.get(term,0) for t in self.terms],dtype=float)
            scores += idf*tf*2.5/(tf+1.5*(.25+.75*self.length/(self.avg or 1)))
        return scores

    def search(self,query,k=3,method='hybrid'):
        if method not in ('semantic','keyword','hybrid'):
            raise ValueError('Unknown retrieval method.')
        if not self.chunks:
            return []
        lex=self.keyword_scores(query)
        if method != 'keyword':
            if self.vectors is None:
                raise RuntimeError('Semantic index is unavailable; explicitly select Keyword or prepare the local model.')
            dense=self.vectors @ encode([query])[0]
        if method=='semantic':
            scores=dense
        elif method=='keyword':
            scores=lex
        else:
            scores=np.zeros(len(self.chunks))
            # RRF includes ranks from both methods over the same corpus; ties stable by input order.
            for values in (dense,lex):
                for rank,i in enumerate(np.argsort(-values,kind='stable')):
                    scores[i]+=1/(60+rank+1)
        chosen=np.argsort(-scores,kind='stable')[:k]
        return [dict(self.chunks[i],retrieval_score=float(scores[i]),method=method) for i in chosen]
