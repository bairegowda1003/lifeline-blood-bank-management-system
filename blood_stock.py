"""
Blood Inventory Management View Module
Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)
Healthcare SaaS-inspired inventory tracking for all 8 standard blood groups,
atomic donation intake, batch shelf-life monitoring, and stock registers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
import tkcalendar

import config
import validators
from ui_components import Card, StatusBadge, ThemedButton, FormFieldWrapper, StockProgressBar


class BloodStockView(tk.Frame):
    """Modern blood inventory interface with 8-group KPI cards, transactional intake, and registers."""

    def __init__(self, parent, db_manager, on_data_changed=None):
        super().__init__(parent, bg=config.BACKGROUND)
        self.db = db_manager
        self.on_data_changed = on_data_changed
        self.selected_stock_id = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_header()
        self._build_stock_summary_cards()
        self._build_operations_and_table()
        self.refresh_stock()

    def _build_header(self):
        """Top section header and quick refresh action."""
        hdr_card = Card(self, bg=config.CARD_BACKGROUND, padx=16, pady=8)
        hdr_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 6))
        hdr_card.columnconfigure(0, weight=1)

        title_box = tk.Frame(hdr_card, bg=config.CARD_BACKGROUND)
        title_box.grid(row=0, column=0, sticky="w")

        tk.Label(
            title_box,
            text="Blood Inventory",
            font=config.FONT_TITLE,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="Monitor available blood units and record new donations.",
            font=config.FONT_SMALL,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w", pady=(1, 0))

        ThemedButton(
            hdr_card,
            text="🔄 Refresh Inventory",
            btn_type="primary",
            font=config.FONT_SMALL_BOLD,
            padx=12, pady=4,
            command=self.refresh_stock
        ).grid(row=0, column=1, sticky="e")

    def _build_stock_summary_cards(self):
        """8 live summary cards representing all 8 blood groups."""
        self.tiles_frame = tk.Frame(self, bg=config.BACKGROUND)
        self.tiles_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))
        for col in range(8):
            self.tiles_frame.columnconfigure(col, weight=1, uniform="tile_col")

    def _build_operations_and_table(self):
        """Lower split layout: Left has Donation Intake & Adjustment; Right has Table Register."""
        content = tk.Frame(self, bg=config.BACKGROUND)
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        content.columnconfigure(0, weight=4)  # Left Operations Panel
        content.columnconfigure(1, weight=6)  # Right Table Register
        content.rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT: NOTEBOOK WITH TWO TABS (Donation Intake vs Adjustment)
        # -------------------------------------------------------------
        ops_notebook = ttk.Notebook(content)
        ops_notebook.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Tab 1: Record Donation Intake
        self.tab_donation = tk.Frame(ops_notebook, bg=config.CARD_BACKGROUND, padx=16, pady=12)
        ops_notebook.add(self.tab_donation, text=" Record Donation Intake ")
        self._build_donation_tab(self.tab_donation)

        # Tab 2: Direct Stock Update
        self.tab_adjust = tk.Frame(ops_notebook, bg=config.CARD_BACKGROUND, padx=16, pady=12)
        ops_notebook.add(self.tab_adjust, text=" Direct Stock Update ")
        self._build_adjustment_tab(self.tab_adjust)

        # -------------------------------------------------------------
        # RIGHT: INVENTORY REGISTER & FILTERS
        # -------------------------------------------------------------
        table_card = Card(content, bg=config.CARD_BACKGROUND, padx=16, pady=14)
        table_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(2, weight=1)

        # Register Header
        tbl_hdr = tk.Frame(table_card, bg=config.CARD_BACKGROUND)
        tbl_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tk.Label(
            tbl_hdr,
            text="Inventory Register Log",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(side="left")

        # Filters Bar
        flt_bar = tk.Frame(table_card, bg="#F8FAFC", padx=10, pady=6)
        flt_bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        tk.Label(
            flt_bar,
            text="Filter Register:",
            font=config.FONT_SMALL_BOLD,
            fg=config.MAIN_TEXT,
            bg="#F8FAFC"
        ).pack(side="left", padx=(0, 8))

        self.var_filter = tk.StringVar(value="All")

        for f_label, f_val in [("All Groups", "All"), ("Low Stock (<5)", "Low"), ("Expiring/Expired", "Expiry")]:
            rb = ttk.Radiobutton(
                flt_bar,
                text=f_label,
                variable=self.var_filter,
                value=f_val,
                command=self.filter_table
            )
            rb.pack(side="left", padx=8)

        # Treeview
        tree_container = tk.Frame(table_card, bg=config.CARD_BACKGROUND)
        tree_container.grid(row=2, column=0, sticky="nsew")
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        cols = ("id", "blood_group", "units", "expiry", "status")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="Stock ID")
        self.tree.heading("blood_group", text="Blood Group")
        self.tree.heading("units", text="Available Units")
        self.tree.heading("expiry", text="Batch Expiry")
        self.tree.heading("status", text="Stock Health")

        self.tree.column("id", width=65, anchor="center")
        self.tree.column("blood_group", width=95, anchor="center")
        self.tree.column("units", width=110, anchor="center")
        self.tree.column("expiry", width=115, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_stock_row_select)

    def _build_donation_tab(self, parent):
        """Constructs transactional donation intake form linking donor to blood stock."""
        parent.columnconfigure(0, weight=1)

        tk.Label(
            parent,
            text="Record Donor Blood Donation",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w", pady=(0, 2))

        # Workflow note
        note_box = tk.Frame(parent, bg="#F0FDFA", padx=10, pady=8, highlightbackground="#99F6E4", highlightthickness=1)
        note_box.pack(fill="x", pady=(0, 12))

        tk.Label(
            note_box,
            text="ℹ️  ACID Transaction Guarantee:\n"
                 "Recording a donation atomically increments blood units in stock "
                 "and updates the donor's last donation date together in SQLite.",
            font=config.FONT_TINY,
            fg=config.PRIMARY_DARK_TEAL,
            bg="#F0FDFA",
            justify="left",
            wraplength=340
        ).pack(anchor="w")

        # 1. Select Donor
        FormFieldWrapper(parent, label="Select Registered Donor", required=True).pack(anchor="w", pady=(4, 2))
        self.combo_donors = ttk.Combobox(parent, state="readonly", font=config.FONT_REGULAR)
        self.combo_donors.pack(fill="x", pady=(0, 4))
        self.combo_donors.bind("<<ComboboxSelected>>", self.on_donation_donor_selected)

        # Selected Donor Live Badge
        self.lbl_donor_preview = tk.Label(
            parent,
            text="● Donor: Please select a donor from list",
            font=config.FONT_SMALL,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_donor_preview.pack(anchor="w", pady=(0, 8))

        # 2. Units Donated (Spinbox)
        FormFieldWrapper(parent, label="Units Donated (1-10 Units)", required=True).pack(anchor="w", pady=(4, 2))
        self.spin_donation_units = tk.Spinbox(
            parent,
            from_=1,
            to=10,
            font=config.FONT_REGULAR,
            width=10,
            relief="solid",
            bd=1
        )
        self.spin_donation_units.pack(anchor="w", pady=(0, 8))

        # 3. Donation Date (DateEntry)
        FormFieldWrapper(parent, label="Donation Date", required=True).pack(anchor="w", pady=(4, 2))
        self.date_donation = tkcalendar.DateEntry(
            parent,
            date_pattern="yyyy-mm-dd",
            maxdate=date.today(),
            font=config.FONT_REGULAR,
            background=config.PRIMARY_DARK_TEAL,
            foreground="white"
        )
        self.date_donation.pack(fill="x", pady=(0, 8))

        # 4. Computed Expiry Date (DateEntry - default +42 days)
        FormFieldWrapper(parent, label="Batch Expiry Date", required=True, helper="Auto-calculated (42 days RBC shelf life)").pack(anchor="w", pady=(4, 2))
        default_exp = date.today() + timedelta(days=config.SHELF_LIFE_DAYS)
        self.date_expiry = tkcalendar.DateEntry(
            parent,
            date_pattern="yyyy-mm-dd",
            mindate=date.today(),
            font=config.FONT_REGULAR,
            background=config.PRIMARY_DARK_TEAL,
            foreground="white"
        )
        self.date_expiry.set_date(default_exp)
        self.date_expiry.pack(fill="x", pady=(0, 16))

        ThemedButton(
            parent,
            text="💉 Record Donation & Update Inventory",
            btn_type="primary",
            font=config.FONT_BOLD,
            pady=9,
            command=self.submit_donation
        ).pack(fill="x")

    def _build_adjustment_tab(self, parent):
        """Constructs direct stock adjustment form."""
        parent.columnconfigure(0, weight=1)

        tk.Label(
            parent,
            text="Direct Stock / Expiry Adjustment",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w", pady=(0, 2))

        self.lbl_selected_stock = tk.Label(
            parent,
            text="Click a row in the table to load its current stock details.",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_selected_stock.pack(anchor="w", pady=(0, 12))

        # 1. Blood Group
        FormFieldWrapper(parent, label="Blood Group", required=True).pack(anchor="w", pady=(4, 2))
        self.combo_adjust_bg = ttk.Combobox(
            parent,
            values=config.BLOOD_GROUPS,
            state="readonly",
            font=config.FONT_REGULAR
        )
        self.combo_adjust_bg.set(config.BLOOD_GROUPS[0])
        self.combo_adjust_bg.pack(fill="x", pady=(0, 8))
        self.combo_adjust_bg.bind("<<ComboboxSelected>>", self.on_adjust_group_selected)

        # 2. Total Units (Spinbox)
        FormFieldWrapper(parent, label="Total Usable Units in Bank", required=True).pack(anchor="w", pady=(4, 2))
        self.spin_adjust_units = tk.Spinbox(
            parent,
            from_=0,
            to=500,
            font=config.FONT_REGULAR,
            width=10,
            relief="solid",
            bd=1
        )
        self.spin_adjust_units.pack(anchor="w", pady=(0, 8))

        # 3. Expiry Date
        FormFieldWrapper(parent, label="Batch Expiry Date", required=True).pack(anchor="w", pady=(4, 2))
        self.date_adjust_expiry = tkcalendar.DateEntry(
            parent,
            date_pattern="yyyy-mm-dd",
            font=config.FONT_REGULAR,
            background=config.PRIMARY_DARK_TEAL,
            foreground="white"
        )
        self.date_adjust_expiry.pack(fill="x", pady=(0, 18))

        ThemedButton(
            parent,
            text="💾 Save Stock Changes",
            btn_type="outline",
            font=config.FONT_BOLD,
            pady=9,
            command=self.submit_adjustment
        ).pack(fill="x")

    def refresh_stock(self):
        """Reloads all stock data, rebuilds top cards, and refreshes the table."""
        all_donors = self.db.get_all_donors()
        self.donor_map = {}
        donor_options = []
        for d in all_donors:
            label = f"#{d['donor_id']} - {d['name']} ({d['blood_group']})"
            donor_options.append(label)
            self.donor_map[label] = d

        self.combo_donors["values"] = donor_options
        if donor_options:
            self.combo_donors.set(donor_options[0])
            self.on_donation_donor_selected(None)

        # Rebuild Top Stock Tiles
        for w in self.tiles_frame.winfo_children():
            w.destroy()

        stock_rows = self.db.get_all_stock()
        stock_dict = {r["blood_group"]: r for r in stock_rows}

        col_idx = 0
        for bg in config.BLOOD_GROUPS:
            item = stock_dict.get(bg)
            units = item["units_available"] if item else 0
            exp = item["expiry_date"] if item else None

            is_expired = False
            if exp:
                try:
                    if datetime.strptime(exp, "%Y-%m-%d").date() < date.today():
                        is_expired = True
                except ValueError:
                    pass

            if is_expired:
                badge_preset = "danger"
                status_name = "EXPIRED"
                bar_color = config.COLOR_DANGER
            elif units <= config.CRITICAL_STOCK_THRESHOLD:
                badge_preset = "danger"
                status_name = "CRITICAL"
                bar_color = config.COLOR_DANGER
            elif units < config.LOW_STOCK_THRESHOLD:
                badge_preset = "warning"
                status_name = "LOW"
                bar_color = config.COLOR_WARNING
            else:
                badge_preset = "success"
                status_name = "OPTIMAL"
                bar_color = config.COLOR_SUCCESS

            tile = Card(
                self.tiles_frame,
                bg=config.CARD_BACKGROUND,
                border_color=config.BORDER,
                padx=6, pady=7
            )
            tile.grid(row=0, column=col_idx, sticky="nsew", padx=3)
            tile.columnconfigure(0, weight=1)

            lbl_bg = tk.Label(
                tile,
                text=bg,
                font=config.FONT_HEADER,
                fg=config.PRIMARY_DARK_TEAL,
                bg=config.CARD_BACKGROUND
            )
            lbl_bg.pack()

            lbl_u = tk.Label(
                tile,
                text=f"{units} u",
                font=config.FONT_TITLE,
                fg=config.MAIN_TEXT,
                bg=config.CARD_BACKGROUND
            )
            lbl_u.pack(pady=(1, 0))

            pbar = StockProgressBar(tile, value=units, max_value=25, color=bar_color, height=4)
            pbar.pack(fill="x", padx=4, pady=(3, 3))

            StatusBadge(tile, text=status_name, preset=badge_preset).pack()

            col_idx += 1

        self.filter_table()

    def filter_table(self):
        """Applies radio button filter to Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        filter_mode = self.var_filter.get()
        stock_rows = self.db.get_all_stock()

        for item in stock_rows:
            units = item["units_available"]
            exp = item["expiry_date"]
            is_expired = False
            is_soon = False
            if exp:
                try:
                    exp_dt = datetime.strptime(exp, "%Y-%m-%d").date()
                    if exp_dt < date.today():
                        is_expired = True
                    elif exp_dt <= date.today() + timedelta(days=config.EXPIRY_WARN_DAYS):
                        is_soon = True
                except ValueError:
                    pass

            if is_expired:
                status = "EXPIRED"
            elif units <= config.CRITICAL_STOCK_THRESHOLD:
                status = "CRITICAL"
            elif units < config.LOW_STOCK_THRESHOLD:
                status = "LOW STOCK"
            elif is_soon:
                status = "EXPIRING SOON"
            else:
                status = "OPTIMAL"

            if filter_mode == "Low" and units >= config.LOW_STOCK_THRESHOLD:
                continue
            if filter_mode == "Expiry" and not (is_expired or is_soon):
                continue

            self.tree.insert("", "end", values=(
                item["stock_id"],
                item["blood_group"],
                f"{units} units",
                exp or "N/A",
                status
            ))

    def on_donation_donor_selected(self, event):
        """Updates preview when donor selection changes in donation form."""
        sel = self.combo_donors.get()
        donor = self.donor_map.get(sel)
        if donor:
            self.lbl_donor_preview.config(
                text=f"● {donor['name']} | Blood Group: {donor['blood_group']} | Status: {donor['eligibility']}",
                fg=config.PRIMARY_TEAL
            )

    def on_stock_row_select(self, event):
        """Populates direct adjustment form when a table row is clicked."""
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0], "values")
        if not vals:
            return

        stock_id, bg, units_str, exp_str, status = vals
        self.selected_stock_id = int(stock_id)

        try:
            units_int = int(units_str.replace("units", "").strip())
        except ValueError:
            units_int = 0

        self.combo_adjust_bg.set(bg)
        self.spin_adjust_units.delete(0, tk.END)
        self.spin_adjust_units.insert(0, str(units_int))

        if exp_str and exp_str != "N/A":
            try:
                exp_dt = datetime.strptime(exp_str, "%Y-%m-%d").date()
                self.date_adjust_expiry.set_date(exp_dt)
            except Exception:
                pass

        self.lbl_selected_stock.config(
            text=f"Loaded Record #{self.selected_stock_id} for Group {bg} ({units_int} units).",
            fg=config.COLOR_INFO
        )

    def on_adjust_group_selected(self, event):
        """Loads existing stock values when blood group dropdown is changed in adjustment tab."""
        bg = self.combo_adjust_bg.get()
        stock = self.db.get_stock_by_group(bg)
        if stock:
            self.selected_stock_id = stock["stock_id"]
            self.spin_adjust_units.delete(0, tk.END)
            self.spin_adjust_units.insert(0, str(stock["units_available"]))
            if stock["expiry_date"]:
                try:
                    exp_dt = datetime.strptime(stock["expiry_date"], "%Y-%m-%d").date()
                    self.date_adjust_expiry.set_date(exp_dt)
                except Exception:
                    pass
            self.lbl_selected_stock.config(
                text=f"Loaded Record #{self.selected_stock_id} for Group {bg}.",
                fg=config.COLOR_INFO
            )

    def submit_donation(self):
        """Processes atomic donation intake: updates donor and increases stock."""
        sel = self.combo_donors.get()
        donor = self.donor_map.get(sel)
        if not donor:
            messagebox.showerror("Selection Error", "Please select a registered donor first.")
            return

        if donor["eligibility"] != "Eligible":
            proceed = messagebox.askyesno(
                "Clinical Eligibility Notice",
                f"Donor {donor['name']} is currently categorized as '{donor['eligibility']}'.\n\n"
                f"Do you want to proceed with recording this donation after clinical verification?",
                icon="warning"
            )
            if not proceed:
                return

        units_str = self.spin_donation_units.get()
        valid, res = validators.validate_units(units_str, field_name="Donated Units")
        if not valid:
            messagebox.showerror("Validation Error", res)
            return
        units = res

        donation_date = self.date_donation.get_date().strftime("%Y-%m-%d")
        expiry_date = self.date_expiry.get_date().strftime("%Y-%m-%d")

        success, msg = self.db.record_donation(
            donor_id=donor["donor_id"],
            units=units,
            donation_date=donation_date,
            expiry_date=expiry_date
        )

        if success:
            messagebox.showinfo("Donation Recorded", f"{msg}\n\nInventory updated successfully.")
            self.refresh_stock()
            if self.on_data_changed:
                self.on_data_changed()
        else:
            messagebox.showerror("Transaction Error", msg)

    def submit_adjustment(self):
        """Saves manual stock unit and expiry changes."""
        bg = self.combo_adjust_bg.get()
        units_str = self.spin_adjust_units.get()

        try:
            units = int(units_str)
            if units < 0:
                raise ValueError("Units cannot be negative.")
        except ValueError:
            messagebox.showerror("Validation Error", "Units available must be a non-negative whole integer.")
            return

        exp_date = self.date_adjust_expiry.get_date().strftime("%Y-%m-%d")

        try:
            if self.selected_stock_id:
                self.db.update_stock_record(self.selected_stock_id, units, exp_date)
            else:
                self.db.add_direct_stock(bg, units, exp_date)

            messagebox.showinfo("Success", f"Stock for blood group {bg} updated to {units} units.")
            self.refresh_stock()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update stock:\n{str(e)}")
