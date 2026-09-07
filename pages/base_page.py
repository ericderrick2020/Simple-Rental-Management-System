import tkinter as tk

from config.settings import COLORS, FONTS


class BasePage(tk.Frame):
    """Base design shared by all pages."""

    def __init__(self, parent, title, description):
        super().__init__(
            parent,
            bg=COLORS["background"]
        )

        # Make the content section expandable.
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Create the introduction section shown at the top of every page.
        self.introduction_frame = tk.Frame(
            self,
            bg=COLORS["background"]
        )
        self.introduction_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(25, 15)
        )
        self.introduction_frame.columnconfigure(0, weight=1)

        title_frame = tk.Frame(
            self.introduction_frame,
            bg=COLORS["background"]
        )
        title_frame.grid(row=0, column=0, sticky="w")

        tk.Label(
            title_frame,
            text=title,
            font=FONTS["subheading"],
            bg=COLORS["background"],
            fg=COLORS["text"]
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text=description,
            font=FONTS["normal"],
            bg=COLORS["background"],
            fg=COLORS["text_light"]
        ).pack(anchor="w", pady=(4, 0))

        self.header_actions=tk.Frame(
            self.introduction_frame,
            bg=COLORS["background"]
        )

        self.header_actions.grid(
            row=0,
            column=1,
            sticky="e"
        )

        # Child pages place content inside this scrollable body frame.
        self.content_area = tk.Frame(
            self,
            bg=COLORS["background"]
        )
        self.content_area.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 25)
        )
        self.content_area.rowconfigure(0, weight=1)
        self.content_area.columnconfigure(0, weight=1)

        self.content_canvas = tk.Canvas(
            self.content_area,
            bg=COLORS["background"],
            highlightthickness=0,
        )
        self.content_canvas.grid(row=0, column=0, sticky="nsew")

        self.content_scrollbar = tk.Scrollbar(
            self.content_area,
            orient="vertical",
            command=self.content_canvas.yview,
        )
        self.content_scrollbar.grid(row=0, column=1, sticky="ns")

        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)

        self.content_frame = tk.Frame(
            self.content_canvas,
            bg=COLORS["background"],
        )
        self.content_window = self.content_canvas.create_window(
            (0, 0),
            window=self.content_frame,
            anchor="nw",
        )

        self.content_frame.bind("<Configure>", self._update_scroll_region)
        self.content_canvas.bind("<Configure>", self._resize_scroll_content)
        self.content_canvas.bind("<Enter>", self._bind_mousewheel)
        self.content_canvas.bind("<Leave>", self._unbind_mousewheel)

        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

    def _update_scroll_region(self, event=None):
        """Update the scrollable area when page content changes size."""

        self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))

    def _resize_scroll_content(self, event):
        """Keep the inner page content the same width as the visible body."""

        self.content_canvas.itemconfigure(self.content_window, width=event.width)

    def _bind_mousewheel(self, event=None):
        """Enable mouse wheel scrolling while the pointer is over the page body."""

        self.content_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        """Disable page body mouse wheel scrolling when the pointer leaves it."""

        self.content_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Scroll the page body with the mouse wheel."""

        direction = -1 if event.delta > 0 else 1
        self.content_canvas.yview_scroll(direction, "units")

    def create_empty_section(self, parent, title, note, row, column=0):
        """Create an empty area where page UI can be added later."""

        section = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        section.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
        section.columnconfigure(0, weight=1)
        section.rowconfigure(1, weight=1)

        tk.Label(
            section,
            text=title,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 4))

        tk.Label(
            section,
            text=note,
            font=FONTS["small"],
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
            wraplength=420,
            justify="left",
        ).grid(row=1, column=0, sticky="nw", padx=16, pady=(0, 16))

        return section

    def create_primary_button(self, parent, text, command):
        """Create a reusable primary button."""

        return tk.Button(
            parent,
            text=text,
            font=FONTS["button"],
            bg=COLORS["primary"],
            fg=COLORS["white"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["white"],
            relief="flat",
            borderwidth=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=command
        )

    def create_secondary_button(self, parent, text, command):
        """Create a reusable secondary button."""

        return tk.Button(
            parent,
            text=text,
            font=FONTS["button"],
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief="solid",
            borderwidth=1,
            padx=18,
            pady=9,
            cursor="hand2",
            command=command
        )
