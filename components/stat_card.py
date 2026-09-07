import tkinter as tk

from config.settings import COLORS, FONTS


class StatCard(tk.Frame):
    """Small summary box for dashboard numbers."""

    def __init__(self, parent, title, value, note=""):
        super().__init__(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )

        # Later you can connect these labels to real property, tenant, or payment data.
        self.value_label = tk.Label(
            self,
            text=value,
            font=FONTS["stat_number"],
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        )
        self.value_label.pack(anchor="w", padx=18, pady=(16, 2))

        self.title_label = tk.Label(
            self,
            text=title,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        )
        self.title_label.pack(anchor="w", padx=18)

        self.note_label = tk.Label(
            self,
            text=note,
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        )
        self.note_label.pack(anchor="w", padx=18, pady=(4, 16))

    def update_value(self, value, note=""):
        """Change the number shown on the card."""

        self.value_label.config(text=value)
        self.note_label.config(text=note)
