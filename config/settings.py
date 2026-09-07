import os

# Settings Stores details about the application

APP_NAME = "Rental Management System"
APP_WIDTH = 1250
APP_HEIGHT = 750

# Default login details for this beginner project.
# In a real system, passwords should be stored securely in a database, not in plain text.
DEFAULT_USERNAME = "eric"
DEFAULT_PASSWORD = "12345"

# MySQL database settings.
# XAMPP/WAMP usually uses user "root" with an empty password during class projects.
DATABASE_CONFIG = {
    "host": os.getenv("RMS_DB_HOST", "localhost"),
    "user": os.getenv("RMS_DB_USER", "root"),
    "password": os.getenv("RMS_DB_PASSWORD", ""),
    "database": os.getenv("RMS_DB_NAME", "rental_management_system"),
    "port": int(os.getenv("RMS_DB_PORT", "3306")),
}

# Application colors.
COLORS = {
    "primary": "#1E3A5F",
    "primary_hover": "#294F7A",
    "secondary": "#4F86C6",
    "background": "#F4F6F8",
    "surface": "#FFFFFF",
    "sidebar": "#102A43",
    "sidebar_hover": "#1D4668",
    "text": "#243B53",
    "text_light": "#829AB1",
    "white": "#FFFFFF",
    "border": "#D9E2EC",
    "success": "#2D9D78",
    "warning": "#E9A23B",
    "danger": "#D64545",
}

# Font settings that will be used in different parts of the application
FONTS = {
    "logo": ("Segoe UI", 18, "bold"),
    "heading": ("Segoe UI", 22, "bold"),
    "subheading": ("Segoe UI", 14, "bold"),
    "normal": ("Segoe UI", 10),
    "button": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "stat_number": ("Segoe UI", 24, "bold"),
}
