"""Build Word and PDF reports following the supplied LMS report's structure."""
from pathlib import Path
import sys, re, json
from html import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.report_tools'))
from PIL import Image as PILImage, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, PageBreak, Image, LongTable, TableStyle, Preformatted)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

OUT = ROOT / 'reports' / 'template_matched_report'
OUT.mkdir(exist_ok=True)
BASE = OUT / 'Nahabwe_Derrick_Eric_Rental_Management_System_Project_Report'
blocks = []
def h(text, level=1): blocks.append(('heading', text, level))
def p(text): blocks.append(('paragraph', text))
def page(): blocks.append(('break',))
def table(caption, headers, rows, widths=None): blocks.append(('table', caption, headers, rows, widths))
def figure(caption, path, max_height=360): blocks.append(('figure', caption, str(path), max_height))
def code(text): blocks.append(('code', text))

def flow(name, steps):
    """Draw compact, readable operation flows without implying extra features."""
    path = OUT / (name + '.png')
    im = PILImage.new('RGB', (1250, 210 * len(steps) + 50), 'white')
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype('C:/Windows/Fonts/times.ttf', 35)
    for i, text in enumerate(steps):
        y = 20 + 210*i
        draw.rounded_rectangle((55,y,1195,y+145), radius=35 if i in (0,len(steps)-1) else 3,
                               fill='#f4f4f4', outline='black', width=3)
        lines = text.split('\n')
        for j,line in enumerate(lines):
            draw.text((625, y+72+(j-(len(lines)-1)/2)*44),line,font=font,fill='black',anchor='mm')
        if i < len(steps)-1:
            draw.line((625,y+145,625,y+201),fill='black',width=3)
            draw.polygon([(614,y+187),(636,y+187),(625,y+204)],fill='black')
    im.save(path)
    return path

