import tkinter as tk
from tkinter import messagebox, ttk

from components.simple_table import SimpleTable
from config.settings import COLORS, FONTS
from data.database import (
    DatabaseUnavailable,
    add_tenant as save_tenant_to_database,
    get_property_options,
    get_tenants,
)
from pages.base_page import BasePage


class TenantsPage(BasePage):
    """Page where tenant records will be managed."""

    def __init__(self, parent):
        # BasePage creates the title, description, header action area, and body area.
        super().__init__(
            parent,
            title="Tenants",
            description="This page will store tenant names, contacts, and rental details.",
        )

        # Header buttons live on the right side of the page title area.
        self.refresh_button = self.create_secondary_button(
            self.header_actions,
            text="Refresh",
            command=self.refresh_page,
        )
        self.refresh_button.pack(side="right", padx=(0, 20))

        self.add_tenant_button = self.create_primary_button(
            self.header_actions,
            text="+ Add Tenant",
            command=self.add_tenant,
        )
        self.add_tenant_button.pack(side="right", padx=(0, 8))

        # These names become the column headings in the tenant table.
        self.tenant_columns = (
            "Tenant Name",
            "Phone",
            "Email",
            "Property / Unit",
            "Monthly Rent",
            "Status",
        )
        self.tenant_rows = []
        self.property_options = []
        self.property_lookup = {}

        # SimpleTable is a reusable component that displays rows in a neat table.
        self.tenant_table = SimpleTable(self.content_frame, columns=self.tenant_columns)
        self.tenant_table.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_tenant_data()

    def add_tenant(self):
        """Open a professional modal form for registering a tenant."""

        # A Toplevel window is a popup window that appears above the main app.
        modal = tk.Toplevel(self)
        modal.title("Add Tenant")
        modal.configure(bg=COLORS["surface"])
        modal.resizable(False, False)

        # transient keeps the popup connected to the main window.
        # grab_set makes the user finish this form before using the main window again.
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        # The form uses four grid columns: label, field, label, field.
        form_frame = tk.Frame(modal, bg=COLORS["surface"], padx=26, pady=24)
        form_frame.pack(fill="both", expand=True)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        tk.Label(
            form_frame,
            text="Add Tenant",
            font=FONTS["subheading"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=0, column=0, columnspan=4, sticky="w")

        tk.Label(
            form_frame,
            text="Capture the tenant profile, assigned unit, and rent status.",
            font=FONTS["normal"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(4, 20))

        entries = {}

        # Each tuple describes one input: dictionary key, label text, row, and column.
        # This keeps the form organized and avoids copying the same code many times.
        fields = [
            ("tenant_name", "Tenant Name", 2, 0),
            ("phone", "Phone Number", 2, 2),
            ("email", "Email Address", 3, 0),
            ("unit_number", "Unit Number", 4, 0),
            ("lease_start", "Lease Start Date", 4, 2),
            ("monthly_rent", "Monthly Rent", 5, 0),
            ("emergency_contact", "Emergency Contact", 5, 2),
        ]

        for field_name, label_text, row, column in fields:
            self._create_form_label(form_frame, label_text, row, column)
            entry = self._create_entry(form_frame)
            entry.grid(row=row, column=column + 1, sticky="ew", padx=(12, 18), pady=(0, 14), ipady=6)
            entries[field_name] = entry

        self._create_form_label(form_frame, "Property", 3, 2)
        property_field = self._create_property_dropdown(form_frame, entries)
        property_field.grid(row=3, column=3, sticky="ew", padx=(12, 18), pady=(0, 14), ipady=4)
        entries["property"] = property_field

        # Combobox creates a drop-down list, which prevents random status text.
        self._create_form_label(form_frame, "Status", 6, 0)
        status_field = ttk.Combobox(
            form_frame,
            values=("Active", "Pending Move-in", "Notice Given"),
            state="readonly",
            font=FONTS["normal"],
            width=26,
        )
        status_field.current(0)
        status_field.grid(row=6, column=1, sticky="ew", padx=(12, 18), pady=(0, 14), ipady=4)
        entries["status"] = status_field

        button_frame = tk.Frame(form_frame, bg=COLORS["surface"])
        button_frame.grid(row=7, column=0, columnspan=4, sticky="e", pady=(8, 0))

        # The buttons call small functions so the form logic stays easy to read.
        self.create_secondary_button(button_frame, "Cancel", modal.destroy).pack(side="left", padx=(0, 8))
        self.create_primary_button(
            button_frame,
            "Save Tenant",
            lambda: self.save_tenant(entries, modal),
        ).pack(side="left")

        # Keyboard shortcuts make data entry faster for users.
        entries["tenant_name"].focus_set()
        modal.bind("<Return>", lambda event: self.save_tenant(entries, modal))
        modal.bind("<Escape>", lambda event: modal.destroy())
        self.center_modal(modal)

    def _create_form_label(self, parent, text, row, column):
        """Create a label for one form field."""

        tk.Label(
            parent,
            text=text,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=row, column=column, sticky="w", pady=(0, 14))

    def _create_entry(self, parent):
        """Create a standard text input used by the tenant form."""

        return tk.Entry(
            parent,
            font=FONTS["normal"],
            bg=COLORS["white"],
            fg=COLORS["text"],
            relief="solid",
            borderwidth=1,
            width=28,
        )

    def _create_property_dropdown(self, parent, entries):
        """Create a property dropdown using MySQL records when available."""

        self.load_property_options()

        property_names = list(self.property_lookup.keys())
        property_field = ttk.Combobox(
            parent,
            values=property_names,
            state="readonly",
            font=FONTS["normal"],
            width=26,
        )

        if property_names:
            property_field.current(0)
            self._fill_rent_from_property(entries, property_names[0])

        property_field.bind(
            "<<ComboboxSelected>>",
            lambda event: self._fill_rent_from_property(entries, property_field.get()),
        )

        return property_field

    def load_property_options(self):
        """Load property names for the tenant form dropdown."""

        self.property_options = get_property_options()
        self.property_lookup = {}

        for property_record in self.property_options:
            label = f"{property_record['property_name']} - {property_record['location']}"
            self.property_lookup[label] = property_record

    def _fill_rent_from_property(self, entries, property_label):
        """Put the selected property's default rent into the monthly rent field."""

        property_record = self.property_lookup.get(property_label)

        if not property_record or "monthly_rent" not in entries:
            return

        monthly_rent = property_record["monthly_rent"]
        entries["monthly_rent"].delete(0, tk.END)
        entries["monthly_rent"].insert(0, str(monthly_rent))

    def center_modal(self, modal):
        """Center the modal over the application window."""

        modal.update_idletasks()
        parent = self.winfo_toplevel()

        x = parent.winfo_rootx() + (parent.winfo_width() - modal.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - modal.winfo_height()) // 2
        modal.geometry(f"+{x}+{y}")

    def save_tenant(self, entries, modal):
        """Validate and add a tenant to the table."""

        # .get() reads the value from a Tkinter input. .strip() removes extra spaces.
        tenant_name = entries["tenant_name"].get().strip()
        phone = entries["phone"].get().strip()
        email = entries["email"].get().strip()
        property_label = entries["property"].get().strip()
        unit_number = entries["unit_number"].get().strip()
        lease_start = entries["lease_start"].get().strip()
        monthly_rent = entries["monthly_rent"].get().strip()
        emergency_contact = entries["emergency_contact"].get().strip()
        status = entries["status"].get().strip()

        # These are the most important fields, so the tenant should not be saved without them.
        if not tenant_name or not phone or not property_label or not unit_number or not monthly_rent:
            messagebox.showwarning(
                "Missing Details",
                "Please enter the tenant name, phone number, property, unit number, and monthly rent.",
                parent=modal,
            )
            return

        if email and "@" not in email:
            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address or leave the email field empty.",
                parent=modal,
            )
            entries["email"].focus_set()
            return

        try:
            rent_amount = float(monthly_rent.replace("UGX", "").replace(",", "").strip())
        except ValueError:
            messagebox.showwarning(
                "Invalid Rent",
                "Please enter monthly rent as a number.",
                parent=modal,
            )
            entries["monthly_rent"].focus_set()
            return

        selected_property = self.property_lookup.get(property_label)
        if selected_property is None:
            messagebox.showwarning(
                "Property Required",
                "Please select a property from the database before saving this tenant.",
                parent=modal,
            )
            entries["property"].focus_set()
            return

        tenant_data = {
            "property_id": selected_property["property_id"],
            "tenant_name": tenant_name,
            "phone": phone,
            "email": email,
            "unit_number": unit_number,
            "lease_start": lease_start,
            "monthly_rent": rent_amount,
            "emergency_contact": emergency_contact,
            "status": status,
        }

        try:
            save_tenant_to_database(tenant_data)
        except DatabaseUnavailable as exc:
            messagebox.showerror(
                "Database Unavailable",
                f"Tenant could not be saved because MySQL is unavailable.\n\n{exc}",
                parent=modal,
            )
            return
        except Exception as exc:
            messagebox.showerror(
                "Database Error",
                f"Tenant could not be saved to MySQL.\n\n{exc}",
                parent=modal,
            )
            return

        # Reload from MySQL so the table only shows tenants that are really stored.
        self.load_tenant_data()
        modal.destroy()

    def load_tenant_data(self):
        """Load tenant rows from the database."""

        database_rows = get_tenants()

        self.tenant_rows = [
            (
                row["tenant_name"],
                row["phone"],
                row["email"] or "",
                f"{row['property_name']} / {row['unit_number']}",
                f"UGX {float(row['monthly_rent']):,.2f}",
                row["status"],
            )
            for row in database_rows
        ]

        self.tenant_table.set_rows(self.tenant_rows)

    def refresh_page(self):
        """Refresh the tenant list when the page is opened or refreshed."""

        self.load_tenant_data()
