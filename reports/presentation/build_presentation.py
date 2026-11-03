"""Build the separate Part B deck, PDF slides, and presentation notes."""
from pathlib import Path
import sys
import os
import json
import math
import textwrap
import time
from contextlib import ExitStack
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(os.environ['TEMP'])/'rms-presentation-tools'))
from PIL import Image,ImageDraw,ImageFont,ImageGrab
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

OUT=Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
NAVY='#15354D';TEAL='#087F8C';WHITE='#FFFFFF';INK='#243B53';MUTED='#526577';PALE='#EDF3F7';AMBER='#9D6200'
prs=Presentation();prs.slide_width=Inches(13.333333);prs.slide_height=Inches(7.5)
prs.core_properties.title='Rental Management System — Phase 3 Presentation'
prs.core_properties.author='Nahabwe Derrick Eric'
FONTS=Path('C:/Windows/Fonts')
notes=[];images=[]


def capture():
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
    import main
    from config.settings import DEFAULT_PASSWORD
    from data.database import DEFAULT_APP_SETTINGS
    summary=dict(property_count=1,total_units=10,tenant_count=1,expected_rent=500000,paid_rent=350000,
                 payment_status_counts={'Paid':1},overdue_tenants=0,recent_payments=[dict(tenant_name='Sample Tenant',property_name='Sample Apartments',unit_number='A1',amount=350000,status='Paid')],recent_tenants=[])
    replacements={
        'main.initialize_database':True,
        'pages.dashboard_page.get_dashboard_summary':summary,
        'pages.properties_page.get_properties':[],
        'pages.tenants_page.get_tenants':[],
        'pages.payments_page.get_payments':[],
        'pages.settings_page.get_app_settings':DEFAULT_APP_SETTINGS.copy(),
        'pages.settings_page.get_account_settings':dict(role='Administrator',last_password_change='Sample account',two_factor_login='Not enabled'),
    }
    with ExitStack() as stack:
        for name,value in replacements.items():stack.enter_context(patch(name,return_value=value))
        app=main.RentalManagementApp()
        try:
            app.geometry('1250x750+20+20')
            app.login_page.password_var.set(DEFAULT_PASSWORD);app.login_page.check_login()
            app.update();time.sleep(.35)
            x,y=app.winfo_rootx(),app.winfo_rooty()
            ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height())).save(OUT/'current_dashboard_sample.png')
            app.sidebar.logout_button.invoke();app.update();time.sleep(.2)
            x,y=app.winfo_rootx(),app.winfo_rooty()
            ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height())).save(OUT/'logout_login_sample.png')
        finally:app.destroy()


def rgb(color):return RGBColor.from_string(color.lstrip('#'))
def inch(px):return Inches(px/144)
def font(size,bold=False):return ImageFont.truetype(str(FONTS/('arialbd.ttf' if bold else 'arial.ttf')),size)


