import tkinter as tk
from tkinter import messagebox

from components.simple_table import SimpleTable
from config.settings import COLORS, FONTS
from data.database import (
    DatabaseUnavailable,
    add_property as save_property_to_database,
    get_properties,
)
from pages.base_page import BasePage


class PropertiesPage(BasePage):
    """Page where property records will be managed."""

    def __init__(self, parent):
        # Initializing the base page structure first
        super().__init__(
            parent,
            title="Properties",
            description="This page will list rental houses, rooms, or apartments.",
        )

        refresh_button = self.create_secondary_button(
            self.header_actions,
            text="Refresh",
            command=self.refresh_page,
        )
        refresh_button.pack(side="right", padx=(0, 20))

        # This button opens the modal form used to register a new property.
        add_property_button = self.create_primary_button(
            self.header_actions,
            text="+ Add Property",
            command=self.add_property,
        )
        add_property_button.pack(side="right", padx=(0, 8))

        # These columns control the headings shown in the properties table.
        self.property_columns = ("Property Name", "Location", "Units", "Monthly Rent")
        self.property_rows = []

        # Create the table once when the page loads, then update its rows when data changes.
        self.property_table = SimpleTable(self.content_frame, columns=self.property_columns)
        self.property_table.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_property_data()

    def add_property(self):
        """Open a modal form for adding a property."""

        # Toplevel creates a separate popup window above the main application.
        modal = tk.Toplevel(self)
        modal.title("Add Property")
        modal.configure(bg=COLORS["surface"])
        modal.resizable(False, False)

        # Keep the modal attached to the main app and block clicks outside it.
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        # Main container for the labels, text fields, and action buttons.
        form_frame = tk.Frame(modal, bg=COLORS["surface"], padx=24, pady=22)
        form_frame.pack(fill="both", expand=True)

        tk.Label(
            form_frame,
            text="Add Property",
            font=FONTS["subheading"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Label(
            form_frame,
            text="Fill in the property details below.",
            font=FONTS["normal"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 18))

        entries = {}

        # Each tuple stores the dictionary key and the label shown to the user.
        # We do not ask for a Property ID here because IDs should be created by
        # the system or database later, not typed manually by the user.
        fields = [
            ("property_name", "Property Name"),
            ("location", "Location"),
            ("units", "Units"),
            ("revenue", "Monthly Rent"),
        ]

        # Build the form inputs from the fields list to avoid repeating the same layout code.
        for row, (field_name, label_text) in enumerate(fields, start=2):
            tk.Label(
                form_frame,
                text=label_text,
                font=FONTS["button"],
                bg=COLORS["surface"],
                fg=COLORS["text"],
            ).grid(row=row, column=0, sticky="w", pady=(0, 12))

            entry = tk.Entry(
                form_frame,
                font=FONTS["normal"],
                bg=COLORS["white"],
                fg=COLORS["text"],
                relief="solid",
                borderwidth=1,
                width=34,
            )
            entry.grid(row=row, column=1, sticky="ew", padx=(16, 0), pady=(0, 12), ipady=6)
            entries[field_name] = entry

        # Action buttons are grouped in their own frame at the bottom right.
        button_frame = tk.Frame(form_frame, bg=COLORS["surface"])
        button_frame.grid(row=6, column=0, columnspan=2, sticky="e", pady=(8, 0))

        tk.Button(
            button_frame,
            text="Cancel",
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief="solid",
            borderwidth=1,
            padx=16,
            pady=8,
            cursor="hand2",
            command=modal.destroy,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            button_frame,
            text="Save Property",
            font=FONTS["button"],
            bg=COLORS["primary"],
            fg=COLORS["white"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["white"],
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=9,
            cursor="hand2",
            command=lambda: self.save_property(entries, modal),
        ).pack(side="left")

        # Focus and keyboard shortcuts make the modal quicker to use.
        entries["property_name"].focus_set()
        modal.bind("<Return>", lambda event: self.save_property(entries, modal))
        modal.bind("<Escape>", lambda event: modal.destroy())

        self.center_modal(modal)

    def center_modal(self, modal):
        """Center the modal over the main application window."""

        modal.update_idletasks()
        parent = self.winfo_toplevel()

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        modal_width = modal.winfo_width()
        modal_height = modal.winfo_height()

        # Calculate the modal position so it appears in the middle of the app window.
        x = parent_x + (parent_width - modal_width) // 2
        y = parent_y + (parent_height - modal_height) // 2

        modal.geometry(f"+{x}+{y}")

    def save_property(self, entries, modal):
        """Validate and save a property from the modal form."""

        # Read and trim the values entered by the user.
        property_name = entries["property_name"].get().strip()
        location = entries["location"].get().strip()
        units = entries["units"].get().strip()
        revenue = entries["revenue"].get().strip()

        # Stop saving if any required field is empty.
        if not property_name or not location or not units or not revenue:
            messagebox.showwarning(
                "Missing Details",
                "Please fill in all property details.",
                parent=modal,
            )
            return

        # Units should be stored as a whole number.
        if not units.isdigit():
            messagebox.showwarning(
                "Invalid Units",
                "Units must be a whole number.",
                parent=modal,
            )
            entries["units"].focus_set()
            return

        try:
            monthly_rent = float(revenue.replace("UGX", "").replace(",", "").strip())
        except ValueError:
            messagebox.showwarning(
                "Invalid Rent",
                "Monthly rent must be a number.",
                parent=modal,
            )
            entries["revenue"].focus_set()
            return

        property_data = {
            "property_name": property_name,
            "location": location,
            "total_units": int(units),
            "monthly_rent": monthly_rent,
            "status": "Active",
        }

        try:
            save_property_to_database(property_data)
        except DatabaseUnavailable as exc:
            messagebox.showerror(
                "Database Unavailable",
                f"Property could not be saved because MySQL is unavailable.\n\n{exc}",
                parent=modal,
            )
            return
        except Exception as exc:
            messagebox.showerror(
                "Database Error",
                f"Property could not be saved to MySQL.\n\n{exc}",
                parent=modal,
            )
            return

        # Reload from MySQL so the table only shows records that are really stored.
        self.load_property_data()
        modal.destroy()

    def load_property_data(self):
        """Load property rows from the database."""

        database_rows = get_properties()

        self.property_rows = [
            (
                row["property_name"],
                row["location"],
                str(row["total_units"]),
                f"UGX {float(row['monthly_rent']):,.2f}",
            )
            for row in database_rows
        ]

        self.property_table.set_rows(self.property_rows)

    def refresh_page(self):
        """Refresh the property list when the page is opened or refreshed."""

        self.load_property_data()
