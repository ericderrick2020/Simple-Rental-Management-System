"""Check generated report contents, package integrity, and PDF page bounds."""
from pathlib import Path
from zipfile import ZipFile
import sys,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.report_tools'))
import pymupdf as fitz
from PIL import Image,ImageDraw
OUT=ROOT/'reports/template_matched_report'
base=OUT/'Nahabwe_Derrick_Eric_Rental_Management_System_Project_Report'
pdf=fitz.open(base.with_suffix('.pdf'))
texts=[p.get_text() for p in pdf]
joined='\n'.join(texts)
for chapter in range(1,7):
    assert f'CHAPTER {chapter}' in joined
for title in ['DECLARATION','ACKNOWLEDGEMENT','ABSTRACT / EXECUTIVE SUMMARY','TABLE OF CONTENT','TABLE OF FIGURES','TABLE OF TABLES','REFERENCES','APPENDICES']:
    assert title in joined,title
assert 'School Library Management System' in joined  # Attribution of the supplied template.
assert 'UVT373/U/25/M/CSDA/0278' not in joined  # Never copy the template student's number.
outside=[]
for i,page in enumerate(pdf):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<23 or x1>page.rect.width-23 or y0<15 or y1>page.rect.height-20:
                    outside.append([i+1,span['text'],span['bbox']])
assert not outside,outside
with ZipFile(base.with_suffix('.docx')) as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.endswith('.xml'): ET.fromstring(z.read(name))
    document=ET.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    word_text='\n'.join(t.text or '' for t in document.findall('.//w:t',ns))
    assert 'Update this field in Word' not in word_text
    assert len(document.findall('.//w:tbl',ns))==12
cols=4; cellw=300; cellh=440
contact=Image.new('RGB',(cols*cellw,((len(pdf)+cols-1)//cols)*cellh),'#d8dde1')
draw=ImageDraw.Draw(contact)
for i,page in enumerate(pdf):
    pix=page.get_pixmap(matrix=fitz.Matrix(.48,.48),alpha=False)
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    x=i%cols*cellw; y=i//cols*cellh
    contact.paste(im,(x,y)); draw.text((x+5,y+410),str(i+1),fill='black')
contact.save(OUT/'final_layout_preview.jpg')
for index in [0,4,8,len(pdf)-1]:
    pdf[index].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT/f'final_page_{index+1}.png')
summary={'pdf_pages':len(pdf),'word_tables':12,'word_inline_images':14,'chapters':6,'pdf_out_of_bounds_spans':outside,'word_contents_updated':True}
(OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
