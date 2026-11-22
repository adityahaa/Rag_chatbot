"""Local input parsing. Never execute HTML, macros, scripts or document instructions."""
from __future__ import annotations
import csv, hashlib, io, json, re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 10 * 1024 * 1024
MAX_CHARS = 500_000

class InputError(ValueError):
    pass

def safe_url(value: str) -> str:
    if not value:
        return ''
    p = urlsplit(value)
    if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
        raise InputError('Source links must be public HTTP(S) links without credentials.')
    # Links are metadata only: no server-side fetching / SSRF.
    return value

def parse_document(name: str, data: bytes, product: str = '', source_url: str = '',
                   source_date: str = '', synthetic: bool = False) -> dict:
    name = name.replace('\\', '/').split('/')[-1]
    if not data or len(data) > MAX_BYTES:
        raise InputError('Use a nonempty file smaller than 10 MB.')
    if source_date:
        try:
            date.fromisoformat(source_date)
        except ValueError:
            raise InputError('Source date must use YYYY-MM-DD.') from None
    source_url = safe_url(source_url)
    suffix = Path(name).suffix.lower()
    pages, warnings = [], []
    try:
        if suffix == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                raise InputError('Encrypted PDF: provide an unlocked, permitted copy.')
            if len(reader.pages) > 200:
                raise InputError('Use PDFs with at most 200 pages.')
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ''
                if text.strip():
                    pages.append({'page': i+1, 'section': f'Page {i+1}', 'text': text})
                else:
                    warnings.append(f'Page {i+1}: no extractable text; OCR is not included.')
        elif suffix == '.docx':
            from docx import Document
            import zipfile
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if sum(x.file_size for x in z.infolist()) > 25_000_000:
                    raise InputError('DOCX expanded size exceeds 25 MB.')
            doc = Document(io.BytesIO(data))
            text = '\n'.join(p.text for p in doc.paragraphs)
            text += '\n' + '\n'.join(' | '.join(c.text for c in row.cells) for t in doc.tables for row in t.rows)
            pages = [{'page': None, 'section': 'Document body and tables', 'text': text}]
            warnings.append('DOCX page numbers are unavailable; paragraph/table text is retained.')
        elif suffix in ('.txt', '.md', '.csv', '.json'):
            text = data.decode('utf-8-sig')
            if suffix == '.json':
                value = json.loads(text)
                if isinstance(value, dict):
                    text = '\n'.join(f'{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}' for k,v in value.items())
                else:
                    text = json.dumps(value, ensure_ascii=False, indent=2)
            elif suffix == '.csv':
                rows = list(csv.DictReader(io.StringIO(text)))
                if len(rows)>5000:
                    raise InputError('Use CSV files with at most 5,000 rows.')
                text = '\n\n'.join('\n'.join(f'{k}: {v}' for k,v in row.items()) for row in rows)
            pages = [{'page': None, 'section': 'Text / rows', 'text': text}]
        else:
            raise InputError('Supported: text PDF, UTF-8 TXT/MD/CSV/JSON, and DOCX. Scans need external OCR.')
    except InputError:
        raise
    except Exception:
        raise InputError('Could not read this file. Check its format, encoding, and whether it is damaged.') from None
    if not pages or not any(p['text'].strip() for p in pages):
        raise InputError('No readable text found. This may be a scanned PDF; OCR is not included.')
    if sum(len(p['text']) for p in pages)>MAX_CHARS:
        raise InputError('Extracted text exceeds 500,000 characters; split this document.')
    digest = hashlib.sha256(data).hexdigest()
    identity = json.dumps([digest, name, product, source_url, source_date, synthetic])
    return dict(id=hashlib.sha256(identity.encode()).hexdigest()[:16], name=name,
                product=(product.strip() or Path(name).stem)[:100], sha256=digest,
                source_url=source_url, source_date=source_date or None, synthetic=synthetic,
                pages=pages, warnings=warnings)

def chunk_documents(documents: list[dict], size: int = 1000, overlap: int = 200) -> list[dict]:
    if size < 100 or overlap < 0 or overlap >= size:
        raise ValueError('Require size >= 100 and 0 <= overlap < size.')
    chunks=[]
    for doc in documents:
        for page in doc['pages']:
            text=page['text']
            for start in range(0,len(text),size-overlap):
                content=text[start:start+size]
                if content.strip():
                    chunks.append(dict(id=f"{doc['id']}:{page['page'] or 0}:{start}", text=content,
                        doc_id=doc['id'], name=doc['name'], product=doc['product'],
                        source_url=doc['source_url'], source_date=doc['source_date'], synthetic=doc['synthetic'],
                        page=page['page'], section=page['section'], start=start, end=start+len(content)))
                if start+size >= len(text):
                    break
    return chunks