class Slide:
    def __init__(self,title,kicker='FINAL PROJECT PRESENTATION',dark=False):
        self.slide=prs.slides.add_slide(prs.slide_layouts[6]);self.im=Image.new('RGB',(1920,1080),NAVY if dark else WHITE);self.d=ImageDraw.Draw(self.im)
        self.rect(0,0,1920,1080,NAVY if dark else WHITE)
        self.text(100,55,1720,kicker,25,TEAL if not dark else '#80D3DB',True)
        self.text(100,118,1720,title,62,WHITE if dark else NAVY,True)
        self.rect(100,225,100,7,TEAL)
        self.text(100,1013,1610,'NAHABWE DERRICK ERIC  |  Rental Management System',22,'#BED0DD' if dark else MUTED)
        self.text(1755,1008,90,f'{len(prs.slides):02}',28,WHITE if dark else NAVY,True)

    def rect(self,x,y,w,h,fill,outline=None):
        s=self.slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,inch(x),inch(y),inch(w),inch(h))
        s.fill.solid();s.fill.fore_color.rgb=rgb(fill)
        if outline:s.line.color.rgb=rgb(outline)
        else:s.line.fill.background()
        self.d.rectangle((x,y,x+w,y+h),fill=fill,outline=outline)

    def text(self,x,y,w,text,size=36,color=INK,bold=False):
        f=font(size,bold);lines=[]
        for para in str(text).split('\n'):
            if not para:lines.append('');continue
            words=para.split();line=''
            for word in words:
                candidate=(line+' '+word).strip()
                if self.d.textlength(candidate,font=f)>w and line:lines.append(line);line=word
                else:line=candidate
            lines.append(line)
        h=int(len(lines)*size*1.32+15)
        if y+h>(1080 if y>=1000 else 1000):raise ValueError(f'Text overflows slide {len(prs.slides)}: {text[:60]}')
        box=self.slide.shapes.add_textbox(inch(x),inch(y),inch(w),inch(h))
        tf=box.text_frame;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        tf.word_wrap=False
        for i,line in enumerate(lines):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
            p.font.name='Arial';p.font.size=Pt(size/2);p.font.bold=bold;p.font.color.rgb=rgb(color)
            p.space_after=Pt(0);p.line_spacing=1.15
        self.d.multiline_text((x,y), '\n'.join(lines),font=f,fill=color,spacing=int(size*.32))
        return h

    def picture(self,path,x,y,w,h):
        with Image.open(path) as source:
            source=source.convert('RGB');iw,ih=source.size
            scale=min(w/iw,h/ih);nw,nh=round(iw*scale),round(ih*scale)
            xx=x+(w-nw)//2;yy=y+(h-nh)//2
            self.im.paste(source.resize((nw,nh),Image.Resampling.LANCZOS),(xx,yy))
        self.slide.shapes.add_picture(str(path),inch(xx),inch(yy),width=inch(nw),height=inch(nh))

    def card(self,x,y,w,h,label,body,color=TEAL):
        self.rect(x,y,w,h,PALE);self.rect(x,y,7,h,color)
        self.text(x+30,y+25,w-60,label,35,color,True)
        self.text(x+30,y+90,w-60,body,31)

    def finish(self,seconds,note):
        self.slide.notes_slide.notes_text_frame.text=f'Target speaking time: {seconds} seconds\n\n{note}'
        notes.append((len(prs.slides),seconds,note))
        images.append(self.im)


