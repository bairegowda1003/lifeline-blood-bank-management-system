"""
Executive Dashboard View Module
Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)
Healthcare SaaS-inspired dashboard featuring live KPI cards, unclipped 8-group inventory matrix
with visual progress indicators, smart alert banners, and recent activity feeds.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import config
from ui_components import Card, StatusBadge, ThemedButton, StockProgressBar


class DashboardView(tk.Frame):
    """Refined healthcare analytics dashboard with live SQLite metrics, progress bars, and clean layout."""

    def __init__(self, parent, db_manager, navigate_callback):
        super().__init__(parent, bg=config.BACKGROUND)
        self.db = db_manager
        self.navigate = navigate_callback

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self._build_header()
        self._build_kpi_cards()
        self._build_alerts_section()
        self._build_main_content()

        # Load live database metrics
        self.refresh()

    def _build_header(self):
        """Top greeting banner and quick refresh action."""
        hdr_card = Card(self, bg=config.CARD_BACKGROUND, padx=16, pady=6)
        hdr_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(8, 4))
        hdr_card.columnconfigure(0, weight=1)

        left_box = tk.Frame(hdr_card, bg=config.CARD_BACKGROUND)
        left_box.grid(row=0, column=0, sticky="w")

        lbl_greet = tk.Label(
            left_box,
            text=f"Good morning, {config.STUDENT_NAME.split()[0]}!",
            font=config.FONT_TITLE,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        )
        lbl_greet.pack(anchor="w")

        lbl_sub = tk.Label(
            left_box,
            text="Welcome to Lifeline Blood Bank Management. Here's your inventory and operations overview.",
            font=config.FONT_SMALL,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        )
        lbl_sub.pack(anchor="w", pady=(1, 0))

        btn_refresh = ThemedButton(
            hdr_card,
            text="🔄  Refresh Overview",
            btn_type="primary",
            font=config.FONT_SMALL_BOLD,
            padx=14,
            pady=4,
            command=self.refresh
        )
        btn_refresh.grid(row=0, column=1, sticky="e")

    def _build_kpi_cards(self):
        """Builds 4 healthcare SaaS-style live statistic cards with compact vertical footprint."""
        cards_frame = tk.Frame(self, bg=config.BACKGROUND)
        cards_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 4))
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1, uniform="kpi_col")

        # Card 1: Total Registered Donors
        self.card_donors, self.val_donors, self.badge_donors = self._create_kpi_card(
            cards_frame, 0,
            title="TOTAL REGISTERED DONORS",
            icon="👥",
            icon_bg=config.TINT_INFO_LIGHT,
            icon_fg=config.COLOR_INFO,
            initial_val="0",
            initial_sub="Active in directory"
        )

        # Card 2: Available Blood Units
        self.card_units, self.val_units, self.badge_units = self._create_kpi_card(
            cards_frame, 1,
            title="AVAILABLE BLOOD UNITS",
            icon="🩸",
            icon_bg=config.TINT_MINT_LIGHT,
            icon_fg=config.PRIMARY_TEAL,
            initial_val="0",
            initial_sub="Tested & Usable RBC"
        )

        # Card 3: Pending Hospital Requests
        self.card_reqs, self.val_reqs, self.badge_reqs = self._create_kpi_card(
            cards_frame, 2,
            title="PENDING REQUESTS",
            icon="⏳",
            icon_bg=config.TINT_WARNING_LIGHT,
            icon_fg=config.COLOR_WARNING,
            initial_val="0",
            initial_sub="Awaiting fulfillment"
        )

        # Card 4: Blood Groups Available
        self.card_groups, self.val_groups, self.badge_groups = self._create_kpi_card(
            cards_frame, 3,
            title="BLOOD GROUPS IN STOCK",
            icon="🏥",
            icon_bg=config.TINT_SUCCESS_LIGHT,
            icon_fg=config.COLOR_SUCCESS,
            initial_val="0 / 8",
            initial_sub="Types with active stock"
        )

    def _create_kpi_card(self, parent, col, title, icon, icon_bg, icon_fg,
                          initial_val, initial_sub):
        """Constructs an individual KPI summary card with subtle top accent line."""
        card = Card(parent, bg=config.CARD_BACKGROUND, padx=14, pady=8)
        card.grid(row=0, column=col, sticky="nsew", padx=4)
        card.columnconfigure(0, weight=1)

        # Superdesign subtle top accent line
        tk.Frame(card, bg=icon_fg, height=3).pack(fill="x", pady=(0, 6))

        # Top row: Title and Icon
        top_row = tk.Frame(card, bg=config.CARD_BACKGROUND)
        top_row.pack(fill="x")

        lbl_title = tk.Label(
            top_row,
            text=title,
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        )
        lbl_title.pack(side="left")

        lbl_icon = tk.Label(
            top_row,
            text=icon,
            font=("Segoe UI", 11),
            bg=icon_bg,
            fg=icon_fg,
            width=2,
            pady=1
        )
        lbl_icon.pack(side="right")

        # Value
        val_lbl = tk.Label(
            card,
            text=initial_val,
            font=("Segoe UI", 18, "bold"),
            fg=config.MAIN_TEXT,
            bg=config.CARD_BACKGROUND
        )
        val_lbl.pack(anchor="w", pady=(2, 1))

        # Bottom Subtitle/Badge
        sub_lbl = tk.Label(
            card,
            text=f"● {initial_sub}",
            font=config.FONT_TINY,
            fg=config.PRIMARY_TEAL,
            bg=config.CARD_BACKGROUND
        )
        sub_lbl.pack(anchor="w")

        return card, val_lbl, sub_lbl

    def _build_alerts_section(self):
        """Banner container for low-stock and expiry notifications."""
        self.alerts_frame = tk.Frame(self, bg=config.BACKGROUND)
        self.alerts_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 6))
        self.alerts_frame.columnconfigure(0, weight=1)

    def _build_main_content(self):
        """Two-column bottom layout: Inventory Matrix (Left) + Activity Feeds (Right)."""
        content = tk.Frame(self, bg=config.BACKGROUND)
        content.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 10))
        content.columnconfigure(0, weight=5)  # Left: Blood Stock Matrix
        content.columnconfigure(1, weight=5)  # Right: Recent Feeds
        content.rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT PANE: BLOOD INVENTORY MATRIX (8 GROUPS)
        # -------------------------------------------------------------
        stock_card = Card(content, bg=config.CARD_BACKGROUND, padx=14, pady=10)
        stock_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        stock_card.rowconfigure(1, weight=1)
        stock_card.columnconfigure(0, weight=1)

        # Header of Left Card
        stock_hdr = tk.Frame(stock_card, bg=config.CARD_BACKGROUND)
        stock_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        stock_hdr.columnconfigure(0, weight=1)

        left_hdr = tk.Frame(stock_hdr, bg=config.CARD_BACKGROUND)
        left_hdr.pack(side="left")

        tk.Label(
            left_hdr,
            text="Blood Inventory Status",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w")

        tk.Label(
            left_hdr,
            text="Live capacity & batch health across all 8 standard blood groups",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w")

        btn_go_stock = ThemedButton(
            stock_hdr,
            text="Manage Stock ➔",
            btn_type="outline",
            font=config.FONT_TINY,
            padx=8,
            pady=3,
            command=lambda: self.navigate("stock")
        )
        btn_go_stock.pack(side="right")

        # Container for the 8 Blood Group Tiles (2 columns x 4 rows)
        self.grid_container = tk.Frame(stock_card, bg=config.CARD_BACKGROUND)
        self.grid_container.grid(row=1, column=0, sticky="nsew")
        for c in range(2):
            self.grid_container.columnconfigure(c, weight=1, uniform="tile_col")
        for r in range(4):
            self.grid_container.rowconfigure(r, weight=1)

        # -------------------------------------------------------------
        # RIGHT PANE: TWO SEPARATE RECENT ACTIVITY CARDS
        # -------------------------------------------------------------
        right_panel = tk.Frame(content, bg=config.BACKGROUND)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        # Card 1: Recent Donor Registrations
        donors_box = Card(right_panel, bg=config.CARD_BACKGROUND, padx=12, pady=8)
        donors_box.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        donors_box.rowconfigure(1, weight=1)
        donors_box.columnconfigure(0, weight=1)

        d_hdr = tk.Frame(donors_box, bg=config.CARD_BACKGROUND)
        d_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        tk.Label(
            d_hdr,
            text="Recent Donor Registrations",
            font=config.FONT_SUBHEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(side="left")

        ThemedButton(
            d_hdr,
            text="View All ➔",
            btn_type="outline",
            font=config.FONT_TINY,
            padx=7,
            pady=2,
            command=lambda: self.navigate("donors")
        ).pack(side="right")

        # Treeview for Donors
        self.tree_recent_donors = ttk.Treeview(
            donors_box,
            columns=("name", "group", "phone", "eligibility"),
            show="headings",
            height=3
        )
        self.tree_recent_donors.heading("name", text="Donor Name")
        self.tree_recent_donors.heading("group", text="Group")
        self.tree_recent_donors.heading("phone", text="Phone")
        self.tree_recent_donors.heading("eligibility", text="Status")

        self.tree_recent_donors.column("name", width=140, anchor="w")
        self.tree_recent_donors.column("group", width=55, anchor="center")
        self.tree_recent_donors.column("phone", width=105, anchor="center")
        self.tree_recent_donors.column("eligibility", width=95, anchor="center")
        self.tree_recent_donors.grid(row=1, column=0, sticky="nsew")

        # Card 2: Recent Hospital Requests
        reqs_box = Card(right_panel, bg=config.CARD_BACKGROUND, padx=12, pady=8)
        reqs_box.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        reqs_box.rowconfigure(1, weight=1)
        reqs_box.columnconfigure(0, weight=1)

        r_hdr = tk.Frame(reqs_box, bg=config.CARD_BACKGROUND)
        r_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        tk.Label(
            r_hdr,
            text="Recent Hospital Requisitions",
            font=config.FONT_SUBHEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(side="left")

        ThemedButton(
            r_hdr,
            text="View All ➔",
            btn_type="outline",
            font=config.FONT_TINY,
            padx=7,
            pady=2,
            command=lambda: self.navigate("requests")
        ).pack(side="right")

        # Treeview for Requests
        self.tree_recent_requests = ttk.Treeview(
            reqs_box,
            columns=("hospital", "group", "units", "status"),
            show="headings",
            height=3
        )
        self.tree_recent_requests.heading("hospital", text="Hospital Name")
        self.tree_recent_requests.heading("group", text="Group")
        self.tree_recent_requests.heading("units", text="Units")
        self.tree_recent_requests.heading("status", text="Status")

        self.tree_recent_requests.column("hospital", width=160, anchor="w")
        self.tree_recent_requests.column("group", width=55, anchor="center")
        self.tree_recent_requests.column("units", width=65, anchor="center")
        self.tree_recent_requests.column("status", width=90, anchor="center")
        self.tree_recent_requests.grid(row=1, column=0, sticky="nsew")

        r_hdr = tk.Frame(reqs_box, bg=config.CARD_BACKGROUND)
        r_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        tk.Label(
            r_hdr,
            text="Recent Hospital Requisitions",
            font=config.FONT_SUBHEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(side="left")

        ThemedButton(
            r_hdr,
            text="View All ➔",
            btn_type="outline",
            font=config.FONT_TINY,
            padx=7,
            pady=2,
            command=lambda: self.navigate("requests")
        ).pack(side="right")

        # Treeview for Requests
        self.tree_recent_requests = ttk.Treeview(
            reqs_box,
            columns=("hospital", "group", "units", "status"),
            show="headings",
            height=3
        )
        self.tree_recent_requests.heading("hospital", text="Hospital Name")
        self.tree_recent_requests.heading("group", text="Group")
        self.tree_recent_requests.heading("units", text="Units")
        self.tree_recent_requests.heading("status", text="Status")

        self.tree_recent_requests.column("hospital", width=160, anchor="w")
        self.tree_recent_requests.column("group", width=55, anchor="center")
        self.tree_recent_requests.column("units", width=65, anchor="center")
        self.tree_recent_requests.column("status", width=90, anchor="center")
        self.tree_recent_requests.grid(row=1, column=0, sticky="nsew")

    def refresh(self):
        """Fetches live SQLite statistics and populates all widgets without clipping or duplication."""
        try:
            stats = self.db.get_dashboard_stats()
        except Exception as e:
            messagebox.showerror("System Error", f"Could not load dashboard statistics:\n{str(e)}")
            return

        # 1. Update KPI Values
        self.val_donors.config(text=f"{stats['total_donors']}")
        self.badge_donors.config(text=f"● {stats['eligible_donors']} Eligible Donors Verified")

        self.val_units.config(text=f"{stats['total_blood_units']} Units")
        self.badge_units.config(text=f"● Tested RBC Units in Bank")

        self.val_reqs.config(text=f"{stats['pending_requests']} Pending")
        if stats['pending_requests'] > 0:
            self.badge_reqs.config(text=f"● Action Required Immediately", fg=config.COLOR_WARNING)
        else:
            self.badge_reqs.config(text=f"● All Requisitions Addressed", fg=config.COLOR_SUCCESS)

        self.val_groups.config(text=f"{stats['groups_available']} / 8")
        self.badge_groups.config(text=f"● Active Blood Groups in Stock", fg=config.PRIMARY_TEAL)

        # 2. Render Alert Banners
        for w in self.alerts_frame.winfo_children():
            w.destroy()

        if stats["low_stock_alerts"]:
            crit = [a["blood_group"] for a in stats["low_stock_alerts"] if a["status"] == "CRITICAL"]
            low = [a["blood_group"] for a in stats["low_stock_alerts"] if a["status"] == "LOW"]
            parts = []
            if crit: parts.append(f"Critical Shortage (≤2 units): {', '.join(crit)}")
            if low: parts.append(f"Low Supply (<5 units): {', '.join(low)}")

            alert_card = Card(
                self.alerts_frame,
                bg=config.TINT_WARNING_LIGHT,
                border_color=config.COLOR_WARNING,
                padx=12, pady=6
            )
            alert_card.pack(fill="x", pady=2)
            tk.Label(
                alert_card,
                text="⚠️  Inventory Alert: " + " | ".join(parts),
                font=config.FONT_BOLD,
                fg=config.COLOR_WARNING,
                bg=config.TINT_WARNING_LIGHT
            ).pack(side="left")

        if stats["expiry_alerts"]:
            exp_text = ", ".join([f"{a['blood_group']} ({a['units']}u - {a['status']})" for a in stats["expiry_alerts"]])
            exp_card = Card(
                self.alerts_frame,
                bg=config.TINT_DANGER_LIGHT,
                border_color=config.COLOR_DANGER,
                padx=12, pady=6
            )
            exp_card.pack(fill="x", pady=2)
            tk.Label(
                exp_card,
                text="⏳  Shelf-Life Notice: " + exp_text,
                font=config.FONT_BOLD,
                fg=config.COLOR_DANGER,
                bg=config.TINT_DANGER_LIGHT
            ).pack(side="left")

        # 3. Render 8 Blood Group Inventory Tiles with Clean Vertical Structure (ZERO CLIPPING)
        for w in self.grid_container.winfo_children():
            w.destroy()

        stock_rows = stats["stock_rows"]
        row_idx = 0
        col_idx = 0

        for item in stock_rows:
            bg_name = item["blood_group"]
            units = item["units_available"]
            exp = item["expiry_date"]

            # Expiry check
            is_expired = False
            if exp:
                try:
                    if datetime.strptime(exp, "%Y-%m-%d").date() < date.today():
                        is_expired = True
                except ValueError:
                    pass

            if is_expired:
                status_preset = "danger"
                status_label = "EXPIRED"
                bar_color = config.COLOR_DANGER
            elif units <= config.CRITICAL_STOCK_THRESHOLD:
                status_preset = "danger"
                status_label = "CRITICAL"
                bar_color = config.COLOR_DANGER
            elif units < config.LOW_STOCK_THRESHOLD:
                status_preset = "warning"
                status_label = "LOW STOCK"
                bar_color = config.COLOR_WARNING
            else:
                status_preset = "success"
                status_label = "OPTIMAL"
                bar_color = config.COLOR_SUCCESS

            tile = Card(
                self.grid_container,
                bg="#FAFAFA",
                border_color=config.BORDER,
                padx=8, pady=5
            )
            tile.grid(row=row_idx, column=col_idx, sticky="nsew", padx=4, pady=2)
            tile.columnconfigure(0, weight=1)

            # Row 1: Header (Left: Blood Group Emblem; Right: Status Badge)
            row_top = tk.Frame(tile, bg="#FAFAFA")
            row_top.pack(fill="x", anchor="w")

            emblem = tk.Label(
                row_top,
                text=f" {bg_name} ",
                font=config.FONT_BOLD,
                fg=config.PRIMARY_DARK_TEAL,
                bg=config.TINT_MINT_LIGHT,
                padx=3,
                pady=1
            )
            emblem.pack(side="left")

            tk.Label(
                row_top,
                text=" Group",
                font=config.FONT_TINY,
                fg=config.SECONDARY_TEXT,
                bg="#FAFAFA"
            ).pack(side="left")

            StatusBadge(row_top, text=status_label, preset=status_preset).pack(side="right")

            # Row 2: Units Metric
            lbl_u = tk.Label(
                tile,
                text=f"{units} Units Available",
                font=config.FONT_BOLD,
                fg=config.MAIN_TEXT,
                bg="#FAFAFA"
            )
            lbl_u.pack(anchor="w", pady=(2, 1))

            # Row 3: Visual Progress Bar (Capacity against 25 units benchmark)
            pbar = StockProgressBar(tile, value=units, max_value=25, color=bar_color, height=4)
            pbar.pack(fill="x", pady=(1, 2))

            # Row 4: Dedicated Batch Expiry Line (No horizontal squeeze or clipping)
            lbl_exp = tk.Label(
                tile,
                text=f"📅 Batch Exp: {exp or 'Not Set'}",
                font=config.FONT_TINY,
                fg=config.SECONDARY_TEXT,
                bg="#FAFAFA"
            )
            lbl_exp.pack(anchor="w")

            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

        # 4. Populate Recent Donors Table (Distinct latest 5)
        for item in self.tree_recent_donors.get_children():
            self.tree_recent_donors.delete(item)
        for donor in stats["recent_donors"]:
            self.tree_recent_donors.insert("", "end", values=(
                donor["name"],
                donor["blood_group"],
                donor["phone"],
                donor["eligibility"]
            ))

        # 5. Populate Recent Requests Table (Distinct latest 5)
        for item in self.tree_recent_requests.get_children():
            self.tree_recent_requests.delete(item)
        for req in stats["recent_requests"]:
            self.tree_recent_requests.insert("", "end", values=(
                req["hospital_name"],
                req["blood_group"],
                f"{req['units_needed']} units",
                req["req_status"]
            ))
