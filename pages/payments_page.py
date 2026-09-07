from datetime import datetime

import tkinter as tk
from tkinter import messagebox, ttk

from components.simple_table import SimpleTable
from config.settings import COLORS, FONTS
from data.database import (
    DatabaseUnavailable,
    add_payment as save_payment_to_database,
    get_payments,
    get_tenant_options,
)
from pages.base_page import BasePage


class PaymentsPage(BasePage):
    """Page where rent payments will be managed."""

    def __init__(self, parent):
        # BasePage gives this screen the same layout used by the other pages.
        super().__init__(
            parent,
            title="Payments",
            description="This page will track rent paid by tenants.",
        )

        # This button opens the popup where users enter a new payment.
        self.refresh_button = self.create_secondary_button(
            self.header_actions,
            text="Refresh",
            command=self.refresh_page,
        )
        self.refresh_button.pack(side="right", padx=(0, 20))

        self.record_payment_button = self.create_primary_button(
            self.header_actions,
            text="+ Record Payment",
            command=self.record_payment,
        )
        self.record_payment_button.pack(side="right", padx=(0, 8))

        # Column names must match the order of values added in save_payment().
        self.payment_columns = (
            "Tenant",
            "Property / Unit",
            "Amount",
            "Payment Date",
            "Method",
            "Status",
        )
        self.payment_rows = []
        self.tenant_options = []
        self.tenant_lookup = {}

        # The table displays the payment list on the main page.
        self.payment_table = SimpleTable(self.content_frame, columns=self.payment_columns)
        self.payment_table.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_payment_data()

    def record_payment(self):
        """Open a modal form for recording rent payments."""

        # Toplevel creates a new popup window for the payment form.
        modal = tk.Toplevel(self)
        modal.title("Record Payment")
        modal.configure(bg=COLORS["surface"])
        modal.resizable(False, False)

        # These two lines make the popup behave like a proper modal dialog.
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        # The grid layout below uses two fields per row to keep the form compact.
        form_frame = tk.Frame(modal, bg=COLORS["surface"], padx=26, pady=24)
        form_frame.pack(fill="both", expand=True)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        tk.Label(
            form_frame,
            text="Record Payment",
            font=FONTS["subheading"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=0, column=0, columnspan=4, sticky="w")

        tk.Label(
            form_frame,
            text="Enter the rent payment details and payment status.",
            font=FONTS["normal"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(4, 20))

        entries = {}

        self._create_form_label(form_frame, "Tenant", 2, 0)
        tenant_field = self._create_tenant_dropdown(form_frame, entries)
        tenant_field.grid(row=2, column=1, sticky="ew", padx=(12, 18), pady=(0, 14), ipady=4)
        entries["tenant"] = tenant_field

        self._create_form_label(form_frame, "Property / Unit", 2, 2)
        property_unit_field = self._create_entry(form_frame)
        property_unit_field.grid(row=2, column=3, sticky="ew", padx=(12, 18), pady=(0, 14), ipady=6)
        property_unit_field.config(state="readonly")
        entries["property_unit"] = property_unit_field

        if self.tenant_lookup:
            self._fill_payment_details_from_tenant(entries, tenant_field.get())

        # Each field definition tells the loop where to place that input on the form.
        fields = [
            ("amount", "Amount", 3, 0),
            ("payment_date", "Payment Date", 3, 2),
            ("reference", "Reference No.", 5, 0),
            ("notes", "Notes", 5, 2),
        ]

        for field_name, label_text, row, column in fields:
            self._create_form_label(form_frame, label_text, row, column)
            entry = self._create_entry(form_frame)
            entry.grid(row=row, column=column + 1, sticky="ew", padx=(12, 18), pady=(0, 14), ipady=6)
            entries[field_name] = entry

        # Drop-downs are useful for values that should come from a fixed list.
        self._create_form_label(form_frame, "Payment Method", 4, 0)
        method_field = ttk.Combobox(
            form_frame,
            values=("Cash", "Mobile Money", "Bank Transfer", "Card"),
            state="readonly",
            font=FONTS["normal"],
            width=26,
        )
        method_field.current(1)
        method_field.grid(row=4, column=1, sticky="ew", padx=(12, 18), pady=(0, 14), ipady=4)
        entries["method"] = method_field

        # Payment status is also controlled by a drop-down to keep records consistent.
        self._create_form_label(form_frame, "Status", 4, 2)
        status_field = ttk.Combobox(
            form_frame,
            values=("Paid", "Pending", "Overdue"),
            state="readonly",
            font=FONTS["normal"],
            width=26,
        )
        status_field.current(0)
        status_field.grid(row=4, column=3, sticky="ew", padx=(12, 18), pady=(0, 14), ipady=4)
        entries["status"] = status_field

        if self.tenant_lookup:
            self._fill_payment_details_from_tenant(entries, tenant_field.get())

        button_frame = tk.Frame(form_frame, bg=COLORS["surface"])
        button_frame.grid(row=6, column=0, columnspan=4, sticky="e", pady=(8, 0))

        # Cancel closes the form. Save validates the data before adding it to the table.
        self.create_secondary_button(button_frame, "Cancel", modal.destroy).pack(side="left", padx=(0, 8))
        self.create_primary_button(
            button_frame,
            "Save Payment",
            lambda: self.save_payment(entries, modal),
        ).pack(side="left")

        # Focus puts the typing cursor in the first field when the popup opens.
        entries["tenant"].focus_set()
        modal.bind("<Return>", lambda event: self.save_payment(entries, modal))
        modal.bind("<Escape>", lambda event: modal.destroy())
        self.center_modal(modal)

    def _create_tenant_dropdown(self, parent, entries):
        """Create a tenant dropdown using MySQL records."""

        self.load_tenant_options()

        tenant_names = list(self.tenant_lookup.keys())
        tenant_field = ttk.Combobox(
            parent,
            values=tenant_names,
            state="readonly",
            font=FONTS["normal"],
            width=26,
        )

        if tenant_names:
            tenant_field.current(0)

        tenant_field.bind(
            "<<ComboboxSelected>>",
            lambda event: self._fill_payment_details_from_tenant(entries, tenant_field.get()),
        )

        return tenant_field

    def load_tenant_options(self):
        """Load tenants for the payment form dropdown."""

        self.tenant_options = get_tenant_options()
        self.tenant_lookup = {}

        for tenant_record in self.tenant_options:
            label = f"{tenant_record['tenant_name']} - {tenant_record['property_name']} / {tenant_record['unit_number']}"
            self.tenant_lookup[label] = tenant_record

    def _fill_payment_details_from_tenant(self, entries, tenant_label):
        """Fill property/unit and amount from the selected tenant."""

        tenant_record = self.tenant_lookup.get(tenant_label)
        if not tenant_record:
            return

        if "property_unit" in entries:
            property_unit = f"{tenant_record['property_name']} / {tenant_record['unit_number']}"
            entries["property_unit"].config(state="normal")
            entries["property_unit"].delete(0, tk.END)
            entries["property_unit"].insert(0, property_unit)
            entries["property_unit"].config(state="readonly")

        if "amount" in entries:
            entries["amount"].delete(0, tk.END)
            entries["amount"].insert(0, str(tenant_record["monthly_rent"]))

    def _create_form_label(self, parent, text, row, column):
        """Create a label for one payment form field."""

        tk.Label(
            parent,
            text=text,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=row, column=column, sticky="w", pady=(0, 14))

    def _create_entry(self, parent):
        """Create a standard text input used by the payment form."""

        return tk.Entry(
            parent,
            font=FONTS["normal"],
            bg=COLORS["white"],
            fg=COLORS["text"],
            relief="solid",
            borderwidth=1,
            width=28,
        )

    def center_modal(self, modal):
        """Center the modal over the application window."""

        modal.update_idletasks()
        parent = self.winfo_toplevel()

        x = parent.winfo_rootx() + (parent.winfo_width() - modal.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - modal.winfo_height()) // 2
        modal.geometry(f"+{x}+{y}")

    def save_payment(self, entries, modal):
        """Validate and add a payment record to the table."""

        # Read values from the form fields before checking them.
        tenant = entries["tenant"].get().strip()
        property_unit = entries["property_unit"].get().strip()
        amount = entries["amount"].get().strip()
        payment_date = entries["payment_date"].get().strip()
        reference = entries["reference"].get().strip()
        notes = entries["notes"].get().strip()
        method = entries["method"].get().strip()
        status = entries["status"].get().strip()

        # Required fields protect the table from incomplete payment records.
        if not tenant or not property_unit or not amount or not payment_date:
            messagebox.showwarning(
                "Missing Details",
                "Please enter the tenant, property/unit, amount, and payment date.",
                parent=modal,
            )
            return

        selected_tenant = self.tenant_lookup.get(tenant)
        if selected_tenant is None:
            messagebox.showwarning(
                "Tenant Required",
                "Please select a tenant from the database before saving this payment.",
                parent=modal,
            )
            entries["tenant"].focus_set()
            return

        try:
            payment_amount = float(amount.replace(",", "").replace("UGX", "").strip())
        except ValueError:
            messagebox.showwarning(
                "Invalid Amount",
                "Please enter a valid payment amount.",
                parent=modal,
            )
            entries["amount"].focus_set()
            return

        try:
            datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Please enter the payment date as YYYY-MM-DD.",
                parent=modal,
            )
            entries["payment_date"].focus_set()
            return

        payment_data = {
            "tenant_id": selected_tenant["tenant_id"],
            "amount": payment_amount,
            "payment_date": payment_date,
            "payment_method": method,
            "reference_no": reference,
            "notes": notes,
            "status": status,
        }

        try:
            save_payment_to_database(payment_data)
        except DatabaseUnavailable as exc:
            messagebox.showerror(
                "Database Unavailable",
                f"Payment could not be saved because MySQL is unavailable.\n\n{exc}",
                parent=modal,
            )
            return
        except Exception as exc:
            messagebox.showerror(
                "Database Error",
                f"Payment could not be saved to MySQL.\n\n{exc}",
                parent=modal,
            )
            return

        # Reload from MySQL so the table only shows payments that are really stored.
        self.load_payment_data()
        modal.destroy()

    def load_payment_data(self):
        """Load payment rows from the database."""

        database_rows = get_payments()

        self.payment_rows = [
            (
                row["tenant_name"],
                f"{row['property_name']} / {row['unit_number']}",
                f"UGX {float(row['amount']):,.2f}",
                str(row["payment_date"]),
                row["payment_method"],
                row["status"],
            )
            for row in database_rows
        ]

        self.payment_table.set_rows(self.payment_rows)

    def refresh_page(self):
        """Refresh the payment list when the page is opened or refreshed."""

        self.load_payment_data()
