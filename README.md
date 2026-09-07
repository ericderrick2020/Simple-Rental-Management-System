# Rental Management System

This is a simple Python Tkinter project for a rental management system.

## Where I Started

I started by checking the project folders:

- `main.py` starts the application.
- `config/settings.py` stores app colors, fonts, width, and height.
- `components/` stores reusable parts like the header, sidebar, stat cards, and tables.
- `pages/` stores each app page.

Some files were already started, but a few were still empty or unfinished.

## What I Did

I fixed the main structure so the app can open and move between pages.

I completed the reusable components:

- `Header` shows the current page title.
- `Sidebar` shows the menu buttons.
- `StatCard` gives a small box for dashboard numbers.
- `SimpleTable` gives a reusable table space for future lists.

I also created starter pages:

- `Dashboard`
- `Properties`
- `Tenants`
- `Payments`
- `Settings`

These pages do not have the full UI yet. They only have empty spaces and comments showing where to add the UI later.

## How The App Works

When you run `main.py`, the app creates the main window.

Then it creates the sidebar on the left side.

Then it creates the header at the top.

Then it creates all pages one time and stores them in a dictionary called `self.pages`.

When you click a sidebar button, the app shows the correct page and changes the header title.

## Where To Add UI Later

Open the page file you want to work on inside the `pages/` folder.

For example:

- Add dashboard content in `pages/dashboard_page.py`.
- Add property content in `pages/properties_page.py`.
- Add tenant content in `pages/tenants_page.py`.
- Add payment content in `pages/payments_page.py`.
- Add settings content in `pages/settings_page.py`.

Look for comments that say where to add future content. That is the place to build your forms, tables, buttons, and labels.

## How To Run

Use this command:

```bash
python main.py
```

If your computer uses `py` instead of `python`, use:

```bash
py main.py
```

### AUTH DETAILS
- Username: eric
- Password: 12345

## MySQL Database Setup

This project now includes a MySQL database schema in `data/schema.sql`.

Install the Python MySQL connector:

```bash
pip install -r requirements.txt
```

Create the database using MySQL or XAMPP:

```bash
mysql -u root < data/schema.sql
```

The default database settings are in `config/settings.py`:

- Host: `localhost`
- User: `root`
- Password: empty
- Database: `rental_management_system`

The Tenants form now loads properties into a dropdown. If MySQL is not installed or running yet, the app will still show sample properties so development can continue.
