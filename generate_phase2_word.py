from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import html


OUTPUT_DOCX = Path("Phase2_Design_And_Incubation_Report.docx")
PROJECT_SCREENSHOT = Path("assets/report_project_screen.png")
TENANT_SCREENSHOT = Path("assets/report_add_tenant_screen.png")


def esc(text):
    return html.escape(str(text), quote=False)


def paragraph(text="", style=None):
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    if text == "":
        return "<w:p/>"
    lines = str(text).split("\n")
    runs = []
    for index, line in enumerate(lines):
        if index:
            runs.append("<w:br/>")
        runs.append(f"<w:t xml:space=\"preserve\">{esc(line)}</w:t>")
    return f"<w:p>{style_xml}<w:r>{''.join(runs)}</w:r></w:p>"


def bullet(text):
    return (
        '<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/>'
        '<w:numId w:val="1"/></w:numPr></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
    )


def table(headers, rows):
    grid = "".join('<w:gridCol w:w="2400"/>' for _ in headers)
    out = [
        "<w:tbl>",
        '<w:tblPr><w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '</w:tblBorders></w:tblPr>',
        f"<w:tblGrid>{grid}</w:tblGrid>",
    ]

    def tr(cells, header=False):
        row_xml = ["<w:tr>"]
        for cell in cells:
            shade = '<w:shd w:fill="D9EAF7"/>' if header else ""
            bold_open = "<w:b/>" if header else ""
            row_xml.append(
                "<w:tc><w:tcPr>"
                '<w:tcW w:w="2400" w:type="dxa"/>'
                f"{shade}</w:tcPr>"
                f"<w:p><w:r><w:rPr>{bold_open}</w:rPr>"
                f'<w:t xml:space="preserve">{esc(cell)}</w:t></w:r></w:p>'
                "</w:tc>"
            )
        row_xml.append("</w:tr>")
        return "".join(row_xml)

    out.append(tr(headers, header=True))
    for row in rows:
        out.append(tr(row))
    out.append("</w:tbl>")
    out.append("<w:p/>")
    return "".join(out)


def codeblock(text):
    return (
        '<w:p><w:pPr><w:pStyle w:val="Code"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{esc(text.strip())}</w:t></w:r></w:p>'
    )


def image_paragraph(rel_id, description, doc_id, width_inches, source_width, source_height):
    cx = int(width_inches * 914400)
    cy = int(cx * source_height / source_width)
    return f'''
<w:p>
<w:r>
<w:drawing>
<wp:inline distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/>
<wp:effectExtent l="0" t="0" r="0" b="0"/>
<wp:docPr id="{doc_id}" name="{esc(description)}"/>
<wp:cNvGraphicFramePr/>
<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:nvPicPr>
<pic:cNvPr id="{doc_id}" name="{esc(description)}"/>
<pic:cNvPicPr/>
</pic:nvPicPr>
<pic:blipFill>
<a:blip r:embed="{rel_id}"/>
<a:stretch><a:fillRect/></a:stretch>
</pic:blipFill>
<pic:spPr>
<a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
</pic:spPr>
</pic:pic>
</a:graphicData>
</a:graphic>
</wp:inline>
</w:drawing>
</w:r>
</w:p>
'''


def document_xml(body_items):
    body = "".join(body_items)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14">
