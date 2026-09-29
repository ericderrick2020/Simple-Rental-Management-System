from pathlib import Path

from config.settings import DATABASE_CONFIG, DEFAULT_USERNAME


SCHEMA_FILE = Path(__file__).with_name("schema.sql")

DEFAULT_APP_SETTINGS = {
    "company_name": "Saipali Rentals",
    "manager_name": "Property Manager",
    "phone": "+256 700 000 000",
    "email": "manager@example.com",
    "currency": "UGX",
    "rent_due_day": "5",
    "late_fee": "50000",
    "theme": "Light",
    "email_reminders": "1",
    "sms_reminders": "1",
    "backup_reminder": "0",
    "two_factor_login": "Not enabled",
}


class DatabaseUnavailable(Exception):
    """Raised when MySQL cannot be used from this computer yet."""


def _load_connector():
    try:
        import mysql.connector
    except ImportError as exc:
        raise DatabaseUnavailable(
            "mysql-connector-python is not installed. Run: pip install mysql-connector-python"
        ) from exc

    return mysql.connector


def get_connection(use_database=True):
    """Open a MySQL connection using the project database settings."""

    connector = _load_connector()
    config = DATABASE_CONFIG.copy()

    if not use_database:
        config.pop("database", None)

    try:
        return connector.connect(**config)
    except connector.Error as exc:
        raise DatabaseUnavailable(str(exc)) from exc


def initialize_database():
    """Create the project database and starter tables if MySQL is available."""

    statements = _read_schema_statements()

    try:
        connection = get_connection(use_database=False)
    except DatabaseUnavailable:
        return False

    try:
        cursor = connection.cursor()
        for statement in statements:
            cursor.execute(statement)
        cursor.execute(f"USE {DATABASE_CONFIG['database']}")
        _ensure_optional_columns(cursor)
        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close()


def get_property_options():
    """Return active properties for tenant dropdowns."""

    try:
        connection = get_connection()
    except DatabaseUnavailable:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT property_id, property_name, location, monthly_rent
            FROM properties
            WHERE status = 'Active'
            ORDER BY property_name
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_properties():
    """Return property records for the Properties page."""

    try:
        connection = get_connection()
    except DatabaseUnavailable:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                property_id,
                property_name,
                location,
                total_units,
                monthly_rent,
                extra_details
            FROM properties
            ORDER BY property_name
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def add_property(property_data):
    """Save a property record in MySQL."""

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO properties (
                property_name,
                location,
                total_units,
                monthly_rent,
                status,
                extra_details
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                property_data["property_name"],
                property_data["location"],
                property_data["total_units"],
                property_data["monthly_rent"],
                property_data["status"],
                property_data["extra_details"] or None,
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()


def delete_property(property_id):
    """Delete a property and records that depend on it."""

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            DELETE payments
            FROM payments
            INNER JOIN tenants
                ON tenants.tenant_id = payments.tenant_id
            WHERE tenants.property_id = %s
            """,
            (property_id,),
        )
        cursor.execute(
            """
            DELETE FROM tenants
            WHERE property_id = %s
            """,
            (property_id,),
        )
        cursor.execute(
            """
            DELETE FROM properties
            WHERE property_id = %s
            """,
            (property_id,),
        )
        connection.commit()
        return cursor.rowcount
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def add_tenant(tenant_data):
    """Save a tenant record in MySQL."""

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO tenants (
                property_id,
                tenant_name,
                phone,
                email,
                unit_number,
                lease_start,
                monthly_rent,
                emergency_contact,
                status,
                kyc_image_path,
                lc1_letter_path,
                extra_details
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                tenant_data["property_id"],
                tenant_data["tenant_name"],
                tenant_data["phone"],
                tenant_data["email"] or None,
                tenant_data["unit_number"],
                tenant_data["lease_start"] or None,
                tenant_data["monthly_rent"],
                tenant_data["emergency_contact"] or None,
                tenant_data["status"],
                tenant_data["kyc_image_path"] or None,
                tenant_data["lc1_letter_path"] or None,
                tenant_data["extra_details"] or None,
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()


def get_tenants():
    """Return tenant records joined with their selected property."""

    try:
        connection = get_connection()
    except DatabaseUnavailable:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                tenants.tenant_id,
                tenants.tenant_name,
                tenants.phone,
                tenants.email,
                properties.property_name,
                tenants.unit_number,
                tenants.monthly_rent,
                tenants.status,
                tenants.kyc_image_path,
                tenants.lc1_letter_path,
                tenants.extra_details
            FROM tenants
            INNER JOIN properties
                ON properties.property_id = tenants.property_id
            ORDER BY tenants.tenant_name
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def delete_tenant(tenant_id):
    """Delete a tenant and their payment records."""

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            DELETE FROM payments
            WHERE tenant_id = %s
            """,
            (tenant_id,),
        )
        cursor.execute(
            """
            DELETE FROM tenants
            WHERE tenant_id = %s
            """,
            (tenant_id,),
        )
        connection.commit()
        return cursor.rowcount
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_tenant_options():
    """Return tenants for payment dropdowns."""

    try:
        connection = get_connection()
    except DatabaseUnavailable:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                tenants.tenant_id,
                tenants.tenant_name,
                tenants.unit_number,
                tenants.monthly_rent,
                properties.property_name
            FROM tenants
            INNER JOIN properties
                ON properties.property_id = tenants.property_id
            WHERE tenants.status = 'Active'
            ORDER BY tenants.tenant_name
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def add_payment(payment_data):
    """Save a rent payment record in MySQL."""

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO payments (
                tenant_id,
                amount,
                payment_date,
                payment_method,
                reference_no,
                notes,
                balance,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                payment_data["tenant_id"],
                payment_data["amount"],
                payment_data["payment_date"],
                payment_data["payment_method"],
                payment_data["reference_no"] or None,
                payment_data["notes"] or None,
                payment_data["balance"],
                payment_data["status"],
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()


def get_payments():
    """Return payment records joined with tenant and property details."""

    try:
        connection = get_connection()
    except DatabaseUnavailable:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                payments.payment_id,
                tenants.tenant_name,
                tenants.phone,
                properties.property_name,
                tenants.unit_number,
                payments.amount,
                payments.balance,
                payments.payment_date,
                payments.payment_method,
                payments.reference_no,
                payments.notes,
                payments.status
            FROM payments
            INNER JOIN tenants
                ON tenants.tenant_id = payments.tenant_id
            INNER JOIN properties
                ON properties.property_id = tenants.property_id
            ORDER BY payments.payment_date DESC, payments.created_at DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_dashboard_summary():
    """Return live dashboard summary values from MySQL."""

    try:
        connection = get_connection()
    except DatabaseUnavailable:
        return None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                COUNT(*) AS property_count,
                COALESCE(SUM(total_units), 0) AS total_units
            FROM properties
            WHERE status = 'Active'
            """
        )
        property_summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS tenant_count,
                COALESCE(SUM(monthly_rent), 0) AS expected_rent
            FROM tenants
            WHERE status = 'Active'
            """
        )
        tenant_summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS paid_rent
            FROM payments
            WHERE status = 'Paid'
                AND YEAR(payment_date) = YEAR(CURDATE())
                AND MONTH(payment_date) = MONTH(CURDATE())
            """
        )
        payment_summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT status, COUNT(*) AS status_count
            FROM payments
            GROUP BY status
            """
        )
        payment_status_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT COUNT(DISTINCT tenant_id) AS overdue_tenants
            FROM payments
            WHERE status = 'Overdue'
            """
        )
        overdue_summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                tenants.tenant_name,
                properties.property_name,
                tenants.unit_number,
                payments.amount,
                payments.status,
                payments.payment_date
            FROM payments
            INNER JOIN tenants
                ON tenants.tenant_id = payments.tenant_id
            INNER JOIN properties
                ON properties.property_id = tenants.property_id
            ORDER BY payments.created_at DESC, payments.payment_date DESC
            LIMIT 4
            """
        )
        recent_payments = cursor.fetchall()

        cursor.execute(
            """
            SELECT tenant_name, unit_number, created_at
            FROM tenants
            ORDER BY created_at DESC
            LIMIT 4
            """
        )
        recent_tenants = cursor.fetchall()

        return {
            "property_count": property_summary["property_count"],
            "total_units": property_summary["total_units"],
            "tenant_count": tenant_summary["tenant_count"],
            "expected_rent": tenant_summary["expected_rent"],
            "paid_rent": payment_summary["paid_rent"],
            "payment_status_counts": {
                row["status"]: row["status_count"]
                for row in payment_status_rows
            },
            "overdue_tenants": overdue_summary["overdue_tenants"],
            "recent_payments": recent_payments,
            "recent_tenants": recent_tenants,
        }
    finally:
        cursor.close()
        connection.close()


