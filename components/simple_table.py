import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS


class SimpleTable(tk.Frame):
    """Reusable table area for lists like properties, tenants, and payments."""

    def __init__(self, parent, columns):
        super().__init__(parent, bg=COLORS["surface"])

        table_frame = tk.Frame(self, bg=COLORS["surface"])
        table_frame.pack(fill="both", expand=True)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        horizontal_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")

        # Add or remove column names from the page where this table is created.
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=8,
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        vertical_scrollbar.config(command=self.tree.yview)
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        horizontal_scrollbar.config(command=self.tree.xview)
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="w", width=140)

        self.empty_label = tk.Label(
            self,
            text="Table space is ready. Add rows here when you connect your data.",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        )
        self.empty_label.pack(anchor="w", padx=4, pady=(8, 0))

    def set_rows(self, rows):
        """Replace the current rows with new table data."""

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", "end", values=row)

        if rows:
            self.empty_label.pack_forget()
        elif not self.empty_label.winfo_ismapped():
            self.empty_label.pack(anchor="w", padx=4, pady=(8, 0))

    def get_selected_index(self):
        """Return the index of the selected row, or None when no row is selected."""

        selected_items = self.tree.selection()
        if not selected_items:
            return None

        table_items = self.tree.get_children()
        return table_items.index(selected_items[0])
