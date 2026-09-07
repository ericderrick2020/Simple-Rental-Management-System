CREATE DATABASE IF NOT EXISTS rental_management_system;

USE rental_management_system;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'Admin',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS properties (
    property_id INT AUTO_INCREMENT PRIMARY KEY,
    property_name VARCHAR(120) NOT NULL,
    location VARCHAR(120) NOT NULL,
    total_units INT NOT NULL DEFAULT 0,
    monthly_rent DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(30) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    tenant_name VARCHAR(120) NOT NULL,
    phone VARCHAR(40) NOT NULL UNIQUE,
    email VARCHAR(120),
    unit_number VARCHAR(40) NOT NULL,
    lease_start DATE,
    monthly_rent DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    emergency_contact VARCHAR(120),
    status VARCHAR(30) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tenants_property
        FOREIGN KEY (property_id)
        REFERENCES properties(property_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    tenant_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(40) NOT NULL,
    reference_no VARCHAR(80) UNIQUE,
    notes TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'Paid',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payments_tenant
        FOREIGN KEY (tenant_id)
        REFERENCES tenants(tenant_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS app_settings (
    setting_key VARCHAR(80) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT IGNORE INTO users (username, password, role)
VALUES ('eric', '12345', 'Admin');

INSERT IGNORE INTO app_settings (setting_key, setting_value)
VALUES
    ('company_name', 'Saipali Rentals'),
    ('manager_name', 'Property Manager'),
    ('phone', '+256 700 000 000'),
    ('email', 'manager@example.com'),
    ('currency', 'UGX'),
    ('rent_due_day', '5'),
    ('late_fee', '50000'),
    ('theme', 'Light'),
    ('email_reminders', '1'),
    ('sms_reminders', '1'),
    ('backup_reminder', '0'),
    ('two_factor_login', 'Not enabled');

INSERT INTO properties (property_id, property_name, location, total_units, monthly_rent, status)
VALUES
    (1, 'Rocky Estates', 'Kampala', 20, 1200000.00, 'Active'),
    (2, 'Entebbe Apartment', 'Entebbe', 10, 500000.00, 'Active'),
    (3, 'Kampala Flats', 'Kampala', 12, 850000.00, 'Active')
ON DUPLICATE KEY UPDATE
    property_name = VALUES(property_name),
    location = VALUES(location),
    total_units = VALUES(total_units),
    monthly_rent = VALUES(monthly_rent),
    status = VALUES(status);
