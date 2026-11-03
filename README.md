# Rental Management System

A Python desktop application built with Tkinter and MySQL. It manages properties,
tenants, rent payment records, company settings, and printable text receipts.

## Requirements

- Python with Tkinter support; checked with Python 3.13.5.
- A running MySQL server with the application's tables already configured.
- The connector listed in `requirements.txt`.
- Windows and a default printer for automatic receipt printing.

## Setup and run

From the project folder:

```powershell
python -m pip install -r requirements.txt
python main.py
```

The current demonstration login is username `eric` and password `12345`.

The application requires `users`, `properties`, `tenants`, `payments`, and
`app_settings` tables. Startup checks access; it does not create tables, import a
schema, or add sample records. A verified database setup/export is still required
for a fresh installation. See `data/database.py` and the final report for fields.

Database connection settings come from environment variables, with defaults in
`config/settings.py`:

| Variable | Default |
| --- | --- |
| `RMS_DB_HOST` | `localhost` |
| `RMS_DB_PORT` | `3306` |
| `RMS_DB_USER` | `root` |
| `RMS_DB_PASSWORD` | Empty |
| `RMS_DB_NAME` | `rental_management_system` |

The program reads process environment variables directly; it does not load a
`.env` file automatically. Do not commit local database credentials.

## Project layout

| Path | Contents |
| --- | --- |
| `main.py` | Startup, login, and navigation |
| `config/` | Appearance and connection settings |
| `components/` | Shared header, sidebar, cards, and tables |
| `pages/` | Dashboard, properties, tenants, payments, and settings |
| `data/database.py` | MySQL queries and transactions |
| `data/receipts/` | Created for receipts; excluded from Git |
| `assets/` | Earlier report screenshots |
| `reports/` | Finished reports, screenshots, diagrams, and test evidence |
| `reports/reference/` | Earlier design documents and guidelines |
| `report_checks.py` | Read-only syntax and isolated function checks |

## Using the application

1. Add a property before registering its tenants.
2. Register a tenant using the property dropdown. Optional document fields store
   local paths; keep those documents in an accessible, stable location.
3. Record a payment using the tenant dropdown. The saved amount paid is the main
   amount minus the balance entered on the form.
4. Select a payment and click **Print Receipt** to create a text receipt in
   `data/receipts/` and request printing on Windows.
5. Open Dashboard for summaries or Settings for company preferences.
6. Click **Logout** at the bottom of the sidebar to return to a fresh login screen.
   Open forms are closed and unsaved entries are discarded. Saved records remain
   in MySQL. Enter your password again to access the application.

Deleting a tenant also deletes their payments. Deleting a property deletes its
tenants and related payments after confirmation. Back up the database before
deleting records.

## Verification

```powershell
python -B report_checks.py
```

These checks parse application files and exercise selected login, money, date,
and balance logic using simulated controls and database calls. They do not
change rental records or verify live MySQL access or physical printing. Results
are written to `reports/test_evidence.json`.

## Deployment status

The folder has been cleaned for handover, but the application is still a
prototype. Real deployment requires secure authentication, a verified database
setup, suitable database credentials, and live integration testing. Editing,
filtered search, full lease tracking, history-preserving archiving, and the
approved detailed reports and exports remain incomplete. Reminder preferences
do not send messages. See Phase 3 for the full evaluation.

The runtime needs `main.py`, `config/`, `components/`, `pages/`, `data/database.py`,
the package `__init__.py` files, and installed requirements. Reports, report
images, and the check script are supporting handover material.
