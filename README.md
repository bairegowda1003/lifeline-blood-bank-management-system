# LIFELINE | Blood Bank Donor Directory & Stock Tracker 🩸🏥

**A Premium Healthcare Desktop Application for Blood Bank Management & Stock Tracking**

![Python](https://img.shields.io/badge/Python-3.12.4-blue.svg)
![GUI](https://img.shields.io/badge/GUI-Tkinter%20%2B%20ttkbootstrap-teal.svg)
![Database](https://img.shields.io/badge/Database-SQLite%203-lightgrey.svg)
![Design](https://img.shields.io/badge/Design-Healthcare%20SaaS%20Teal-0F766E.svg)
![Status](https://img.shields.io/badge/Status-Completed%20%26%20Verified-brightgreen.svg)

---

## 🎓 Academic Profile

- **Student Name:** Baire Gowda
- **Student ID:** 25PG00157
- **Course:** Master of Computer Applications (MCA)
- **Semester:** 3rd Semester
- **Category:** Public Health / Healthcare Informatics
- **Presentation Date:** 25 November 2026

---

## 📌 Project Overview

**LIFELINE** is a modern, healthcare SaaS-inspired desktop application designed for regional blood centers, hospital blood banks, and emergency medical logistics. Developed in Python using Tkinter, `ttkbootstrap`, and an ACID-compliant SQLite relational database, it enforces clinical business logic, input validation, atomic transactional inventory tracking, and low-stock/expiry warning systems.

---

## 🎨 Brand Colour System (Dark Navy, Cyan & Medical Red)

| Role | Color Name | Hex Code | Purpose |
| :--- | :--- | :---: | :--- |
| **Dark Navy** | Dark Navy | `#0B2545` | Navigation sidebar background, dark brand headers |
| **Deep Navy** | Deep Navy | `#102F50` | Active sidebar item background, subheaders |
| **Primary Cyan** | Primary Cyan | `#13B8CC` | Primary action buttons, active navigation indicators, highlights |
| **Bright Teal** | Bright Teal | `#16B8C5` | Vivid focal accents, progress indicators, brand emblems |
| **Light Cyan** | Light Cyan | `#E0FAFC` | Status pill backgrounds, selected row tint, soft container backgrounds |
| **White** | Pure White | `#FFFFFF` | Cards, forms, data tables, elevated panels |
| **Soft Background** | Soft Slate Canvas | `#F4F9FC` | Clean modern application background |
| **Soft Pink** | Soft Pink | `#FFF0F1` | Emergency requisition backdrop, critical shortage tint |
| **Medical Red** | Medical Red | `#DC3545` | Emergency actions, dispense button, critical shortages, destructive actions |
| **Success Green** | Success Green | `#16A34A` | Optimal stock, verified donors, fulfilled requests |
| **Warning Amber** | Warning Amber | `#D97706` | Low-stock notices, pending hospital requests |
| **Main Text** | Deep Navy Text | `#142D45` | Primary typography and headings |
| **Secondary Text** | Slate Gray | `#64748B` | Subtitles, labels, and helper guidance |
| **Border** | Modern Border | `#E2E8F0` | Subtle modern card outlines |

---

## 🚀 Key Modules & Features

1. **Overview (Dashboard):**
   - Personal greeting banner (`Good morning, Baire!`) with quick refresh.
   - 4 live KPI metric cards: *Total Registered Donors*, *Available Blood Units*, *Pending Hospital Requests*, *Blood Groups in Stock*.
   - Live 8-Group Inventory Matrix (A+, A-, B+, B-, AB+, AB-, O+, O-) with color-coded status pills.
   - Smart Alert Banners for low stock (<5 units), critical shortages (≤2 units), and RBC shelf-life expiry (>42 days).
   - Recent activity feeds for donor registrations and hospital requisitions.

2. **Donor Directory:**
   - Registration with Full Name, Blood Group (A, B, AB, O), Rh Factor (+ / -), 10-digit Phone, Last Donation Date (`DateEntry`), and manual medical verification for Eligibility.
   - Comprehensive CRUD operations: Register, Update, Delete, Search, and Filter.
   - Treeview row selection with auto-population of input fields.

3. **Blood Inventory & Transactional Intake:**
   - Tracks all eight standard blood groups.
   - **Atomic Donation Intake:** Automatically updates a donor's `last_donation_date` and increments blood stock within an ACID SQLite transaction.
   - Direct stock adjustments with non-negative constraints.
   - Filter views: All Groups, Low Stock Only, Expiring/Expired Only.

4. **Hospital Blood Requests:**
   - Hospital name, required blood group, units requested, and workflow status (`Pending`, `Approved`, `Rejected`, `Fulfilled`).
   - **Safe Inventory Accounting:**
     - Dynamic live stock availability calculation shown as you type.
     - Only `Fulfilled` status deducts stock.
     - Verifies inventory before dispensing (prevents negative stock).
     - Prevents duplicate deductions when requests are updated or edited.
     - Restores units to stock if a fulfilled request is cancelled or deleted.

5. **About & Help:**
   - Complete academic profile, student credentials, and architecture overview.
   - 5-step operational workflow explanation.
   - One-click presentation sample data loading tool.

---

## 🛠️ Technology Stack

- **Programming Language:** Python 3.12+ (64-bit)
- **GUI Framework:** Python Tkinter + `ttk` + `ttkbootstrap`
- **Date Picker Widget:** `tkcalendar.DateEntry`
- **Database Engine:** SQLite 3 (Python Standard Library `sqlite3`)
- **Layout Managers:** `pack()` and `grid()`
- **Architecture:** Layered Architecture (Separation of GUI, Database Operations, and Business Validators)

---

## 📁 Project Directory Structure

```text
Blood Bank Donor Directory & Stock Tracker/
│
├── main.py                     # Application entry point & master navigation window
├── ui_components.py            # Reusable healthcare SaaS UI components (Cards, Buttons, Badges)
├── database.py                 # SQLite database manager, CRUD, transactions & stats
├── config.py                   # Centralized application constants, themes, and paths
├── validators.py               # Regex, phone, date, and numeric validation functions
├── dashboard.py                # Executive dashboard view with live KPI cards & alerts
├── donor.py                    # Donor directory management module
├── blood_stock.py              # Blood stock management & donation intake module
├── requests.py                 # Emergency hospital request & dispensing module
├── capture_screenshots.py      # Automated high-resolution screenshot utility
├── requirements.txt            # Python dependencies (tkcalendar, ttkbootstrap, babel, pillow)
├── README.md                   # Project overview & documentation
│
├── database/
│   └── blood_bank.db           # SQLite database file (auto-initialized)
│
├── tests/
│   ├── test_app.py             # Automated unit tests (CRUD, transactions, stock logic)
│   └── test_gui.py             # Automated GUI integration tests
│
├── assets/                     # Visual assets & icons
├── screenshots/                # Application UI screenshots & capture checklist
│
└── documentation/
    ├── Project_Report.md       # Comprehensive academic project report
    ├── Database_Design.md      # Detailed database schema and transaction design
    ├── User_Guide.md           # Step-by-step operating manual
    ├── Viva_Questions.md       # In-depth viva voce questions & model answers
    └── Screenshot_Checklist.md # Practical checklist for capturing demo screenshots
```

---

## 📦 Installation & Setup

### Prerequisites
- Windows 10 / Windows 11
- Python 3.12.x installed with "Add Python to PATH" enabled.

### 1. Install Dependencies
Open PowerShell or Command Prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```

---

## 🧪 Running Automated Tests

Run the full suite of automated unit tests:
```bash
python -m unittest discover -s tests -v
```

All 14 tests execute in < 3 seconds, covering:
- Database table creation & schema enforcement
- Regular expression validations (Name, Phone, Dates, Units)
- Donor CRUD & search operations
- Atomic donation intake transactions
- Emergency request fulfillment & safe stock deduction
- Duplicate deduction prevention
- Stock restoration on request deletion
- GUI window initialization, navigation switching, and form interaction

---

## 👨‍🎓 Viva Demonstration Workflow

For your MCA Mini Project presentation on 25 November 2026:
1. Launch the app (`python main.py`).
2. Point out the **Healthcare SaaS Visual Hierarchy**: Teal primary brand, white elevated cards, soft background, and live clock.
3. Demonstrate **Overview Dashboard**: Show the 4 live KPI cards (*Total Donors: 10*, *Available Units: 74*, *Pending Requests: 3*, *Groups in Stock: 8/8*).
4. Demonstrate **Donor Registration**: Show regex validation on invalid phone numbers, then register a valid donor and show auto-fill on row selection.
5. Demonstrate **Atomic Blood Donation Intake**: Go to *Blood Inventory* -> *Record Donation Intake* -> select donor -> record 2 units. Show the professor that both the donor's last donation date and the stock table updated atomically in a single SQLite transaction.
6. Demonstrate **Hospital Requisitions**: Submit a request -> highlight the dynamic live stock indicator -> click *Dispense Blood & Fulfil Selected* -> explain how SQLite transaction verifies stock and prevents negative inventory.
7. Open **About & Help** view to show system architecture and student profile.