<w:body>
{body}
<w:sectPr>
<w:pgSz w:w="12240" w:h="15840"/>
<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
</w:sectPr>
</w:body>
</w:document>'''


def styles_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/>
<w:qFormat/>
<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Title">
<w:name w:val="Title"/>
<w:qFormat/>
<w:rPr><w:b/><w:sz w:val="36"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Heading1">
<w:name w:val="heading 1"/>
<w:basedOn w:val="Normal"/>
<w:next w:val="Normal"/>
<w:qFormat/>
<w:pPr><w:spacing w:before="360" w:after="160"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="28"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Heading2">
<w:name w:val="heading 2"/>
<w:basedOn w:val="Normal"/>
<w:next w:val="Normal"/>
<w:qFormat/>
<w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="24"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Code">
<w:name w:val="Code"/>
<w:basedOn w:val="Normal"/>
<w:pPr><w:spacing w:before="120" w:after="120"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/><w:sz w:val="18"/></w:rPr>
</w:style>
<w:style w:type="table" w:styleId="TableGrid">
<w:name w:val="Table Grid"/>
<w:tblPr>
<w:tblBorders>
<w:top w:val="single" w:sz="4" w:space="0" w:color="999999"/>
<w:left w:val="single" w:sz="4" w:space="0" w:color="999999"/>
<w:bottom w:val="single" w:sz="4" w:space="0" w:color="999999"/>
<w:right w:val="single" w:sz="4" w:space="0" w:color="999999"/>
<w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>
<w:insideV w:val="single" w:sz="4" w:space="0" w:color="999999"/>
</w:tblBorders>
</w:tblPr>
</w:style>
</w:styles>'''


def numbering_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:abstractNum w:abstractNumId="0">
<w:multiLevelType w:val="hybridMultilevel"/>
<w:lvl w:ilvl="0">
<w:start w:val="1"/>
<w:numFmt w:val="bullet"/>
<w:lvlText w:val="-"/>
<w:lvlJc w:val="left"/>
<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
</w:lvl>
</w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>'''


def static_files():
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "[Content_Types].xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>''',
        "_rels/.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>''',
        "word/_rels/document.xml.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/report_project_screen.png"/>
<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/report_add_tenant_screen.png"/>
</Relationships>''',
        "docProps/core.xml": f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>Python Project - Phase 2 Design and Incubation Report</dc:title>
<dc:subject>Rental Management System</dc:subject>
<dc:creator>Codex</dc:creator>
<cp:lastModifiedBy>Codex</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>''',
        "docProps/app.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Application>Microsoft Word</Application>
