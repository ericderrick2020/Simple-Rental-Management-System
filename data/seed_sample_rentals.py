"""Add realistic fictional rentals: run python -B -m data.seed_sample_rentals."""

from data.database import get_connection


PROPERTIES = [
    ("Kisaasi Palm Court", "Kisaasi, Kampala", 8, 650000, "One-bedroom apartments; gated compound, water tanks and parking.", "Amina Nansubuga", "David Ssekandi"),
    ("Naalya Green Apartments", "Naalya, Wakiso", 12, 950000, "Two-bedroom apartments with balconies, security and separate electricity meters.", "Grace Nakato", "Brian Mugisha"),
    ("Ntinda View Residences", "Ntinda, Kampala", 6, 1200000, "Two-bedroom apartments; paved parking and an on-site caretaker.", "Sarah Namutebi", "Daniel Okello"),
    ("Kira Garden Homes", "Kira, Wakiso", 10, 750000, "One-bedroom homes with shared gardens and individual water meters.", "Esther Akello", "Michael Kato"),
    ("Najjera Heights", "Najjera, Wakiso", 8, 1100000, "Two-bedroom apartments; secure gate, balconies and covered laundry space.", "Patricia Nabirye", "Joseph Tumusiime"),
    ("Kyanja Olive Court", "Kyanja, Kampala", 6, 850000, "One-bedroom apartments with fitted kitchens and backup water storage.", "Rebecca Achieng", "Samuel Wasswa"),
    ("Makindye Hill Flats", "Makindye, Kampala", 10, 550000, "One-bedroom flats near public transport; fenced compound and caretaker.", "Florence Nakiwala", "Peter Ssentongo"),
    ("Entebbe Lakeview Court", "Katabi, Entebbe", 8, 900000, "Two-bedroom apartments with shared green space and resident parking.", "Lydia Atim", "Emmanuel Ssemanda"),
    ("Mbarara Acacia Homes", "Nyamitanga, Mbarara", 6, 500000, "One-bedroom homes; tiled floors, water tanks and secure perimeter fence.", "Doreen Asiimwe", "Andrew Byaruhanga"),
    ("Jinja Riverside Apartments", "Walukuba, Jinja", 8, 600000, "Two-bedroom apartments with separate meters and shared courtyard.", "Harriet Naigaga", "Patrick Waiswa"),
]

MARKER = "Fictional sample rental data (November 2026)."


def main():
    connection = get_connection()
    cursor = connection.cursor()
    added_properties = added_tenants = 0
    try:
        connection.start_transaction()
        for index, (name, location, units, rent, details, first, second) in enumerate(PROPERTIES):
            cursor.execute(
                "SELECT property_id FROM properties WHERE property_name = %s AND extra_details LIKE %s",
                (name, MARKER + "%"),
            )
            existing = cursor.fetchall()
            if existing:
                property_id = existing[0][0]
            else:
                cursor.execute(
                    "INSERT INTO properties (property_name, location, total_units, monthly_rent, status, extra_details) VALUES (%s, %s, %s, %s, 'Active', %s)",
                    (name, location, units, rent, MARKER + " " + details),
                )
                property_id = cursor.lastrowid
                added_properties += 1
            for offset, tenant_name in enumerate((first, second)):
                number = index * 2 + offset + 1
                email = tenant_name.lower().replace(" ", ".") + "@example.com"
                cursor.execute("SELECT tenant_id FROM tenants WHERE email = %s AND property_id = %s", (email, property_id))
                if cursor.fetchall():
                    continue
                cursor.execute(
                    """INSERT INTO tenants
                    (property_id, tenant_name, phone, email, unit_number, lease_start,
                     monthly_rent, emergency_contact, status, extra_details)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Active', %s)""",
                    (property_id, tenant_name, f"+256 770 900 {number:03d}", email,
                     f"A{offset + 1:02d}", f"2026-{3 + index % 7:02d}-01", rent,
                     f"{'Rose Namusoke' if offset == 0 else 'James Mukasa'} (sibling), +256 770 901 {number:03d}",
                     MARKER + " Contact numbers are placeholders. Rent payable monthly by the 5th; "
                     f"refundable security deposit UGX {rent:,}. No identity documents supplied."),
                )
                added_tenants += 1
        cursor.execute("SELECT COUNT(*) FROM properties WHERE extra_details LIKE %s", (MARKER + "%",))
        assert cursor.fetchone()[0] == 10, "Expected 10 sample properties"
        cursor.execute("SELECT COUNT(*) FROM tenants WHERE extra_details LIKE %s", (MARKER + "%",))
        assert cursor.fetchone()[0] == 20, "Expected 20 sample tenants"
        connection.commit()
        print(f"Added {added_properties} properties and {added_tenants} tenants. Verified 10 sample properties and 20 linked tenants.")
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
