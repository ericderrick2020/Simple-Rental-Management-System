import tkinter as tk

from components.header import Header
from components.sidebar import Sidebar
from config.settings import APP_NAME, APP_HEIGHT, APP_WIDTH, COLORS
from data.database import initialize_database
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.payments_page import PaymentsPage
from pages.properties_page import PropertiesPage
from pages.settings_page import SettingsPage
from pages.tenants_page import TenantsPage


class RentalManagementApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Set the application title.
        self.title(APP_NAME)

        # Set the starting window size
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")

        # Set the smallest allowed window size
        self.minsize(1000, 650)

        # Set the main background color
        self.configure(bg=COLORS["background"])

        # The login page is shown before the real application layout is created.
        self.login_page = None

        # Store all application pages here
        self.pages = {}

        # Store the name of the current page
        self.current_page_name = "Dashboard"

        # Create MySQL tables when the database server and connector are available.
        self.database_ready = initialize_database()

        # Make the login page fill the starting window.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.show_login_page()

    def show_login_page(self):
        """Display the login screen before showing app pages."""

        self.login_page = LoginPage(self, login_success_function=self.create_app_layout)
        self.login_page.grid(row=0, column=0, sticky="nsew")

    def create_app_layout(self):
        """Create the sidebar, header, and pages after login succeeds."""

        # Remove the login screen so the main application can take its place.
        if self.login_page is not None:
            self.login_page.destroy()
            self.login_page = None

        # Column 0 becomes the sidebar, and column 1 becomes the main content area.
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Create the sidebar
        self.sidebar = Sidebar(parent=self, page_change_function=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # Create the right side of the application.
        self.main_area = tk.Frame(self, bg=COLORS["background"])
        self.main_area.grid(row=0, column=1, sticky="nsew")

        # Make the content area expandable
        self.main_area.rowconfigure(1, weight=1)
        self.main_area.columnconfigure(0, weight=1)

        # Create the reusable header
        self.header = Header(parent=self.main_area, page_title="Dashboard")
        self.header.grid(row=0, column=0, sticky="ew")

        # This frame will display the selected page
        self.page_container = tk.Frame(self.main_area, bg=COLORS["background"])
        self.page_container.grid(row=1, column=0, sticky="nsew")

        # Make every page fill the container
        self.page_container.rowconfigure(0, weight=1)
        self.page_container.columnconfigure(0, weight=1)

        # Create all application pages
        self.create_pages()

        # Show the dashboard when the application starts
        self.show_page("Dashboard")

    def create_pages(self):
        """Create every page only once."""
        page_classes = {
            "Dashboard": DashboardPage,
            "Properties": PropertiesPage,
            "Tenants": TenantsPage,
            "Payments": PaymentsPage,
            "Settings": SettingsPage,
        }

        # Create each page and store it in the pages dictionary
        for page_name, page_class in page_classes.items():
            page = page_class(self.page_container)

            page.grid(row=0, column=0, sticky="nsew")

            self.pages[page_name] = page

    def show_page(self, page_name):
        """Display the selected page."""
        page = self.pages.get(page_name)

        if page is None:
            return

        # Move the selected page to the front
        page.tkraise()

        # Update the header title
        self.header.set_page_title(page_name)

        # Highlight the selected sidebar button
        self.sidebar.set_active_button(page_name)

        self.current_page_name = page_name

        # Refresh the page when it becomes visible
        if hasattr(page, "refresh_page"):
            page.refresh_page()


if __name__ == "__main__":
    app = RentalManagementApp()
    app.mainloop()