def get_app_settings():
    """Return application settings stored in MySQL."""

    settings = DEFAULT_APP_SETTINGS.copy()

    try:
        connection = get_connection()
    except DatabaseUnavailable:
        return settings

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT setting_key, setting_value
            FROM app_settings
            """
        )

        for row in cursor.fetchall():
            settings[row["setting_key"]] = row["setting_value"]

        return settings
    finally:
        cursor.close()
        connection.close()


def save_app_settings(settings_data):
    """Save application settings in MySQL."""

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.executemany(
            """
            INSERT INTO app_settings (setting_key, setting_value)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                setting_value = VALUES(setting_value)
            """,
            list(settings_data.items()),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_account_settings(username=DEFAULT_USERNAME):
    """Return account display values from MySQL."""

    account = {
        "role": "Administrator",
        "last_password_change": "Not connected yet",
        "two_factor_login": DEFAULT_APP_SETTINGS["two_factor_login"],
    }

    try:
        connection = get_connection()
    except DatabaseUnavailable:
        return account

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT role, created_at
            FROM users
            WHERE username = %s
            LIMIT 1
            """,
            (username,),
        )
        user_row = cursor.fetchone()

        if user_row:
            account["role"] = user_row["role"]
            account["last_password_change"] = f"Account created {user_row['created_at']}"

        cursor.execute(
            """
            SELECT setting_value
            FROM app_settings
            WHERE setting_key = 'two_factor_login'
            LIMIT 1
            """
        )
        two_factor_row = cursor.fetchone()

        if two_factor_row:
            account["two_factor_login"] = two_factor_row["setting_value"]

        return account
    finally:
        cursor.close()
        connection.close()


def _read_schema_statements():
    """Split the class-project SQL file into individual statements."""

    content = SCHEMA_FILE.read_text(encoding="utf-8")
    statements = []

    for chunk in content.split(";"):
        statement = chunk.strip()
        if statement:
            statements.append(statement)

    return statements


def _ensure_optional_columns(cursor):
    """Add columns introduced after the original class-project schema."""

    columns = {
        "properties": {
            "extra_details": "TEXT",
        },
        "tenants": {
            "kyc_image_path": "VARCHAR(500)",
            "lc1_letter_path": "VARCHAR(500)",
            "extra_details": "TEXT",
        },
        "payments": {
            "balance": "DECIMAL(12, 2) NOT NULL DEFAULT 0.00",
        },
    }

    for table_name, table_columns in columns.items():
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        existing_columns = {row[0] for row in cursor.fetchall()}

        for column_name, column_type in table_columns.items():
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                )
