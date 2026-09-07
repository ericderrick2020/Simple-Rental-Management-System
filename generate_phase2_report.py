from pathlib import Path
import textwrap


OUTPUT_PDF = Path("Phase2_Design_And_Incubation_Report.pdf")
OUTPUT_MD = Path("Phase2_Design_And_Incubation_Report.md")

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN_X = 54
MARGIN_TOP = 58
MARGIN_BOTTOM = 48


def pdf_escape(text):
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


class SimplePDF:
    def __init__(self):
        self.pages = []
        self.new_page()

    def new_page(self):
        self.pages.append([])
        self.y = PAGE_HEIGHT - MARGIN_TOP
        self._footer_reserved = False

    @property
    def current(self):
        return self.pages[-1]

    def ensure_space(self, amount):
        if self.y - amount < MARGIN_BOTTOM:
            self.new_page()

    def text(self, x, y, content, font="F1", size=10):
        self.current.append(f"BT /{font} {size} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm ({pdf_escape(content)}) Tj ET")

    def line(self, x1, y1, x2, y2):
        self.current.append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def rect(self, x, y, w, h):
        self.current.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re S")

    def heading(self, text):
        self.ensure_space(36)
        self.text(MARGIN_X, self.y, text, "F2", 16)
        self.y -= 22
        self.line(MARGIN_X, self.y + 8, PAGE_WIDTH - MARGIN_X, self.y + 8)
        self.y -= 8

    def subheading(self, text):
        self.ensure_space(28)
        self.text(MARGIN_X, self.y, text, "F2", 12)
        self.y -= 18

    def paragraph(self, text, indent=0):
        lines = textwrap.wrap(text, width=95 - indent, break_long_words=False)
        self.ensure_space((len(lines) * 13) + 6)
        for line in lines:
            self.text(MARGIN_X + (indent * 5), self.y, line, "F1", 10)
            self.y -= 13
        self.y -= 4

    def bullet(self, text):
        lines = textwrap.wrap(text, width=91, break_long_words=False)
        self.ensure_space((len(lines) * 13) + 4)
        if lines:
            self.text(MARGIN_X, self.y, "-", "F1", 10)
            self.text(MARGIN_X + 14, self.y, lines[0], "F1", 10)
            self.y -= 13
            for line in lines[1:]:
                self.text(MARGIN_X + 14, self.y, line, "F1", 10)
                self.y -= 13
        self.y -= 2

    def codeblock(self, text, size=8.5):
        lines = text.strip("\n").splitlines()
        line_height = size + 3
        self.ensure_space((len(lines) * line_height) + 14)
        box_top = self.y + 5
        box_height = (len(lines) * line_height) + 8
        self.rect(MARGIN_X - 4, box_top - box_height, PAGE_WIDTH - (2 * MARGIN_X) + 8, box_height)
        self.y -= 6
        for line in lines:
            self.text(MARGIN_X, self.y, line[:112], "F3", size)
            self.y -= line_height
        self.y -= 8

    def table(self, headers, rows, widths=None):
        if widths is None:
            widths = [1] * len(headers)
        total = sum(widths)
        max_chars = [max(8, int((w / total) * 88)) for w in widths]

        def row_lines(row):
            wrapped = []
            for value, chars in zip(row, max_chars):
                wrapped.append(textwrap.wrap(str(value), width=chars, break_long_words=False) or [""])
            return wrapped

        all_rows = [headers] + rows
        for index, row in enumerate(all_rows):
            wrapped = row_lines(row)
            height_lines = max(len(cell) for cell in wrapped)
            self.ensure_space((height_lines * 12) + 8)
            x = MARGIN_X
            for col_index, cell_lines in enumerate(wrapped):
                col_width = ((PAGE_WIDTH - (2 * MARGIN_X)) * widths[col_index]) / total
                font = "F2" if index == 0 else "F1"
                for offset, line in enumerate(cell_lines):
                    self.text(x, self.y - (offset * 12), line, font, 8.5)
                x += col_width
            self.y -= (height_lines * 12) + 6
            if index == 0:
                self.line(MARGIN_X, self.y + 2, PAGE_WIDTH - MARGIN_X, self.y + 2)
                self.y -= 3
        self.y -= 8

    def build(self, path):
        objects = []

        def add_object(data):
            objects.append(data)
            return len(objects)

        font1 = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font2 = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        font3 = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

        page_ids = []
        content_ids = []
        for page_commands in self.pages:
            stream = "\n".join(page_commands)
            content_id = add_object(f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream")
            content_ids.append(content_id)
            page_id = add_object("")
            page_ids.append(page_id)

        pages_id = add_object("")
        catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

        kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
        objects[pages_id - 1] = f"<< /Type /Pages /Kids [ {kids} ] /Count {len(page_ids)} >>"

        for idx, page_id in enumerate(page_ids):
            objects[page_id - 1] = (
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
                f"/Resources << /Font << /F1 {font1} 0 R /F2 {font2} 0 R /F3 {font3} 0 R >> >> "
                f"/Contents {content_ids[idx]} 0 R >>"
            )

        pdf = "%PDF-1.4\n%\xe2\xe3\xcf\xd3\n".encode("latin-1")
        offsets = [0]
        for obj_num, data in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf += f"{obj_num} 0 obj\n{data}\nendobj\n".encode("latin-1")
        xref_offset = len(pdf)
        pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1")
        for offset in offsets[1:]:
            pdf += f"{offset:010d} 00000 n \n".encode("latin-1")
        pdf += (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("latin-1")
        path.write_bytes(pdf)


def flow(title, lines):
    return f"{title}\n" + "\n".join(lines)


def write_pdf():
    pdf = SimplePDF()

    pdf.text(100, 680, "Python Project - Phase 2", "F2", 24)
    pdf.text(100, 650, "Design & Incubation Report", "F2", 20)
    pdf.text(100, 610, "Project: Rental Management System", "F1", 14)
    pdf.text(100, 588, "Prepared for submission: August 18, 2026", "F1", 11)
    pdf.text(100, 566, "Student Name: ______________________________", "F1", 11)
    pdf.text(100, 544, "Class / Course: _____________________________", "F1", 11)
    pdf.text(100, 500, "Scope:", "F2", 12)
    pdf.text(100, 480, "This document refines the design before full development.", "F1", 11)
    pdf.text(100, 463, "It defines modules, data structures, functions, flowcharts,", "F1", 11)
    pdf.text(100, 446, "UI layout, error handling, test cases, and timeline.", "F1", 11)
    pdf.new_page()

    pdf.heading("1. Purpose")
    pdf.paragraph(
        "Phase 2 focuses on refining the Rental Management System before full development. "
        "The system is a Python Tkinter desktop application for managing rental properties, tenants, "
        "rent payments, dashboard summaries, and system settings. The design separates the user interface, "
        "data access, validation, and business logic so the application can be expanded safely."
    )
    pdf.paragraph(
        "Current implementation already includes a login screen, the main application window, sidebar navigation, "
        "reusable layout components, dashboard cards, reusable tables, and modal forms for adding property, tenant, "
        "and payment records in memory. The finalized Phase 2 design adds persistent MySQL storage and complete "
        "CRUD operations."
    )

    pdf.heading("2. Refined System Architecture")
    pdf.paragraph(
        "The system will follow a modular architecture. Tkinter pages will handle screens and user actions. "
        "Service modules will contain business rules. Data modules will connect to MySQL. Validation modules "
        "will check data before records are saved."
    )
    pdf.table(
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
        widths=[1.35, 2.3, 2.1],
    )

    pdf.subheading("Module Interaction Flow")
    pdf.codeblock(
        """
User Action in Tkinter Page
        |
        v
Page method reads form data and calls validation
        |
        v
Service module applies business rules
        |
        v
data/database.py runs MySQL query
        |
        v
Result returns to service, then page
        |
        v
Tkinter page refreshes table, dashboard, or messagebox
"""
    )

    pdf.heading("3. Detailed Flowcharts")
    pdf.subheading("3.1 Add Record Flowchart")
    pdf.codeblock(
        flow(
            "Add Property / Tenant / Payment",
            [
                "+-------+",
                "| Start |",
                "+-------+",
                "    |",
                "    v",
                "+----------------------------+",
                "| User clicks Add button     |",
                "+----------------------------+",
                "    |",
                "    v",
                "+----------------------------+",
                "| Display input form/modal   |",
                "+----------------------------+",
                "    |",
                "    v",
                "+----------------------------+",
                "| User enters record details |",
                "+----------------------------+",
                "    |",
                "    v",
                "+----------------------------+",
                "| Validate required fields   |",
                "+----------------------------+",
                "    |",
                "    +-- Invalid --> Show error message and return to form",
                "    |",
                "    v",
                "+----------------------------+",
                "| Validate data types/ranges |",
                "+----------------------------+",
                "    |",
                "    +-- Invalid --> Highlight field and show correction message",
                "    |",
                "    v",
                "+----------------------------+",
                "| Check duplicate ID/contact |",
                "+----------------------------+",
                "    |",
                "    +-- Duplicate --> Show duplicate record error",
                "    |",
                "    v",
                "+----------------------------+",
                "| Save record to MySQL       |",
                "+----------------------------+",
                "    |",
                "    v",
                "+----------------------------+",
                "| Refresh table/dashboard    |",
                "+----------------------------+",
                "    |",
                "    v",
                "+----------------------------+",
                "| Show success message       |",
                "+----------------------------+",
                "    |",
                "    v",
                "+-----+",
                "| End |",
                "+-----+",
            ],
        )
    )

    pdf.subheading("3.2 Update Record Flowchart")
    pdf.codeblock(
        flow(
            "Update Property / Tenant / Payment",
            [
                "+-------+",
                "| Start |",
                "+-------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| User selects existing row   |",
                "+-----------------------------+",
                "    |",
                "    +-- No row selected --> Show 'select a record' message",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Load record into edit form  |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| User edits details          |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Validate changed values     |",
                "+-----------------------------+",
                "    |",
                "    +-- Invalid --> Show field error and keep form open",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Confirm update action       |",
                "+-----------------------------+",
                "    |",
                "    +-- Cancel --> Close form without saving",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Update record in MySQL      |",
                "+-----------------------------+",
                "    |",
                "    +-- Record missing --> Show not found message",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Refresh list and summaries  |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----+",
                "| End |",
                "+-----+",
            ],
        )
    )

    pdf.subheading("3.3 Delete Record Flowchart")
    pdf.codeblock(
        flow(
            "Delete Property / Tenant / Payment",
            [
                "+-------+",
                "| Start |",
                "+-------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| User selects a record       |",
                "+-----------------------------+",
                "    |",
                "    +-- No selection --> Show selection error",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Check related records       |",
                "+-----------------------------+",
                "    |",
                "    +-- Has dependency --> Block delete or ask to reassign",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Show confirmation dialog    |",
                "+-----------------------------+",
                "    |",
                "    +-- Cancel --> Return to list",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Delete record from MySQL    |",
                "+-----------------------------+",
                "    |",
                "    +-- Database error --> Show error and keep data unchanged",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Refresh table/dashboard     |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----+",
                "| End |",
                "+-----+",
            ],
        )
    )

    pdf.subheading("3.4 Search / View Records Flowchart")
    pdf.codeblock(
        flow(
            "Search and View",
            [
                "+-------+",
                "| Start |",
                "+-------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| User opens target page      |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Load all records from DB    |",
                "+-----------------------------+",
                "    |",
                "    +-- Missing DB --> Create DB and show empty table",
                "    |",
                "    v",
                "+-----------------------------+",
                "| User enters search keyword  |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Validate keyword/filter     |",
                "+-----------------------------+",
                "    |",
                "    +-- Empty keyword --> Display all records",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Query matching records      |",
                "+-----------------------------+",
                "    |",
                "    +-- No match --> Show 'record not found'",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Display results in table    |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----+",
                "| End |",
                "+-----+",
            ],
        )
    )

    pdf.subheading("3.5 Exit Flowchart")
    pdf.codeblock(
        flow(
            "Exit Application",
            [
                "+-------+",
                "| Start |",
                "+-------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| User clicks Exit or closes  |",
                "| application window          |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Check unsaved form changes  |",
                "+-----------------------------+",
                "    |",
                "    +-- Unsaved changes --> Ask user to confirm exit",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Commit/close DB connection  |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----------------------------+",
                "| Destroy Tkinter window      |",
                "+-----------------------------+",
                "    |",
                "    v",
                "+-----+",
                "| End |",
                "+-----+",
            ],
        )
    )

    pdf.heading("4. Function-Level Design")
    pdf.table(
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
        ],
        widths=[1.5, 2.4, 1.5, 1.8],
    )

    pdf.subheading("Proposed CRUD and Storage Functions")
    pdf.table(
        ["Function Name", "Purpose", "Parameters", "Returns / Output"],
        [
            ["initialize_database()", "Create the MySQL database and tables from data/schema.sql when MySQL is available.", "None", "True if initialized, False if unavailable."],
            ["get_property_options()", "Load active properties for the Add Tenant dropdown.", "None", "List of property records."],
            ["add_property()", "Save a new property record.", "property_data: dict", "New property ID or error message."],
            ["get_properties()", "Load properties from MySQL for the Properties page.", "None", "List of property records."],
            ["get_tenants()", "Load tenant records with their linked property names.", "None", "List of tenant records."],
            ["update_property()", "Edit an existing property record.", "property_id: int, updates: dict", "True/False with message."],
            ["delete_property()", "Remove a property if it has no blocked dependencies.", "property_id: int", "True/False with message."],
            ["search_properties()", "Find properties by name, location, status, or ID.", "keyword: str", "List of matching records."],
            ["add_tenant()", "Save a new tenant and link to a property/unit.", "tenant_data: dict", "New tenant ID or error message."],
            ["update_tenant()", "Edit tenant information.", "tenant_id: int, updates: dict", "True/False with message."],
            ["delete_tenant()", "Remove tenant record after confirming no active unpaid balance.", "tenant_id: int", "True/False with message."],
            ["record_payment()", "Save rent payment and update balance history.", "payment_data: dict", "Payment ID or error message."],
            ["calculate_balance()", "Calculate outstanding balance for a tenant.", "tenant_id: int", "Balance amount."],
            ["validate_required()", "Check that required fields are not empty.", "fields: dict", "True or validation message."],
            ["validate_money()", "Confirm currency values are numeric and not negative.", "amount: str", "Float value or error message."],
            ["validate_date()", "Confirm date follows YYYY-MM-DD format.", "date_text: str", "date object or error message."],
        ],
        widths=[1.5, 2.3, 1.6, 1.7],
    )

    pdf.heading("5. Final Data Structure / Database Schema")
    pdf.paragraph(
        "Final storage method: MySQL. MySQL is suitable because the project now needs relational storage that "
        "can link properties, tenants, and payments, while also supporting multi-table queries, constraints, "
        "and future expansion beyond in-memory sample data."
    )
    pdf.subheading("5.1 properties Table")
    pdf.table(
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
        widths=[1.4, 1, 2, 2],
    )

    pdf.subheading("5.2 tenants Table")
    pdf.table(
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
        widths=[1.4, 1, 2, 2],
    )

    pdf.subheading("5.3 payments Table")
    pdf.table(
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
        widths=[1.4, 1, 2, 2],
    )

    pdf.subheading("5.4 Sample JSON-Like Record Structure")
    pdf.codeblock(
        """
{
  "property": {
    "property_id": 1,
    "property_name": "Rocky Estates",
    "location": "Kampala",
    "total_units": 20,
    "monthly_rent": 1200000.00,
    "status": "Active"
  },
  "tenant": {
    "tenant_id": 1,
    "property_id": 1,
    "tenant_name": "Sarah N.",
    "phone": "+256700000000",
    "unit_number": "B12",
    "monthly_rent": 1200000.00,
    "status": "Active"
  },
  "payment": {
    "payment_id": 1,
    "tenant_id": 1,
    "amount": 1200000.00,
    "payment_date": "2026-08-10",
    "payment_method": "Mobile Money",
    "status": "Paid"
  }
}
"""
    )

    pdf.heading("6. UI Mockups and Navigation Layout")
    pdf.paragraph(
        "The project uses a Tkinter graphical interface. The user navigates with a left sidebar, while the top "
        "header displays the active page. Each content page contains summary sections, forms, and tables."
    )
    pdf.codeblock(
        """
+--------------------------------------------------------------------------------+
| Header: Current Page Title                                                     |
+----------------------+---------------------------------------------------------+
| Rental Management    | Dashboard / Properties / Tenants / Payments / Settings  |
| System               |                                                         |
|                      |  Page title and short description                       |
| [Dashboard]          |  [Primary action button] [Secondary action button]      |
| [Properties]         |                                                         |
| [Tenants]            |  +---------------------------------------------------+  |
| [Payments]           |  | Form, cards, tables, or page-specific content     |  |
| [Settings]           |  |                                                   |  |
|                      |  +---------------------------------------------------+  |
+----------------------+---------------------------------------------------------+
"""
    )
    pdf.subheading("Properties Page Mockup")
    pdf.codeblock(
        """
+-------------------------------------------------------------+
| Properties                                      [+ Add]      |
| This page will list rental houses, rooms, or apartments.     |
+-------------------------------------------------------------+
| Search: [________________]  Status: [Active v] [Refresh]     |
+-------------+----------------------+--------+---------------+
| Property    | Location             | Units  | Monthly Rent  |
+-------------+----------------------+--------+---------------+
| Rocky Estate| Kampala              | 20     | UGX 1,200...  |
| Entebbe Apt | Entebbe              | 10     | UGX 500,000   |
+-------------+----------------------+--------+---------------+
"""
    )
    pdf.subheading("Add Property Modal Mockup")
    pdf.codeblock(
        """
+--------------------------------------+
| Add Property                         |
| Fill in the property details below.  |
| Property Name: [__________________]  |
| Location:      [__________________]  |
| Units:         [__________________]  |
| Monthly Rent:  [__________________]  |
|                         [Cancel][Save]|
+--------------------------------------+
"""
    )
    pdf.subheading("Add Tenant Modal Mockup")
    pdf.codeblock(
        """
+------------------------------------------------------+
| Add Tenant                                           |
| Tenant Name: [____________] Phone: [______________]  |
| Email:       [____________] Property: [Rocky... v]   |
| Unit Number: [____________] Lease Start: [YYYY-MM-DD]|
| Monthly Rent:[____________] Status: [Active v]       |
|                                      [Cancel][Save]  |
+------------------------------------------------------+
"""
    )
    pdf.subheading("Navigation Flow")
    pdf.codeblock(
        """
Open App -> Login
Login Success -> Dashboard
Dashboard -> Properties -> Add / Update / Delete / Search Property
Dashboard -> Tenants -> Add / Update / Delete / Search Tenant
Dashboard -> Payments -> Record / Update / Delete / Search Payment
Any Page -> Settings
Any Page -> Close Window -> Confirm Exit -> End
"""
    )

    pdf.heading("7. Error Handling Plan")
    pdf.table(
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
        widths=[1.5, 2.5, 2],
    )

    pdf.subheading("Validation Rules")
    pdf.bullet("Property name, location, tenant name, phone number, amount, and payment date must not be empty.")
    pdf.bullet("Units must be a whole number greater than or equal to zero.")
    pdf.bullet("Money values must be numeric and greater than or equal to zero, except payments which must be greater than zero.")
    pdf.bullet("Phone numbers must be unique and should follow the local/international phone format accepted by the project.")
    pdf.bullet("Dates must use ISO format: YYYY-MM-DD.")
    pdf.bullet("Delete actions must ask for confirmation before changing data.")

    pdf.heading("8. Detailed Testing Plan")
    pdf.table(
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
        widths=[1.25, 2.25, 2.2, 0.8],
    )

    pdf.subheading("Testing Methods")
    pdf.bullet("Manual GUI testing will confirm navigation, button actions, modal behavior, and table refreshes.")
    pdf.bullet("Unit tests will check validators and service functions without opening the Tkinter interface.")
    pdf.bullet("Database tests will use a test MySQL database or sample fallback data to avoid changing real records.")
    pdf.bullet("Regression tests will verify that dashboard totals still update after CRUD changes.")

    pdf.heading("9. Development Timeline")
    pdf.table(
        ["Stage", "Main Work", "Deliverables"],
        [
            ["Week 1 - Menu and Structure", "Confirm navigation, page layout, reusable buttons, tables, and dashboard shell.", "Stable GUI skeleton with Dashboard, Properties, Tenants, Payments, and Settings pages."],
            ["Week 2 - Data Storage", "Create data/database.py, data/schema.sql, seed/sample data, and MySQL connection helpers.", "rental_management_system database created with properties, tenants, and payments tables."],
            ["Week 3 - CRUD Operations", "Implement add, update, delete, search, and list operations for properties and tenants.", "Working property and tenant management screens."],
            ["Week 4 - Payments and Balances", "Implement rent payment recording, payment history, balance calculation, and dashboard summaries.", "Working payment workflow and accurate dashboard totals."],
            ["Week 5 - Validation and Error Handling", "Add validators, try-except handling, confirmation dialogs, and user-friendly messages.", "Reduced crashes and clear feedback for invalid actions."],
            ["Week 6 - Testing and Debugging", "Run manual GUI tests, unit tests, database tests, and fix issues.", "Final tested project ready for Phase 3 development/submission."],
        ],
        widths=[1.4, 2.5, 2.1],
    )

    pdf.heading("10. Conclusion")
    pdf.paragraph(
        "This Phase 2 design prepares the Rental Management System for organized development. The application "
        "will use Tkinter for the interface, MySQL for storage, separate service modules for business logic, "
        "and validators for clean input handling. The flowcharts, function designs, database schema, UI mockups, "
        "error handling plan, test cases, and timeline provide a clear roadmap for the next phase."
    )

    pdf.build(OUTPUT_PDF)


def write_markdown():
    text = """# Python Project - Phase 2: Design & Incubation Report

Project: Rental Management System

Prepared for submission: August 18, 2026

This folder also contains `Phase2_Design_And_Incubation_Report.pdf`, which is the formatted submission copy.
The PDF covers:

- Refined system architecture
- Detailed flowcharts for Add, Update, Delete, Search/View, and Exit
- Function-level design
- Final MySQL database schema
- UI mockups and navigation layout
- Error handling plan
- Detailed testing plan
- Module-wise development timeline
"""
    OUTPUT_MD.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    write_markdown()
    write_pdf()
    print(f"Created {OUTPUT_PDF}")
    print(f"Created {OUTPUT_MD}")