def content():
    blocks.append(('cover',))
    h('DECLARATION')
    p('I, Nahabwe Derrick Eric, submit this report as a record of my Rental Management System project. It explains the design, the current application, the tests carried out, and the work that remains. The project files, earlier reports, tools, and report template used in preparing this document are listed in the References section.')
    p('I am responsible for reviewing this report and explaining the work presented in it.')
    p('Signed: ______________________________')
    p('Date: ________________________________')
    page(); h('ACKNOWLEDGEMENT')
    p('I thank my instructor, Ajwadh Jalal, for the guidance provided during the course, and Sai Pali Institute of Technology and Management for the learning environment and resources.')
    p('I also acknowledge the Python, Tkinter, and MySQL tools used in this project. The earlier proposal and design report helped organise the work. Namwanje Cabrine Jane\'s School Library Management System report was used as a guide for the format and order of this report.')
    page(); h('ABSTRACT / EXECUTIVE SUMMARY')
    p('Landlords and property managers need to keep property details, tenant information, and rent payments together. When these records are kept in notebooks or separate files, finding information and checking balances can take time. The Rental Management System was developed to bring these tasks into one desktop application.')
    p('The application uses Python and Tkinter for its screens and a MySQL-compatible database for storage. Its main sections are Dashboard, Properties, Tenants, Payments, and Settings. The current code supports adding and viewing properties and tenants, recording rent and balances, creating text receipts, saving settings, and logging out. Tenant records can also store paths to identification documents and LC1 letters.')
    p('Thirteen checks were run for this report on 12 November 2026. Ten checked source code and selected functions, and three checked logout using real Tkinter controls. All thirteen passed. Database calls were replaced during these checks, so the results do not confirm live database saving or physical printing. A database export is included in the project folder, but importing it and checking the full application remain separate tasks.')
    p('The project provides a useful starting point for managing rental records. The six main objectives are partly achieved. Editing, filtered search, complete lease tracking, detailed reports, and exports still need work. The login also needs stronger security, and payment history should be kept when a tenant or property is removed.')
    page(); blocks.append(('index','TABLE OF CONTENT','toc'))
    page(); blocks.append(('index','TABLE OF FIGURES','figures'))
    page(); blocks.append(('index','TABLE OF TABLES','tables'))

    page(); h('CHAPTER 1 - INTRODUCTION AND PROJECT OVERVIEW')
    h('1.1 PROJECT BACKGROUND / INTRODUCTION',2)
    p('Managing rental property involves keeping details about houses or apartments, the people renting them, and the money paid each month. A manager may also need contact information, lease dates, identification documents, and receipts. These details are connected and should be easy to find.')
    p('Paper records and spreadsheets can work for a small number of tenants. As the number grows, it becomes harder to keep every record up to date. A payment may be recorded in one place while the tenant details are kept elsewhere. This creates extra work when checking an account or preparing a receipt.')
    p('The Rental Management System is a local desktop application intended for landlords and property managers. It brings property, tenant, and rent information into related screens. This report links the current application to the project proposal and the Phase 2 design.')
    h('1.2 PROBLEM STATEMENT',2)
    p('Manual rental records can be misplaced, repeated, or entered incorrectly. A manager may find it difficult to confirm who occupies a unit, how much rent has been paid, or what balance remains. Separate files also make lease tracking and monthly reporting harder.')
    p('The project therefore aims to provide one place for rental records and routine payment work. The current application addresses registration and payment recording, while full lease management, search, and detailed reporting remain incomplete.')
    h('1.3 PROJECT AIM AND OBJECTIVES',2)
    p('Aim: To develop a Python desktop application that helps landlords and property managers keep property, tenant, lease, and rent-payment records in one place.')
    objectives = [
        ['O1: Add, modify, view, and remove property listings','Partly achieved','Adding, viewing, and deleting are in the code. Editing is not available.'],
        ['O2: Register tenants and update resident profiles','Partly achieved','Registration and viewing are present. Editing tenant details is missing.'],
        ['O3: Record monthly rent and manage lease terms','Partly achieved','Payments and balances are recorded. Lease expiry and move-out processing are missing.'],
        ['O4: Store and retrieve records securely using MySQL','Partly achieved','Database functions and a SQL export are present. Live checks and secure login are still needed.'],
        ['O5: Produce financial and vacancy summaries','Partly achieved','Dashboard figures are present. Full reports and exports are missing.'],
        ['O6: Check entries and handle errors','Partly achieved','Selected checks pass. Contact, duplicate-unit, document, and range checks need improvement.']]
    table('Table 1 Objectives and achievement status',['Objective','Status','Evidence / explanation'],objectives,[.38,.17,.45])
    h('1.4 PROJECT SCOPE',2)
    table('Table 2 Scope: planned versus final',['Area','Original plan','Current outcome'],[
        ['In scope','Property and unit records','Property records and total unit counts exist. There is no separate unit inventory or editing.'],
        ['In scope','Tenant registration and profile management','Registration, viewing, notes, document paths, and deletion exist. Profile editing is missing.'],
        ['In scope','Rent payments and lease tracking','Payments, balances, and lease start dates exist. Lease expiry and move-out tracking are incomplete.'],
        ['In scope','Search, financial reports, vacancy reports, and exports','Dashboard summaries and text receipts exist. Dedicated search, full reports, and exports are missing.'],
        ['In scope','Tkinter interface, login, MySQL storage, and validation','Present in the code, with a demonstration login and partial validation.'],
        ['Out of scope','Web and mobile apps, cloud services, multiple-company management','Remain outside this desktop project.'],
        ['Out of scope','Online payments, digital signing, biometrics, and rent prediction','Not implemented. Payment-method choices only describe how money was received.']],[.14,.38,.48])
    p('A planned feature that is unfinished is still part of the project scope. It has not been moved to the out-of-scope list.')
    h('1.5 INTENDED USERS AND BENEFITS',2)
    p('The direct users are landlords and property managers. They can use the application to look up properties, register tenants, enter rent payments, and prepare receipts. Selecting an existing property or tenant from a list reduces repeated typing.')
    p('Tenants may benefit from clearer records and receipts. These are expected benefits of the design; no study was carried out to measure time saved or reductions in errors.')
    h('1.6 REPORT STRUCTURE',2)
    p('Chapter 1 introduces the project, objectives, and scope. Chapter 2 explains the requirements and design. Chapter 3 describes the implementation. Chapter 4 presents the tests and results. Chapter 5 gives setup instructions, a user guide, limitations, and recommendations. Chapter 6 concludes the report. References and appendices follow.')

    page(); h('CHAPTER 2 - SYSTEM ANALYSIS AND DESIGN')
    h('2.1 FUNCTIONAL REQUIREMENTS',2)
    p('The following requirements follow the approved project scope recorded in the earlier project documents. Implemented means that the feature exists in the source code. Testing is reported separately in Chapter 4.')
    requirements = [
        ('FR01','Secure administrator or manager login','Partial','A fixed demonstration login is used.'),
        ('FR02','Restrict access before login','Partial','Main pages follow login, but there are no user roles.'),
        ('FR03','Add property listings','Implemented','Add Property form and add_property().'),
        ('FR04','Edit property details and prices','Missing','No property editing action.'),
        ('FR05','Remove property listings','Implemented','Confirmed deletion also removes related records.'),
        ('FR06','Display a full rental-unit inventory','Partial','Properties have total unit counts, not separate unit records.'),
        ('FR07','Search listings using several filters','Missing','No dedicated property search or filters.'),
        ('FR08','Register tenants','Implemented','Tenant form and add_tenant().'),
        ('FR09','Update tenant contacts and lease assignments','Missing','No tenant editing workflow.'),
        ('FR10','View tenant records','Implemented','Tenants table shows linked properties and units.'),
        ('FR11','Remove tenants who have left','Partial','Deletion exists, but also removes their payment history.'),
        ('FR12','Process leases for registered tenants','Partial','Property assignment and a start date exist; expiry, renewals, and checkout are missing.'),
        ('FR13','Record rent payments and monthly balances','Partial','Payment entries and balances exist; there is no full monthly ledger or automatic carry-forward.'),
        ('FR14','Update vacancy after leasing or checkout','Missing','No separate unit or checkout workflow.'),
        ('FR15','Preserve tenant and financial history','Missing','Deleting tenants or properties removes related payments; there is no archive.'),
        ('FR16','Show current-vacancy summaries','Partial','Occupancy is estimated from tenant and unit counts, without a vacant-unit list.'),
        ('FR17','Report earnings and outstanding balances','Partial','Dashboard totals exist; detailed period-based reports are absent.'),
        ('FR18','Export active-tenant lists','Missing','No tenant export action.'),
        ('FR19','Display a portfolio dashboard','Implemented','Summary cards, occupancy, rent totals, and recent activity are in the code.'),
        ('FR20','Validate input formats before saving','Partial','Some required-field, number, email, and payment-date checks exist.'),
        ('FR21','Block duplicate records','Partial','No comprehensive form-level checks; the export has unique phone and payment-reference keys.'),
        ('FR22','Show useful invalid-input alerts','Implemented','Selected warning and error messages are present and tested.')]
    table('Table 3 Functional requirements and status',['ID','Requirement','Status','Evidence'],requirements,[.10,.34,.15,.41])
    h('2.2 SYSTEM ARCHITECTURE',2)
    p('The application separates the screens from the database functions. main.py starts the program and controls navigation. The page classes collect input and show results. Shared components provide the sidebar, header, cards, and tables. data/database.py sends queries to the database.')
    p('For example, when a payment is saved, the page reads the form, checks the supported values, calculates the amount paid, and calls the database function. After a successful save, it reloads the payment table. Most validation still sits inside the page classes.')
    figure('Figure 1 System architecture',ROOT/'reports/diagrams/final_architecture.png',320)
    table('Table 4 Modules and files',['Module / file','Responsibility'],[
        ['main.py','Creates the application, checks database access, changes pages, and handles logout.'],
        ['config/settings.py','Stores window settings, colours, fonts, demonstration login, and database configuration.'],
        ['pages/','Contains Login, Dashboard, Properties, Tenants, Payments, Settings, and the shared base page.'],
        ['components/','Contains the sidebar, header, statistic cards, and reusable table.'],
        ['data/database.py','Provides database connections, queries, saves, deletes, and dashboard totals.'],
        ['data/seed_sample_rentals.py','Optional script for adding labelled fictional rental records. It is not run at startup.'],
        ['rental_management_system.sql','Database export with table definitions, keys, and existing records.'],
        ['tests/ and report_checks.py','Contain logout tests and checks for selected application functions.']],[.34,.66])
    h('2.3 FLOWCHARTS',2)
    p('These flows describe operations found in the current application. A rejected entry returns the user to the form for correction. Editing and filtered search are not shown as completed features because they are not available in the current code.')
    flows = [
        ('login','Login flowchart',['Start application and check database access','If unavailable: show error and close\nIf available: show login','Enter username and password','If wrong: show error and clear password\nIf correct: open Dashboard']),
        ('property','Add Property flowchart',['Open Properties and choose Add Property','Enter name, location, units, and rent','Check required values and numeric fields\nIf invalid: show a warning and correct entries','Save to MySQL\nIf successful: reload the Properties table']),
        ('tenant','Register Tenant flowchart',['Open Tenants and choose Register Tenant','Select an active property and enter tenant details','Check required fields and supported values\nIf invalid: show a warning and correct entries','Save the tenant with property_id\nReload the Tenants table']),
        ('payment','Record Payment flowchart',['Open Payments and select a tenant','Enter main amount, balance, date, and method','Check numbers, date, and balance range\nIf invalid: show a warning and correct entries','Amount paid = main amount - balance\nSave the payment and reload the table']),
        ('receipt','Receipt flowchart',['Select a saved payment','Choose Print Receipt','Create a text receipt in data/receipts','On Windows: request default printing\nA saved file alone does not confirm printing']),
        ('delete','Delete Record flowchart',['Select a property or tenant','Ask the user to confirm deletion\nIf cancelled: leave records unchanged','Delete linked payments, then tenant/property records','Commit if successful; roll back on error\nReload the table after success']),
        ('view','View Records flowchart',['Choose Properties, Tenants, or Payments','Read records through data/database.py','Join related records where needed','Display rows in the selected table\nNo dedicated filtered search is available']),
        ('logout','Exit / Log Out flowchart',['Choose Logout','Close old forms and destroy record pages','Clear navigation state and rebuild login','Require the password again\nSaved database records are not deleted'])]
    for i,(name,title,steps) in enumerate(flows,2):
        figure(f'Figure {i} {title}',flow(name,steps),355)
    h('2.4 DATA STRUCTURE / DATABASE DESIGN',2)
    p('The database has five main tables: users, properties, tenants, payments, and app_settings. A property can have many tenants, and a tenant can have many payments. The application uses property_id and tenant_id to link these records.')
    p('There is no separate units or leases table. A unit number and lease start date are stored on the tenant record. The users table exists, but the current login compares values from configuration instead of checking that table.')
    figure('Figure 10 Database relationships',ROOT/'reports/diagrams/final_database_relationships.png',320)
    sql = (ROOT/'rental_management_system.sql').read_text(encoding='utf-8-sig')
    fields=[]
    for name, body in re.findall(r'CREATE TABLE `([^`]+)`\s*\((.*?)\) ENGINE',sql,re.S):
        for line in body.splitlines():
            match=re.match(r'\s*`([^`]+)`\s+(.+)',line)
            if match:
                field, definition=match.groups()
                fields.append([name,field,definition.rstrip(',')])
    table('Table 5 Database tables and fields',['Table','Field','Type and rule in the supplied export'],fields,[.18,.28,.54])
    p('Primary keys identify users, properties, tenants, and payments. app_settings uses setting_key as its key. The export defines indexes and relationships separately with ALTER TABLE statements. Appendix B includes the structure without copying its existing personal or account records.')
    p('The supplied export header identifies MariaDB 10.4.32 and phpMyAdmin 5.2.1. These describe the export source. They do not prove that a matching server was running during the tests in this report.')
    h('2.5 USER INTERFACE / MENU DESIGN',2)
    p('The login screen opens before the main interface. After sign-in, the window has a dark sidebar on the left and a content area on the right. The sidebar contains Dashboard, Properties, Tenants, Payments, Settings, and Logout.')
    p('Dashboard shows summary figures and recent activity. Properties and Tenants show tables with entry and deletion actions. Payments allows the user to record rent and create a receipt. Settings contains company details and preferences. Entry forms open in separate windows with Save and Cancel buttons.')
    h('2.6 DESIGN CHANGES',2)
    table('Table 6 Design changes after Phase 2',['Earlier design','Current implementation','Effect'],[
        ['Separate service and validation modules','Most validation remains in page methods','The code has fewer modules, but form and business rules are closely connected.'],
        ['Complete add, edit, delete, view, and search','Add/view plus property and tenant deletion','Editing and filtered search remain unfinished.'],
        ['Create database tables during setup','Startup checks existing tables; a SQL export is now supplied','The database must be prepared separately.'],
        ['Use sample screens when the database is unavailable','Startup shows an error and closes','The app does not silently treat sample records as saved records.'],
        ['Block or reassign related records on deletion','Delete linked payments and tenants in a transaction','History is removed and should be preserved in a future version.'],
        ['Automatic balance handling','The user enters the balance for each payment','The stored amount paid is main amount minus balance.']],[.30,.35,.35])

    page(); h('CHAPTER 3 - SYSTEM IMPLEMENTATION')
    h('3.1 DEVELOPMENT ENVIRONMENT AND TOOLS',2)
    table('Table 7 Development tools',['Item','Tool','Purpose'],[
        ['Language','Python','Application logic, calculations, and file handling.'],
        ['Interface','Tkinter and ttk','Windows, forms, buttons, dropdowns, and tables.'],
        ['Database connector','mysql-connector-python','Connects Python to the configured MySQL-compatible database.'],
        ['Storage','MySQL-compatible database; MariaDB shown in the export','Stores linked records outside the running program.'],
        ['Operating system','Windows','Runs the current application and supports its print request.'],
        ['Editor','Visual Studio Code, as proposed in the project plan','Proposed tool for editing and running code.'],
        ['Standard modules','datetime, pathlib, os, and platform','Dates, paths, receipt files, and operating-system checks.'],
        ['Testing','ast, unittest, and unittest.mock','Syntax, selected functions, and login/logout checks.']],[.22,.35,.43])
    p('The report-building libraries are documentation tools. They are not required to run the rental application. The project requirements.txt lists mysql-connector-python as its external application dependency.')
    h('3.2 PROJECT FOLDER AND FILE STRUCTURE',2)
    code('Rental Management System/\n  main.py\n  requirements.txt\n  README.md\n  rental_management_system.sql\n  config/\n    settings.py\n  components/\n    header.py, sidebar.py, simple_table.py, stat_card.py\n  pages/\n    base_page.py, login_page.py, dashboard_page.py\n    properties_page.py, tenants_page.py\n    payments_page.py, settings_page.py\n  data/\n    database.py\n    seed_sample_rentals.py\n    receipts/                 (created when needed)\n  tests/\n    test_logout.py\n  report_checks.py\n  assets/\n  reports/')
    p('Configuration, reusable controls, screens, and database functions are kept in separate folders. This makes it easier to locate a feature. receipts/ holds generated text receipts; it may not exist until the first receipt is created.')
    h('3.3 IMPLEMENTED MODULES AND FUNCTIONS',2)
    table('Table 8 Main functions',['Function / module','Input','Result'],[
        ['initialize_database()','Configured database connection','Checks access to all five required tables; it does not create them.'],
        ['LoginPage.check_login()','Username and password fields','Opens the main layout or shows a login error.'],
        ['RentalManagementApp.show_page()','Page name','Changes the visible page and refreshes its data.'],
        ['RentalManagementApp.logout()','Current interface state','Closes old pages and forms and returns to login.'],
        ['add_property()','Property details','Inserts a property and returns its ID.'],
        ['add_tenant()','Tenant details and property_id','Inserts a linked tenant record.'],
        ['add_payment()','Payment details and tenant_id','Inserts a linked payment record.'],
        ['get_properties(), get_tenants(), get_payments()','Current database records','Returns rows for the relevant tables.'],
        ['delete_property(), delete_tenant()','Selected record ID','Deletes the record and linked records in a transaction.'],
        ['get_dashboard_summary()','Current database records','Returns counts, payment totals, and recent activity.'],
        ['save_app_settings()','Setting names and values','Inserts or updates preferences.'],
        ['PaymentsPage._create_receipt_file()','Selected payment record','Creates a local text receipt.']],[.35,.25,.40])
    h('3.4 IMPLEMENTATION OF MAJOR FEATURES',2)
    h('3.4.1 Login',3)
    p('User action: enter the username and password, then sign in. Processing: the login page compares them with the demonstration values in config/settings.py. Result: the main layout opens when they match. An incorrect password is rejected and cleared. The current login is a demonstration check, not secure database authentication.')
    h('3.4.2 Property management',3)
    p('User action: choose Add Property and enter a name, location, number of units, monthly rent, and optional details. Processing: the form checks required entries and numeric values, then calls add_property(). Data: properties table. Result: the saved property appears when the table reloads.')
    p('Delete Selected asks for confirmation. The database function deletes payments linked through the property\'s tenants, then the tenants, and finally the property. It commits the changes together or rolls back if an error occurs. Property editing is not available.')
    h('3.4.3 Tenant management',3)
    p('User action: register a tenant and select an active property. Selecting the property fills its default rent, which can be changed for that tenant. The required details include the name, phone number, property, unit number, and rent.')
    p('Optional fields include email, lease start date, emergency contact, status, identification image path, LC1 letter path, and notes. The program stores document paths; it does not copy the documents into a managed folder. Deleting a tenant also deletes the tenant\'s payments. There is no tenant editing action.')
    h('3.4.4 Rent payments and balances',3)
    p('User action: open Record Payment and select a tenant. The related property, unit, and rent are filled from that record. Enter the main amount, balance, payment date, method, reference, notes, and status. The program checks supported entries before saving.')
    p('The calculation is: amount paid = main amount - balance. For a main amount of UGX 500,000 and balance of UGX 150,000, the amount paid is UGX 350,000. The program rejects a negative balance, a balance above the main amount, and an invalid payment date. Status is chosen manually rather than calculated from the balance.')
    p('Cash, Mobile Money, Bank Transfer, and Card are record labels. Selecting one does not connect the application to a bank or payment gateway.')
    h('3.4.5 Receipt creation',3)
    p('User action: select a saved payment and choose Print Receipt. Processing: the application creates a text file under data/receipts. The receipt includes company details, receipt number, tenant, property, unit, date, amounts, method, reference, and status.')
    p('On Windows, the program asks the default application to print the file. Creating the receipt file and successfully printing it are separate outcomes. Physical printing was not verified in the tests for this report.')
    h('3.4.6 Dashboard',3)
    p('The dashboard shows active property and tenant counts, unit totals, rent figures, occupancy, and recent activity. Current-month collected rent includes payments with status Paid. Pending rent is calculated as active tenants\' expected rent minus that collected amount, with a minimum of zero.')
    p('Occupancy is estimated from active tenant count divided by total units. This assumes one active tenant record per occupied unit. It is not a separate unit-by-unit vacancy register. Manually selected payment statuses and duplicate tenant assignments can affect the figures.')
    h('3.4.7 Settings',3)
    p('Settings stores company and manager details, currency preference, rent due day, late fee, and reminder choices. Saving a reminder preference does not send an email or SMS. The late fee is not automatically charged. Several money displays still use UGX directly, even though a currency preference can be stored.')
    h('3.4.8 Logout',3)
    p('When the user chooses Logout, the application closes open forms, destroys the old pages, clears navigation references, and creates a fresh login screen. The password is cleared and must be entered again. Unsaved form entries are discarded, while saved database records are not deleted by logout.')
    h('3.5 INPUT VALIDATION AND ERROR HANDLING',2)
    p('Property forms check required details and whether units and rent can be converted to numbers. Tenant forms require the key details, check the selected property, and make a basic email check. Payment forms check the selected tenant, numeric amounts, date, and balance range. Settings checks the due day against 1 to 31 and requires a numeric late fee.')
    p('Examples of messages in the program include Missing Details, Invalid Amount, Invalid Balance, Invalid Date, and Database Error. These messages give the user a chance to correct an entry or check the database connection.')
    p('Some checks remain incomplete. Property and tenant rent need clearer non-negative limits. Phone format, document existence, duplicate unit assignments, and lease dates are not fully checked by the forms. A lost connection can also make some lists appear empty. Error reporting should be made consistent across all pages.')
    h('3.6 DATA STORAGE AND RETRIEVAL',2)
    p('Database functions open a connection, run a query, and close the cursor and connection afterwards. Insert statements use parameter placeholders for record values. Successful writes are committed. Related deletions are rolled back if an error occurs. Settings uses an insert-or-update query to change existing values.')
    p('The design supports keeping saved data after the program closes because the records are stored in the database. A live save-and-reopen test is still required to confirm this on the target computer. Document files remain at their selected paths, while receipts are separate text files.')
    h('3.7 SCREENSHOTS OF THE COMPLETED APPLICATION',2)
    p('The following figures show the current interface with controlled sample data. They were captured from real Tkinter screens with database calls replaced. They illustrate the layout and forms; they are not evidence of a live save or printer test.')
    figure('Figure 11 Home dashboard with sample data',ROOT/'reports/presentation/current_dashboard_sample.png',290)
    figure('Figure 12 Tenant registration form with sample data',ROOT/'reports/tenant_form_sample.png',345)
    figure('Figure 13 Payment form with sample data',ROOT/'reports/payment_form_sample.png',345)

    page(); h('CHAPTER 4 - TESTING AND RESULTS')
    h('4.1 TESTING APPROACH',2)
    p('Testing for this report was carried out on 12 November 2026. The report_checks.py functions were run without writing rental records. One check parsed all 19 application Python files. The remaining checks used simulated controls and replaced database and message-box calls to test selected login, payment, date, and filename logic.')
    p('The three tests in tests/test_logout.py were also run. They used real Tkinter controls, with database startup and record pages replaced. They checked closing old forms, signing in again, and rejecting a wrong password after logout. These tests do not confirm live MySQL access.')
    h('4.2 TEST CASES AND ACTUAL RESULTS',2)
    results=json.loads((ROOT/'reports/template_review/current_test_results.json').read_text(encoding='utf-8'))
    rows=[[r['id']+' '+r['feature'],r['condition'],r['expected'],r['actual'],r['status']] for r in results]
    rows.extend([
        ['T11 Logout cleanup','Open page and popup, then logout','Close old pages and forms; clear password','Real-widget logout test passed.','Pass'],
        ['T12 Sign in again','Logout, then sign in again','Create fresh pages and layout','Real-widget sign-in test passed.','Pass'],
        ['T13 Wrong password after logout','Logout, then enter wrong password','Keep record pages inaccessible','Real-widget rejection test passed.','Pass']])
    table('Table 9 Test cases and actual results',['ID / feature','Input / condition','Expected','Actual result','Status'],rows,[.17,.23,.20,.30,.10])
    p('The calculation test confirms that the save function receives UGX 350,000 for a main amount of UGX 500,000 and balance of UGX 150,000. It does not perform a real database write. A syntax check confirms that files can be parsed; it does not check every runtime path.')
    h('4.3 TESTING SUMMARY',2)
    table('Table 10 Testing summary',['Item','Result'],[
        ['Source and selected-function checks run','10'],['Real-widget logout checks run','3'],['Total checks run','13'],['Passed','13'],['Failed','0'],['Pending live scenarios listed below','8'],['Live database writes in this report\'s tests','0'],['Physical printing verified','No']],[.70,.30])
    p('Eight live scenarios remain pending: property save and reload; tenant save with document paths; payment save and joined history; property deletion with linked records; tenant deletion with linked payments; settings save and reset; close and reopen to confirm saved records; and receipt creation with actual printing. These should be run with sample records in a separate test database.')
    h('4.4 PROBLEMS ENCOUNTERED AND SOLUTIONS',2)
    p('The following issues are visible in the design and source code. The table describes current handling without assuming an undocumented development history.')
    table('Table 11 Problems and solutions',['Problem','Current handling','Remaining work'],[
        ['The app needs prepared database tables','Startup checks access and shows an error if it fails. A SQL export is supplied.','Import into a test database and verify all screens.'],
        ['Property, tenant, and payment records depend on each other','IDs link records; related deletions use ordered queries and rollback.','Test live rollback and preserve payment history.'],
        ['An incorrect balance changes the amount paid','Numeric, date, and balance checks run before saving.','Add broader range checks and test more boundaries.'],
        ['Old forms may remain after logout','Old widgets are destroyed and the login layout is rebuilt.','Keep the logout tests when changing navigation.'],
        ['The login uses fixed credentials','The limitation is documented.','Replace it with securely stored credentials and access rules.'],
        ['Some planned features are missing','They are listed as incomplete.','Finish editing, filtered search, leases, reports, and exports.']],[.32,.38,.30])
    h('4.5 EVALUATION AGAINST OBJECTIVES AND REQUIREMENTS',2)
    table('Table 12 Evaluation against objectives',['Objective','Evidence','Evaluation'],[
        ['O1 Property management','Forms and database functions for adding, viewing, and deleting.','Partly achieved; editing and detailed unit records are missing.'],
        ['O2 Tenant management','Registration, linked property selection, viewing, and deletion.','Partly achieved; profile editing and safe archiving are missing.'],
        ['O3 Rent and leases','Payment entry, amount calculation, balances, and a lease start field.','Partly achieved; full leases and move-out processing are missing.'],
        ['O4 Database and security','Database functions, related tables, and a supplied SQL export.','Partly achieved; secure authentication and live tests are needed.'],
        ['O5 Summaries and reports','Dashboard figures and text receipts.','Partly achieved; vacancy and financial reports and exports are incomplete.'],
        ['O6 Validation and error handling','Selected payment, login, and logout checks passed.','Partly achieved; validation and error handling are not complete.']],[.23,.40,.37])
    p('Passing thirteen selected checks does not mean that every requirement is complete. The system should be evaluated as a desktop prototype with working code for several core operations and clear gaps against the original plan.')

    page(); h('CHAPTER 5 - USER GUIDE AND PROJECT COMPLETION')
    h('5.1 SYSTEM REQUIREMENTS',2)
    p('The current application needs a Windows computer with Python and Tkinter, the mysql-connector-python package, and access to a running MySQL-compatible database. A default printer and an application that can print text files are needed for physical receipts. The project does not provide measured minimum processor, memory, or storage requirements.')
    h('5.2 INSTALLATION / SETUP INSTRUCTIONS',2)
    p('1. Place the project folder on the computer. Open a terminal in that folder and install the application dependency:')
    code('python -m pip install -r requirements.txt')
    p('2. Start the database server. In a database tool such as phpMyAdmin, create a separate database for the project and import rental_management_system.sql into it. The export contains both structure and existing records, so review it first and do not import it over a working database.')
    p('3. Check the connection settings in config/settings.py or set RMS_DB_HOST, RMS_DB_PORT, RMS_DB_USER, RMS_DB_PASSWORD, and RMS_DB_NAME in the environment. The default database name is rental_management_system. The program reads process environment variables; it does not automatically read a .env file.')
    p('4. Confirm that users, properties, tenants, payments, and app_settings can be read. Startup checks these tables but does not create them. Then run:')
    code('python main.py')
    p('5. For the current classroom demonstration, the configured username is eric and the password is 12345. These fixed credentials should be replaced before use with real records.')
    p('6. Use sample data to check property entry, tenant registration, payment saving, and reopening the application. The supplied SQL export gives a setup starting point; a fresh import and complete live workflow were not tested for this report.')
    h('5.3 HOW TO USE THE APPLICATION',2)
    p('Sign in: open the application and enter the configured login details. The Dashboard opens after a successful login.')
    p('Add a property: open Properties, select Add Property, enter the property name, location, total units, and monthly rent, then save. Create the property before registering its tenants.')
    p('Register a tenant: open Tenants and select the registration action. Choose the property, enter the tenant name, contact, unit number, and agreed rent. Add optional lease and document details, then save. Keep selected document files at accessible paths.')
    p('Record rent: open Payments, choose Record Payment, and select a tenant. Check the property and unit, then enter the main amount, remaining balance, date, method, and other details. Use YYYY-MM-DD for the date. For rent of UGX 500,000 with UGX 150,000 remaining, the program records UGX 350,000 paid.')
    p('Create a receipt: select a payment and choose Print Receipt. Check the generated text file in data/receipts. If printing is needed, confirm that the default application and printer complete the job.')
    p('View summaries and settings: open Dashboard for totals and recent activity. Open Settings to change company details and available preferences. Reminder choices store preferences only.')
    p('Delete a record: select a property or tenant and confirm the deletion only when the linked records can also be removed. Deletion removes associated payments. Keep a database backup before trying this with records that matter.')
    p('Log out: choose Logout in the sidebar. Open forms close and unsaved entries are lost. The next user must sign in again. Saved records remain in the database.')
    h('5.4 KNOWN LIMITATIONS',2)
    p('The login uses fixed demonstration credentials and has no role-based permissions. Property and tenant editing, filtered search, complete lease tracking, move-out handling, tenant exports, and detailed financial and vacancy reports are missing.')
    p('Deleting a property or tenant removes related payment history. Units do not have their own records, and occupancy is estimated from tenant counts. Document paths can stop working if files are moved. Reminder preferences and late fees are not automated. Live database persistence and printing still need verification.')
    h('5.5 RECOMMENDATIONS FOR FUTURE IMPROVEMENT',2)
    p('First, improve authentication and verify a repeatable database setup. Replace fixed credentials with securely stored passwords, use appropriate database permissions, and test the application against a separate database before introducing real records.')
    p('Second, finish property and tenant editing, filtered search, separate unit records, lease expiry, and move-out processing. Add checks for negative rent, duplicate active unit assignments, contact information, dates, and document paths.')
    p('Third, preserve historical records through archiving instead of deleting payments. Complete the approved financial and vacancy reports and export functions. Clearly distinguish stored reminder preferences from any future reminder service.')

    page(); h('CHAPTER 6 - CONCLUSION')
    h('6.1 PROJECT SUMMARY',2)
    p('The Rental Management System brings property, tenant, and rent-payment records into one Python desktop application. Tkinter provides the screens, while a MySQL-compatible database stores the related records. The current code includes entry and viewing features, text receipts, a dashboard, settings, and logout.')
    h('6.2 ACHIEVEMENT OF OBJECTIVES',2)
    p('All six main objectives are partly achieved. The system provides a base for routine rental records, but important parts of the approved plan remain incomplete. These include editing, search, lease management, full reports, secure login, and safe history retention. The thirteen passing checks support selected parts of the implementation; they do not establish full completion.')
    h('6.3 LESSONS LEARNT',2)
    p('The project shows why related records need clear IDs and careful handling. A payment must match the correct tenant and property. Small calculation or input errors can affect rent figures, so validation should happen before saving.')
    p('It also shows that a feature in source code, a screenshot, and a successful live test provide different kinds of evidence. Testing needs to cover calculations, screen behaviour, database saving, reopening records, and output. Keeping interface, validation, and database responsibilities clear makes later changes easier.')
    h('6.4 REMARKS',2)
    p('The project is a useful desktop prototype for rental records. Completing the remaining features and carrying out live database and printer checks would make it more suitable for daily use. The next stage should focus on correctness, secure access, and keeping reliable payment history.')

    page(); h('REFERENCES')
    for text in [
        'Nahabwe Derrick Eric. Rental Management System project source files: main.py, config/settings.py, pages/, components/, and data/database.py. Local project files reviewed on 12 November 2026.',
        'Nahabwe Derrick Eric. Phase 2 Design and Incubation Report. reports/Phase2_Design_Report.md. Used for the earlier design and planned features.',
        'Nahabwe Derrick Eric. Phase 3 Final Project Report. reports/Final_Report.md. Used for the recorded proposal objectives, scope, and earlier implementation review.',
        'Nahabwe Derrick Eric. Rental Management System README.md and requirements.txt. Used for setup notes and application dependencies.',
        'Nahabwe Derrick Eric. rental_management_system.sql. Database export dated 12 November 2026. Used for table fields, keys, and database-source details.',
        'Nahabwe Derrick Eric. report_checks.py and tests/test_logout.py. Checks rerun on 12 November 2026. Results summarised in Chapter 4.',
        'Nahabwe Derrick Eric. Existing project diagrams and controlled-sample screenshots in reports/. Used to illustrate the design and interface.',
        'Namwanje Cabrine Jane. School Library Management System Project Report. User-supplied PDF, 45 pages. Used as the formatting and report-structure template; library-system claims and results were not transferred to this project.'
    ]: p(text)

    page(); h('APPENDICES')
    h('APPENDIX A - ADDITIONAL SCREENSHOTS AND OUTPUT SAMPLES',2)
    figure('Figure 14 Login screen after logout',ROOT/'reports/presentation/logout_login_sample.png',310)
    p('The login screenshot is a controlled interface sample. The following is an illustrative receipt summary showing the same calculation used in the payment test. It is not presented as a receipt generated by a live database or printer run.')
    code('RENT PAYMENT - ILLUSTRATIVE SAMPLE\nTenant: Sample Tenant\nProperty: Sample Apartments\nUnit: A1\nMain amount: UGX 500,000\nAmount paid: UGX 350,000\nBalance: UGX 150,000\nMethod: Cash\n\nAmount paid = main amount - balance')
    page(); h('APPENDIX B - DATABASE STRUCTURE (rental_management_system.sql)',2)
    p('This structure is taken from the supplied SQL export. INSERT statements containing existing records are omitted. The complete export remains in the project root. The following definitions are for reference; use the supplied export for setup and review it before importing.')
    statements = re.findall(r'(CREATE TABLE `.*?;|ALTER TABLE `.*?;)',sql,re.S)
    for statement in statements: code(statement)

