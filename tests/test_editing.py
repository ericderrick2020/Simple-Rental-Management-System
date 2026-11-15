"""Verify editing prefilled forms saves the original record and preserves its values."""
from decimal import Decimal
import tkinter as tk
import unittest
from unittest.mock import patch

from pages import properties_page, tenants_page, payments_page
from data import database


class EditingTests(unittest.TestCase):
    def test_edit_forms_preserve_values_and_update_existing_id(self):
        cases = [
            (properties_page, 'PropertiesPage', 'property', dict(
                property_id=3, property_name='House', location='Kampala', total_units=2,
                monthly_rent=Decimal('500000'), extra_details='Details', status='Active')),
            (tenants_page, 'TenantsPage', 'tenant', dict(
                tenant_id=4, property_id=3, property_name='House', location='Kampala',
                tenant_name='Jane', phone='0700000000', email=None, unit_number='A',
                lease_start=None, monthly_rent=Decimal('500000'), emergency_contact='John',
                status='Notice Given', kyc_image_path='kyc.png', lc1_letter_path=None,
                extra_details='Details')),
            (payments_page, 'PaymentsPage', 'payment', dict(
                payment_id=5, tenant_id=4, tenant_name='Jane', phone='0700000000',
                property_name='House', unit_number='A', monthly_rent=Decimal('500000'),
                amount=Decimal('400000'), balance=Decimal('100000'), payment_date='2026-11-15',
                payment_method='Cash', reference_no='REF', notes='Details', status='Pending')),
        ]
        for module, class_name, entity, record in cases:
            with self.subTest(entity=entity):
                root = tk.Tk()
                root.withdraw()
                self.addCleanup(root.destroy)
                loader = dict(property='get_properties', tenant='get_tenants', payment='get_payments')[entity]
                with patch.object(module, loader, return_value=[record]), \
                     patch.object(module, f'update_{entity}_in_database') as update, \
                     patch.object(module, f'save_{entity}_to_database') as add:
                    # Empty choices exercise editing records linked to inactive properties/tenants.
                    with patch.object(module, 'get_property_options' if entity == 'tenant' else
                                      'get_tenant_options' if entity == 'payment' else loader,
                                      return_value=[] if entity != 'property' else [record]):
                        page = getattr(module, class_name)(root)
                        table = getattr(page, f'{entity}_table')
                        table.tree.selection_set(table.tree.get_children()[0])
                        getattr(page, f'edit_selected_{entity}')()
                        modal = next(w for w in page.winfo_children() if isinstance(w, tk.Toplevel))
                        def save_button(widget):
                            for child in widget.winfo_children():
                                if isinstance(child, tk.Button) and child.cget('text') == f'Save {entity.title()}':
                                    return child
                                found = save_button(child)
                                if found is not None:
                                    return found
                        save_button(modal).invoke()
                        update.assert_called_once()
                        add.assert_not_called()
                        record_id, values = update.call_args.args
                        self.assertEqual(record_id, record[f'{entity}_id'])
                        for key, value in values.items():
                            if entity == 'property' and key == 'status':
                                continue
                            self.assertEqual(value or None, record[key] or None, key)

    def test_updates_use_id_and_commit_or_rollback(self):
        from unittest.mock import MagicMock
        for entity, fields in (
            ('property', 'property_name location total_units monthly_rent extra_details'),
            ('tenant', 'property_id tenant_name phone email unit_number lease_start monthly_rent emergency_contact status kyc_image_path lc1_letter_path extra_details'),
            ('payment', 'tenant_id amount payment_date payment_method reference_no notes balance status'),
        ):
            connection = MagicMock()
            with patch.object(database, 'get_connection', return_value=connection):
                update = getattr(database, f'update_{entity}')
                values = dict.fromkeys(fields.split(), 'value')
                update(42, values)
                sql, parameters = connection.cursor.return_value.execute.call_args.args
                self.assertIn(f'WHERE {entity}_id = %s', sql)
                self.assertEqual(parameters[-1], 42)
                connection.commit.assert_called_once()
                connection.cursor.return_value.execute.side_effect = RuntimeError('failure')
                with self.assertRaises(RuntimeError):
                    update(42, values)
                connection.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
