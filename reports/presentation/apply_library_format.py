"""Apply the supplied slide template to the approved rental presentation."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.dom import minidom
import xml.etree.ElementTree as E
import sys, posixpath, json, copy

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.report_tools'))
from PIL import Image,ImageDraw,ImageFont

TEMPLATE=Path('C:/Users/NAHABWE/Downloads/School_Library_Management_System_Presentation.pptx')
SOURCE=ROOT/'Nahabwe_Derrick_Eric_Rental_Management_System_Phase3_Simple.pptx'
OUTPUT=ROOT/'Nahabwe_Derrick_Eric_Rental_Management_System_Phase3_Formatted.pptx'
PREVIEW=ROOT/'reports/presentation/formatted_preview'
PREVIEW.mkdir(exist_ok=True)
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
R='http://schemas.openxmlformats.org/package/2006/relationships'

# Reuse actual template slides: preserve their shapes, colours, fonts and spacing.
SLIDES=[
 (1,{2:'Rental Management System',3:[
    'A Python desktop app for properties, tenants and rent records',' ',
    'Nahabwe Derrick Eric | Certificate in Software Development with AI',
    'Sai Pali Institute of Technology and Management | Instructor: Ajwadh Jalal']}),
 (2,{0:'About the project',2:'A desktop app that helps landlords and property managers keep property details, tenant records and rent payments in one place.',
     4:'Platform',5:'Desktop app',7:'Technology',8:'Python, Tkinter, MySQL',10:'Users',11:'Landlords and managers',13:'Scope',14:'Local rental records',15:'Main sections',16:'Dashboard | Properties | Tenants | Payments | Settings'}),
 (3,{0:'The problem and project goals',2:'Paper records can be lost and are hard to update. Separate files make it difficult to check tenant details, rent paid and the balance due. The goal is to keep related records in one app.',
     6:'Properties',7:'Keep property and unit details.',11:'Tenants',12:'Link each tenant to a property and unit.',16:'Rent payments',17:'Record rent paid and the balance due.'}),
 (9,{0:'What the project covers',2:'Planned features',3:[
     'Property and tenant records', 'Rent payments and lease tracking',
     'Search, reports and exports', 'Login, input checks and MySQL storage'],
     5:'Outside this project',6:[
     'Web and mobile apps', 'Cloud storage and multiple companies',
     'Online payment processing', 'Fingerprint login and rent predictions'],
     7:'Some planned features still need to be completed.'}),
 (6,{0:'How the system works',3:'Startup',4:'main.py',5:'Starts the app, changes pages and handles logout',
     9:'Screens',10:'pages/ + components/',11:'Shows forms and tables; checks entries before saving',
     15:'Data functions',16:'data/database.py',17:'Saves records and reads them back',
     21:'Storage',22:'MySQL',23:'Property, tenant, payment, user and settings tables',
     24:'The forms check entries, then call the database functions to save or read records.'}),
 (2,{0:'Tools used',2:'Python runs the app, Tkinter creates the screens, and MySQL stores the related records. The current app runs on Windows.',
     4:'Language',5:'Python',7:'Interface',8:'Tkinter and ttk',10:'Database',11:'MySQL + connector',13:'System',14:'Windows',15:'Project tools',16:'VS Code was the editor proposed for the project.'}),
 (5,{0:'Features added so far',4:'Properties',5:'Add and view properties and their unit counts.',
     9:'Tenants',10:'Register and view tenants linked to a property.',14:'Rent payments',15:'Record rent paid, balances and payment details.',
     19:'Text receipts',20:'Create a receipt for a selected payment.',24:'Dashboard and settings',25:'View summaries and save company preferences.',
     29:'Logout',30:'Close old pages and require sign-in again.'}),
 (8,{0:'System demonstration',4:'Sign in',8:'Add a property',12:'Register a tenant',16:'Record rent paid',20:'Log out and sign in again',
     21:'Payment example',23:'Rent: 500,000',25:'Balance: 150,000',27:'Paid: 350,000',29:'Check bad input',31:'Save and reopen'}),
 (5,{0:'Test results',4:'10 code checks',5:'Checked syntax and selected login, payment and date functions.',
     9:'3 logout checks',10:'Checked closing old pages and signing in again.',
     14:'13 passed',15:'All 13 selected checks passed. None failed.',
     19:'Payment example',20:'500,000 minus 150,000 gives 350,000 paid.',
     24:'Invalid balance',25:'A balance below zero or above the rent is blocked.',
     29:'Still to test',30:'Live database saving, reopening records and physical printing.'}),
 (4,{0:'Problems and how they were handled',1:'The code links records, checks payment entries and clears old screens when the user logs out.',
     3:'Linking rental records',6:'Use IDs to link properties, tenants and payments.',
     8:'Wrong payment details',11:'Check the amount, balance and date before saving.',
     13:'Old screens after logout',16:'Close old pages and forms, then show login.'}),
 (9,{0:'What I achieved and what is next',2:'What is in place',3:[
     'A desktop app for rental records', 'Property, tenant and payment entry',
     'Text receipts, dashboard and settings', 'Logout and selected passing checks'],
     5:'Next steps',6:[
     'Improve login and test the live database', 'Finish editing, search and lease tracking',
     'Complete reports and exports', 'Keep payment history after deletion'],
     7:'The project is a working prototype with more features still to finish.'}),
 (1,{2:'Thank you',3:[
     'That is my Rental Management System. Any questions?',' ',
     'Next: a short demonstration',
     'Nahabwe Derrick Eric | Python, Tkinter and MySQL']}),
]

# The user has since shortened the approved source to nine slides.
# Preserve that current scope instead of restoring removed sections.
SLIDES=SLIDES[:8]+[SLIDES[-1]]
SLIDES[2]=(5,{0:'The problem and project goals',
    4:'The problem',5:'Paper records can be lost and are hard to update.',
    9:'Properties',10:'Keep property and unit details in one place.',
    14:'Tenants',15:'Record tenants and their assigned units.',
    19:'Rent and leases',20:'Track payments, balances and rental agreements.',
    24:'Database',25:'Store related records in MySQL.',
    29:'Reports and checks',30:'Show summaries and check entries before saving.'})
SLIDES[3][1][7]='A local desktop app for landlords and property managers.'
SLIDES[5]=(3,{0:'Tools used',2:'Python runs the application, Tkinter creates the screens, and MySQL stores the related records.',
    6:'Python',7:'Runs the app and its calculations.',
    11:'Tkinter',12:'Creates windows, forms and tables.',
    16:'MySQL',17:'Stores records; the connector links it to Python.'})

def replace(shape,value):
    body=shape.getElementsByTagName('p:txBody')[0]
    old=list(body.getElementsByTagName('a:p'))
    lines=value if isinstance(value,list) else value.split('\n')
    for paragraph in old: body.removeChild(paragraph)
    for i,line in enumerate(lines):
        paragraph=old[min(i,len(old)-1)].cloneNode(True)
        runs=paragraph.getElementsByTagName('a:r')
        run=runs[0].cloneNode(True) if runs else body.ownerDocument.createElement('a:r')
        for child in list(paragraph.childNodes):
            if child.nodeType==child.ELEMENT_NODE and child.tagName!='a:pPr': paragraph.removeChild(child)
        for child in list(run.childNodes):
            if child.nodeType==child.ELEMENT_NODE and child.tagName!='a:rPr': run.removeChild(child)
        text=body.ownerDocument.createElement('a:t'); text.appendChild(body.ownerDocument.createTextNode(line))
        run.appendChild(text); paragraph.appendChild(run); body.appendChild(paragraph)

def xml(doc):return doc.toxml(encoding='UTF-8')

def build():
    with ZipFile(TEMPLATE) as template,ZipFile(SOURCE) as source:
        parts={n:template.read(n) for n in template.namelist()
               if not n.startswith(('ppt/slides/','ppt/notesSlides/','docProps/thumbnail'))}
        # Keep the source's slide IDs, current slide order and speaker notes.
        pres=minidom.parseString(source.read('ppt/presentation.xml'))
        size=pres.getElementsByTagName('p:sldSz')[0]; size.setAttribute('cx','9144000');size.setAttribute('cy','5143500')
        parts['ppt/presentation.xml']=xml(pres)
        parts['ppt/_rels/presentation.xml.rels']=source.read('ppt/_rels/presentation.xml.rels')
        parts['docProps/core.xml']=source.read('docProps/core.xml')
        app=minidom.parseString(source.read('docProps/app.xml'))
        if app.getElementsByTagName('Slides'):app.getElementsByTagName('Slides')[0].firstChild.data=str(len(SLIDES))
        parts['docProps/app.xml']=xml(app)
        for i,(layout,replacements) in enumerate(SLIDES,1):
            doc=minidom.parseString(template.read(f'ppt/slides/slide{layout}.xml'))
            shapes=doc.getElementsByTagName('p:sp')
            for index,value in replacements.items():replace(shapes[index],value)
            if layout!=1:replace(shapes[len(shapes)-1],str(i))
            doc.getElementsByTagName('p:cSld')[0].setAttribute('name',f'Rental slide {i}')
            parts[f'ppt/slides/slide{i}.xml']=xml(doc)
            rels=minidom.parseString(template.read(f'ppt/slides/_rels/slide{layout}.xml.rels'))
            for rel in rels.getElementsByTagName('Relationship'):
                if rel.getAttribute('Type').endswith('/notesSlide'):rel.setAttribute('Target',f'../notesSlides/notesSlide{i}.xml')
            parts[f'ppt/slides/_rels/slide{i}.xml.rels']=xml(rels)
            parts[f'ppt/notesSlides/notesSlide{i}.xml']=source.read(f'ppt/notesSlides/notesSlide{i}.xml')
            parts[f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels']=source.read(f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels')
        types=minidom.parseString(template.read('[Content_Types].xml'))
        for override in list(types.getElementsByTagName('Override')):
            if override.getAttribute('PartName').startswith(('/ppt/slides/','/ppt/notesSlides/')):
                override.parentNode.removeChild(override)
        for i in range(1,len(SLIDES)+1):
            for folder,name,kind in [('slides','slide','slide'),('notesSlides','notesSlide','notesSlide')]:
                el=types.createElement('Override');el.setAttribute('PartName',f'/ppt/{folder}/{name}{i}.xml')
                el.setAttribute('ContentType',f'application/vnd.openxmlformats-officedocument.presentationml.{kind}+xml');types.documentElement.appendChild(el)
        parts['[Content_Types].xml']=xml(types)
        # Remove relationships to thumbnails not included in the new package.
        rootrels=minidom.parseString(parts['_rels/.rels'])
        for rel in list(rootrels.getElementsByTagName('Relationship')):
            if rel.getAttribute('Type').endswith('/thumbnail'):rel.parentNode.removeChild(rel)
        parts['_rels/.rels']=xml(rootrels)
        with ZipFile(OUTPUT,'w',ZIP_DEFLATED) as out:
            for name,data in parts.items():out.writestr(name,data)
    validate()

def validate():
    with ZipFile(OUTPUT) as z:
        assert z.testzip() is None
        names=set(z.namelist())
        for name in names:
            if name.endswith(('.xml','.rels')): E.fromstring(z.read(name))
            if name.endswith('.rels'):
                base=posixpath.dirname(posixpath.dirname(name))
                for rel in E.fromstring(z.read(name)):
                    if rel.get('TargetMode')=='External':continue
                    target=rel.get('Target')
                    path=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(base,target))
                    assert path in names,(name,path)
        for i in range(1,len(SLIDES)+1):
            text=' '.join(E.fromstring(z.read(f'ppt/slides/slide{i}.xml')).itertext())
            assert not any(term in text for term in ['Namwanje','ISBN','librarian','Borrowed','book_copies'])
        print(f'Validated: {len(SLIDES)} slides, matching speaker-note pages, and all package relationships.')

# Render a local preview directly from slide geometry for visual checking.
# PowerPoint remains fully editable; previews are not inserted into the deck.
def previews(path,label):
    issues=[]; pics=[]
    with ZipFile(path) as z:
        theme=E.fromstring(z.read('ppt/theme/theme1.xml'))
        palette={c.tag.split('}')[-1]:c[0].get('val',c[0].get('lastClr','FFFFFF')) for c in theme.find('.//a:clrScheme',NS)}
        cmap=E.fromstring(z.read('ppt/slideMasters/slideMaster1.xml')).find('p:clrMap',NS).attrib
        def colour(fill,default=None):
            if fill is None:return default
            s=fill.find('a:schemeClr',NS);r=fill.find('a:srgbClr',NS)
            return '#'+(palette.get(cmap.get(s.get('val'),s.get('val')),'000000') if s is not None else r.get('val') if r is not None else '000000')
        count=len([n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')])
        scale=160; factor=scale/914400
        for i in range(1,count+1):
            doc=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
            rels=E.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
            layout=next(r.get('Target') for r in rels if r.get('Type').endswith('/slideLayout'))
            layout=E.fromstring(z.read(posixpath.normpath(posixpath.join('ppt/slides',layout))))
            bg=doc.find('.//p:bg/p:bgPr/a:solidFill',NS)
            if bg is None:bg=layout.find('.//p:bg/p:bgPr/a:solidFill',NS)
            im=Image.new('RGB',(1600,900),colour(bg,'#F4F6FB'));d=ImageDraw.Draw(im)
            inherited=[s for s in layout.findall('.//p:sp',NS) if s.find('p:txBody',NS) is None]
            for index,s in enumerate(inherited+doc.findall('.//p:sp',NS)):
                sp=s.find('p:spPr',NS);xf=sp.find('a:xfrm',NS)
                if xf is None:continue
                off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
                x,y=float(off.get('x'))*factor,float(off.get('y'))*factor
                w,h=float(ext.get('cx'))*factor,float(ext.get('cy'))*factor
                fill=colour(sp.find('a:solidFill',NS)); line=colour(sp.find('a:ln/a:solidFill',NS))
                geom=sp.find('a:prstGeom',NS);kind=geom.get('prst') if geom is not None else 'rect'
                if fill or line:
                    box=(x,y,x+w,y+h)
                    if kind=='ellipse':d.ellipse(box,fill=fill,outline=line,width=1)
                    elif kind=='roundRect':d.rounded_rectangle(box,radius=min(w,h)*.1,fill=fill,outline=line,width=1)
                    else:d.rectangle(box,fill=fill,outline=line,width=1)
                tx=s.find('p:txBody',NS)
                if tx is None:continue
                body=tx.find('a:bodyPr',NS);margin=[float(body.get(a,'0'))*factor for a in ['lIns','tIns','rIns','bIns']]
                lines=[]
                for para in tx.findall('a:p',NS):
                    text=''.join(t.text or '' for t in para.findall('.//a:t',NS))
                    rp=para.find('a:r/a:rPr',NS)
                    if rp is None:continue
                    size=float(rp.get('sz','1200'))/100
                    bold=rp.get('b')=='1';latin=rp.find('a:latin',NS)
                    fontname=latin.get('typeface') if latin is not None else 'Georgia' if size>=26 else 'Calibri'
                    fn=('georgiab.ttf' if bold else 'georgia.ttf') if fontname=='Georgia' else ('calibrib.ttf' if bold else 'calibri.ttf')
                    font=ImageFont.truetype('C:/Windows/Fonts/'+fn,round(size/72*scale))
                    available=w-margin[0]-margin[2];current='';wrapped=[]
                    for word in text.split():
                        cand=(current+' '+word).strip()
                        if d.textlength(cand,font=font)>available and current:wrapped.append(current);current=word
                        else:current=cand
                    wrapped.append(current)
                    pp=para.find('a:pPr',NS);align=pp.get('algn','l') if pp is not None else 'l'
                    for line_text in wrapped:lines.append((line_text,font,colour(rp.find('a:solidFill',NS),'#1F2430'),size/72*scale*1.16,align))
                total=sum(l[3] for l in lines)
                if total>h-margin[1]-margin[3]+5:issues.append({'slide':i,'shape':index,'height':round(h),'text_height':round(total)})
                yy=y+margin[1]+(max(0,(h-margin[1]-margin[3]-total)/2) if body.get('anchor')=='ctr' else 0)
                for text,font,c,leading,align in lines:
                    xx=x+margin[0]
                    if align=='ctr':xx=x+(w-d.textlength(text,font=font))/2
                    d.text((xx,yy),text,font=font,fill=c,anchor='lt'); yy+=leading
            im.save(PREVIEW/f'{label}_{i:02}.png');pics.append(im)
    sheet=Image.new('RGB',(1200,((len(pics)+2)//3)*245),'#d9dee5')
    for i,im in enumerate(pics):sheet.paste(im.resize((400,225)),(i%3*400,i//3*245))
    sheet.save(PREVIEW/f'{label}_overview.jpg')
    return issues

if __name__=='__main__':
    build()
    previews(TEMPLATE,'reference')
    issues=previews(OUTPUT,'rental')
    (PREVIEW/'layout_checks.json').write_text(json.dumps(issues,indent=2),encoding='utf-8')
    print('Potential text overflow:',issues)
    print('Created:',OUTPUT.name)