class ReportPDF(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=72,rightMargin=72,topMargin=66,bottomMargin=62,
                         title='Rental Management System Project Report',author='Nahabwe Derrick Eric')
        frame=Frame(72,62,A4[0]-144,A4[1]-128,id='normal',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='body',frames=[frame],onPage=self.footer))
    def footer(self,canvas,doc):
        if doc.page>1:
            canvas.setFont('TNR',11); canvas.drawCentredString(A4[0]/2,48,str(doc.page-1))
    def afterFlowable(self,f):
        if hasattr(f,'entry_kind'):
            if f.entry_kind=='toc': self.notify('TOCEntry',(f.entry_level,f.getPlainText(),self.page-1))
            elif f.entry_kind=='figures': self.notify('FigureEntry',(0,f.getPlainText(),self.page-1))
            elif f.entry_kind=='tables': self.notify('TableEntry',(0,f.getPlainText(),self.page-1))

class CustomContents(TableOfContents):
    def __init__(self,kind,**kwargs): self.kind=kind; super().__init__(**kwargs)
    def notify(self,kind,stuff):
        if kind==self.kind: self.addEntry(*stuff)

def build_pdf():
    fonts=Path('C:/Windows/Fonts')
    for name,file in [('TNR','times.ttf'),('TNR-Bold','timesbd.ttf'),('TNR-Italic','timesi.ttf'),('Mono','cour.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNR-Bold',italic='TNR-Italic',boldItalic='TNR-Bold')
    styles={
        'body':ParagraphStyle('body',fontName='TNR',fontSize=12,leading=15.5,spaceAfter=8,alignment=TA_JUSTIFY),
        'h1':ParagraphStyle('h1',fontName='TNR-Bold',fontSize=16,leading=20,spaceAfter=14,keepWithNext=True,alignment=TA_CENTER),
        'h2':ParagraphStyle('h2',fontName='TNR-Bold',fontSize=12,leading=15,spaceBefore=9,spaceAfter=7,keepWithNext=True),
        'h3':ParagraphStyle('h3',fontName='TNR-Bold',fontSize=12,leading=15,spaceBefore=7,spaceAfter=6,keepWithNext=True),
        'caption':ParagraphStyle('caption',fontName='TNR-Italic',fontSize=11,leading=14,spaceBefore=5,spaceAfter=7,keepWithNext=True,textColor=colors.HexColor('#34465b')),
        'cell':ParagraphStyle('cell',fontName='TNR',fontSize=10.5,leading=13,spaceAfter=0),
        'headcell':ParagraphStyle('headcell',fontName='TNR-Bold',fontSize=10.5,leading=13),
        'code':ParagraphStyle('code',fontName='Mono',fontSize=9,leading=11,spaceBefore=5,spaceAfter=9),
        'cover':ParagraphStyle('cover',fontName='TNR-Bold',fontSize=18,leading=23,spaceAfter=23,alignment=TA_CENTER),
    }
    story=[]; width=A4[0]-144
    for block in blocks:
        kind=block[0]
        if kind=='cover':
            for text,size in cover_lines():
                st=ParagraphStyle('coverline',parent=styles['cover'],fontSize=size,leading=size*1.2)
                story.append(Paragraph(escape(text).replace('\n','<br/>'),st))
            story.append(PageBreak())
        elif kind=='heading':
            _,text,level=block
            obj=Paragraph(escape(text),styles['h'+str(level)]); obj.entry_kind='toc'; obj.entry_level=level-1
            story.append(obj)
        elif kind=='paragraph': story.append(Paragraph(escape(block[1]),styles['body']))
        elif kind=='break': story.append(PageBreak())
        elif kind=='index':
            title,topic=block[1:]; story.append(Paragraph(title,styles['h1']))
            kinds={'toc':'TOCEntry','figures':'FigureEntry','tables':'TableEntry'}
            toc=CustomContents(kinds[topic]); toc.dotsMinLevel=0
            toc.tableStyle=TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),1),('VALIGN',(0,0),(-1,-1),'TOP')])
            toc.levelStyles=[ParagraphStyle('toc'+str(i),fontName='TNR-Bold' if i==0 and topic=='toc' else 'TNR',fontSize=11,leading=14,leftIndent=i*12,firstLineIndent=0,spaceBefore=4 if i==0 else 1) for i in range(3)]
            story.append(toc)
        elif kind=='table':
            _,caption,headers,rows,widths=block
            cap=Paragraph(escape(caption),styles['caption']); cap.entry_kind='tables'; story.append(cap)
            data=[[Paragraph(escape(str(v)),styles['headcell' if i==0 else 'cell']) for v in row] for i,row in enumerate([headers]+list(rows))]
            widths=[width*v for v in widths] if widths else None
            t=LongTable(data,colWidths=widths,repeatRows=1,hAlign='LEFT',spaceAfter=10)
            t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.45,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#f3f3f3')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.append(t)
        elif kind=='figure':
            _,caption,path,maxh=block
            cap=Paragraph(escape(caption),styles['caption']); cap.entry_kind='figures'; story.append(cap)
            with PILImage.open(path) as im: iw,ih=im.size
            scale=min(width/iw,maxh/ih)
            story.append(Image(path,width=iw*scale,height=ih*scale,hAlign='CENTER')); story.append(Spacer(1,9))
        elif kind=='code':
            # Keep long SQL field definitions inside the page width.
            import textwrap
            text='\n'.join('\n'.join(textwrap.wrap(line,85,subsequent_indent='    ',replace_whitespace=False)) if len(line)>85 else line for line in block[1].splitlines())
            story.append(Preformatted(text,styles['code']))
    ReportPDF(BASE.with_suffix('.pdf')).multiBuild(story)

