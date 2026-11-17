"""
UI Components and Design System Module
Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)
Provides reusable healthcare SaaS-inspired UI components: cards, badges, buttons,
and form element wrappers.
"""

import tkinter as tk
from tkinter import ttk
import config


class Card(tk.Frame):
    """A clean white card with subtle border and consistent padding."""

    def __init__(self, parent, bg=config.CARD_BACKGROUND, border_color=config.BORDER,
                 accent_color=None, padx=16, pady=16, bd=1, **kwargs):
        super().__init__(
            parent,
            bg=bg,
            highlightbackground=border_color,
            highlightthickness=bd,
            padx=padx,
            pady=pady,
            **kwargs
        )
        self.accent_color = accent_color


# Alias for explicit design architecture
ModernCard = Card


class PageHeader(tk.Frame):
    """Standardized page header with title, descriptive subtitle, and action button area."""

    def __init__(self, parent, title: str, subtitle: str, bg=config.BACKGROUND,
                 action_btn=None, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.columnconfigure(0, weight=1)

        title_box = tk.Frame(self, bg=bg)
        title_box.grid(row=0, column=0, sticky="w")

        self.lbl_title = tk.Label(
            title_box,
            text=title,
            font=config.FONT_HERO,
            fg=config.PRIMARY_DARK_TEAL,
            bg=bg
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = tk.Label(
            title_box,
            text=subtitle,
            font=config.FONT_REGULAR,
            fg=config.SECONDARY_TEXT,
            bg=bg
        )
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

        if action_btn:
            action_btn.grid(row=0, column=1, sticky="e")


class StatusBadge(tk.Label):
    """A clean, rounded-appearance status pill with soft tint background."""

    PRESETS = {
        "success": (config.COLOR_SUCCESS, config.TINT_SUCCESS_LIGHT),
        "warning": (config.COLOR_WARNING, config.TINT_WARNING_LIGHT),
        "danger":  (config.COLOR_MEDICAL_RED, config.COLOR_SOFT_PINK),
        "info":    (config.COLOR_INFO, config.TINT_INFO_LIGHT),
        "cyan":    (config.COLOR_PRIMARY_CYAN, config.COLOR_LIGHT_CYAN),
        "mint":    (config.COLOR_PRIMARY_CYAN, config.COLOR_LIGHT_CYAN),
        "neutral": (config.SECONDARY_TEXT, "#F1F5F9"),
    }

    def __init__(self, parent, text: str, preset="neutral", fg=None, bg=None, dot=False, **kwargs):
        color_fg, color_bg = self.PRESETS.get(preset, self.PRESETS["neutral"])
        if fg: color_fg = fg
        if bg: color_bg = bg

        display_text = f" ● {text} " if dot else f" {text} "

        super().__init__(
            parent,
            text=display_text,
            font=config.FONT_SMALL_BOLD,
            fg=color_fg,
            bg=color_bg,
            padx=8,
            pady=3,
            relief="flat",
            **kwargs
        )


class GlassCard(tk.Frame):
    """
    Superdesign and healthcare SaaS-inspired elevated card with optional top accent strip.
    """

    def __init__(self, parent, bg=config.CARD_BACKGROUND, border_color=config.BORDER,
                 accent_color=None, padx=16, pady=16, bd=1, **kwargs):
        super().__init__(
            parent,
            bg=bg,
            highlightbackground=border_color,
            highlightthickness=bd,
            **kwargs
        )
        if accent_color:
            self.accent_bar = tk.Frame(self, bg=accent_color, height=3)
            self.accent_bar.pack(fill="x", side="top")

        self.inner = tk.Frame(self, bg=bg, padx=padx, pady=pady)
        self.inner.pack(fill="both", expand=True)


class ThemedButton(tk.Button):
    """
    A modern styled healthcare button with smooth hover transitions:
    - 'primary'        : Vivid Primary Cyan (#13B8CC), white text
    - 'secondary'      : Clean light slate/cyan background, dark navy text
    - 'danger'         : Medical Red (#DC3545), white text (Emergency actions)
    - 'success'        : Green (#16A34A), white text
    - 'outline'        : White background with cyan border (#13B8CC)
    - 'outline_danger' : White background with red border (#DC3545)
    """

    STYLES = {
        "primary": {
            "bg": config.COLOR_PRIMARY_CYAN,
            "fg": "#FFFFFF",
            "activebg": config.HOVER_CYAN,
            "activefg": "#FFFFFF",
            "bd": 0,
            "relief": "flat",
        },
        "secondary": {
            "bg": "#F1F5F9",
            "fg": config.COLOR_DARK_NAVY,
            "activebg": "#E2E8F0",
            "activefg": config.COLOR_DARK_NAVY,
            "bd": 1,
            "relief": "solid",
            "highlightbackground": config.BORDER,
        },
        "danger": {
            "bg": config.COLOR_MEDICAL_RED,
            "fg": "#FFFFFF",
            "activebg": config.HOVER_DANGER,
            "activefg": "#FFFFFF",
            "bd": 0,
            "relief": "flat",
        },
        "success": {
            "bg": config.COLOR_SUCCESS,
            "fg": "#FFFFFF",
            "activebg": "#15803D",
            "activefg": "#FFFFFF",
            "bd": 0,
            "relief": "flat",
        },
        "outline": {
            "bg": "#FFFFFF",
            "fg": config.COLOR_PRIMARY_CYAN,
            "activebg": config.COLOR_LIGHT_CYAN,
            "activefg": config.COLOR_PRIMARY_CYAN,
            "bd": 1,
            "relief": "solid",
            "highlightbackground": config.COLOR_PRIMARY_CYAN,
        },
        "outline_danger": {
            "bg": "#FFFFFF",
            "fg": config.COLOR_MEDICAL_RED,
            "activebg": config.COLOR_SOFT_PINK,
            "activefg": config.COLOR_MEDICAL_RED,
            "bd": 1,
            "relief": "solid",
            "highlightbackground": config.COLOR_MEDICAL_RED,
        }
    }

    def __init__(self, parent, text: str, btn_type="primary", font=None,
                 command=None, pady=7, padx=14, **kwargs):
        style_cfg = self.STYLES.get(btn_type, self.STYLES["primary"])
        used_font = font or config.FONT_BOLD

        super().__init__(
            parent,
            text=text,
            font=used_font,
            bg=style_cfg["bg"],
            fg=style_cfg["fg"],
            activebackground=style_cfg["activebg"],
            activeforeground=style_cfg["activefg"],
            relief=style_cfg["relief"],
            bd=style_cfg["bd"],
            padx=padx,
            pady=pady,
            cursor="hand2",
            command=command,
            **kwargs
        )
        self.btn_type = btn_type
        self.default_bg = style_cfg["bg"]
        self.hover_bg = style_cfg["activebg"]

        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        if self["state"] != "disabled":
            self.configure(bg=self.hover_bg)

    def _on_leave(self, e):
        if self["state"] != "disabled":
            self.configure(bg=self.default_bg)


class FormFieldWrapper(tk.Frame):
    """Wraps a label, required indicator, and helper text consistently above/beside an input."""

    def __init__(self, parent, label: str, required: bool = False,
                 helper: str = "", bg=config.CARD_BACKGROUND, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        hdr_row = tk.Frame(self, bg=bg)
        hdr_row.pack(fill="x", anchor="w")

        lbl_text = tk.Label(
            hdr_row,
            text=label,
            font=config.FONT_BOLD,
            fg=config.MAIN_TEXT,
            bg=bg
        )
        lbl_text.pack(side="left")

        if required:
            tk.Label(
                hdr_row,
                text=" *",
                font=config.FONT_BOLD,
                fg=config.COLOR_DANGER,
                bg=bg
            ).pack(side="left")

        if helper:
            tk.Label(
                self,
                text=helper,
                font=config.FONT_TINY,
                fg=config.SECONDARY_TEXT,
                bg=bg
            ).pack(anchor="w", pady=(1, 3))


class StockProgressBar(tk.Canvas):
    """
    A sleek modern horizontal stock capacity indicator bar.
    Shows the available units against the benchmark target capacity.
    """

    def __init__(self, parent, value=0, max_value=25, color=config.COLOR_SUCCESS,
                 height=5, bg="#E2E8F0", **kwargs):
        super().__init__(
            parent,
            height=height,
            width=30,
            bg=bg,
            highlightthickness=0,
            **kwargs
        )
        self.value = value
        self.max_value = max(1, max_value)
        self.color = color
        self.bind("<Configure>", self._draw)

    def set_value(self, value, color=None):
        self.value = value
        if color:
            self.color = color
        self._draw()

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        if w <= 1:
            return
        h = self.winfo_height()
        pct = min(1.0, max(0.0, self.value / self.max_value))
        fill_w = int(w * pct)
        if fill_w > 0:
            self.create_rectangle(0, 0, fill_w, h, fill=self.color, outline="")


# =============================================================================
# REUSABLE ARCHITECTURAL COMPONENT ALIASES
# =============================================================================
ModernButton = ThemedButton
ModernHeader = PageHeader
ModernCard = Card


