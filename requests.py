"""
Hospital Emergency Requisitions View Module
Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)
Healthcare operations console managing emergency hospital blood requisitions,
live stock availability checks, status state transitions, and safe inventory dispensing.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import config
import validators
from ui_components import Card, StatusBadge, ThemedButton, FormFieldWrapper


class RequestsView(tk.Frame):
    """Operations console for hospital emergency requisitions with automated stock validation."""

    def __init__(self, parent, db_manager, on_data_changed=None):
        super().__init__(parent, bg=config.BACKGROUND)
        self.db = db_manager
        self.on_data_changed = on_data_changed
        self.selected_req_id = None

        self.columnconfigure(0, weight=4)  # Left Requisition Form
        self.columnconfigure(1, weight=6)  # Right Requisition Log
        self.rowconfigure(0, weight=1)

        self._build_form_panel()
        self._build_table_panel()
        self.load_requests()

    def _build_form_panel(self):
        """Constructs hospital requisition form in an elevated white card with subtle medical red accent."""
        form_card = Card(self, bg=config.CARD_BACKGROUND, accent_color=config.COLOR_MEDICAL_RED, padx=18, pady=12)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(20, 8), pady=(12, 16))
        form_card.columnconfigure(1, weight=1)

        # Title
        tk.Label(
            form_card,
            text="Hospital Requisition Form",
            font=config.FONT_HEADER,
            fg=config.COLOR_DARK_NAVY,
            bg=config.CARD_BACKGROUND
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))

        self.lbl_selected_id = tk.Label(
            form_card,
            text="● Mode: Creating New Requisition",
            font=config.FONT_SMALL,
            fg=config.COLOR_PRIMARY_CYAN,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_selected_id.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # 1. Hospital Name
        FormFieldWrapper(
            form_card,
            label="Hospital / Medical Center",
            required=True,
            helper="Name of requesting hospital or trauma center"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 2))

        self.entry_hospital = ttk.Entry(
            form_card,
            font=config.FONT_REGULAR
        )
        self.entry_hospital.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # 2 & 3. Blood Group & Units Needed (Side-by-side row)
        grp_row = tk.Frame(form_card, bg=config.CARD_BACKGROUND)
        grp_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(2, 6))
        grp_row.columnconfigure(0, weight=1)
        grp_row.columnconfigure(1, weight=1)

        # Blood Group
        bg_box = tk.Frame(grp_row, bg=config.CARD_BACKGROUND)
        bg_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        FormFieldWrapper(bg_box, label="Blood Group Required", required=True).pack(anchor="w")
        self.combo_bg = ttk.Combobox(
            bg_box,
            values=config.BLOOD_GROUPS,
            state="readonly",
            font=config.FONT_REGULAR
        )
        self.combo_bg.set(config.BLOOD_GROUPS[0])
        self.combo_bg.pack(fill="x", pady=(2, 0))
        self.combo_bg.bind("<<ComboboxSelected>>", self.on_group_or_units_changed)

        # Units Needed
        units_box = tk.Frame(grp_row, bg=config.CARD_BACKGROUND)
        units_box.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        FormFieldWrapper(units_box, label="Units Needed", required=True).pack(anchor="w")
        self.spin_units = tk.Spinbox(
            units_box,
            from_=1,
            to=50,
            font=config.FONT_REGULAR,
            width=8,
            relief="solid",
            bd=1,
            command=self.on_group_or_units_changed
        )
        self.spin_units.pack(fill="x", pady=(2, 0))
        self.spin_units.bind("<KeyRelease>", lambda e: self.on_group_or_units_changed(None))

        # Live Stock Indicator Box
        self.stock_indicator_box = tk.Frame(
            form_card,
            bg=config.TINT_MINT_LIGHT,
            padx=10, pady=8,
            highlightbackground="#99F6E4",
            highlightthickness=1
        )
        self.stock_indicator_box.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 10))

        self.lbl_stock_indicator = tk.Label(
            self.stock_indicator_box,
            text="Checking current blood stock...",
            font=config.FONT_SMALL_BOLD,
            fg=config.PRIMARY_TEAL,
            bg=config.TINT_MINT_LIGHT
        )
        self.lbl_stock_indicator.pack(anchor="w")

        # 4. Request Status
        FormFieldWrapper(
            form_card,
            label="Requisition Workflow Status",
            required=True,
            helper="Pending/Approved: logs request | Fulfilled: dispenses stock"
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(4, 2))

        self.combo_status = ttk.Combobox(
            form_card,
            values=config.REQUEST_STATUSES,
            state="readonly",
            font=config.FONT_REGULAR
        )
        self.combo_status.set(config.REQUEST_STATUSES[0])  # "Pending"
        self.combo_status.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Safety Rules Note Box (Soft Pink Emergency Information Panel)
        rule_box = tk.Frame(form_card, bg=config.COLOR_SOFT_PINK, padx=10, pady=8, highlightbackground="#FECACA", highlightthickness=1)
        rule_box.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(2, 12))

        tk.Label(
            rule_box,
            text="🚨 Safe Emergency Dispensing Rules:\n"
                 "• 'Pending', 'Approved', and 'Rejected' do not alter stock.\n"
                 "• 'Fulfilled' verifies stock and deducts units in an atomic transaction.\n"
                 "• Modifying or deleting a fulfilled request safely adjusts inventory.",
            font=config.FONT_TINY,
            fg=config.COLOR_MEDICAL_RED,
            bg=config.COLOR_SOFT_PINK,
            justify="left"
        ).pack(anchor="w")

        # Button Controls
        btn_grid = tk.Frame(form_card, bg=config.CARD_BACKGROUND)
        btn_grid.grid(row=9, column=0, columnspan=2, sticky="ew")
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        self.btn_add = ThemedButton(
            btn_grid,
            text="➕ Submit Request",
            btn_type="primary",
            command=self.save_request
        )
        self.btn_add.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=4)

        self.btn_update = ThemedButton(
            btn_grid,
            text="✏️ Update Request",
            btn_type="outline",
            state="disabled",
            command=self.update_request
        )
        self.btn_update.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=4)

        self.btn_delete = ThemedButton(
            btn_grid,
            text="🗑️ Delete Request",
            btn_type="danger",
            state="disabled",
            command=self.delete_request
        )
        self.btn_delete.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=4)

        self.btn_clear = ThemedButton(
            btn_grid,
            text="🔄 Clear Form",
            btn_type="secondary",
            command=self.clear_form
        )
        self.btn_clear.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=4)

        # Quick Workflow Row: Approve & Reject
        wf_grid = tk.Frame(form_card, bg=config.CARD_BACKGROUND)
        wf_grid.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        wf_grid.columnconfigure(0, weight=1)
        wf_grid.columnconfigure(1, weight=1)

        self.btn_approve = ThemedButton(
            wf_grid,
            text="✓ Approve Request",
            btn_type="outline",
            state="disabled",
            pady=5,
            command=self.quick_approve_request
        )
        self.btn_approve.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_reject = ThemedButton(
            wf_grid,
            text="✗ Reject Request",
            btn_type="outline_danger",
            state="disabled",
            pady=5,
            command=self.quick_reject_request
        )
        self.btn_reject.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Prominent Emergency Dispense Button (Medical Red Accent)
        self.btn_fulfill_quick = ThemedButton(
            form_card,
            text="🚨 Dispense Blood & Fulfil Selected",
            btn_type="danger",
            font=config.FONT_BOLD,
            pady=8,
            state="disabled",
            command=self.quick_fulfill_request
        )
        self.btn_fulfill_quick.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        # Initial check
        self.on_group_or_units_changed(None)

    def _build_table_panel(self):
        """Constructs requisition log table, search, and filters on the right."""
        table_card = Card(self, bg=config.CARD_BACKGROUND, padx=18, pady=16)
        table_card.grid(row=0, column=1, sticky="nsew", padx=(8, 20), pady=(12, 16))
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(2, weight=1)

        # Table Header
        tbl_hdr = tk.Frame(table_card, bg=config.CARD_BACKGROUND)
        tbl_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        left_title = tk.Frame(tbl_hdr, bg=config.CARD_BACKGROUND)
        left_title.pack(side="left")

        tk.Label(
            left_title,
            text="Hospital Requisition Log",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w")

        self.lbl_count = tk.Label(
            left_title,
            text="0 requests registered",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_count.pack(anchor="w")

        # Filter Bar
        filter_bar = tk.Frame(table_card, bg="#F8FAFC", padx=10, pady=8)
        filter_bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        filter_bar.columnconfigure(1, weight=1)

        tk.Label(
            filter_bar,
            text="🔍 Hospital:",
            font=config.FONT_BOLD,
            fg=config.MAIN_TEXT,
            bg="#F8FAFC"
        ).grid(row=0, column=0, padx=(0, 6), sticky="w")

        self.entry_search = ttk.Entry(filter_bar, font=config.FONT_REGULAR)
        self.entry_search.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.entry_search.bind("<Return>", lambda e: self.search_requests())

        # Status Filter
        tk.Label(
            filter_bar,
            text="Status:",
            font=config.FONT_SMALL_BOLD,
            fg=config.MAIN_TEXT,
            bg="#F8FAFC"
        ).grid(row=0, column=2, padx=(0, 4))

        self.combo_filter_status = ttk.Combobox(
            filter_bar,
            values=["All Statuses"] + config.REQUEST_STATUSES,
            state="readonly",
            width=13,
            font=config.FONT_SMALL
        )
        self.combo_filter_status.set("All Statuses")
        self.combo_filter_status.grid(row=0, column=3, padx=(0, 8))
        self.combo_filter_status.bind("<<ComboboxSelected>>", lambda e: self.search_requests())

        # Group Filter
        tk.Label(
            filter_bar,
            text="Group:",
            font=config.FONT_SMALL_BOLD,
            fg=config.MAIN_TEXT,
            bg="#F8FAFC"
        ).grid(row=0, column=4, padx=(0, 4))

        self.combo_filter_bg = ttk.Combobox(
            filter_bar,
            values=["All Groups"] + config.BLOOD_GROUPS,
            state="readonly",
            width=10,
            font=config.FONT_SMALL
        )
        self.combo_filter_bg.set("All Groups")
        self.combo_filter_bg.grid(row=0, column=5, padx=(0, 8))
        self.combo_filter_bg.bind("<<ComboboxSelected>>", lambda e: self.search_requests())

        ThemedButton(
            filter_bar,
            text="Search",
            btn_type="primary",
            font=config.FONT_SMALL_BOLD,
            padx=10, pady=3,
            command=self.search_requests
        ).grid(row=0, column=6, padx=(0, 4))

        ThemedButton(
            filter_bar,
            text="Reset",
            btn_type="secondary",
            font=config.FONT_SMALL,
            padx=8, pady=3,
            command=self.reset_search
        ).grid(row=0, column=7)

        # Treeview Log Table
        tree_container = tk.Frame(table_card, bg=config.CARD_BACKGROUND)
        tree_container.grid(row=2, column=0, sticky="nsew")
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        cols = ("id", "hospital", "blood_group", "units", "status")
        self.tree = ttk.Treeview(
            tree_container,
            columns=cols,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("id", text="Req ID")
        self.tree.heading("hospital", text="Hospital / Healthcare Center")
        self.tree.heading("blood_group", text="Group")
        self.tree.heading("units", text="Units Needed")
        self.tree.heading("status", text="Workflow Status")

        self.tree.column("id", width=55, anchor="center")
        self.tree.column("hospital", width=220, anchor="w")
        self.tree.column("blood_group", width=75, anchor="center")
        self.tree.column("units", width=95, anchor="center")
        self.tree.column("status", width=110, anchor="center")

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Alternating row tag colors
        self.tree.tag_configure("evenrow", background="#FFFFFF")
        self.tree.tag_configure("oddrow", background="#F8FAFC")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_group_or_units_changed(self, event):
        """Displays real-time stock availability for currently entered blood group and units."""
        bg = self.combo_bg.get().strip()
        stock = self.db.get_stock_by_group(bg)
        avail = stock["units_available"] if stock else 0

        try:
            needed = int(self.spin_units.get())
        except (ValueError, TypeError):
            needed = 1

        if avail >= needed:
            self.stock_indicator_box.config(bg=config.COLOR_LIGHT_CYAN, highlightbackground=config.COLOR_PRIMARY_CYAN)
            self.lbl_stock_indicator.config(
                text=f"✓ Stock Available: {avail} units of {bg} in blood bank (Requested: {needed})",
                fg=config.COLOR_DARK_NAVY,
                bg=config.COLOR_LIGHT_CYAN
            )
        else:
            self.stock_indicator_box.config(bg=config.COLOR_SOFT_PINK, highlightbackground=config.COLOR_MEDICAL_RED)
            self.lbl_stock_indicator.config(
                text=f"⚠️ Insufficient Stock: Only {avail} units of {bg} available (Short by {needed - avail} units)",
                fg=config.COLOR_MEDICAL_RED,
                bg=config.COLOR_SOFT_PINK
            )

    def load_requests(self, requests_list=None):
        """Clears and re-populates Treeview with hospital requests."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if requests_list is None:
            reqs = self.db.get_all_requests()
        else:
            reqs = requests_list

        for i, r in enumerate(reqs):
            row_tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(
                r["req_id"],
                r["hospital_name"],
                r["blood_group"],
                f"{r['units_needed']} units",
                r["req_status"]
            ), tags=(row_tag,))

        self.lbl_count.config(text=f"{len(reqs)} request(s) listed in log")

    def search_requests(self):
        """Searches hospital requests by query and filters."""
        query = self.entry_search.get().strip()
        status_flt = self.combo_filter_status.get()
        bg_flt = self.combo_filter_bg.get()
        results = self.db.search_requests(query=query, status_filter=status_flt, blood_group=bg_flt)
        self.load_requests(results)

    def reset_search(self):
        """Resets filter inputs."""
        self.entry_search.delete(0, tk.END)
        self.combo_filter_status.set("All Statuses")
        self.combo_filter_bg.set("All Groups")
        self.load_requests()

    def on_tree_select(self, event):
        """Populates form when a table row is clicked."""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        if not values:
            return

        req_id, hospital, bg, units_str, status = values
        self.selected_req_id = int(req_id)
        self.lbl_selected_id.config(
            text=f"● Mode: Editing Request #{self.selected_req_id} ({hospital})",
            fg=config.COLOR_WARNING
        )

        self.entry_hospital.delete(0, tk.END)
        self.entry_hospital.insert(0, hospital)

        if bg in config.BLOOD_GROUPS:
            self.combo_bg.set(bg)

        # Parse units
        try:
            u_val = int(units_str.replace("units", "").strip())
        except ValueError:
            u_val = 1

        self.spin_units.delete(0, tk.END)
        self.spin_units.insert(0, str(u_val))

        if status in config.REQUEST_STATUSES:
            self.combo_status.set(status)

        self.on_group_or_units_changed(None)

        self.btn_update.config(state="normal")
        self.btn_delete.config(state="normal")
        self.btn_add.config(state="disabled")

        if status != "Fulfilled":
            self.btn_fulfill_quick.config(state="normal")
            self.btn_approve.config(state="normal" if status != "Approved" else "disabled")
            self.btn_reject.config(state="normal" if status != "Rejected" else "disabled")
        else:
            self.btn_fulfill_quick.config(state="disabled")
            self.btn_approve.config(state="disabled")
            self.btn_reject.config(state="disabled")

    def validate_inputs(self):
        """Validates all request fields using validators.py."""
        hosp = self.entry_hospital.get()
        valid, msg = validators.validate_hospital_name(hosp)
        if not valid:
            raise validators.ValidationError(msg)
        clean_hosp = msg

        bg = self.combo_bg.get()
        valid, msg = validators.validate_blood_group(bg)
        if not valid:
            raise validators.ValidationError(msg)
        clean_bg = msg

        units_str = self.spin_units.get()
        valid, res = validators.validate_units(units_str, field_name="Units Needed")
        if not valid:
            raise validators.ValidationError(res)
        clean_units = res

        status = self.combo_status.get()
        valid, msg = validators.validate_request_status(status)
        if not valid:
            raise validators.ValidationError(msg)
        clean_status = msg

        return clean_hosp, clean_bg, clean_units, clean_status

    def save_request(self):
        """Submits a new emergency hospital request."""
        try:
            hosp, bg, units, status = self.validate_inputs()
            success, msg, new_id = self.db.add_request(hosp, bg, units, status)
            if success:
                messagebox.showinfo("Success", f"{msg}")
                self.clear_form()
                self.load_requests()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                messagebox.showerror("Error", msg)
        except validators.ValidationError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Database integrity error:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"A database error occurred:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to submit request:\n{str(e)}")

    def update_request(self):
        """Updates an existing request with transactional stock adjustment."""
        if not self.selected_req_id:
            messagebox.showwarning("Selection Required", "Please select a request from the table to update.")
            return

        try:
            hosp, bg, units, status = self.validate_inputs()
            success, msg = self.db.update_request(self.selected_req_id, hosp, bg, units, status)
            if success:
                messagebox.showinfo("Success", f"{msg}")
                self.clear_form()
                self.load_requests()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                messagebox.showerror("Error", msg)
        except validators.ValidationError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Database integrity error:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"A database error occurred:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to update request:\n{str(e)}")

    def quick_fulfill_request(self):
        """Shortcut action: Sets status to Fulfilled and dispenses inventory immediately."""
        if not self.selected_req_id:
            messagebox.showwarning("Selection Required", "Please select a pending request to fulfill.")
            return

        hosp = self.entry_hospital.get()
        bg = self.combo_bg.get()
        try:
            units = int(self.spin_units.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid units quantity.")
            return

        confirm = messagebox.askyesno(
            "Confirm Dispensing Blood",
            f"Are you sure you want to FULFILL Request #{self.selected_req_id} for {hosp}?\n\n"
            f"• Blood Group: {bg}\n"
            f"• Units to Dispense: {units}\n\n"
            f"This will deduct {units} units from blood inventory immediately.",
            icon="question"
        )
        if not confirm:
            return

        try:
            success, msg = self.db.update_request(self.selected_req_id, hosp, bg, units, "Fulfilled")
            if success:
                messagebox.showinfo("Dispensed Successfully", f"Request #{self.selected_req_id} has been fulfilled!\n{units} units of {bg} dispensed to {hosp}.")
                self.clear_form()
                self.load_requests()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                messagebox.showerror("Dispensing Blocked", msg)
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Database integrity error:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"A database error occurred:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to dispense blood:\n{str(e)}")

    def quick_approve_request(self):
        """Shortcut action: Sets status of selected requisition to Approved."""
        if not self.selected_req_id:
            messagebox.showwarning("Selection Required", "Please select a request from the table to approve.")
            return

        hosp = self.entry_hospital.get()
        bg = self.combo_bg.get()
        try:
            units = int(self.spin_units.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid units quantity.")
            return

        try:
            success, msg = self.db.update_request(self.selected_req_id, hosp, bg, units, "Approved")
            if success:
                messagebox.showinfo("Approved", f"Request #{self.selected_req_id} for {hosp} has been Approved.")
                self.clear_form()
                self.load_requests()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                messagebox.showerror("Error", msg)
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Database integrity error:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"A database error occurred:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to approve request:\n{str(e)}")

    def quick_reject_request(self):
        """Shortcut action: Sets status of selected requisition to Rejected."""
        if not self.selected_req_id:
            messagebox.showwarning("Selection Required", "Please select a request from the table to reject.")
            return

        hosp = self.entry_hospital.get()
        bg = self.combo_bg.get()
        try:
            units = int(self.spin_units.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid units quantity.")
            return

        try:
            success, msg = self.db.update_request(self.selected_req_id, hosp, bg, units, "Rejected")
            if success:
                messagebox.showinfo("Rejected", f"Request #{self.selected_req_id} for {hosp} has been Rejected.")
                self.clear_form()
                self.load_requests()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                messagebox.showerror("Error", msg)
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Database integrity error:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"A database error occurred:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to reject request:\n{str(e)}")

    def delete_request(self):
        """Deletes selected request with option to restore inventory if already fulfilled."""
        if not self.selected_req_id:
            messagebox.showwarning("Selection Required", "Please select a request to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete Request #{self.selected_req_id}?\n"
            f"If this request was fulfilled, the dispensed units will be safely restored to blood stock.",
            icon="warning"
        )
        if not confirm:
            return

        try:
            success, msg = self.db.delete_request(self.selected_req_id, restore_if_fulfilled=True)
            if success:
                messagebox.showinfo("Success", f"{msg}")
                self.clear_form()
                self.load_requests()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                messagebox.showerror("Error", msg)
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Database integrity error:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"A database error occurred:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to delete request:\n{str(e)}")

    def clear_form(self):
        """Clears form fields and resets selection state."""
        self.selected_req_id = None
        self.lbl_selected_id.config(
            text="● Mode: Creating New Requisition",
            fg=config.COLOR_PRIMARY_CYAN
        )
        self.entry_hospital.delete(0, tk.END)
        self.combo_bg.set(config.BLOOD_GROUPS[0])
        self.spin_units.delete(0, tk.END)
        self.spin_units.insert(0, "1")
        self.combo_status.set(config.REQUEST_STATUSES[0])

        self.btn_add.config(state="normal")
        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")
        self.btn_fulfill_quick.config(state="disabled")
        self.btn_approve.config(state="disabled")
        self.btn_reject.config(state="disabled")

        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

        self.on_group_or_units_changed(None)