def cover_lines():
    return [('RENTAL MANAGEMENT\nSYSTEM',24),('PROJECT REPORT',18),('BY',18),('NAHABWE DERRICK ERIC',18),
        ('YEAR: __________  SEMESTER: __________',16),('REGISTRATION NUMBER: __________________',16),
        ('COURSE NAME: CERTIFICATE IN SOFTWARE\nDEVELOPMENT WITH AI',18),
        ('INSTITUTION: SAI PALI INSTITUTE OF\nTECHNOLOGY AND MANAGEMENT',18),('INSTRUCTOR: AJWADH JALAL',18),('12 NOVEMBER 2026',14)]

def field(paragraph,instruction,text='Update this field in Word to show page numbers.'):
    run=paragraph.add_run(); begin=OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'),'begin'); run._r.append(begin)
    instr=OxmlElement('w:instrText'); instr.set(qn('xml:space'),'preserve'); instr.text=' '+instruction+' '; run._r.append(instr)
    sep=OxmlElement('w:fldChar'); sep.set(qn('w:fldCharType'),'separate'); run._r.append(sep)
    paragraph.add_run(text)
    end=OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'),'end'); paragraph.add_run()._r.append(end)

def build_docx():
    doc=Document(); sec=doc.sections[0]
    sec.page_width=Pt(A4[0]); sec.page_height=Pt(A4[1]); sec.top_margin=Pt(66); sec.bottom_margin=Pt(62); sec.left_margin=sec.right_margin=Pt(72)
    normal=doc.styles['Normal']; normal.font.name='Times New Roman'; normal.font.size=Pt(12)
    normal.paragraph_format.line_spacing=1.15; normal.paragraph_format.space_after=Pt(8)
    normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    for level in [1,2,3]:
        st=doc.styles[f'Heading {level}']; st.font.name='Times New Roman'; st.font.size=Pt(16 if level==1 else 12); st.font.bold=True; st.font.color.rgb=RGBColor(0,0,0)
        st.paragraph_format.space_before=Pt(0 if level==1 else 9); st.paragraph_format.space_after=Pt(14 if level==1 else 7)
        st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER if level==1 else WD_ALIGN_PARAGRAPH.LEFT
    doc.styles['Caption'].font.name='Times New Roman'; doc.styles['Caption'].font.size=Pt(11)
    for name in ['TOC 1','TOC 2','TOC 3']:
        if name not in doc.styles:
            from docx.enum.style import WD_STYLE_TYPE
            doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
        st=doc.styles[name]; st.font.name='Times New Roman'; st.font.size=Pt(11)
        st.paragraph_format.space_after=Pt(3); st.paragraph_format.line_spacing=1
        st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
    settings=doc.settings.element; upd=OxmlElement('w:updateFields'); upd.set(qn('w:val'),'true'); settings.append(upd)
    for block in blocks:
        kind=block[0]
        if kind=='cover':
            for text,size in cover_lines():
                para=doc.add_paragraph(); para.alignment=WD_ALIGN_PARAGRAPH.CENTER
                para.paragraph_format.space_after=Pt(23)
                run=para.add_run(text); run.font.size=Pt(size); run.bold=True
            # Separate the unnumbered cover from the numbered report.
            from docx.enum.section import WD_SECTION_START
            body=doc.add_section(WD_SECTION_START.NEW_PAGE)
            body.footer.is_linked_to_previous=False
            numbering=OxmlElement('w:pgNumType'); numbering.set(qn('w:start'),'1'); body._sectPr.append(numbering)
            para=body.footer.paragraphs[0]; para.alignment=WD_ALIGN_PARAGRAPH.CENTER
            field(para,'PAGE','1')
        elif kind=='heading': doc.add_heading(block[1],level=block[2])
        elif kind=='paragraph': doc.add_paragraph(block[1])
        elif kind=='break': doc.add_page_break()
        elif kind=='index':
            para=doc.add_paragraph(block[1]); para.alignment=WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs: run.bold=True; run.font.size=Pt(16)
            instruction={'toc':'TOC \\o "1-3" \\h \\z \\u','figures':'TOC \\h \\z \\t "Figure Caption,1"','tables':'TOC \\h \\z \\t "Table Caption,1"'}[block[2]]
            field(doc.add_paragraph(),instruction)
        elif kind=='table':
            _,caption,headers,rows,widths=block
            doc.add_paragraph(caption,style='Table Caption')
            t=doc.add_table(rows=1,cols=len(headers)); t.style='Table Grid'; t.autofit=False
            if widths:
                for col,w in zip(t.columns,widths): col.width=Pt((A4[0]-144)*w)
            for cell,value in zip(t.rows[0].cells,headers): cell.text=str(value)
            repeat=OxmlElement('w:tblHeader'); repeat.set(qn('w:val'),'true'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
            for row in rows:
                for cell,value in zip(t.add_row().cells,row): cell.text=str(value)
            for row_index,row in enumerate(t.rows):
                if widths:
                    for cell,w in zip(row.cells,widths): cell.width=Pt((A4[0]-144)*w)
                for cell in row.cells:
                    for para in cell.paragraphs:
                        para.alignment=WD_ALIGN_PARAGRAPH.LEFT
                        para.paragraph_format.space_after=Pt(3); para.paragraph_format.line_spacing=1
                        for run in para.runs: run.font.size=Pt(10.5); run.bold=row_index==0
            doc.add_paragraph().paragraph_format.space_after=Pt(1)
        elif kind=='figure':
            _,caption,path,maxh=block
            doc.add_paragraph(caption,style='Figure Caption')
            with PILImage.open(path) as im: iw,ih=im.size
            scale=min((A4[0]-144)/iw,maxh/ih)
            para=doc.add_paragraph(); para.alignment=WD_ALIGN_PARAGRAPH.CENTER
            para.add_run().add_picture(path,width=Pt(iw*scale),height=Pt(ih*scale))
        elif kind=='code':
            para=doc.add_paragraph(block[1]); para.alignment=WD_ALIGN_PARAGRAPH.LEFT
            para.paragraph_format.line_spacing=1; para.paragraph_format.space_after=Pt(9)
            for run in para.runs: run.font.name='Courier New'; run.font.size=Pt(9)
    doc.core_properties.author='Nahabwe Derrick Eric'; doc.core_properties.title='Rental Management System Project Report'
    doc.save(BASE.with_suffix('.docx'))

def main():
    content()
    # Caption styles allow Word to regenerate separate figure and table lists.
    from docx.enum.style import WD_STYLE_TYPE
    original=Document
    def document_with_styles():
        d=original()
        for name in ['Figure Caption','Table Caption']:
            st=d.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH); st.base_style=d.styles['Caption']
            st.paragraph_format.keep_with_next=True
        return d
    globals()['Document']=document_with_styles
    build_pdf(); build_docx()
    (OUT/'report_content.json').write_text(json.dumps(blocks,indent=2),encoding='utf-8')
    print('Created:',BASE.with_suffix('.pdf'))
    print('Created:',BASE.with_suffix('.docx'))

if __name__=='__main__': main()
