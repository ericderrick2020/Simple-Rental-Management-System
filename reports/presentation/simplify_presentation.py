"""Create a plain-English copy while preserving the original slide layout."""
from pathlib import Path
from zipfile import ZipFile
from xml.dom import minidom

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Nahabwe_Derrick_Eric_Rental_Management_System_Phase3_Presentation.pptx'
OUTPUT = ROOT / 'Nahabwe_Derrick_Eric_Rental_Management_System_Phase3_Simple.pptx'

TEXT = {
1: {6:'Phase 3 Project Presentation', 10:'PROPERTIES\nTENANTS\nRENT',11:'Python and Tkinter\nMySQL'},
2: {2:'About the project',6:'A desktop app for managing rental records.',9:'PROPERTIES',10:'Keep property details\nand number of units.',14:'Keep tenant details\nand their assigned units.',18:'Record rent paid\nand the balance due.',19:'For landlords and property managers'},
3: {2:'The problem and project goals',6:'Paper records can be lost and are hard to update.',8:'Properties',9:'Keep property and unit details in one place',11:'Tenants',12:'Record tenants and their assigned units',14:'Rent and leases',15:'Track payments, balances, and rental agreements',17:'Database',18:'Store related records in MySQL',20:'Reports and checks',21:'Show summaries and check entries before saving'},
4: {2:'What the project covers',8:'PLANNED FEATURES',9:'Property and tenant records\nRent payments and leases\nSearch, reports, and exports\nA desktop app with MySQL\nLogin and checks on entries',12:'OUTSIDE THIS PROJECT',13:'Web and mobile apps\nCloud storage\nManaging several companies\nOnline payment processing\nFingerprint login and rent predictions',14:'Some planned features still need to be completed.'},
5: {2:'How the system works',6:'main.py\nStarts the app and handles navigation',7:'pages/ and components/\nShow forms, buttons, and tables',8:'data/database.py\nSaves and reads records',9:'Forms check entries before saving.\nEditing and search still need work.'},
6: {2:'Tools used',8:'PYTHON',9:'Runs the application\nand its calculations',12:'TKINTER',13:'Creates the windows,\nforms, and tables',16:'MYSQL',17:'Stores records\nThe connector links it to Python',20:'WINDOWS',21:'The current app\nruns on Windows',22:'VS Code was the editor proposed for the project.'},
7: {2:'Features added so far',6:'Features in the code',7:'Add and view properties\nRegister and view tenants\nRecord rent and balances\nCreate text receipts\nView the dashboard\nLog out and sign in again',8:'Still to finish',9:'Secure login, editing, search,\nleases, exports, and full reports.',10:'This screenshot uses sample data. It does not show a live database test.'},
8: {2:'System demonstration',23:'PAYMENT EXAMPLE',24:'Rent due: UGX 500,000\nBalance: UGX 150,000\nAmount paid: UGX 350,000',27:'CHECK AN INCORRECT ENTRY',28:'Enter a balance higher than the rent.\nShow the warning, then correct it.\nSave and open the record again.',29:'Use sample records in a test database for the demonstration.'},
9: {2:'Test results',8:'CHECKS RUN',16:'TEST',17:'WHAT WAS CHECKED',18:'RESULT',21:'500,000 - 150,000',22:'Calculated 350,000 correctly',25:'Balance below zero or above rent',26:'Warning shown; entry blocked',28:'Log out and sign in',29:'Old pages close; login is required',30:'Returned to a fresh login screen',31:'Earlier results: 10 code checks and 3 logout checks passed. Live database and printing tests are still needed.'},
10: {2:'Problems and how they were handled',7:'Linking records',8:'Each payment belongs to a tenant and a property.',9:'Use record IDs to link the data.',10:'Live database checks are still needed.',12:'Wrong payment details',13:'A wrong balance gives a wrong amount paid.',14:'Check the amount, balance, and date before saving.',15:'The selected payment checks passed.',17:'Logging out',18:'Old pages and forms could stay open after logout.',19:'Close them before showing the login screen.',20:'All three logout checks passed.'},
11: {2:'What I achieved and what is next',8:'WHAT IS IN PLACE',9:'A desktop app for property, tenant,\nand rent records, with a dashboard,\ntext receipts, settings, and logout.',12:'WHAT NEEDS WORK',13:'A safer login\nEditing, search, leases, and exports\nKeeping payment history after deletion',14:'Next steps',15:'1  Improve login and test the live database',16:'2  Finish editing, search, leases, and vacant-unit tracking',17:'3  Keep payment history and complete reports and exports'},
12: {2:'Thank you',6:'That is my Rental Management System.\nAny questions?',7:'Next: a short demonstration',8:'Screenshot with sample data.'},
}

