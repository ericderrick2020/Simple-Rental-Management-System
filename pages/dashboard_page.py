import tkinter as tk
from tkinter import messagebox

from components.stat_card import StatCard
from config.settings import COLORS, FONTS
from data.database import get_dashboard_summary
from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Dashboard page showing a summary of the system."""

    def __init__(self, parent):
        super().__init__(
            parent,
            title="Property Overview",
            description="This page shows the main summary of properties, tenants, and payments.",
        )

        self.dashboard_data = self._get_dashboard_data()
        self.stat_cards = {}
        self.metric_blocks = {}
        self.activity_widgets = []
        self.rent_status_widgets = []

        self.refresh_button = self.create_secondary_button(
            self.header_actions,
            text="Refresh",
            command=self.refresh_page,
        )
        self.refresh_button.pack(side="right", padx=20)

        self._configure_layout()
        self._create_stat_cards()
        self._create_main_dashboard()
        self._create_side_dashboard()
        self._create_bottom_dashboard()

    def _configure_layout(self):
        """Set up the dashboard grid before placing widgets."""

        self.content_frame.columnconfigure(0, weight=2)
        self.content_frame.columnconfigure(1, weight=2)
        self.content_frame.columnconfigure(2, weight=1)
        self.content_frame.rowconfigure(1, weight=1)
        self.content_frame.rowconfigure(2, weight=1)

    def _get_dashboard_data(self):
        """Load dashboard values from the database."""

        summary = get_dashboard_summary()

        if summary is None:
            return {
                "properties": 0,
                "tenants": 0,
                "monthly_payments": self._format_money(0),
                "occupancy_rate": 0,
                "occupied_units": 0,
                "total_units": 0,
                "paid_rent": self._format_money(0),
                "pending_rent": self._format_money(0),
                "overdue_tenants": 0,
                "activities": [("Database unavailable", "Start MySQL to load live dashboard data.")],
                "rent_status": [
                    ("Paid", 0, COLORS["success"]),
                    ("Pending", 0, COLORS["warning"]),
                    ("Overdue", 0, COLORS["danger"]),
                ],
            }

        properties = int(summary["property_count"] or 0)
        tenants = int(summary["tenant_count"] or 0)
        total_units = int(summary["total_units"] or 0)
        occupied_units = tenants
        occupancy_rate = 0

        if total_units:
            occupancy_rate = min(100, round((occupied_units / total_units) * 100))

        paid_rent = float(summary["paid_rent"] or 0)
        expected_rent = float(summary["expected_rent"] or 0)
        pending_rent = max(expected_rent - paid_rent, 0)
        status_counts = summary["payment_status_counts"]

        return {
            "properties": properties,
            "tenants": tenants,
            "monthly_payments": self._format_compact_money(paid_rent),
            "occupancy_rate": occupancy_rate,
            "occupied_units": occupied_units,
            "total_units": total_units,
            "paid_rent": self._format_money(paid_rent),
            "pending_rent": self._format_money(pending_rent),
            "overdue_tenants": int(summary["overdue_tenants"] or 0),
            "activities": self._build_recent_activities(summary),
            "rent_status": [
                ("Paid", int(status_counts.get("Paid", 0)), COLORS["success"]),
                ("Pending", int(status_counts.get("Pending", 0)), COLORS["warning"]),
                ("Overdue", int(status_counts.get("Overdue", 0)), COLORS["danger"]),
            ],
        }

    def _format_money(self, amount):
        """Format a number as Ugandan shillings."""

        return f"UGX {float(amount):,.2f}"

    def _format_compact_money(self, amount):
        """Format dashboard money with compact suffixes where useful."""

        amount = float(amount)

        if amount >= 1_000_000:
            return f"UGX {amount / 1_000_000:.1f}M"

        if amount >= 1_000:
            return f"UGX {amount / 1_000:.1f}K"

        return self._format_money(amount)

    def _build_recent_activities(self, summary):
        """Build recent dashboard activity from saved payment and tenant rows."""

        activities = []

        for payment in summary["recent_payments"]:
            title = "Payment received" if payment["status"] == "Paid" else f"Payment {payment['status'].lower()}"
            detail = (
                f"{payment['tenant_name']} - {payment['property_name']} / "
                f"{payment['unit_number']} - {self._format_money(payment['amount'])}"
            )
            activities.append((title, detail))

        if activities:
            return activities

        for tenant in summary["recent_tenants"]:
            detail = f"{tenant['tenant_name']} assigned to Unit {tenant['unit_number']}"
            activities.append(("Tenant added", detail))

        if activities:
            return activities

        return [("No activity yet", "Add tenants and payments to populate this dashboard.")]

    def _create_stat_cards(self):
        """Create the top summary cards."""

        stats = [
            (
                "Properties",
                str(self.dashboard_data["properties"]),
                "Active rental properties",
            ),
            (
                "Tenants",
                str(self.dashboard_data["tenants"]),
                "Current registered tenants",
            ),
            (
                "Payments",
                self.dashboard_data["monthly_payments"],
                "Collected this month",
            ),
        ]

        for column, (title, value, note) in enumerate(stats):
            card = StatCard(self.content_frame, title=title, value=value, note=note)
            card.grid(row=0, column=column, sticky="nsew", padx=8, pady=(0, 10))
            self.stat_cards[title] = card

    def _create_main_dashboard(self):
        """Create occupancy and payment summary sections."""

        panel = self._create_panel(
            row=1,
            column=0,
            columnspan=2,
            title="Portfolio Health",
        )
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)

        self.metric_blocks["occupancy"] = self._create_metric_block(
            panel,
            row=1,
            column=0,
            title="Occupancy",
            value=f"{self.dashboard_data['occupancy_rate']}%",
            note=f"{self.dashboard_data['occupied_units']} of {self.dashboard_data['total_units']} units occupied",
            color=COLORS["success"],
        )

        self.occupancy_canvas = self._create_progress_bar(
            panel,
            row=2,
            column=0,
            percent=self.dashboard_data["occupancy_rate"],
            color=COLORS["success"],
        )

        self.metric_blocks["rent"] = self._create_metric_block(
            panel,
            row=1,
            column=1,
            title="Rent Collected",
            value=self.dashboard_data["paid_rent"],
            note=f"{self.dashboard_data['pending_rent']} still pending",
            color=COLORS["primary"],
        )

        self.rent_status_frame = self._create_rent_status(panel, row=2, column=1)

    def _create_side_dashboard(self):
        """Create a quick action panel."""

        panel = self._create_panel(
            row=1,
            column=2,
            title="Quick Actions",
        )

        actions = [
            ("Add Property", "Open the Properties page to register a property."),
            ("Add Tenant", "Open the Tenants page to register a tenant."),
            ("Record Payment", "Open the Payments page to record rent."),
        ]

        for row, (label, message) in enumerate(actions, start=1):
            button = self.create_primary_button(
                panel,
                text=label,
                command=lambda text=label, note=message: self._show_action_message(text, note),
            )
            button.grid(row=row, column=0, sticky="ew", padx=16, pady=(4, 8))

    def _create_bottom_dashboard(self):
        """Create recent activity and rent reminder panels."""

        self.activity_panel = self._create_panel(
            row=2,
            column=0,
            columnspan=2,
            title="Recent Activity",
        )

        self._render_recent_activities()

        reminder_panel = self._create_panel(
            row=2,
            column=2,
            title="Rent Reminders",
        )

        self.metric_blocks["overdue"] = self._create_metric_block(
            reminder_panel,
            row=1,
            column=0,
            title="Overdue Tenants",
            value=str(self.dashboard_data["overdue_tenants"]),
            note="Follow up before the end of the week",
            color=COLORS["danger"],
        )

        reminder_button = self.create_secondary_button(
            reminder_panel,
            text="View Payments",
            command=lambda: self._show_action_message(
                "View Payments",
                "Use the Payments page to review pending and overdue rent.",
            ),
        )
        reminder_button.grid(row=3, column=0, sticky="ew", padx=16, pady=(12, 16))

    def _create_panel(self, row, column, title, columnspan=1):
        """Create a bordered dashboard panel."""

        panel = tk.Frame(
            self.content_frame,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        panel.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="nsew",
            padx=8,
            pady=8,
        )
        panel.columnconfigure(0, weight=1)

        tk.Label(
            panel,
            text=title,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        return panel

    def _create_metric_block(self, parent, row, column, title, value, note, color):
        """Create a compact label group for an important number."""

        block = tk.Frame(parent, bg=COLORS["surface"])
        block.grid(row=row, column=column, sticky="nsew", padx=16, pady=(2, 8))

        tk.Label(
            block,
            text=title,
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        ).pack(anchor="w")

        value_label = tk.Label(
            block,
            text=value,
            font=FONTS["heading"],
            bg=COLORS["surface"],
            fg=color,
        )
        value_label.pack(anchor="w", pady=(2, 0))

        note_label = tk.Label(
            block,
            text=note,
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
            wraplength=260,
            justify="left",
        )
        note_label.pack(anchor="w", pady=(2, 0))

        return {"value": value_label, "note": note_label}

    def _update_metric_block(self, key, value, note):
        """Update a dashboard metric block created earlier."""

        metric = self.metric_blocks[key]
        metric["value"].config(text=value)
        metric["note"].config(text=note)

    def _create_progress_bar(self, parent, row, column, percent, color):
        """Draw a simple progress bar for occupancy."""

        canvas = tk.Canvas(
            parent,
            height=14,
            bg=COLORS["surface"],
            highlightthickness=0,
        )
        canvas.grid(row=row, column=column, sticky="ew", padx=16, pady=(0, 16))
        canvas.percent = percent
        canvas.color = color

        canvas.bind(
            "<Configure>",
            lambda event: self._draw_progress(canvas, event.width, canvas.percent, canvas.color),
        )

        return canvas

    def _draw_progress(self, canvas, width, percent, color):
        """Redraw the progress bar whenever its size changes."""

        canvas.delete("all")
        canvas.create_rectangle(0, 2, width, 12, fill=COLORS["border"], outline="")
        canvas.create_rectangle(0, 2, width * (percent / 100), 12, fill=color, outline="")

    def _create_rent_status(self, parent, row, column):
        """Show a short breakdown of paid, pending, and overdue rent."""

        status_frame = tk.Frame(parent, bg=COLORS["surface"])
        status_frame.grid(row=row, column=column, sticky="ew", padx=16, pady=(0, 16))
        status_frame.columnconfigure(1, weight=1)
        self.rent_status_frame = status_frame

        self._render_rent_status()

        return status_frame

    def _render_rent_status(self):
        """Draw the current rent status counts."""

        for widget in self.rent_status_widgets:
            widget.destroy()
        self.rent_status_widgets = []

        for index, (label, count, color) in enumerate(self.dashboard_data["rent_status"]):
            dot = tk.Label(self.rent_status_frame, text="o", font=FONTS["normal"], bg=COLORS["surface"], fg=color)
            dot.grid(row=index, column=0, sticky="w", pady=2)
            self.rent_status_widgets.append(dot)

            label_widget = tk.Label(
                self.rent_status_frame,
                text=label,
                font=FONTS["small"],
                bg=COLORS["surface"],
                fg=COLORS["text"],
            )
            label_widget.grid(row=index, column=1, sticky="w", padx=(8, 0), pady=2)
            self.rent_status_widgets.append(label_widget)

            count_widget = tk.Label(
                self.rent_status_frame,
                text=str(count),
                font=FONTS["small"],
                bg=COLORS["surface"],
                fg=COLORS["text_light"],
            )
            count_widget.grid(row=index, column=2, sticky="e", padx=(8, 0), pady=2)
            self.rent_status_widgets.append(count_widget)

    def _render_recent_activities(self):
        """Draw current activity rows."""

        for widget in self.activity_widgets:
            widget.destroy()
        self.activity_widgets = []

        for row, (title, detail) in enumerate(self.dashboard_data["activities"], start=1):
            self.activity_widgets.append(self._create_activity_row(self.activity_panel, row, title, detail))

    def _create_activity_row(self, parent, row, title, detail):
        """Create one recent activity row."""

        activity = tk.Frame(parent, bg=COLORS["surface"])
        activity.grid(row=row, column=0, sticky="ew", padx=16, pady=(2, 8))
        activity.columnconfigure(0, weight=1)

        tk.Label(
            activity,
            text=title,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            activity,
            text=detail,
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
            wraplength=560,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        return activity

    def _show_action_message(self, title, message):
        """Show a helpful message until the pages are connected together."""

        messagebox.showinfo(title, message, parent=self.winfo_toplevel())

    def refresh_page(self):
        """Refresh dashboard values from the current data source."""

        self.dashboard_data = self._get_dashboard_data()
        self.stat_cards["Properties"].update_value(
            str(self.dashboard_data["properties"]),
            "Active rental properties",
        )
        self.stat_cards["Tenants"].update_value(
            str(self.dashboard_data["tenants"]),
            "Current registered tenants",
        )
        self.stat_cards["Payments"].update_value(
            self.dashboard_data["monthly_payments"],
            "Collected this month",
        )
        self._update_metric_block(
            "occupancy",
            f"{self.dashboard_data['occupancy_rate']}%",
            f"{self.dashboard_data['occupied_units']} of {self.dashboard_data['total_units']} units occupied",
        )
        self._update_metric_block(
            "rent",
            self.dashboard_data["paid_rent"],
            f"{self.dashboard_data['pending_rent']} still pending",
        )
        self._update_metric_block(
            "overdue",
            str(self.dashboard_data["overdue_tenants"]),
            "Follow up before the end of the week",
        )
        self.occupancy_canvas.percent = self.dashboard_data["occupancy_rate"]
        self._draw_progress(
            self.occupancy_canvas,
            self.occupancy_canvas.winfo_width(),
            self.occupancy_canvas.percent,
            self.occupancy_canvas.color,
        )
        self._render_rent_status()
        self._render_recent_activities()
