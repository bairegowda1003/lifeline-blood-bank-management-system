"""
Main Application Entry Point & Shell Architecture
Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)
Student: Baire Gowda (25PG00157) - MCA 3rd Semester
Healthcare SaaS-inspired Desktop GUI using Python 3.12 + Tkinter + ttkbootstrap + SQLite 3.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Dependency verification check
try:
    import tkcalendar
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Missing Dependency",
        "Required dependency 'tkcalendar' was not found.\n\n"
        "Please install it using:\n"
        "pip install -r requirements.txt\n"
    )
    sys.exit(1)

try:
    import ttkbootstrap as tb
    from ttkbootstrap.style.theme import ThemeDefinition
    HAS_TTKBOOTSTRAP = True
except ImportError:
    HAS_TTKBOOTSTRAP = False

import config
from database import DatabaseManager
from dashboard import DashboardView
from donor import DonorView
from blood_stock import BloodStockView
from requests import RequestsView
from ui_components import Card, ThemedButton, StatusBadge


class AboutHelpView(tk.Frame):
    """About & Help Documentation view embedded inside the desktop application."""

    def __init__(self, parent, db_manager, on_data_changed=None):
        super().__init__(parent, bg=config.BACKGROUND)
        self.db = db_manager
        self.on_data_changed = on_data_changed

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = tk.Frame(self, bg=config.BACKGROUND)
        container.pack(fill="both", expand=True, padx=20, pady=(12, 16))
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT CARD: ACADEMIC PROFILE & DEMO MANAGEMENT
        # -------------------------------------------------------------
        left_card = Card(container, bg=config.CARD_BACKGROUND, accent_color=config.COLOR_PRIMARY_CYAN, padx=20, pady=16)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_card.columnconfigure(0, weight=1)

        tk.Label(
            left_card,
            text="🎓 Academic Project Profile",
            font=config.FONT_HERO,
            fg=config.COLOR_DARK_NAVY,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            left_card,
            text="Verified submission details for MCA mini-project evaluation.",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w", pady=(0, 14))

        details = [
            ("Application Brand:", config.APP_BRAND),
            ("Project Title:", config.APP_TITLE),
            ("Category:", "Public Health / Healthcare IT"),
            ("Student Name:", config.STUDENT_NAME),
            ("Student ID / Reg:", config.STUDENT_ID),
            ("Course & Degree:", config.COURSE),
            ("Academic Semester:", config.SEMESTER),
            ("Academic Year:", config.ACADEMIC_YEAR),
            ("Architecture:", "Layered Desktop Architecture (MVC-Style)"),
            ("GUI Framework:", "Python Tkinter + ttk + ttkbootstrap"),
            ("Database Engine:", "SQLite 3 (ACID Transactions & Parameterized SQL)"),
            ("Special Widgets:", "tkcalendar.DateEntry, ttk.Treeview, ttk.Combobox, Spinbox"),
        ]

        for label, val in details:
            row = tk.Frame(left_card, bg=config.CARD_BACKGROUND)
            row.pack(fill="x", pady=2)
            tk.Label(
                row,
                text=label,
                font=config.FONT_BOLD,
                fg=config.PRIMARY_DARK_TEAL,
                bg=config.CARD_BACKGROUND,
                width=18,
                anchor="w"
            ).pack(side="left")
            tk.Label(
                row,
                text=val,
                font=config.FONT_REGULAR,
                fg=config.SECONDARY_TEXT,
                bg=config.CARD_BACKGROUND,
                anchor="w"
            ).pack(side="left")

        # Demo Data Management Section
        tk.Label(
            left_card,
            text="\n🛠️ Presentation & Showcase Tools",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w", pady=(10, 4))

        tk.Label(
            left_card,
            text="Load realistic presentation records (10 donors, 8 stock lines, 6 hospital requests). "
                 "Existing demonstration records will be safely updated.",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND,
            wraplength=380,
            justify="left"
        ).pack(anchor="w", pady=(0, 12))

        ThemedButton(
            left_card,
            text="✨ Reset & Populate Presentation Sample Data",
            btn_type="primary",
            font=config.FONT_BOLD,
            padx=16, pady=8,
            command=self.seed_demo_data
        ).pack(anchor="w")

        # -------------------------------------------------------------
        # RIGHT CARD: ARCHITECTURE & WORKFLOW SUMMARY
        # -------------------------------------------------------------
        right_card = Card(container, bg=config.CARD_BACKGROUND, accent_color=config.COLOR_PRIMARY_CYAN, padx=20, pady=16)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_card.columnconfigure(0, weight=1)
        right_card.rowconfigure(1, weight=1)

        tk.Label(
            right_card,
            text="📖 Workflow & Architecture Summary",
            font=config.FONT_HERO,
            fg=config.COLOR_DARK_NAVY,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            right_card,
            text="Core healthcare operational workflows implemented in this system:",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w", pady=(0, 12))

        guide_text = (
            "1. OVERVIEW & ANALYTICS:\n"
            "   • Real-time KPI summaries computed directly from SQLite tables.\n"
            "   • Multi-level stock alerts (<5 units Low, ≤2 units Critical, >42 days Expired).\n\n"
            "2. DONOR DIRECTORY:\n"
            "   • Captures donor demographics, blood group, Rh factor (+/-), and 10-digit mobile number.\n"
            "   • Regular Expression validation protects contact and data consistency.\n"
            "   • Human-in-the-loop medical eligibility verification.\n\n"
            "3. BLOOD INVENTORY & INTAKE:\n"
            "   • Tracks all eight standard blood groups (A+, A-, B+, B-, AB+, AB-, O+, O-).\n"
            "   • Atomic SQLite Transaction: records donation, advances donor's last donation date, "
            "and increments stock simultaneously with rollback protection.\n\n"
            "4. HOSPITAL REQUISITIONS:\n"
            "   • Emergency requisitions logged and monitored in a unified console.\n"
            "   • Safe Dispensing Logic: only 'Fulfilled' status deducts inventory; "
            "insufficient stock blocks fulfillment; duplicate deductions are prevented; "
            "and stock is restored if a request is cancelled or deleted."
        )

        txt_box = tk.Text(
            right_card,
            wrap="word",
            font=config.FONT_REGULAR,
            fg=config.MAIN_TEXT,
            bg="#F8FAFC",
            relief="solid",
            bd=1,
            padx=12,
            pady=12
        )
        txt_box.insert("1.0", guide_text)
        txt_box.config(state="disabled")
        txt_box.pack(fill="both", expand=True)

    def seed_demo_data(self):
        """Seeds demo data with user confirmation."""
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "This will reset and load realistic presentation records for Donors, Blood Stock, and Hospital Requests.\n\nContinue?",
            icon="question"
        )
        if not confirm:
            return

        try:
            self.db.seed_sample_data(force=True)
            messagebox.showinfo("Success", "Sample presentation data loaded successfully!\nNavigate to Overview to view the live metrics.")
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to seed demo data:\n{str(e)}")


class BloodBankApp(tk.Tk):
    """Main Application Shell Window."""

    def __init__(self):
        super().__init__()
        self.title(f"{config.APP_TITLE} - {config.STUDENT_NAME} ({config.STUDENT_ID})")
        self.geometry("1320x820")
        self.minsize(1100, 700)

        # Base background
        self.configure(bg=config.BACKGROUND)

        # Database Manager
        self.db = DatabaseManager()

        # Configure TTK Styles (Using ttkbootstrap custom theme)
        self._setup_styles()

        # Layout grid: Column 0 = Sidebar, Column 1 = Content
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # State tracking
        self.current_view_name = None
        self.sidebar_buttons = {}
        self.sidebar_indicators = {}

        self._build_sidebar()
        self._build_topbar()
        self._build_content_area()
        self._build_footer()

        # Initial view
        self.show_view("dashboard")

        # Window close handler
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def _setup_styles(self):
        """Initializes ttkbootstrap with custom lifeline theme and modern widget styles."""
        if HAS_TTKBOOTSTRAP:
            try:
                style = tb.Style()
                # Register custom lifeline theme matching exact user color system
                td = ThemeDefinition(
                    name="lifeline",
                    mode="light",
                    colors={
                        "primary": config.COLOR_PRIMARY_CYAN,
                        "secondary": config.SECONDARY_TEXT,
                        "success": config.COLOR_SUCCESS,
                        "info": config.COLOR_PRIMARY_CYAN,
                        "warning": config.COLOR_WARNING,
                        "danger": config.COLOR_MEDICAL_RED,
                        "light": config.COLOR_SOFT_BG,
                        "dark": config.COLOR_DARK_NAVY,
                        "bg": config.COLOR_SOFT_BG,
                        "fg": config.COLOR_MAIN_TEXT,
                        "selectbg": config.COLOR_PRIMARY_CYAN,
                        "selectfg": "#FFFFFF",
                        "border": config.BORDER,
                        "inputfg": config.COLOR_MAIN_TEXT,
                        "inputbg": "#FFFFFF",
                        "active": config.COLOR_DEEP_NAVY
                    }
                )
                style.register_theme(td)
                style.theme_use("lifeline")
            except Exception:
                pass
        else:
            style = ttk.Style()
            try:
                style.theme_use("clam")
            except Exception:
                pass

        # Treeview fine-tuning for modern healthcare SaaS feel
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground=config.COLOR_MAIN_TEXT,
            rowheight=28,
            fieldbackground="#FFFFFF",
            font=config.FONT_REGULAR,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background="#F1F5F9",
            foreground=config.COLOR_DARK_NAVY,
            font=config.FONT_SMALL_BOLD,
            relief="flat",
            padding=6
        )
        style.map(
            "Treeview.Heading",
            background=[("active", config.COLOR_LIGHT_CYAN)]
        )
        style.map(
            "Treeview",
            background=[("selected", config.COLOR_LIGHT_CYAN)],
            foreground=[("selected", config.COLOR_DARK_NAVY)]
        )

        # Notebook tabs
        style.configure(
            "TNotebook",
            background=config.BACKGROUND,
            borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            font=config.FONT_BOLD,
            padding=[14, 8],
            background="#E2E8F0",
            foreground=config.SECONDARY_TEXT
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", config.CARD_BACKGROUND)],
            foreground=[("selected", config.COLOR_PRIMARY_CYAN)]
        )

    def _build_sidebar(self):
        """Constructs modern healthcare navigation sidebar with Dark Navy & Cyan styling."""
        self.sidebar = tk.Frame(self, bg=config.COLOR_DARK_NAVY, width=250)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.columnconfigure(0, weight=1)

        # Brand / Logo Header
        brand_box = tk.Frame(self.sidebar, bg=config.COLOR_DARK_NAVY, padx=20, pady=24)
        brand_box.pack(fill="x")

        brand_row = tk.Frame(brand_box, bg=config.COLOR_DARK_NAVY)
        brand_row.pack(anchor="w")

        tk.Label(
            brand_row,
            text="✚",
            font=("Segoe UI", 18, "bold"),
            fg=config.COLOR_PRIMARY_CYAN,
            bg=config.COLOR_DARK_NAVY
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            brand_row,
            text=config.APP_BRAND,
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg=config.COLOR_DARK_NAVY
        ).pack(side="left")

        tk.Label(
            brand_box,
            text="Blood Bank Management",
            font=config.FONT_SMALL,
            fg=config.COLOR_LIGHT_CYAN,
            bg=config.COLOR_DARK_NAVY
        ).pack(anchor="w", pady=(3, 0))

        # Thin divider
        tk.Frame(self.sidebar, bg=config.COLOR_DEEP_NAVY, height=1).pack(fill="x", padx=18, pady=12)

        # Navigation Items List
        nav_items = [
            ("dashboard", "📊  Overview"),
            ("donors",    "👥  Donor Directory"),
            ("stock",     "🩸  Blood Inventory"),
            ("requests",  "🏥  Hospital Requests"),
            ("about",     "ℹ️   About & Help"),
            ("exit",      "🚪  Exit System")
        ]

        self.nav_frame = tk.Frame(self.sidebar, bg=config.COLOR_DARK_NAVY)
        self.nav_frame.pack(fill="both", expand=True, padx=12, pady=4)

        for key, label in nav_items:
            item_frame = tk.Frame(self.nav_frame, bg=config.COLOR_DARK_NAVY)
            item_frame.pack(fill="x", pady=3)
            item_frame.columnconfigure(1, weight=1)

            # Left active accent indicator line (Cyan)
            indicator = tk.Frame(item_frame, bg=config.COLOR_DARK_NAVY, width=4)
            indicator.grid(row=0, column=0, sticky="ns")
            self.sidebar_indicators[key] = indicator

            btn = tk.Button(
                item_frame,
                text=label,
                font=config.FONT_BOLD,
                fg="#CBD5E1",
                bg=config.COLOR_DARK_NAVY,
                activebackground=config.COLOR_DEEP_NAVY,
                activeforeground="#FFFFFF",
                relief="flat",
                anchor="w",
                padx=14,
                pady=10,
                cursor="hand2",
                command=lambda k=key: self.navigate_to(k)
            )
            btn.grid(row=0, column=1, sticky="ew")
            self.sidebar_buttons[key] = btn

            # Subtle hover effect
            btn.bind("<Enter>", lambda e, k=key: self._on_nav_hover(k, True))
            btn.bind("<Leave>", lambda e, k=key: self._on_nav_hover(k, False))

        # Bottom Student Profile Card
        stud_card = tk.Frame(self.sidebar, bg=config.COLOR_DEEP_NAVY, padx=14, pady=12)
        stud_card.pack(fill="x", side="bottom", padx=14, pady=16)

        tk.Label(
            stud_card,
            text="✚ LIFELINE",
            font=config.FONT_SMALL_BOLD,
            fg=config.COLOR_PRIMARY_CYAN,
            bg=config.COLOR_DEEP_NAVY
        ).pack(anchor="w")

        tk.Label(
            stud_card,
            text=f"{config.STUDENT_NAME}\nID: {config.STUDENT_ID}",
            font=config.FONT_SMALL,
            fg="#94A3B8",
            bg=config.COLOR_DEEP_NAVY,
            justify="left"
        ).pack(anchor="w", pady=(2, 6))

        tk.Label(
            stud_card,
            text="● System Online (SQLite)",
            font=config.FONT_TINY,
            fg=config.COLOR_SUCCESS,
            bg=config.COLOR_DEEP_NAVY
        ).pack(anchor="w")

    def _on_nav_hover(self, key, is_entering):
        """Applies subtle hover transitions to non-active navigation items."""
        if key == self.current_view_name:
            return
        btn = self.sidebar_buttons.get(key)
        if btn:
            if is_entering:
                btn.config(bg=config.COLOR_DEEP_NAVY, fg="#FFFFFF")
            else:
                btn.config(bg=config.COLOR_DARK_NAVY, fg="#CBD5E1")

    def _build_topbar(self):
        """Clean top header bar with page title, clock, and demo actions."""
        self.topbar = tk.Frame(
            self,
            bg=config.CARD_BACKGROUND,
            height=58,
            highlightthickness=1,
            highlightbackground=config.BORDER
        )
        self.topbar.grid(row=0, column=1, sticky="ew")
        self.topbar.columnconfigure(0, weight=1)

        inner = tk.Frame(self.topbar, bg=config.CARD_BACKGROUND, padx=24)
        inner.pack(fill="both", expand=True)

        left_title = tk.Frame(inner, bg=config.CARD_BACKGROUND)
        left_title.pack(side="left")

        self.lbl_top_title = tk.Label(
            left_title,
            text="Overview",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_top_title.pack(anchor="w")

        self.lbl_top_breadcrumb = tk.Label(
            left_title,
            text="Lifeline Blood Bank Operations Console",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_top_breadcrumb.pack(anchor="w")

        # Right side: system status pill, clock and quick demo button
        right_box = tk.Frame(inner, bg=config.CARD_BACKGROUND)
        right_box.pack(side="right")

        self.sys_status_badge = StatusBadge(right_box, text="System Online • SQLite 3", preset="mint")
        self.sys_status_badge.pack(side="left", padx=(0, 14))

        self.lbl_clock = tk.Label(
            right_box,
            text="",
            font=config.FONT_SMALL_BOLD,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_clock.pack(side="left", padx=(0, 14))
        self._update_clock()

        btn_sample = ThemedButton(
            right_box,
            text="✨ Load Demo Data",
            btn_type="outline",
            font=config.FONT_SMALL_BOLD,
            padx=12, pady=4,
            command=self.load_sample_data_dialog
        )
        btn_sample.pack(side="right")

    def _build_content_area(self):
        """Container frame where different views are loaded dynamically."""
        self.content_container = tk.Frame(self, bg=config.BACKGROUND)
        self.content_container.grid(row=1, column=1, sticky="nsew")
        self.content_container.columnconfigure(0, weight=1)
        self.content_container.rowconfigure(0, weight=1)

        # Instantiate modular views
        self.views = {
            "dashboard": DashboardView(self.content_container, self.db, self.show_view),
            "donors":    DonorView(self.content_container, self.db, on_data_changed=self.on_data_modified),
            "stock":     BloodStockView(self.content_container, self.db, on_data_changed=self.on_data_modified),
            "requests":  RequestsView(self.content_container, self.db, on_data_changed=self.on_data_modified),
            "about":     AboutHelpView(self.content_container, self.db, on_data_changed=self.on_data_modified),
        }

    def _build_footer(self):
        """Subtle bottom footer bar."""
        self.footer = tk.Frame(
            self,
            bg=config.CARD_BACKGROUND,
            height=28,
            padx=24,
            highlightthickness=1,
            highlightbackground=config.BORDER
        )
        self.footer.grid(row=2, column=1, sticky="ew")

        tk.Label(
            self.footer,
            text=f"MCA 3rd Semester Mini-Project | Student: {config.STUDENT_NAME} ({config.STUDENT_ID}) | Category: Public Health",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        ).pack(side="left")

        tk.Label(
            self.footer,
            text="Python 3.12 • Tkinter • ttkbootstrap • SQLite 3",
            font=config.FONT_TINY,
            fg=config.PRIMARY_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(side="right")

    def _update_clock(self):
        """Updates clock on top bar every second."""
        now_str = datetime.now().strftime("%I:%M:%S %p | %d %b %Y")
        self.lbl_clock.config(text=now_str)
        self.after(1000, self._update_clock)

    def navigate_to(self, view_name):
        """Handles navigation click."""
        if view_name == "exit":
            self.on_exit()
        else:
            self.show_view(view_name)

    def show_view(self, view_name):
        """Switches active view and updates modern sidebar styling."""
        if view_name not in self.views:
            return

        # Update button and indicator highlights
        for key, btn in self.sidebar_buttons.items():
            indicator = self.sidebar_indicators.get(key)
            if key == view_name:
                btn.config(bg=config.COLOR_DEEP_NAVY, fg=config.COLOR_PRIMARY_CYAN)
                if indicator:
                    indicator.config(bg=config.COLOR_PRIMARY_CYAN)
            else:
                btn.config(bg=config.COLOR_DARK_NAVY, fg="#CBD5E1")
                if indicator:
                    indicator.config(bg=config.COLOR_DARK_NAVY)

        # Hide current view
        for v in self.views.values():
            v.pack_forget()

        # Show target view
        target_view = self.views[view_name]
        target_view.pack(fill="both", expand=True)
        self.current_view_name = view_name

        # Update top bar titles & breadcrumbs
        titles = {
            "dashboard": ("Overview", "Executive Dashboard & Live Stock Indicators"),
            "donors":    ("Donor Directory", "Register, search and manage blood donors"),
            "stock":     ("Blood Inventory", "Monitor available blood units and record new donations"),
            "requests":  ("Hospital Blood Requests", "Manage emergency blood requirements from hospitals"),
            "about":     ("About & Help", "Project Information & Healthcare Workflow Guide")
        }
        title_info = titles.get(view_name, (config.APP_TITLE, "Lifeline Console"))
        self.lbl_top_title.config(text=title_info[0])
        self.lbl_top_breadcrumb.config(text=title_info[1])

        # Auto-refresh data on view switch
        if hasattr(target_view, "refresh"):
            target_view.refresh()
        elif hasattr(target_view, "refresh_stock"):
            target_view.refresh_stock()
        elif hasattr(target_view, "load_donors"):
            target_view.load_donors()
        elif hasattr(target_view, "load_requests"):
            target_view.load_requests()

    def on_data_modified(self):
        """Callback invoked when database records are modified by any view."""
        dashboard = self.views.get("dashboard")
        if dashboard and hasattr(dashboard, "refresh"):
            dashboard.refresh()

        stock_view = self.views.get("stock")
        if stock_view and hasattr(stock_view, "refresh_stock"):
            stock_view.refresh_stock()

    def load_sample_data_dialog(self):
        """Allows loading demo data with user confirmation."""
        confirm = messagebox.askyesno(
            "Load Presentation Demo Records",
            "This will populate realistic demo records (10 donors, 8 stock lines, 6 hospital requests).\n\nContinue?",
            icon="question"
        )
        if not confirm:
            return

        try:
            self.db.seed_sample_data(force=True)
            self.on_data_modified()
            self.show_view("dashboard")
            messagebox.showinfo("Success", "Presentation records loaded successfully!\nOverview dashboard updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to seed demo data:\n{str(e)}")

    def on_exit(self):
        """Prompts before closing application."""
        if messagebox.askyesno("Exit Application", "Are you sure you want to close LIFELINE Blood Bank System?", icon="question"):
            self.destroy()


def main():
    """Application launcher."""
    app = BloodBankApp()
    app.mainloop()


if __name__ == "__main__":
    main()