NOTES = [
 'Hello, my name is Nahabwe Derrick Eric. This is my Phase 3 presentation for the Rental Management System. I will explain the problem, show what I have built, and discuss what still needs work.',
 'This project is for landlords and property managers. Keeping records in notebooks or separate files can make it hard to find information. The idea is to keep properties, tenants, and rent payments in one desktop app.',
 'The main goal is to make rental records easier to manage. The app should store property and tenant details, track rent and leases, and show useful summaries. These goals are partly complete. Editing, full lease tracking, and some reports still need work.',
 'The plan covers a local desktop app with records, payments, reports, and a login. Some of these features are still unfinished. Web apps, mobile apps, cloud services, and online payments were outside the project. Choosing Mobile Money on a form only records the payment method; it does not process money.',
 'The system has three main parts. The startup file opens the app and handles navigation. The pages show the forms and tables. The database file saves and reads records. When a user saves a form, the page checks the supported entries before sending them to MySQL.',
 'Python runs the app. Tkinter creates the windows and forms. MySQL stores the records, and the Python connector lets the app communicate with it. The current app runs on Windows. VS Code was the editor proposed in the project plan.',
 'The code includes adding and viewing properties and tenants, recording rent, and creating text receipts. It also has a dashboard, settings, and logout. The screenshot uses sample data. It does not prove that all database operations work. Secure login, editing, search, leases, exports, and detailed reports still need work.',
 'For the demonstration, I will use sample records in a test database. The steps are to sign in, add a property, register a tenant, and record rent. If rent is 500,000 shillings and the balance is 150,000, the amount paid is 350,000. I will show the warning for an invalid balance, correct it, save, and reopen the record. If the database is unavailable, I will explain that and use the screenshots as a backup.',
 'The earlier recorded test run had 13 passing checks and no failures. Ten checked selected code and functions, and three checked logout using real interface controls. The payment checks covered calculations and invalid entries. These checks used simulated database calls, so live database saving and physical printing still need testing.',
 'The records need to stay linked so that each payment matches the right tenant and property. The code uses IDs for this. Payment entries also need checks so that the amount paid is correct. For logout, the app closes old pages and forms before returning to login. The selected payment and logout checks passed. Live database checks are still needed.',
 'The project now has a basic desktop app for linked rental records. It still needs a safer login, editing, search, full lease tracking, and more reports. Deleting a property or tenant currently also deletes related payments, so keeping payment history is another improvement. I would first improve login and verify the database, then finish the missing features.',
 'Thank you for listening. I will now give a short demonstration and answer your questions.',
]

def replace_text(shape, value):
    body = shape.getElementsByTagName('p:txBody')[0]
    paragraphs = list(body.getElementsByTagName('a:p'))
    template = paragraphs[0].cloneNode(True)
    for paragraph in paragraphs:
        body.removeChild(paragraph)
    for line in value.split('\n'):
        paragraph = template.cloneNode(True)
        runs = list(paragraph.getElementsByTagName('a:r'))
        run = runs[0].cloneNode(True) if runs else body.ownerDocument.createElement('a:r')
        for child in list(paragraph.childNodes):
            if child.nodeType == child.ELEMENT_NODE and child.tagName != 'a:pPr':
                paragraph.removeChild(child)
        for child in list(run.childNodes):
            if child.nodeType == child.ELEMENT_NODE and child.tagName != 'a:rPr':
                run.removeChild(child)
        text = body.ownerDocument.createElement('a:t')
        text.appendChild(body.ownerDocument.createTextNode(line))
        run.appendChild(text)
        paragraph.appendChild(run)
        body.appendChild(paragraph)

def main():
    with ZipFile(SOURCE) as source, ZipFile(OUTPUT, 'w') as output:
        for entry in source.infolist():
            content = source.read(entry.filename)
            if entry.filename.startswith('ppt/slides/slide') and entry.filename.endswith('.xml'):
                number = int(Path(entry.filename).stem.removeprefix('slide'))
                doc = minidom.parseString(content)
                shapes = doc.getElementsByTagName('p:sp')
                replace_text(shapes[1], 'PHASE 3 PRESENTATION')
                for index, value in TEXT[number].items():
                    replace_text(shapes[index], value)
                content = doc.toxml(encoding='UTF-8')
            elif entry.filename.startswith('ppt/notesSlides/notesSlide') and entry.filename.endswith('.xml'):
                number = int(Path(entry.filename).stem.removeprefix('notesSlide'))
                doc = minidom.parseString(content)
                for shape in doc.getElementsByTagName('p:sp'):
                    placeholders = shape.getElementsByTagName('p:ph')
                    if placeholders and placeholders[0].getAttribute('type') == 'body':
                        replace_text(shape, NOTES[number-1])
                content = doc.toxml(encoding='UTF-8')
            output.writestr(entry, content)
    with ZipFile(OUTPUT) as deck:
        assert deck.testzip() is None
        for name in deck.namelist():
            if name.endswith('.xml'):
                minidom.parseString(deck.read(name))
        assert len([n for n in deck.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]) == 12
    print(f'Created and checked: {OUTPUT.name}')

if __name__ == '__main__':
    main()
