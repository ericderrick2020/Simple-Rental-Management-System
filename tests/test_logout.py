"""Exercise real Tkinter login/logout widgets without a MySQL connection."""
import tkinter as tk
import unittest
from unittest.mock import patch

import main
from config.settings import DEFAULT_PASSWORD


class RecordPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.refresh_count = 0

    def refresh_page(self):
        self.refresh_count += 1


class LogoutTests(unittest.TestCase):
    def setUp(self):
        replacements = {name: RecordPage for name in (
            "DashboardPage", "PropertiesPage", "TenantsPage",
            "PaymentsPage", "SettingsPage",
        )}
        replacements["initialize_database"] = lambda: True
        self.patches = patch.multiple(main, **replacements)
        self.patches.start()
        self.addCleanup(self.patches.stop)
        self.app = main.RentalManagementApp()
        self.app.withdraw()
        self.addCleanup(self.app.destroy)

    def sign_in(self):
        self.app.login_page.password_var.set(DEFAULT_PASSWORD)
        self.app.login_page.check_login()
        self.assertIsNone(self.app.login_page)
        self.assertEqual(self.app.current_page_name, "Dashboard")

    def test_logout_closes_forms_and_removes_record_pages(self):
        self.sign_in()
        old_page = self.app.pages["Tenants"]
        modal = tk.Toplevel(old_page)
        self.app.sidebar.logout_button.invoke()
        self.assertFalse(old_page.winfo_exists())
        self.assertFalse(modal.winfo_exists())
        self.assertEqual(self.app.pages, {})
        self.assertIsNone(self.app.current_page_name)
        self.assertIsNone(self.app.sidebar)
        self.assertEqual(self.app.login_page.password_var.get(), "")
        self.assertFalse(self.app.login_page.show_password_var.get())
        self.assertEqual(self.app.login_page.password_entry.cget("show"), "*")
        self.assertTrue(self.app.bind_all("<Return>"))
        self.app.show_page("Tenants")
        self.assertIsNotNone(self.app.login_page)

    def test_sign_in_again_creates_fresh_pages_and_layout(self):
        for _ in range(2):
            self.sign_in()
            old_pages = list(self.app.pages.values())
            self.assertEqual(len(old_pages), 5)
            self.assertEqual(self.app.columnconfigure(0)["weight"], 0)
            self.assertEqual(self.app.columnconfigure(1)["weight"], 1)
            self.app.sidebar.logout_button.invoke()
            self.assertEqual(self.app.columnconfigure(0)["weight"], 1)
            self.assertEqual(self.app.columnconfigure(1)["weight"], 0)
            self.assertTrue(all(not page.winfo_exists() for page in old_pages))
        self.sign_in()
        self.assertEqual(len(self.app.pages), 5)
        self.assertEqual(self.app.pages["Dashboard"].refresh_count, 1)

    def test_wrong_password_after_logout_keeps_pages_locked(self):
        self.sign_in()
        self.app.logout()
        self.app.login_page.password_var.set("wrong password")
        with patch("pages.login_page.messagebox.showerror") as error:
            self.app.login_page.check_login()
        error.assert_called_once()
        self.assertIsNotNone(self.app.login_page)
        self.assertEqual(self.app.pages, {})
        self.assertEqual(self.app.login_page.password_var.get(), "")


if __name__ == "__main__":
    unittest.main()
