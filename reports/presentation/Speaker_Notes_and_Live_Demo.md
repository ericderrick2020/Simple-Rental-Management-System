# Phase 3 Presentation — Speaker Notes


Talk target: 10 minutes 25 seconds, followed by a separate live demonstration and questions.


The slide deck is Part B only. The existing final report remains Part A. Current test summary: 13 passed, 0 failed. Screenshots use controlled sample data; no live MySQL writes are claimed.


## Slide 1 — 40 seconds

Introduce yourself and the project. Explain that this is the same local desktop project approved in Phase 1 and designed in Phase 2. The presentation describes what the current code provides and the remaining gaps. Do not describe it as a fully production-ready system.


## Slide 2 — 45 seconds

Explain the context from the Phase 1 introduction. Rental information is often spread across paper receipts, notebooks, and spreadsheets. The intended users are landlords and property managers overseeing a local portfolio. Linking property, tenant, and payment information reduces repeated lookup work. These are intended benefits; no measured time-saving study was performed.


## Slide 3 — 60 seconds

State the original problem: manual record keeping can cause misplaced agreements, duplicate entries, financial mistakes, and slow reporting. The five groups shown combine the six approved objectives: MySQL security and storage is grouped with reliability, and reporting is grouped with validation. All six objectives remain partly achieved. Give credit to working entry and viewing features while explaining that editing, full leases, exports, and reports are still missing.


## Slide 4 — 50 seconds

Use the approved Phase 1 scope. Emphasise that missing in-scope features have not been reclassified as excluded features. The current scope remains one local desktop system. Payment-method choices such as Mobile Money or Card record how rent was received; they do not connect to payment gateways. The report contains the full mapping of the 22 requirements.


## Slide 5 — 60 seconds

Trace one save operation: the user enters details in a page, the page validates supported inputs, and a function in data/database.py saves the record using parameterised SQL. The interface then reloads the table. Compared with the refined Phase 2 plan, common validation has not been extracted into its own module, and planned edit/search workflows are incomplete. Logout now destroys the old interface and creates a fresh login screen.


## Slide 6 — 45 seconds

Explain why the stack suits a local desktop application: Python organises the logic, Tkinter provides built-in GUI tools, and MySQL holds linked records. The connector sends SQL requests. Python and connector versions were observed in this environment; the MySQL server version was not checked. VS Code is specified in the proposal, but actual editor use and version were not independently verified. Windows supports the current print request.


## Slide 7 — 60 seconds

Point out the actual sidebar and the Logout button at its bottom. This screenshot uses the current application widgets with controlled sample values and no MySQL writes. Distinguish source-code availability from live acceptance: the report has not verified every database workflow. Logout itself has three real-widget checks. Mention that deletion currently removes linked payments, so it must not be demonstrated with real tenant records.


## Slide 8 — 50 seconds

Walk through the journey briefly here; perform the live demonstration after Slide 12. Use an existing prepared test database, a sample property, and a sample tenant. Demonstrate at least property or tenant viewing, payment recording with one invalid balance, and logout followed by re-login. Confirm persistence through an actual save-and-reopen check during the demonstration. If the database is unavailable, say so and use labelled screenshots as backup only. Do not claim this has already been verified.


## Slide 9 — 60 seconds

The current run passed ten source/isolated-function checks and three Tkinter logout integration checks. The logout checks use real widgets but replace database availability and record-page content, so they do not prove MySQL integration. The three cases cover closing forms and clearing pages, repeated sign-in cycles, and rejecting a wrong password after logout. Existing checks cover syntax, money parsing, login, balance computation, and invalid balances/dates. Eight live integration scenarios remain pending in the report.


## Slide 10 — 55 seconds

Describe these as concrete implementation issues visible in the code and checks, rather than inventing a development story. Related records require careful deletion order and rollback. Payment entry needs checks before the amount is calculated. Logout needs more than displaying a login frame: the old records and popups must be destroyed, navigation state cleared, and layout reset. History retention and live database verification still remain limitations.


## Slide 11 — 65 seconds

Evaluate the result honestly against the approved proposal. All six objectives are partly achieved. The system provides a useful base but is not fully complete or production-ready. Prioritise security and repeatable installation, the missing record/lease operations, and reporting plus history preservation. Existing exclusions such as mobile apps, cloud services, online gateways, biometrics, and pricing forecasts should remain outside this delivery.


## Slide 12 — 35 seconds

Close by explaining the value: connected rental records and easier day-to-day lookup in one desktop interface. Acknowledge that the current prototype still needs the approved missing features and live integration tests. Thank the assessor and move into the prepared demonstration, then questions. Be ready to explain the data relationships, balance calculation, logout cleanup, and the limits of the tests.


# Live demonstration guide

1. Before presenting, start MySQL and verify the required tables in a separate test database. Configure the application through its RMS_DB_* environment variables. Do not use real tenant records.

2. Prepare Sample Apartments and Sample Tenant in advance. Keep one small property/tenant entry ready if an add operation is needed. Set a test rent of UGX 500,000.

3. Run python main.py and sign in using the configured demonstration credentials. Show the property and tenant tables and explain their relationship.

4. Open Record Payment. Select the sample tenant, use the current demonstration date in YYYY-MM-DD format, and enter a balance above the main amount. Show the warning. Correct the balance to UGX 150,000 and save. Expected amount paid: UGX 350,000.

5. Select the new payment and create a receipt. Check the saved file under data/receipts. Only claim physical printing if it actually succeeds on the demonstration device.

6. Click Logout, show the empty password field, then sign in again. Reopen Payments to verify that the saved record remains. If time allows, close/reopen the app to verify restart persistence.

7. Explain that deleting a tenant or property also removes linked payment records. Avoid destructive deletion during the demonstration unless using disposable test records.

8. If a live operation fails, explain the error. Use the included screenshots as clearly labelled backup; they do not replace a working live demonstration.


# Assessor question preparation

- Storage: MySQL records are linked using property_id and tenant_id. The installed schema still needs verification.

- Validation: required values, selected numeric values, payment dates, and balances are checked. Validation is not comprehensive.

- Logout: destroys the old pages and popups, clears navigation references, restores login layout, and requires the password again.

- Tests: ten source/isolated checks and three real-widget logout checks pass; no live database or printer acceptance is implied.

- Remaining work: secure authentication, editing/search, lease lifecycle, vacancy changes, history-preserving archiving, detailed reports, and tenant exports.


# Sources

- Approved Phase 1 proposal supplied by the student: objectives, scope, tools, and cover details.

- Phase 2 design and current Part A report: architecture, planned functions, and implementation gaps.

- Current application source, report_checks.py, tests/test_logout.py, and their actual execution results.

- Course title and instructor details follow the approved Phase 1 proposal. Replace the displayed presentation date if the actual submission date changes.