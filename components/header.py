import tkinter as tk
from config.settings import COLORS, FONTS


class Header(tk.Frame):
    """Reusable header displayed above every page"""

    def __init__(self, parent, page_title):
        super().__init__(parent, bg=COLORS["surface"], height=75)

        # Stop the frame from shrinking to fit its children
        self.grid_propagate(False)

        # MaKE THE MIDDLE SECTION EXPANDABLE
        self.columnconfigure(0, weight=1)

        # Create the current page title
        self.title_label = tk.Label(
            self,
            text=page_title,
            font=FONTS["heading"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=30,
            pady=20,
        )

        # Create the user information section.
        user_frame = tk.Frame(self, bg=COLORS["surface"])
        user_frame.grid(row=0, column=1, padx=30, pady=12)
        # Create a simple user icon.
        user_icon = tk.Label(
            user_frame,
            text="A",
            font=("Segoe UI", 12, "bold"),
            width=3,
            height=1,
            bg=COLORS["primary"],
            fg=COLORS["white"],
        )
        user_icon.pack(side="left", padx=(0, 10))

        # Display the user name.
        user_details = tk.Frame(user_frame, bg=COLORS["surface"])
        user_details.pack(side="left")

        tk.Label(
            user_details,
            text="Administrator",
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).pack(anchor="w")

        tk.Label(
            user_details,
            text="Property Manager",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        ).pack(anchor="w")

    def set_page_title(self, title):
        """Change the header title when another page is opened."""

        self.title_label.config(text=title)