</Properties>''',
        "word/styles.xml": styles_xml(),
        "word/numbering.xml": numbering_xml(),
    }


def build_body():
    items = []
    items.append(paragraph("Python Project - Phase 2", "Title"))
    items.append(paragraph("Design & Incubation Report", "Heading1"))
    items.append(paragraph("Project: Rental Management System"))
    items.append(paragraph("Prepared for submission: August 18, 2026"))
    items.append(paragraph("Student Name: ______________________________"))
    items.append(paragraph("Class / Course: _____________________________"))

    items.append(paragraph("1. Purpose", "Heading1"))
    items.append(paragraph(
        "Phase 2 focuses on refining the Rental Management System before full development. "
        "The system is a Python Tkinter desktop application for managing rental properties, tenants, "
        "rent payments, dashboard summaries, and system settings. The design separates the user interface, "
        "data access, validation, and business logic so the application can be expanded safely."
    ))
    items.append(paragraph(
        "Current implementation already includes a login screen, the main application window, sidebar navigation, "
        "reusable layout components, dashboard cards, reusable tables, and modal forms for adding property, tenant, "
        "and payment records in memory. The finalized Phase 2 design adds persistent MySQL storage and complete "
        "CRUD operations."
    ))

    items.append(paragraph("2. Refined System Architecture", "Heading1"))
    items.append(paragraph(
        "The system will follow a modular architecture. Tkinter pages handle screens and user actions. "
        "Service modules contain business rules. Data modules connect to MySQL. Validation modules check "
        "data before records are saved."
    ))
    items.append(table(
        ["Module / File", "Responsibility", "Interaction"],
        [
            ["main.py", "Starts the application, creates the main window, sidebar, header, and page container.", "Imports page classes and displays selected pages through show_page()."],
            ["config/settings.py", "Stores app name, window size, colors, and fonts.", "Used by pages and components for consistent styling."],
            ["components/header.py", "Reusable top header that displays the active page title.", "Updated by main.py when navigation changes."],
            ["components/sidebar.py", "Navigation menu for Dashboard, Properties, Tenants, Payments, and Settings.", "Calls main.py show_page() when a user selects a page."],
            ["components/stat_card.py", "Reusable dashboard summary card.", "Used by dashboard_page.py to display totals."],
            ["components/simple_table.py", "Reusable Treeview table for record lists.", "Used by pages that display properties, tenants, and payments."],
            ["pages/base_page.py", "Shared page layout, scrollable content area, and reusable buttons.", "Inherited by all page modules."],
            ["pages/login_page.py", "Authenticates the user before the main application layout is shown.", "Calls create_app_layout() after a successful username and password check."],
            ["pages/dashboard_page.py", "Displays portfolio health, occupancy, payment totals, activity, and quick actions.", "Reads summary data from services after storage is connected."],
            ["pages/properties_page.py", "Manages rental property records and property forms.", "Calls validation and property service functions."],
            ["pages/tenants_page.py", "Manages tenant records and assigned property/unit information.", "Calls validation and tenant service functions."],
            ["pages/payments_page.py", "Records rent payments, displays payment history, and tracks balances.", "Calls validation and payment service functions."],
            ["pages/settings_page.py", "Stores application settings and user preferences.", "Calls settings service where required."],
            ["data/database.py", "Opens MySQL connections, initializes the database, loads property options, and saves property/tenant records.", "Used by pages and future service modules."],
            ["data/schema.sql", "Defines the MySQL database, users, properties, tenants, and payments tables.", "Imported into MySQL/XAMPP before using persistent storage."],
            ["requirements.txt", "Lists required external packages for database connection.", "Installs mysql-connector-python."],
            ["services/property_service.py", "Proposed module: add, update, delete, search, and list properties.", "Uses database.py and validators.py."],
            ["services/tenant_service.py", "Proposed module: add, update, delete, search, and list tenants.", "Uses database.py and validators.py."],
            ["services/payment_service.py", "Proposed module: record payments, search payments, calculate balances.", "Uses database.py and validators.py."],
            ["utils/validators.py", "Proposed module: validates names, phone numbers, money values, dates, and IDs.", "Called before data is saved or updated."],
        ],
    ))
    items.append(paragraph("Module Interaction Flow", "Heading2"))
    items.append(codeblock(
        "User Action in Tkinter Page\n"
        "        |\n"
        "        v\n"
        "Page method reads form data and calls validation\n"
        "        |\n"
        "        v\n"
        "Service module applies business rules\n"
        "        |\n"
        "        v\n"
        "data/database.py runs MySQL query\n"
        "        |\n"
        "        v\n"
        "Result returns to service, then page\n"
        "        |\n"
        "        v\n"
        "Tkinter page refreshes table, dashboard, or messagebox"
    ))

    items.append(paragraph("3. Detailed Flowcharts", "Heading1"))
    flowcharts = {
        "3.1 Add Record Flowchart": [
            "Start", "User clicks Add button", "Display input form/modal", "User enters record details",
            "Validate required fields", "If invalid: show error and return to form",
            "Validate data types and ranges", "If invalid: highlight field and show correction message",
            "Check duplicate ID/contact", "If duplicate: show duplicate record error",
            "Save record to MySQL", "Refresh table/dashboard", "Show success message", "End"
        ],
        "3.2 Update Record Flowchart": [
            "Start", "User selects existing row", "If no row selected: show selection message",
            "Load record into edit form", "User edits details", "Validate changed values",
            "If invalid: keep form open and show field error", "Confirm update action",
            "If cancelled: close form without saving", "Update record in MySQL",
            "If record missing: show not found message", "Refresh list and summaries", "End"
        ],
        "3.3 Delete Record Flowchart": [
            "Start", "User selects a record", "If no selection: show selection error",
            "Check related records", "If dependency exists: block delete or ask to reassign",
            "Show confirmation dialog", "If cancelled: return to list",
            "Delete record from MySQL", "If database error: show error and keep data unchanged",
            "Refresh table/dashboard", "End"
        ],
        "3.4 Search / View Records Flowchart": [
            "Start", "User opens target page", "Load all records from database",
            "If database file is missing: create database and show empty table",
            "User enters search keyword", "Validate keyword/filter",
            "If keyword is empty: display all records", "Query matching records",
            "If no match: show record not found message", "Display results in table", "End"
        ],
        "3.5 Exit Flowchart": [
            "Start", "User clicks Exit or closes application window",
            "Check unsaved form changes", "If unsaved changes exist: ask user to confirm exit",
            "Commit and close database connection", "Destroy Tkinter window", "End"
        ],
    }
    for title, steps in flowcharts.items():
        items.append(paragraph(title, "Heading2"))
        items.append(codeblock("\n   v\n".join(steps)))

    items.append(paragraph("4. Function-Level Design", "Heading1"))
    items.append(table(
        ["Function Name", "Purpose", "Parameters", "Returns / Output"],
        [
            ["RentalManagementApp.__init__()", "Create the main Tkinter app window and layout.", "self", "Initialized application window."],
            ["create_pages()", "Create page objects once and store them in a dictionary.", "self", "None."],
            ["show_page()", "Display the selected page and update header/sidebar state.", "page_name: str", "None. Ignores invalid page name."],
            ["LoginPage.check_login()", "Check username and password before opening the main dashboard.", "self", "Calls login success function or shows login error."],
            ["LoginPage.toggle_password_visibility()", "Show or hide password characters on the login form.", "self", "None. Updates password entry display."],
            ["BasePage.create_primary_button()", "Create a consistent primary action button.", "parent, text, command", "tk.Button instance."],
            ["BasePage.create_secondary_button()", "Create a consistent secondary action button.", "parent, text, command", "tk.Button instance."],
            ["PropertiesPage.add_property()", "Open modal form used to capture property details.", "self", "None. Shows modal."],
            ["PropertiesPage.save_property()", "Validate property fields and save them.", "entries: dict, modal", "Success through table refresh or warning message."],
            ["PropertiesPage.center_modal()", "Position a modal window at the center of the main app.", "modal", "None."],
            ["SimpleTable.set_rows()", "Replace current table rows with a provided record list.", "rows: list[tuple]", "None. Updates Treeview."],
            ["DashboardPage.refresh_page()", "Reload dashboard data and update stat cards.", "self", "None. Updates cards."],
            ["initialize_database()", "Create the MySQL database and tables from data/schema.sql when MySQL is available.", "None", "True if initialized, False if unavailable."],
            ["get_property_options()", "Load active properties for the Add Tenant dropdown.", "None", "List of property records."],
            ["add_property()", "Save a new property record.", "property_data: dict", "New property ID or error message."],
            ["get_properties()", "Load properties from MySQL for the Properties page.", "None", "List of property records."],
            ["update_property()", "Edit an existing property record.", "property_id: int, updates: dict", "True/False with message."],
            ["delete_property()", "Remove a property if it has no blocked dependencies.", "property_id: int", "True/False with message."],
            ["search_properties()", "Find properties by name, location, status, or ID.", "keyword: str", "List of matching records."],
            ["add_tenant()", "Save a new tenant and link to a property/unit.", "tenant_data: dict", "New tenant ID or error message."],
            ["get_tenants()", "Load tenant records with their linked property names.", "None", "List of tenant records."],
            ["record_payment()", "Save rent payment and update balance history.", "payment_data: dict", "Payment ID or error message."],
            ["calculate_balance()", "Calculate outstanding balance for a tenant.", "tenant_id: int", "Balance amount."],
            ["validate_required()", "Check that required fields are not empty.", "fields: dict", "True or validation message."],
            ["validate_money()", "Confirm currency values are numeric and not negative.", "amount: str", "Float value or error message."],
            ["validate_date()", "Confirm date follows YYYY-MM-DD format.", "date_text: str", "date object or error message."],
        ],
    ))

    items.append(paragraph("5. Final Data Structure / Database Schema", "Heading1"))
    items.append(paragraph(
        "Final storage method: MySQL. MySQL is suitable because the project now needs relational storage that "
        "can link properties, tenants, and payments, while also supporting multi-table queries, constraints, "
        "and future expansion beyond in-memory sample data."
    ))
    items.append(paragraph("5.1 properties Table", "Heading2"))
    items.append(table(
        ["Field Name", "Data Type", "Constraint", "Description"],
        [
            ["property_id", "INT", "PRIMARY KEY AUTO_INCREMENT", "Unique property record ID."],
            ["property_name", "VARCHAR(120)", "NOT NULL", "Name of property."],
            ["location", "VARCHAR(120)", "NOT NULL", "Physical location."],
            ["total_units", "INT", "NOT NULL DEFAULT 0", "Number of rentable units."],
            ["monthly_rent", "DECIMAL(12,2)", "NOT NULL DEFAULT 0.00", "Default monthly rent per unit."],
            ["status", "VARCHAR(30)", "NOT NULL DEFAULT 'Active'", "Active or Inactive."],
            ["created_at", "TIMESTAMP", "NOT NULL DEFAULT CURRENT_TIMESTAMP", "Date created."],
        ],
    ))
    items.append(paragraph("5.2 tenants Table", "Heading2"))
    items.append(table(
        ["Field Name", "Data Type", "Constraint", "Description"],
        [
            ["tenant_id", "INT", "PRIMARY KEY AUTO_INCREMENT", "Unique tenant ID."],
            ["property_id", "INT", "FOREIGN KEY REFERENCES properties(property_id)", "Selected property from the dropdown."],
            ["tenant_name", "VARCHAR(120)", "NOT NULL", "Tenant full name."],
            ["phone", "VARCHAR(40)", "UNIQUE NOT NULL", "Tenant phone number."],
            ["email", "VARCHAR(120)", "NULL", "Optional tenant email."],
            ["unit_number", "VARCHAR(40)", "NOT NULL", "Assigned room/unit."],
            ["lease_start", "DATE", "NULL", "Lease start date."],
            ["monthly_rent", "DECIMAL(12,2)", "NOT NULL DEFAULT 0.00", "Tenant monthly rent."],
            ["emergency_contact", "VARCHAR(120)", "NULL", "Emergency contact details."],
            ["status", "VARCHAR(30)", "NOT NULL DEFAULT 'Active'", "Active, Pending Move-in, or Notice Given."],
        ],
    ))
    items.append(paragraph("5.3 payments Table", "Heading2"))
    items.append(table(
        ["Field Name", "Data Type", "Constraint", "Description"],
        [
            ["payment_id", "INT", "PRIMARY KEY AUTO_INCREMENT", "Unique payment ID."],
            ["tenant_id", "INT", "FOREIGN KEY REFERENCES tenants(tenant_id)", "Tenant who paid rent."],
            ["amount", "DECIMAL(12,2)", "NOT NULL", "Payment amount."],
            ["payment_date", "DATE", "NOT NULL", "Date payment was received."],
            ["payment_method", "VARCHAR(40)", "NOT NULL", "Cash, Mobile Money, Bank Transfer, or Card."],
            ["reference_no", "VARCHAR(80)", "UNIQUE", "Transaction or receipt reference."],
            ["notes", "TEXT", "NULL", "Optional payment notes."],
            ["status", "VARCHAR(30)", "NOT NULL DEFAULT 'Paid'", "Paid, Pending, or Overdue."],
        ],
    ))

    items.append(paragraph("5.4 Sample Record Structure", "Heading2"))
    items.append(paragraph(
        "The screenshot below shows sample property records as they appear in the project interface after the "
        "database fields are connected to the table view."
    ))
    items.append(image_paragraph("rId3", "Project property records screenshot", 1, 6.4, 1400, 900))

    items.append(paragraph("6. UI Mockups and Navigation Layout", "Heading1"))
    items.append(paragraph(
        "The project uses a Tkinter graphical interface. The user navigates with a left sidebar, while the top "
        "header displays the active page. The screenshots below show the properties screen and the Add Tenant form "
        "with the new property dropdown."
    ))
    items.append(paragraph("Main Project Screen", "Heading2"))
    items.append(image_paragraph("rId3", "Main project screen screenshot", 2, 6.4, 1400, 900))
    items.append(paragraph("Add Tenant Form With Property Dropdown", "Heading2"))
    items.append(image_paragraph("rId4", "Add tenant property dropdown screenshot", 3, 6.4, 1400, 900))
    items.append(paragraph("Navigation Flow", "Heading2"))
    items.append(codeblock(
        "Open App -> Login\n"
        "Login Success -> Dashboard\n"
        "Dashboard -> Properties -> Add / Update / Delete / Search Property\n"
        "Dashboard -> Tenants -> Add / Update / Delete / Search Tenant\n"
        "Dashboard -> Payments -> Record / Update / Delete / Search Payment\n"
        "Any Page -> Settings\n"
        "Any Page -> Close Window -> Confirm Exit -> End"
    ))

    items.append(paragraph("7. Error Handling Plan", "Heading1"))
    items.append(table(
        ["Possible Error", "Handling Method", "User Feedback"],
        [
            ["Empty required field", "Check field before save using validate_required().", "Show warning: Please fill in all required details."],
            ["Incorrect data type", "Convert values inside try-except blocks.", "Show warning: Units must be a whole number or amount must be numeric."],
            ["Negative amount or unit count", "Use range checks and database CHECK constraints.", "Show warning: Value cannot be negative."],
            ["Duplicate phone or payment reference", "Catch MySQL integrity errors.", "Show warning: Record already exists."],
            ["Missing connector or MySQL server", "Return fallback sample data and keep the app open.", "Continue with sample properties until setup is complete."],
            ["Record not found", "Check query result before update/delete.", "Show message: Record not found."],
            ["Foreign key conflict", "Use MySQL foreign key constraints and catch database errors.", "Show message explaining related tenant/payment records exist."],
            ["Unexpected database failure", "Use try-except-finally around database operations.", "Show safe error message and keep app open."],
            ["Invalid date", "Parse date using datetime.strptime().", "Show warning: Use YYYY-MM-DD date format."],
            ["User cancels operation", "Close modal without calling save/update/delete.", "No data is changed."],
        ],
    ))
    items.append(paragraph("Validation Rules", "Heading2"))
    for text in [
        "Property name, location, tenant name, phone number, amount, and payment date must not be empty.",
        "Units must be a whole number greater than or equal to zero.",
        "Money values must be numeric and greater than or equal to zero, except payments which must be greater than zero.",
        "Phone numbers must be unique and should follow the local/international phone format accepted by the project.",
        "Dates must use ISO format: YYYY-MM-DD.",
        "Delete actions must ask for confirmation before changing data.",
    ]:
        items.append(bullet(text))

    items.append(paragraph("8. Detailed Testing Plan", "Heading1"))
    items.append(table(
        ["Function", "Test Input", "Expected Output", "Type"],
        [
            ["add_property", "PROP-004, Ntinda Villas, 8, 7000000", "Record saved and table refreshes.", "Normal"],
            ["add_property", "Empty property name", "Error message for missing details.", "Invalid"],
            ["add_property", "Units = abc", "Error message: Units must be a whole number.", "Invalid"],
            ["add_property", "Duplicate property code PROP-001", "Duplicate record error.", "Edge"],
            ["update_property", "Change Rocky Estates units from 20 to 22", "Record updated and dashboard refreshes.", "Normal"],
            ["update_property", "No selected row", "Message asks user to select a record.", "Invalid"],
            ["delete_property", "Delete property with no tenants", "Property removed from database and table.", "Normal"],
            ["delete_property", "Delete property with active tenants", "Delete blocked or user asked to reassign tenants.", "Edge"],
            ["search_properties", "Keyword Kampala", "Only matching property records display.", "Normal"],
            ["search_properties", "Unknown keyword ZZZ", "No records found message or empty table.", "Edge"],
            ["add_tenant", "Valid tenant linked to property 1", "Tenant saved successfully.", "Normal"],
            ["add_tenant", "Duplicate phone number", "Duplicate phone warning.", "Invalid"],
            ["record_payment", "Tenant 1, UGX 1200000, 2026-08-10", "Payment saved and balance recalculated.", "Normal"],
            ["record_payment", "Amount = -50000", "Error message: payment amount must be greater than zero.", "Invalid"],
            ["record_payment", "Date = 10/08/2026", "Error message: Use YYYY-MM-DD.", "Invalid"],
            ["calculate_balance", "Tenant with partial payment", "Correct unpaid balance displayed.", "Edge"],
            ["check_login", "Username eric and password 12345", "Main dashboard opens.", "Normal"],
            ["check_login", "Wrong password", "Login Failed error message appears.", "Invalid"],
            ["show_page", "Dashboard", "Dashboard page appears and sidebar highlights Dashboard.", "Normal"],
            ["show_page", "UnknownPage", "No crash; page remains unchanged.", "Edge"],
            ["exit_app", "Close window with no unsaved data", "Database closes and app exits.", "Normal"],
            ["exit_app", "Close window with unsaved form data", "Confirmation message appears.", "Edge"],
        ],
    ))
    items.append(paragraph("Testing Methods", "Heading2"))
    for text in [
        "Manual GUI testing will confirm navigation, button actions, modal behavior, and table refreshes.",
        "Unit tests will check validators and service functions without opening the Tkinter interface.",
        "Database tests will use a test MySQL database or sample fallback data to avoid changing real records.",
        "Regression tests will verify that dashboard totals still update after CRUD changes.",
    ]:
        items.append(bullet(text))

    items.append(paragraph("9. Development Timeline", "Heading1"))
    items.append(table(
        ["Stage", "Main Work", "Deliverables"],
        [
            ["Week 1 - Menu and Structure", "Confirm navigation, page layout, reusable buttons, tables, and dashboard shell.", "Stable GUI skeleton with Dashboard, Properties, Tenants, Payments, and Settings pages."],
            ["Week 2 - Data Storage", "Create data/database.py, data/schema.sql, seed/sample data, and MySQL connection helpers.", "rental_management_system database created with properties, tenants, and payments tables."],
            ["Week 3 - CRUD Operations", "Implement add, update, delete, search, and list operations for properties and tenants.", "Working property and tenant management screens."],
            ["Week 4 - Payments and Balances", "Implement rent payment recording, payment history, balance calculation, and dashboard summaries.", "Working payment workflow and accurate dashboard totals."],
            ["Week 5 - Validation and Error Handling", "Add validators, try-except handling, confirmation dialogs, and user-friendly messages.", "Reduced crashes and clear feedback for invalid actions."],
            ["Week 6 - Testing and Debugging", "Run manual GUI tests, unit tests, database tests, and fix issues.", "Final tested project ready for Phase 3 development/submission."],
        ],
    ))

    items.append(paragraph("10. Conclusion", "Heading1"))
    items.append(paragraph(
        "This Phase 2 design prepares the Rental Management System for organized development. The application "
        "will use Tkinter for the interface, MySQL for storage, separate service modules for business logic, "
        "and validators for clean input handling. The flowcharts, function designs, database schema, UI mockups, "
        "error handling plan, test cases, and timeline provide a clear roadmap for the next phase."
    ))
    return items


def write_docx():
    if not PROJECT_SCREENSHOT.exists() or not TENANT_SCREENSHOT.exists():
        raise FileNotFoundError(
            "Run generate_report_screenshots.ps1 before generating the Word report."
        )

    files = static_files()
    files["word/document.xml"] = document_xml(build_body())
    files["word/media/report_project_screen.png"] = PROJECT_SCREENSHOT.read_bytes()
    files["word/media/report_add_tenant_screen.png"] = TENANT_SCREENSHOT.read_bytes()
    with ZipFile(OUTPUT_DOCX, "w", ZIP_DEFLATED) as docx:
        for name, content in files.items():
            docx.writestr(name, content)
    print(f"Created {OUTPUT_DOCX}")


if __name__ == "__main__":
    write_docx()
