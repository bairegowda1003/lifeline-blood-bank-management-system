"""
Donor Directory Management View Module
Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)
Healthcare SaaS-inspired interface for donor registration, profile editing,
regular expression validation, multi-parameter search, and directory tracking.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date, datetime
import tkcalendar

import config
import validators
from ui_components import Card, StatusBadge, ThemedButton, FormFieldWrapper


class DonorView(tk.Frame):
    """Modern donor directory with validated registration form and real-time search table."""

    def __init__(self, parent, db_manager, on_data_changed=None):
        super().__init__(parent, bg=config.BACKGROUND)
        self.db = db_manager
        self.on_data_changed = on_data_changed
        self.selected_donor_id = None

        self.columnconfigure(0, weight=4)  # Left: Registration Form
        self.columnconfigure(1, weight=6)  # Right: Directory Table & Search
        self.rowconfigure(0, weight=1)

        self._build_form_panel()
        self._build_table_panel()
        self.load_donors()

    def _build_form_panel(self):
        """Constructs donor registration and update form in an elevated white card."""
        form_card = Card(self, bg=config.CARD_BACKGROUND, padx=20, pady=16)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(20, 8), pady=(12, 16))
        form_card.columnconfigure(1, weight=1)

        # Section Header
        tk.Label(
            form_card,
            text="Donor Registration",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))

        self.lbl_selected_id = tk.Label(
            form_card,
            text="● Mode: Registering New Donor",
            font=config.FONT_SMALL,
            fg=config.PRIMARY_TEAL,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_selected_id.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        # 1. Full Name
        FormFieldWrapper(
            form_card,
            label="Full Name",
            required=True,
            helper="Enter legal name (alphabets, spaces, dots)"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 2))

        self.entry_name = ttk.Entry(
            form_card,
            font=config.FONT_REGULAR
        )
        self.entry_name.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # 2 & 3. Blood Group & Rh Factor (Side-by-side row)
        bg_row = tk.Frame(form_card, bg=config.CARD_BACKGROUND)
        bg_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(2, 8))
        bg_row.columnconfigure(0, weight=1)
        bg_row.columnconfigure(1, weight=1)

        # Blood Type
        type_box = tk.Frame(bg_row, bg=config.CARD_BACKGROUND)
        type_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        FormFieldWrapper(type_box, label="Blood Group", required=True).pack(anchor="w")
        self.combo_blood_type = ttk.Combobox(
            type_box,
            values=config.BLOOD_TYPES,
            state="readonly",
            font=config.FONT_REGULAR
        )
        self.combo_blood_type.set(config.BLOOD_TYPES[0])
        self.combo_blood_type.pack(fill="x", pady=(2, 0))

        # Rh Factor
        rh_box = tk.Frame(bg_row, bg=config.CARD_BACKGROUND)
        rh_box.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        FormFieldWrapper(rh_box, label="Rh Factor", required=True).pack(anchor="w")
        self.combo_rh = ttk.Combobox(
            rh_box,
            values=config.RH_FACTORS,
            state="readonly",
            font=config.FONT_REGULAR
        )
        self.combo_rh.set(config.RH_FACTORS[0])
        self.combo_rh.pack(fill="x", pady=(2, 0))

        # 4. Phone Number
        FormFieldWrapper(
            form_card,
            label="Mobile Phone",
            required=True,
            helper="10-digit number starting with 6, 7, 8, or 9"
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(4, 2))

        self.entry_phone = ttk.Entry(
            form_card,
            font=config.FONT_REGULAR
        )
        self.entry_phone.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # 5. Last Donation Date
        FormFieldWrapper(
            form_card,
            label="Last Donation Date",
            required=False,
            helper="Select previous donation or keep today if initial"
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(4, 2))

        date_container = tk.Frame(form_card, bg=config.CARD_BACKGROUND)
        date_container.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        date_container.columnconfigure(0, weight=1)

        self.date_entry = tkcalendar.DateEntry(
            date_container,
            date_pattern="yyyy-mm-dd",
            maxdate=date.today(),
            font=config.FONT_REGULAR,
            background=config.COLOR_DARK_NAVY,
            foreground="white",
            borderwidth=1
        )
        self.date_entry.pack(fill="x")

        # 6. Medical Eligibility
        FormFieldWrapper(
            form_card,
            label="Eligibility Status",
            required=True,
            helper="Verified manually by clinical staff per health guidelines"
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=(4, 2))

        self.combo_eligibility = ttk.Combobox(
            form_card,
            values=config.ELIGIBILITY_STATUSES,
            state="readonly",
            font=config.FONT_REGULAR
        )
        self.combo_eligibility.set(config.ELIGIBILITY_STATUSES[0])
        self.combo_eligibility.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # Buttons Grid
        btn_frame = tk.Frame(form_card, bg=config.CARD_BACKGROUND)
        btn_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        self.btn_add = ThemedButton(
            btn_frame,
            text="➕ Register Donor",
            btn_type="primary",
            command=self.save_donor
        )
        self.btn_add.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=4)

        self.btn_update = ThemedButton(
            btn_frame,
            text="✏️ Update Profile",
            btn_type="outline",
            state="disabled",
            command=self.update_donor
        )
        self.btn_update.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=4)

        self.btn_delete = ThemedButton(
            btn_frame,
            text="🗑️ Delete Donor",
            btn_type="danger",
            state="disabled",
            command=self.delete_donor
        )
        self.btn_delete.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=4)

        self.btn_clear = ThemedButton(
            btn_frame,
            text="🔄 Clear Form",
            btn_type="secondary",
            command=self.clear_form
        )
        self.btn_clear.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=4)

    def _build_table_panel(self):
        """Constructs donor directory table, search, and filters on the right."""
        table_card = Card(self, bg=config.CARD_BACKGROUND, padx=18, pady=16)
        table_card.grid(row=0, column=1, sticky="nsew", padx=(8, 20), pady=(12, 16))
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(2, weight=1)

        # Header of Directory
        tbl_hdr = tk.Frame(table_card, bg=config.CARD_BACKGROUND)
        tbl_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        left_title = tk.Frame(tbl_hdr, bg=config.CARD_BACKGROUND)
        left_title.pack(side="left")

        tk.Label(
            left_title,
            text="Donor Directory",
            font=config.FONT_HEADER,
            fg=config.PRIMARY_DARK_TEAL,
            bg=config.CARD_BACKGROUND
        ).pack(anchor="w")

        self.lbl_count = tk.Label(
            left_title,
            text="0 donors listed in directory",
            font=config.FONT_TINY,
            fg=config.SECONDARY_TEXT,
            bg=config.CARD_BACKGROUND
        )
        self.lbl_count.pack(anchor="w")

        # Search & Filter Tool Bar
        filter_bar = tk.Frame(table_card, bg="#F8FAFC", padx=10, pady=8)
        filter_bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        filter_bar.columnconfigure(1, weight=1)

        tk.Label(
            filter_bar,
            text="🔍 Search:",
            font=config.FONT_BOLD,
            fg=config.MAIN_TEXT,
            bg="#F8FAFC"
        ).grid(row=0, column=0, padx=(0, 6), sticky="w")

        self.entry_search = ttk.Entry(filter_bar, font=config.FONT_REGULAR)
        self.entry_search.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.entry_search.bind("<Return>", lambda e: self.search_donors())

        # Blood Group Filter
        tk.Label(
            filter_bar,
            text="Group:",
            font=config.FONT_SMALL_BOLD,
            fg=config.MAIN_TEXT,
            bg="#F8FAFC"
        ).grid(row=0, column=2, padx=(0, 4))

        self.combo_filter_bg = ttk.Combobox(
            filter_bar,
            values=["All Groups"] + config.BLOOD_GROUPS,
            state="readonly",
            width=10,
            font=config.FONT_SMALL
        )
        self.combo_filter_bg.set("All Groups")
        self.combo_filter_bg.grid(row=0, column=3, padx=(0, 8))
        self.combo_filter_bg.bind("<<ComboboxSelected>>", lambda e: self.search_donors())

        # Eligibility Filter
        tk.Label(
            filter_bar,
            text="Status:",
            font=config.FONT_SMALL_BOLD,
            fg=config.MAIN_TEXT,
            bg="#F8FAFC"
        ).grid(row=0, column=4, padx=(0, 4))

        self.combo_filter_elig = ttk.Combobox(
            filter_bar,
            values=["All Statuses"] + config.ELIGIBILITY_STATUSES,
            state="readonly",
            width=13,
            font=config.FONT_SMALL
        )
        self.combo_filter_elig.set("All Statuses")
        self.combo_filter_elig.grid(row=0, column=5, padx=(0, 8))
        self.combo_filter_elig.bind("<<ComboboxSelected>>", lambda e: self.search_donors())

        # Search & Reset Actions
        ThemedButton(
            filter_bar,
            text="Search",
            btn_type="primary",
            font=config.FONT_SMALL_BOLD,
            padx=10, pady=3,
            command=self.search_donors
        ).grid(row=0, column=6, padx=(0, 4))

        ThemedButton(
            filter_bar,
            text="Reset",
            btn_type="secondary",
            font=config.FONT_SMALL,
            padx=8, pady=3,
            command=self.reset_search
        ).grid(row=0, column=7)

        # Treeview Directory Table
        tree_container = tk.Frame(table_card, bg=config.CARD_BACKGROUND)
        tree_container.grid(row=2, column=0, sticky="nsew")
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        cols = ("id", "name", "blood_group", "phone", "last_donation", "eligibility")
        self.tree = ttk.Treeview(
            tree_container,
            columns=cols,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Donor Name")
        self.tree.heading("blood_group", text="Group")
        self.tree.heading("phone", text="Phone Number")
        self.tree.heading("last_donation", text="Last Donation")
        self.tree.heading("eligibility", text="Eligibility Status")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("blood_group", width=70, anchor="center")
        self.tree.column("phone", width=110, anchor="center")
        self.tree.column("last_donation", width=105, anchor="center")
        self.tree.column("eligibility", width=125, anchor="center")

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Alternating row tag colors
        self.tree.tag_configure("evenrow", background="#FFFFFF")
        self.tree.tag_configure("oddrow", background="#F8FAFC")

        # Row selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def get_combined_blood_group(self) -> str:
        """Combines blood type ('A', 'B', 'AB', 'O') with Rh factor ('+' or '-') consistently."""
        b_type = self.combo_blood_type.get().strip()
        rh_str = self.combo_rh.get().strip()
        rh_symbol = "+" if "Positive" in rh_str else "-"
        return f"{b_type}{rh_symbol}"

    def split_blood_group(self, combined_group: str):
        """Splits 'A+' or 'O-' into ('A', 'Positive (+)') for the dropdowns."""
        combined = combined_group.strip().upper()
        if combined.endswith("+"):
            return combined[:-1], "Positive (+)"
        elif combined.endswith("-"):
            return combined[:-1], "Negative (-)"
        return "O", "Positive (+)"

    def load_donors(self, donors_list=None):
        """Clears and re-populates the Treeview with donors."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if donors_list is None:
            donors = self.db.get_all_donors()
        else:
            donors = donors_list

        for i, d in enumerate(donors):
            row_tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(
                d["donor_id"],
                d["name"],
                d["blood_group"],
                d["phone"],
                d["last_donation_date"] or "Never",
                d["eligibility"]
            ), tags=(row_tag,))

        self.lbl_count.config(text=f"{len(donors)} donor(s) registered in directory")

    def search_donors(self):
        """Applies search filters and refreshes Treeview."""
        query = self.entry_search.get().strip()
        bg = self.combo_filter_bg.get()
        elig = self.combo_filter_elig.get()
        results = self.db.search_donors(query=query, blood_group=bg, eligibility=elig)
        self.load_donors(results)

    def reset_search(self):
        """Resets search filters to default."""
        self.entry_search.delete(0, tk.END)
        self.combo_filter_bg.set("All Groups")
        self.combo_filter_elig.set("All Statuses")
        self.load_donors()

    def on_tree_select(self, event):
        """Populates form inputs when a row is selected."""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        if not values:
            return

        donor_id, name, bg, phone, last_date, elig = values
        self.selected_donor_id = int(donor_id)
        self.lbl_selected_id.config(
            text=f"● Mode: Editing Donor #{self.selected_donor_id} ({name})",
            fg=config.COLOR_WARNING
        )

        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, name)

        b_type, rh_str = self.split_blood_group(bg)
        if b_type in config.BLOOD_TYPES:
            self.combo_blood_type.set(b_type)
        if rh_str in config.RH_FACTORS:
            self.combo_rh.set(rh_str)

        self.entry_phone.delete(0, tk.END)
        self.entry_phone.insert(0, phone)

        try:
            if last_date and last_date != "Never":
                dt = datetime.strptime(last_date, "%Y-%m-%d").date()
                self.date_entry.set_date(dt)
        except Exception:
            pass

        if elig in config.ELIGIBILITY_STATUSES:
            self.combo_eligibility.set(elig)

        self.btn_update.config(state="normal")
        self.btn_delete.config(state="normal")
        self.btn_add.config(state="disabled")

    def validate_inputs(self):
        """Validates all form fields using validators.py."""
        name = self.entry_name.get()
        valid, msg = validators.validate_name(name)
        if not valid:
            raise validators.ValidationError(msg)
        clean_name = msg

        phone = self.entry_phone.get()
        valid, msg = validators.validate_phone(phone)
        if not valid:
            raise validators.ValidationError(msg)
        clean_phone = msg

        date_val = self.date_entry.get_date().strftime("%Y-%m-%d")
        valid, msg = validators.validate_date(date_val, allow_future=False, field_name="Last Donation Date")
        if not valid:
            raise validators.ValidationError(msg)
        clean_date = msg

        combined_bg = self.get_combined_blood_group()
        valid, msg = validators.validate_blood_group(combined_bg)
        if not valid:
            raise validators.ValidationError(msg)

        elig = self.combo_eligibility.get()
        valid, msg = validators.validate_eligibility(elig)
        if not valid:
            raise validators.ValidationError(msg)

        return clean_name, combined_bg, clean_phone, clean_date, elig

    def save_donor(self):
        """Registers a new donor into SQLite."""
        try:
            name, bg, phone, last_date, elig = self.validate_inputs()
            new_id = self.db.add_donor(name, bg, phone, last_date, elig)
            messagebox.showinfo("Success", f"Donor registered successfully!\nAssigned Donor ID: #{new_id}")
            self.clear_form()
            self.load_donors()
            if self.on_data_changed:
                self.on_data_changed()
        except validators.ValidationError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Database integrity conflict:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"Database error:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to add donor:\n{str(e)}")

    def update_donor(self):
        """Updates the selected donor record in SQLite."""
        if not self.selected_donor_id:
            messagebox.showwarning("Selection Required", "Please select a donor from the table to update.")
            return

        try:
            name, bg, phone, last_date, elig = self.validate_inputs()
            success = self.db.update_donor(self.selected_donor_id, name, bg, phone, last_date, elig)
            if success:
                messagebox.showinfo("Success", f"Donor ID #{self.selected_donor_id} updated successfully!")
                self.clear_form()
                self.load_donors()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                messagebox.showerror("Error", "Update failed. Record may have been modified or deleted.")
        except validators.ValidationError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Database integrity conflict:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"Database error:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to update donor:\n{str(e)}")

    def delete_donor(self):
        """Deletes the selected donor after user confirmation."""
        if not self.selected_donor_id:
            messagebox.showwarning("Selection Required", "Please select a donor from the table to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete Donor #{self.selected_donor_id}?\nThis action cannot be undone.",
            icon="warning"
        )
        if not confirm:
            return

        try:
            success = self.db.delete_donor(self.selected_donor_id)
            if success:
                messagebox.showinfo("Success", f"Donor #{self.selected_donor_id} has been deleted.")
                self.clear_form()
                self.load_donors()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                messagebox.showerror("Error", "Could not delete donor. Record might not exist.")
        except sqlite3.IntegrityError as ie:
            messagebox.showerror("Database Conflict", f"Cannot delete donor due to database constraints:\n{str(ie)}")
        except sqlite3.Error as se:
            messagebox.showerror("Database Error", f"Database error:\n{str(se)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to delete donor:\n{str(e)}")

    def clear_form(self):
        """Clears form fields and resets selection mode."""
        self.selected_donor_id = None
        self.lbl_selected_id.config(
            text="● Mode: Registering New Donor",
            fg=config.PRIMARY_TEAL
        )
        self.entry_name.delete(0, tk.END)
        self.combo_blood_type.set(config.BLOOD_TYPES[0])
        self.combo_rh.set(config.RH_FACTORS[0])
        self.entry_phone.delete(0, tk.END)
        self.date_entry.set_date(date.today())
        self.combo_eligibility.set(config.ELIGIBILITY_STATUSES[0])

        self.btn_add.config(state="normal")
        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")

        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
