import tkinter as tk

from config.settings import APP_NAME, COLORS, FONTS


class Sidebar(tk.Frame):
    """Left menu used to move between pages."""

    def __init__(self, parent, page_change_function):
        super().__init__(parent, bg=COLORS["sidebar"], width=220)

        # Keep the sidebar width stable.
        self.grid_propagate(False)

        self.page_change_function = page_change_function
        self.buttons = {}

        # App name area.
        tk.Label(
            self,
            text=APP_NAME,
            font=FONTS["logo"],
            bg=COLORS["sidebar"],
            fg=COLORS["white"],
            wraplength=170,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(25, 30))

        # Add page names here when you create more pages.
        page_names = [
            "Dashboard",
            "Properties",
            "Tenants",
            "Payments",
            "Settings",
        ]

        for page_name in page_names:
            button = tk.Button(
                self,
                text=page_name,
                font=FONTS["button"],
                bg=COLORS["sidebar"],
                fg=COLORS["white"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["white"],
                relief="flat",
                borderwidth=0,
                anchor="w",
                padx=20,
                pady=12,
                cursor="hand2",
                command=lambda selected_page=page_name: self.page_change_function(selected_page),
            )
            button.pack(fill="x", padx=10, pady=3)
            self.buttons[page_name] = button

    def set_active_button(self, active_page_name):
        """Highlight the button for the page that is currently open."""

        for page_name, button in self.buttons.items():
            if page_name == active_page_name:
                button.config(bg=COLORS["secondary"])
            else:
                button.config(bg=COLORS["sidebar"])
