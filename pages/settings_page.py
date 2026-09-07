import tkinter as tk
from tkinter import messagebox, ttk

from config.settings import COLORS, FONTS
from data.database import (
    DEFAULT_APP_SETTINGS,
    DatabaseUnavailable,
    get_account_settings,
    get_app_settings,
    save_app_settings,
)
from pages.base_page import BasePage


class SettingsPage(BasePage):
    """Page where application settings and user preferences are managed."""

    def __init__(self, parent):
        # BasePage builds the common title area and scrollable content area.
        super().__init__(
            parent,
            title="Settings",
            description="Manage company details, rent preferences, notifications, and account settings.",
        )

        self.settings_data = get_app_settings()
        self.account_data = get_account_settings()
        self.account_value_labels = {}

        # Tkinter variables remember values even after widgets are created.
        self.company_name_var = tk.StringVar(value=self.settings_data["company_name"])
        self.manager_name_var = tk.StringVar(value=self.settings_data["manager_name"])
        self.phone_var = tk.StringVar(value=self.settings_data["phone"])
        self.email_var = tk.StringVar(value=self.settings_data["email"])
        self.currency_var = tk.StringVar(value=self.settings_data["currency"])
        self.rent_due_day_var = tk.StringVar(value=self.settings_data["rent_due_day"])
        self.late_fee_var = tk.StringVar(value=self.settings_data["late_fee"])
        self.theme_var = tk.StringVar(value=self.settings_data["theme"])
        self.email_reminders_var = tk.BooleanVar(value=self._setting_is_enabled("email_reminders"))
        self.sms_reminders_var = tk.BooleanVar(value=self._setting_is_enabled("sms_reminders"))
        self.backup_var = tk.BooleanVar(value=self._setting_is_enabled("backup_reminder"))

        self.refresh_button = self.create_secondary_button(
            self.header_actions,
            text="Refresh",
            command=self.refresh_page,
        )
        self.refresh_button.pack(side="right", padx=20)

        # The content frame uses two equal columns for a professional settings layout.
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)

        self._create_company_panel()
        self._create_rent_panel()
        self._create_notification_panel()
        self._create_account_panel()

        # The save button is placed at the bottom so users finish reviewing settings first.
        action_frame = tk.Frame(self.content_frame, bg=COLORS["background"])
        action_frame.grid(row=2, column=0, columnspan=2, sticky="e", padx=8, pady=(10, 20))

        self.create_secondary_button(
            action_frame,
            "Reset",
            self.reset_settings,
        ).pack(side="left", padx=(0, 8))

        self.create_primary_button(
            action_frame,
            "Save Settings",
            self.save_settings,
        ).pack(side="left")

    def _create_company_panel(self):
        """Create the company profile settings section."""

        panel = self._create_panel(0, 0, "Company Profile")

        # These inputs store the details shown on receipts and reports.
        self._create_entry(panel, "Company Name", self.company_name_var, 1)
        self._create_entry(panel, "Manager Name", self.manager_name_var, 2)
        self._create_entry(panel, "Phone Number", self.phone_var, 3)
        self._create_entry(panel, "Email Address", self.email_var, 4)

    def _create_rent_panel(self):
        """Create the rent and payment preference section."""

        panel = self._create_panel(0, 1, "Rent Preferences")

        # Combobox is a drop-down menu. It helps keep currency values consistent.
        self._create_select(panel, "Default Currency", self.currency_var, ("UGX", "USD", "KES"), 1)
        self._create_entry(panel, "Rent Due Day", self.rent_due_day_var, 2)
        self._create_entry(panel, "Late Fee Amount", self.late_fee_var, 3)
        self._create_select(panel, "App Theme", self.theme_var, ("Light", "Dark", "System"), 4)

    def _create_notification_panel(self):
        """Create the reminder and backup settings section."""

        panel = self._create_panel(1, 0, "Notifications")

        # Checkbuttons are used for yes/no options.
        self._create_checkbutton(panel, "Send email rent reminders", self.email_reminders_var, 1)
        self._create_checkbutton(panel, "Send SMS rent reminders", self.sms_reminders_var, 2)
        self._create_checkbutton(panel, "Create weekly backup reminder", self.backup_var, 3)

    def _create_account_panel(self):
        """Create account and security settings section."""

        panel = self._create_panel(1, 1, "Account Security")

        # These labels are read from the users and app_settings tables.
        self.account_value_labels["role"] = self._create_readonly_row(
            panel,
            "Role",
            self.account_data["role"],
            1,
        )
        self.account_value_labels["last_password_change"] = self._create_readonly_row(
            panel,
            "Last Password Change",
            self.account_data["last_password_change"],
            2,
        )
        self.account_value_labels["two_factor_login"] = self._create_readonly_row(
            panel,
            "Two-Factor Login",
            self.account_data["two_factor_login"],
            3,
        )

    def _create_panel(self, row, column, title):
        """Create one bordered settings section."""

        panel = tk.Frame(
            self.content_frame,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=18,
            pady=16,
        )
        panel.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
        panel.columnconfigure(1, weight=1)

        tk.Label(
            panel,
            text=title,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        return panel

    def _create_entry(self, parent, label_text, variable, row):
        """Create a label and text input on the same row."""

        self._create_label(parent, label_text, row)

        tk.Entry(
            parent,
            textvariable=variable,
            font=FONTS["normal"],
            bg=COLORS["white"],
            fg=COLORS["text"],
            relief="solid",
            borderwidth=1,
        ).grid(row=row, column=1, sticky="ew", padx=(14, 0), pady=(0, 12), ipady=6)

    def _create_select(self, parent, label_text, variable, values, row):
        """Create a label and drop-down menu on the same row."""

        self._create_label(parent, label_text, row)

        ttk.Combobox(
            parent,
            textvariable=variable,
            values=values,
            state="readonly",
            font=FONTS["normal"],
        ).grid(row=row, column=1, sticky="ew", padx=(14, 0), pady=(0, 12), ipady=4)

    def _create_checkbutton(self, parent, text, variable, row):
        """Create one on/off checkbox setting."""

        tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            font=FONTS["normal"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            selectcolor=COLORS["white"],
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))

    def _create_readonly_row(self, parent, label_text, value_text, row):
        """Create a row that displays information without allowing edits."""

        self._create_label(parent, label_text, row)

        value_label = tk.Label(
            parent,
            text=value_text,
            font=FONTS["normal"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        )
        value_label.grid(row=row, column=1, sticky="w", padx=(14, 0), pady=(0, 12))
        return value_label

    def _create_label(self, parent, text, row):
        """Create the left-side label used by several settings rows."""

        tk.Label(
            parent,
            text=text,
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        ).grid(row=row, column=0, sticky="w", pady=(0, 12))

    def save_settings(self):
        """Validate and save settings to the database."""

        # Required values are checked before the settings are accepted.
        if not self.company_name_var.get().strip() or not self.manager_name_var.get().strip():
            messagebox.showwarning(
                "Missing Details",
                "Please enter the company name and manager name.",
                parent=self.winfo_toplevel(),
            )
            return

        if "@" not in self.email_var.get().strip():
            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address.",
                parent=self.winfo_toplevel(),
            )
            return

        rent_due_day = self.rent_due_day_var.get().strip()
        if not rent_due_day.isdigit() or not 1 <= int(rent_due_day) <= 31:
            messagebox.showwarning(
                "Invalid Rent Due Day",
                "Rent due day must be a number from 1 to 31.",
                parent=self.winfo_toplevel(),
            )
            return

        try:
            float(self.late_fee_var.get().replace(",", "").strip())
        except ValueError:
            messagebox.showwarning(
                "Invalid Late Fee",
                "Late fee amount must be a number.",
                parent=self.winfo_toplevel(),
            )
            return

        try:
            save_app_settings(self._collect_settings())
        except DatabaseUnavailable as exc:
            messagebox.showerror(
                "Database Unavailable",
                f"Settings could not be saved because MySQL is unavailable.\n\n{exc}",
                parent=self.winfo_toplevel(),
            )
            return
        except Exception as exc:
            messagebox.showerror(
                "Database Error",
                f"Settings could not be saved to MySQL.\n\n{exc}",
                parent=self.winfo_toplevel(),
            )
            return

        self.refresh_page()
        messagebox.showinfo(
            "Settings Saved",
            "Settings changed successfully.",
            parent=self.winfo_toplevel(),
        )

    def reset_settings(self):
        """Reset the settings form to defaults and save them to the database."""

        self._apply_settings(DEFAULT_APP_SETTINGS)

        try:
            save_app_settings(self._collect_settings())
        except DatabaseUnavailable as exc:
            messagebox.showerror(
                "Database Unavailable",
                f"Default settings could not be saved because MySQL is unavailable.\n\n{exc}",
                parent=self.winfo_toplevel(),
            )
            return
        except Exception as exc:
            messagebox.showerror(
                "Database Error",
                f"Default settings could not be saved to MySQL.\n\n{exc}",
                parent=self.winfo_toplevel(),
            )
            return

        self.refresh_page()
        messagebox.showinfo(
            "Settings Reset",
            "Default settings have been saved to the database.",
            parent=self.winfo_toplevel(),
        )

    def refresh_page(self):
        """Refresh settings and account values from the database."""

        self.settings_data = get_app_settings()
        self.account_data = get_account_settings()
        self._apply_settings(self.settings_data)
        self._apply_account_settings()

    def _setting_is_enabled(self, key):
        """Return True when a saved checkbox setting is enabled."""

        return self.settings_data.get(key) == "1"

    def _collect_settings(self):
        """Collect the current form values for database storage."""

        return {
            "company_name": self.company_name_var.get().strip(),
            "manager_name": self.manager_name_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "email": self.email_var.get().strip(),
            "currency": self.currency_var.get().strip(),
            "rent_due_day": self.rent_due_day_var.get().strip(),
            "late_fee": self.late_fee_var.get().replace(",", "").strip(),
            "theme": self.theme_var.get().strip(),
            "email_reminders": "1" if self.email_reminders_var.get() else "0",
            "sms_reminders": "1" if self.sms_reminders_var.get() else "0",
            "backup_reminder": "1" if self.backup_var.get() else "0",
            "two_factor_login": self.account_data["two_factor_login"],
        }

    def _apply_settings(self, settings):
        """Put settings from the database into the form variables."""

        self.company_name_var.set(settings["company_name"])
        self.manager_name_var.set(settings["manager_name"])
        self.phone_var.set(settings["phone"])
        self.email_var.set(settings["email"])
        self.currency_var.set(settings["currency"])
        self.rent_due_day_var.set(settings["rent_due_day"])
        self.late_fee_var.set(settings["late_fee"])
        self.theme_var.set(settings["theme"])
        self.email_reminders_var.set(settings["email_reminders"] == "1")
        self.sms_reminders_var.set(settings["sms_reminders"] == "1")
        self.backup_var.set(settings["backup_reminder"] == "1")

    def _apply_account_settings(self):
        """Update read-only account labels from database values."""

        for key, label in self.account_value_labels.items():
            label.config(text=self.account_data[key])
