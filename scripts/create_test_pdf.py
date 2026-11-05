"""Create a deliberately synthetic single-page PDF for browser upload verification."""
from pathlib import Path
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
def create(path):
    writer=PdfWriter();page=writer.add_blank_page(width=612,height=792)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
    lines=['Beacon - SYNTHETIC TEST DOCUMENT','All names and values are invented.',
        'Price: USD 15 per user/month, monthly billing','SSO: SAML included','Data residency: EU',
        'Support: Email on weekdays','Limitations: Maximum 20 projects','Intended users: Small engineering teams']
    text='BT /F1 12 Tf 50 740 Td 20 TL '+' Tj T* '.join('('+v+')' for v in lines)+' Tj ET'
    stream=DecodedStreamObject();stream.set_data(text.encode('ascii'));page[NameObject('/Contents')]=writer._add_object(stream)
    writer.write(str(path))
if __name__=='__main__':create(Path(__file__).resolve().parents[1]/'data/demo/beacon-synthetic.pdf')
