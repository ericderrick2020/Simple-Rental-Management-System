import tkinter as tk
from tkinter import messagebox

from config.settings import APP_NAME, COLORS, DEFAULT_PASSWORD, DEFAULT_USERNAME, FONTS


class LoginPage(tk.Frame):
    """Login screen shown before the main application opens."""

    def __init__(self, parent, login_success_function):
        # tk.Frame creates a container that can hold labels, entries, and buttons.
        super().__init__(parent, bg=COLORS["background"])

        # This function is called only when the username and password are correct.
        self.login_success_function = login_success_function

        # Tkinter variables store the values typed in the input fields.
        self.username_var = tk.StringVar(value=DEFAULT_USERNAME)
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)

        # Make the login content stay centered as the window changes size.
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self._create_login_card()

    def _create_login_card(self):
        """Create the centered login form."""

        card = tk.Frame(
            self,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=34,
            pady=30,
        )
        card.grid(row=1, column=0, sticky="n", padx=30)
        card.columnconfigure(0, weight=1)

        tk.Label(
            card,
            text=APP_NAME,
            font=FONTS["heading"],
            bg=COLORS["surface"],
            fg=COLORS["primary"],
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            card,
            text="Sign in to continue",
            font=FONTS["normal"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        ).grid(row=1, column=0, sticky="w", pady=(4, 22))

        self._create_label(card, "Username", 2)
        username_entry = self._create_entry(card, self.username_var)
        username_entry.grid(row=3, column=0, sticky="ew", pady=(0, 14), ipady=7)

        self._create_label(card, "Password", 4)
        self.password_entry = self._create_entry(card, self.password_var, show="*")
        self.password_entry.grid(row=5, column=0, sticky="ew", pady=(0, 8), ipady=7)

        tk.Checkbutton(
            card,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            selectcolor=COLORS["white"],
        ).grid(row=6, column=0, sticky="w", pady=(0, 18))

        tk.Button(
            card,
            text="Login",
            font=FONTS["button"],
            bg=COLORS["primary"],
            fg=COLORS["white"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["white"],
            relief="flat",
            borderwidth=0,
            padx=18,
            pady=11,
            cursor="hand2",
            command=self.check_login,
        ).grid(row=7, column=0, sticky="ew")

        tk.Label(
            card,
            text="Default login: eric / 12345",
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
        ).grid(row=8, column=0, sticky="w", pady=(16, 0))

        # Focus puts the typing cursor in the password field when the login page opens.
        self.password_entry.focus_set()

        # Pressing Enter should try to log in, just like clicking the Login button.
        self.bind_all("<Return>", lambda event: self.check_login())

    def _create_label(self, parent, text, row):
        """Create a small label above an input field."""

        tk.Label(
            parent,
            text=text,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=row, column=0, sticky="w", pady=(0, 6))

    def _create_entry(self, parent, variable, show=None):
        """Create a text input for the username or password."""

        return tk.Entry(
            parent,
            textvariable=variable,
            show=show,
            font=FONTS["normal"],
            bg=COLORS["white"],
            fg=COLORS["text"],
            relief="solid",
            borderwidth=1,
            width=36,
        )

    def toggle_password_visibility(self):
        """Show or hide the password characters."""

        # The show option controls how password text appears on screen.
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def check_login(self):
        """Check whether the typed username and password are correct."""

        # strip() removes accidental spaces before and after the typed text.
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            # Stop listening for Enter on the login page before opening the main app.
            self.unbind_all("<Return>")
            self.login_success_function()
            return

        messagebox.showerror(
            "Login Failed",
            "Incorrect username or password.",
            parent=self.winfo_toplevel(),
        )
        self.password_var.set("")
        self.password_entry.focus_set()
