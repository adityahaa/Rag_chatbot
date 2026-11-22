"""Download public Apache-2.0 models once; app inference never calls Hugging Face."""
import argparse, hashlib, json, os, sys
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
def prepare(generation=False):
    manifest_path=ROOT/'models_manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    models=[('minilm','sentence-transformers/all-MiniLM-L6-v2',[
        'config.json','modules.json','sentence_bert_config.json','config_sentence_transformers.json',
        'tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.txt',
        'model.safetensors','1_Pooling/config.json','README.md'])]
    if generation:
        models.append(('flan-t5-small','google/flan-t5-small',[
            'config.json','generation_config.json','tokenizer.json','tokenizer_config.json',
            'special_tokens_map.json','spiece.model','model.safetensors','README.md']))
    for folder,repo,files in models:
        record=manifest.get(folder,{})
        revision=record.get('revision')
        if not revision:
            r=requests.get('https://huggingface.co/api/models/'+repo,timeout=60);r.raise_for_status()
            revision=r.json()['sha']
        checks={}
        for f in files:
            path=ROOT/'models'/folder/f;path.parent.mkdir(parents=True,exist_ok=True)
            expected=record.get('files',{}).get(f)
            if path.exists() and (not expected or hashlib.sha256(path.read_bytes()).hexdigest()==expected):
                checks[f]=hashlib.sha256(path.read_bytes()).hexdigest();continue
            response=requests.get(f'https://huggingface.co/{repo}/resolve/{revision}/{f}',timeout=180,stream=True)
            if response.status_code==404 and f in ('config_sentence_transformers.json','generation_config.json','special_tokens_map.json'):
                continue
            response.raise_for_status()
            part=path.with_suffix(path.suffix+'.part')
            with part.open('wb') as output:
                for block in response.iter_content(1024*1024):
                    output.write(block)
            digest=hashlib.sha256(part.read_bytes()).hexdigest()
            if expected and expected != digest:
                raise RuntimeError('Downloaded model hash mismatch: '+f)
            part.replace(path);checks[f]=digest
        manifest[folder]={'repo':repo,'revision':revision,'license':'Apache-2.0','files':checks,'downloaded':'2026-11-04'}
        manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        print('Prepared local model:',repo,revision,flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--generation',action='store_true')
    prepare(parser.parse_args().generation)