def build():
    s=Slide('RENTAL MANAGEMENT SYSTEM',dark=True)
    s.text(100,330,1000,'Phase 3 — Final Project Presentation',43,'#80D3DB',True)
    s.text(100,450,1070,'NAHABWE DERRICK ERIC\nCertificate in Software Development with AI (CSDA)',34,WHITE)
    s.text(100,620,1000,'Instructor: AJWADH JALAL\nSAI PALI INSTITUTE OF TECHNOLOGY AND MANAGEMENT\n2 November 2026',31,'#D1DEE8')
    s.rect(1320,350,420,420,'#21465F')
    s.text(1370,405,320,'PROPERTY\nTENANTS\nPAYMENTS',46,WHITE,True)
    s.text(1370,645,320,'Python · Tkinter\nMySQL',32,'#80D3DB')
    s.finish(40,'Introduce yourself and the project. Explain that this is the same local desktop project approved in Phase 1 and designed in Phase 2. The presentation describes what the current code provides and the remaining gaps. Do not describe it as a fully production-ready system.')

    s=Slide('Project background')
    s.text(100,290,1650,'One workspace for a landlord or property manager.',42,NAVY,True)
    for x,label,body in [(100,'PROPERTY','Keep rental locations\nand unit counts together.'),(690,'TENANTS','Connect resident details\nto a property and unit.'),(1280,'PAYMENTS','Record rent and balances;\nprepare a receipt.')]:s.card(x,420,540,310,label,body)
    s.text(100,810,1700,'Local desktop use · One office or property portfolio',36,TEAL,True)
    s.finish(45,'Explain the context from the Phase 1 introduction. Rental information is often spread across paper receipts, notebooks, and spreadsheets. The intended users are landlords and property managers overseeing a local portfolio. Linking property, tenant, and payment information reduces repeated lookup work. These are intended benefits; no measured time-saving study was performed.')

    s=Slide('Problem statement and objectives')
    s.text(100,285,1720,'Scattered records make rent, leases, and vacant units difficult to track.',40,NAVY,True)
    rows=[('Property control','Add / view / delete present; editing missing'),('Tenant registry','Registration present; profile editing missing'),('Payments and leases','Payment entry present; lease lifecycle incomplete'),('MySQL and reliability','Storage code present; live integration pending'),('Reporting and validation','Dashboard and selected checks; full scope incomplete')]
    for i,(a,b) in enumerate(rows):
        y=405+i*100;s.rect(100,y,1720,82,PALE);s.text(125,y+16,440,a,31,TEAL,True);s.text(600,y+16,1190,b,31)
    s.finish(60,'State the original problem: manual record keeping can cause misplaced agreements, duplicate entries, financial mistakes, and slow reporting. The five groups shown combine the six approved objectives: MySQL security and storage is grouped with reliability, and reporting is grouped with validation. All six objectives remain partly achieved. Give credit to working entry and viewing features while explaining that editing, full leases, exports, and reports are still missing.')

    s=Slide('Scope and key requirements')
    s.card(100,300,820,485,'APPROVED IN SCOPE','Property and tenant records\nPayments and lease tracking\nSearch, reports, and exports\nTkinter interface + MySQL\nValidation and admin access')
    s.card(1000,300,820,485,'APPROVED OUT OF SCOPE','Web and mobile applications\nCloud synchronisation\nMultiple-company management\nOnline payment gateways\nBiometrics and price forecasting')
    s.text(100,840,1720,'In scope does not mean complete. Current delivery is evaluated against all 22 approved requirements.',32,AMBER,True)
    s.finish(50,'Use the approved Phase 1 scope. Emphasise that missing in-scope features have not been reclassified as excluded features. The current scope remains one local desktop system. Payment-method choices such as Mobile Money or Card record how rent was received; they do not connect to payment gateways. The report contains the full mapping of the 22 requirements.')

    s=Slide('System design and architecture')
    s.picture(ROOT/'reports/diagrams/final_architecture.png',70,275,1100,650)
    s.text(1240,295,590,'main.py\nStartup, navigation, logout',32,TEAL,True)
    s.text(1240,435,590,'pages/ + components/\nForms and shared controls',31)
    s.text(1240,575,590,'data/database.py\nQueries and transactions',31)
    s.text(1240,735,590,'Since Phase 2:\nValidation stays in pages;\nediting and search remain planned.',29,AMBER)
    s.finish(60,'Trace one save operation: the user enters details in a page, the page validates supported inputs, and a function in data/database.py saves the record using parameterised SQL. The interface then reloads the table. Compared with the refined Phase 2 plan, common validation has not been extracted into its own module, and planned edit/search workflows are incomplete. Logout now destroys the old interface and creates a fresh login screen.')

    s=Slide('Tools and technologies')
    cards=[(100,300,'PYTHON 3.13.5','Application logic\nand standard modules'),(990,300,'TKINTER + ttk','Desktop windows, forms,\ndropdowns, and tables'),(100,590,'MYSQL + CONNECTOR','Related persistent records\nmysql-connector-python 26.7.0'),(990,590,'WINDOWS + VS CODE','Windows: inspected environment\nVS Code: proposed Phase 1 editor')]
    for x,y,a,b in cards:s.card(x,y,830,245,a,b)
    s.text(100,880,1720,'MySQL server version and the editor version were not independently verified.',28,MUTED)
    s.finish(45,'Explain why the stack suits a local desktop application: Python organises the logic, Tkinter provides built-in GUI tools, and MySQL holds linked records. The connector sends SQL requests. Python and connector versions were observed in this environment; the MySQL server version was not checked. VS Code is specified in the proposal, but actual editor use and version were not independently verified. Windows supports the current print request.')

    s=Slide('Implemented features')
    s.picture(OUT/'current_dashboard_sample.png',70,285,1180,630)
    s.text(1300,300,525,'Available in code',35,TEAL,True)
    s.text(1300,365,525,'Add / view properties\nRegister / view tenants\nRecord payment + balance\nCreate text receipts\nSettings and dashboard\nLogout and sign in again',31)
    s.text(1300,685,525,'Partial / missing',33,AMBER,True)
    s.text(1300,745,525,'Secure login, editing, search, leases, exports, and detailed reports.',30)
    s.text(100,935,1700,'Current application widgets with controlled sample data; no live database save is implied.',24,MUTED)
    s.finish(60,'Point out the actual sidebar and the Logout button at its bottom. This screenshot uses the current application widgets with controlled sample values and no MySQL writes. Distinguish source-code availability from live acceptance: the report has not verified every database workflow. Logout itself has three real-widget checks. Mention that deletion currently removes linked payments, so it must not be demonstrated with real tenant records.')

    s=Slide('Application workflow / live demonstration')
    steps=[('01','LOGIN'),('02','ADD PROPERTY'),('03','REGISTER TENANT'),('04','RECORD PAYMENT'),('05','LOGOUT')]
    for i,(num,label) in enumerate(steps):
        x=100+i*350;s.rect(x,315,315,170,PALE);s.text(x+22,338,270,num,46,TEAL,True);s.text(x+22,410,280,label,26,NAVY,True)
    s.card(100,555,825,265,'DEMO INPUT','Main amount: UGX 500,000\nBalance: UGX 150,000\nExpected paid amount: UGX 350,000')
    s.card(995,555,825,265,'SHOW ONE INVALID INPUT','Balance above main amount → warning\nThen correct and save in test database.\nReopen records to check persistence.')
    s.text(100,880,1710,'Live demonstration follows the talk. Prepare a test database and sample records first.',30,AMBER,True)
    s.finish(50,'Walk through the journey briefly here; perform the live demonstration after Slide 12. Use an existing prepared test database, a sample property, and a sample tenant. Demonstrate at least property or tenant viewing, payment recording with one invalid balance, and logout followed by re-login. Confirm persistence through an actual save-and-reopen check during the demonstration. If the database is unavailable, say so and use labelled screenshots as backup only. Do not claim this has already been verified.')

    s=Slide('Testing and results')
    for x,num,label,color in [(100,'13','CHECKS EXECUTED',TEAL),(690,'13','PASSED',TEAL),(1280,'0','FAILED',TEAL)]:
        s.rect(x,285,540,195,PALE);s.text(x+25,305,480,num,80,color,True);s.text(x+25,410,480,label,27,MUTED,True)
    rows=[('Partial payment','500,000 − 150,000','350,000 passed to save'),('Invalid balance','Negative / above main amount','Warning; save blocked'),('Logout + re-login','Close old UI, enter password again','Fresh login and pages confirmed')]
    s.rect(100,540,1720,60,NAVY)
    for x,w,t in [(120,420,'FEATURE'),(570,530,'EXPECTED'),(1140,650,'ACTUAL')]:s.text(x,551,w,t,26,WHITE,True)
    for i,(a,b,c) in enumerate(rows):
        y=605+i*88;s.rect(100,y,1720,81,PALE)
        for x,w,t in [(120,420,a),(570,530,b),(1140,650,c)]:s.text(x,y+16,w,t,27)
    s.text(100,915,1720,'10 isolated/source checks + 3 real-widget logout checks. Live database and printer scenarios remain pending.',26,AMBER,True)
    s.finish(60,'The current run passed ten source/isolated-function checks and three Tkinter logout integration checks. The logout checks use real widgets but replace database availability and record-page content, so they do not prove MySQL integration. The three cases cover closing forms and clearing pages, repeated sign-in cycles, and rejecting a wrong password after logout. Existing checks cover syntax, money parsing, login, balance computation, and invalid balances/dates. Eight live integration scenarios remain pending in the report.')

    s=Slide('Challenges and solutions')
    for i,(title,cause,action,outcome) in enumerate([
        ('Connected records','Properties, tenants, and payments depend on each other.','Use linked queries and ordered transactional deletes.','Code present; live rollback check pending.'),
        ('Incorrect payment entries','An invalid balance can produce a wrong paid amount.','Check number, date, and balance before saving.','Selected validation and calculation checks pass.'),
        ('Logout and stale screens','Old pages or forms must not remain available after sign-out.','Destroy old widgets and reset the layout before login.','Three logout / re-login checks pass.')]):
        y=285+i*215;s.rect(100,y,1720,190,PALE);s.text(125,y+20,420,title,34,TEAL,True)
        s.text(585,y+18,1200,cause,29);s.text(585,y+65,1200,action,29);s.text(585,y+112,1200,outcome,28,AMBER,True)
    s.finish(55,'Describe these as concrete implementation issues visible in the code and checks, rather than inventing a development story. Related records require careful deletion order and rollback. Payment entry needs checks before the amount is calculated. Logout needs more than displaying a login frame: the old records and popups must be destroyed, navigation state cleared, and layout reset. History retention and live database verification still remain limitations.')

    s=Slide('Final outcome and next improvements')
    s.card(100,290,825,270,'CURRENT RESULT','A local desktop prototype for linked\nproperty, tenant, and payment records.\nReceipts, dashboard, settings, and logout.')
    s.card(995,290,825,270,'KNOWN LIMITATIONS','Fixed demonstration credentials\nIncomplete leases, editing, search, exports\nDeletion removes payment history',AMBER)
    s.text(100,625,1720,'Next priorities',38,TEAL,True)
    for i,t in enumerate(['1  Secure login + verified database setup and live tests','2  Editing + filtered search + complete lease / vacancy workflow','3  Preserve history + provide the approved reports and exports']):s.text(120,705+i*77,1650,t,34)
    s.finish(65,'Evaluate the result honestly against the approved proposal. All six objectives are partly achieved. The system provides a useful base but is not fully complete or production-ready. Prioritise security and repeatable installation, the missing record/lease operations, and reporting plus history preservation. Existing exclusions such as mobile apps, cloud services, online gateways, biometrics, and pricing forecasts should remain outside this delivery.')

    s=Slide('Thank you. Questions?',dark=True)
    s.text(100,315,850,'One place for rental records.\nA clear foundation to improve.',48,WHITE,True)
    s.text(100,535,820,'Python · Tkinter · MySQL\n\nNext: live demonstration\nand assessor questions',38,'#80D3DB')
    s.picture(OUT/'current_dashboard_sample.png',1050,320,770,510)
    s.text(1050,850,760,'Backup screenshot uses controlled sample data.',23,'#D1DEE8')
    s.finish(35,'Close by explaining the value: connected rental records and easier day-to-day lookup in one desktop interface. Acknowledge that the current prototype still needs the approved missing features and live integration tests. Thank the assessor and move into the prepared demonstration, then questions. Be ready to explain the data relationships, balance calculation, logout cleanup, and the limits of the tests.')


