"""Check search results and selection safety using real table widgets."""
import tkinter as tk
import unittest

from components.simple_table import SimpleTable


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.table = SimpleTable(self.root, ("Name", "Location", "Rent"))
        self.rows = [
            ("Alice Homes", "Kampala", "UGX 500,000.00"),
            ("Bob Apartments", "Entebbe", "UGX 350,000.00"),
            ("Carol House", "Kampala", "UGX 350,000.00"),
        ]
        self.table.set_rows(self.rows)

    def test_search_ignores_case_and_matches_multiple_words(self):
        self.table.search_var.set("  KAMPALA   carol ")
        self.assertEqual(self.table.tree.get_children(), ("2",))
        self.table.tree.selection_set("2")
        # Editing, deleting, and printing must use the original record index.
        self.assertEqual(self.table.get_selected_index(), 2)

    def test_column_filter_and_clear(self):
        self.table.search_column.set("Name")
        self.table.search_var.set("kampala")
        self.assertEqual(self.table.tree.get_children(), ())
        self.assertEqual(self.table.empty_label.cget("text"), "No matching records found.")
        self.assertIsNone(self.table.get_selected_index())
        self.table.clear_search()
        self.assertEqual(self.table.tree.get_children(), ("0", "1", "2"))

    def test_refresh_keeps_search_and_clears_old_selection(self):
        self.table.search_var.set("350,000")
        self.table.tree.selection_set("2")
        self.table.set_rows([self.rows[2], self.rows[0]])
        self.assertEqual(self.table.tree.get_children(), ("0",))
        self.assertIsNone(self.table.get_selected_index())
        self.table.tree.selection_set("0")
        self.assertEqual(self.table.get_selected_index(), 0)


if __name__ == "__main__":
    unittest.main()
