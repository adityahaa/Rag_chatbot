"""Credential-free reproducible source package, with original public history bundle."""
import hashlib,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DENIED={'.git','.venv','.cache','models','__pycache__','.pytest_cache','uploads','chroma_db','streamlit_chroma_db'}
def included(path):
    relative=path.relative_to(ROOT)
    return not (set(relative.parts)&DENIED or relative.parts[:2] in (('data','raw'),('data','derived')) or
        path.name.startswith('.env') or path.suffix in ('.log','.part') or 'private' in path.name.lower())
def main():
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and included(p))
    secret_patterns=[re.compile(rb'AIza[0-9A-Za-z_-]{30,}'),re.compile(rb'gh[pousr]_[0-9A-Za-z]{30,}'),
        re.compile(rb'sk-[A-Za-z0-9_-]{25,}'),re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
    for p in files:
        if p.suffix not in ('.jpg','.png','.pdf','.bundle'):
            content=p.read_bytes()
            if any(pattern.search(content) for pattern in secret_patterns):
                raise RuntimeError('Potential credential found in '+str(p.relative_to(ROOT))+'. Package stopped; no value printed.')
    manifest={'files':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files if p.name!='PACKAGE_MANIFEST.json'],
        'exclusions':sorted(DENIED|{'data/raw','data/derived','.env*','*.log','*.part','private*'}),
        'credential_scan':'No matching Google/GitHub/OpenAI token or private-key patterns found; no exhaustive secret-detection guarantee.',
        'original_history':'history/original-rag-chatbot.bundle'}
    (ROOT/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and included(p))
    dest=ROOT.parent/'DecisionLens-source.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,'DecisionLens/'+str(p.relative_to(ROOT)).replace('\\','/'))
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert not any('/models/' in n or '/data/raw/' in n or '/.venv/' in n or '/.env' in n for n in z.namelist())
    print('Created',dest.name,'files:',len(files),'bytes:',dest.stat().st_size)
    print('SHA-256:',hashlib.sha256(dest.read_bytes()).hexdigest())
if __name__=='__main__':main()