def save():
    base=OUT/'Nahabwe_Derrick_Eric_Rental_Management_System_Phase3_Presentation'
    prs.save(base.with_suffix('.pptx'))
    images[0].save(base.with_suffix('.pdf'),save_all=True,append_images=images[1:],resolution=144,quality=95)
    # Preview and a portable timed talk/demo guide.
    contact=Image.new('RGB',(1440,1620),'#DCE5EC')
    for i,image in enumerate(images):contact.paste(image.resize((480,270)),((i%3)*480,(i//3)*405))
    contact.save(OUT/'slide_preview.jpg',quality=90)
    total=sum(t for _,t,_ in notes)
    lines=['# Phase 3 Presentation — Speaker Notes',f'\nTalk target: {total//60} minutes {total%60} seconds, followed by a separate live demonstration and questions.',
           '\nThe slide deck is Part B only. The existing final report remains Part A. Current test summary: 13 passed, 0 failed. Screenshots use controlled sample data; no live MySQL writes are claimed.']
    for number,seconds,note in notes:lines.extend([f'\n## Slide {number} — {seconds} seconds',note])
    lines.extend(['\n# Live demonstration guide',
        '1. Before presenting, start MySQL and verify the required tables in a separate test database. Configure the application through its RMS_DB_* environment variables. Do not use real tenant records.',
        '2. Prepare Sample Apartments and Sample Tenant in advance. Keep one small property/tenant entry ready if an add operation is needed. Set a test rent of UGX 500,000.',
        '3. Run python main.py and sign in using the configured demonstration credentials. Show the property and tenant tables and explain their relationship.',
        '4. Open Record Payment. Select the sample tenant, use the current demonstration date in YYYY-MM-DD format, and enter a balance above the main amount. Show the warning. Correct the balance to UGX 150,000 and save. Expected amount paid: UGX 350,000.',
        '5. Select the new payment and create a receipt. Check the saved file under data/receipts. Only claim physical printing if it actually succeeds on the demonstration device.',
        '6. Click Logout, show the empty password field, then sign in again. Reopen Payments to verify that the saved record remains. If time allows, close/reopen the app to verify restart persistence.',
        '7. Explain that deleting a tenant or property also removes linked payment records. Avoid destructive deletion during the demonstration unless using disposable test records.',
        '8. If a live operation fails, explain the error. Use the included screenshots as clearly labelled backup; they do not replace a working live demonstration.',
        '\n# Assessor question preparation',
        '- Storage: MySQL records are linked using property_id and tenant_id. The installed schema still needs verification.',
        '- Validation: required values, selected numeric values, payment dates, and balances are checked. Validation is not comprehensive.',
        '- Logout: destroys the old pages and popups, clears navigation references, restores login layout, and requires the password again.',
        '- Tests: ten source/isolated checks and three real-widget logout checks pass; no live database or printer acceptance is implied.',
        '- Remaining work: secure authentication, editing/search, lease lifecycle, vacancy changes, history-preserving archiving, detailed reports, and tenant exports.',
        '\n# Sources',
        '- Approved Phase 1 proposal supplied by the student: objectives, scope, tools, and cover details.',
        '- Phase 2 design and current Part A report: architecture, planned functions, and implementation gaps.',
        '- Current application source, report_checks.py, tests/test_logout.py, and their actual execution results.',
        '- Course title and instructor details follow the approved Phase 1 proposal. Replace the displayed presentation date if the actual submission date changes.'])
    (OUT/'Speaker_Notes_and_Live_Demo.md').write_text('\n\n'.join(lines),encoding='utf-8')
    evidence=dict(source_checks=10,logout_widget_checks=3,passed=13,failed=0,live_database_verified=False,physical_printing_verified=False,
                  screenshot_mode='Real application widgets; controlled sample data; MySQL calls mocked')
    (OUT/'presentation_test_summary.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    from zipfile import ZipFile
    with ZipFile(base.with_suffix('.pptx')) as z:
        slides=[n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
        speaker=[n for n in z.namelist() if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml')]
        assert len(slides)==12 and len(speaker)==12
    print(f'Created 12-slide editable PowerPoint, PDF, and speaker/demo notes. Talk target: {total//60}:{total%60:02}.')


if __name__=='__main__':
    capture();build();save()
