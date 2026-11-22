"""Download audited public data, pinned to source_manifest.json with integrity checks.

No account or AWS billing needed. Raw files remain ignored and are never packaged.
"""
import hashlib,json
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
def main():
    manifest=json.loads((ROOT/'data/source_manifest.json').read_text(encoding='utf-8'))
    for item in manifest['sources']:
        path=ROOT/'data/raw'/item['path']
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']:
            continue
        r=requests.get(item['url'],timeout=180);r.raise_for_status()
        if hashlib.sha256(r.content).hexdigest()!=item['sha256']:
            raise RuntimeError('Source changed: '+item['path']+'. Stop and audit a new dataset version before evaluation.')
        path.write_bytes(r.content)
    print('Verified',len(manifest['sources']),'public source files against the recorded hashes.')
if __name__=='__main__':main()
