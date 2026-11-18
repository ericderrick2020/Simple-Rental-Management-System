import tkinter as tk
from tkinter import ttk

from config.settings import COLORS, FONTS


class SimpleTable(tk.Frame):
    """Reusable table area for lists like properties, tenants, and payments."""

    def __init__(self, parent, columns):
        super().__init__(parent, bg=COLORS["surface"])

        self.rows = []
        self.columns = tuple(columns)
        self.search_var = tk.StringVar(self)
        self.search_column = tk.StringVar(self, value="All columns")

        search_frame = tk.Frame(self, bg=COLORS["surface"])
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(
            search_frame, text="Search:", font=FONTS["normal"],
            bg=COLORS["surface"], fg=COLORS["text"],
        ).pack(side="left", padx=(0, 8))
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.column_picker = ttk.Combobox(
            search_frame, textvariable=self.search_column, state="readonly",
            values=("All columns",) + self.columns, width=18,
        )
        self.column_picker.pack(side="left", padx=8)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left")
        self.search_entry.bind("<Escape>", lambda event: self.clear_search())

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
            text="No records found.",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        )
        self.empty_label.pack(anchor="w", padx=4, pady=(8, 0))
        self.search_var.trace_add("write", self._apply_search)
        self.search_column.trace_add("write", self._apply_search)

    def set_rows(self, rows):
        """Replace the current rows with new table data."""

        self.rows = list(rows)
        self._apply_search()

    def clear_search(self):
        """Show all records again."""

        self.search_column.set("All columns")
        self.search_var.set("")

    def _apply_search(self, *args):
        """Filter displayed values while keeping each row's original index."""

        terms = self.search_var.get().casefold().split()
        column = self.search_column.get()
        column_index = self.columns.index(column) if column in self.columns else None
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, row in enumerate(self.rows):
            values = row if column_index is None else (row[column_index],)
            searchable = " ".join(str(value) for value in values if value is not None).casefold()
            if all(term in searchable for term in terms):
                self.tree.insert("", "end", iid=str(index), values=row)

        if self.tree.get_children():
            self.empty_label.pack_forget()
        else:
            self.empty_label.config(
                text="No matching records found." if terms else "No records found."
            )
            self.empty_label.pack(anchor="w", padx=4, pady=(8, 0))

    def get_selected_index(self):
        """Return the index of the selected row, or None when no row is selected."""

        selected_items = self.tree.selection()
        if not selected_items:
            return None

        return int(selected_items[0])
