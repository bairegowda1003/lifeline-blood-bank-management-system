# APPLICATION SCREENSHOT CHECKLIST & CAPTURE GUIDE

**Project:** Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)  
**Student:** Baire Gowda (25PG00157)  
**Academic Semester:** MCA 3rd Semester  
**Target Submission / Presentation Date:** 25 November 2026  

---

## 1. OVERVIEW

A dedicated automated screenshot utility (`capture_screenshots.py`) is provided in the project root. When executed on your Windows desktop monitor, it opens each screen, waits for visual rendering, and saves pixel-perfect PNG images directly into the `screenshots/` directory.

---

## 2. AUTOMATIC ONE-CLICK CAPTURE INSTRUCTION

1. Open PowerShell or Command Prompt in the project folder:
   ```powershell
   cd "C:\Users\BAIRE GOWDA\Downloads\Blood Bank Donor Directory & Stock Tracker"
   ```
2. Run the capture tool:
   ```powershell
   python capture_screenshots.py
   ```
3. The script will:
   - Launch each of the 5 redesigned screens in sequence.
   - Wait 1.2 seconds for layout settlement and rendering.
   - Capture each screen into `screenshots/`.

---

## 3. REQUIRED SCREENSHOT CHECKLIST FOR PROJECT REPORT

Check off each screenshot after running the script or manually capturing them:

| # | Screenshot Filename | Screen / View Description | Key Visual Elements to Verify | Status |
| :-: | :--- | :--- | :--- | :-: |
| 1 | `01_dashboard.png` | **Overview (Dashboard)** | Greeting banner ("Good morning, Baire!"), 4 KPI summary cards (Donors, Available Units, Pending Requests, Active Groups), Low Stock / Expiry alert banners, 8-group inventory matrix, and recent tables. | [ ] |
| 2 | `02_donor_directory.png` | **Donor Directory** | Form on left with Name, Blood Type, Rh, Phone, `DateEntry`, and Eligibility; Treeview table on right with search bar, filters, and count label. | [ ] |
| 3 | `03_blood_inventory.png` | **Blood Inventory** | Top 8 blood group cards (color-coded), 'Record Donation Intake' form with Spinbox & DateEntry, direct stock adjustment tab, and full stock register table with filters. | [ ] |
| 4 | `04_hospital_requests.png` | **Hospital Requisitions** | Form with Hospital Name, Group, Units Needed, Status dropdown, dynamic live stock availability indicator, and Requisition Log table. | [ ] |
| 5 | `05_about_help.png` | **About & Help Guide** | Academic student profile (Baire Gowda, 25PG00157), course info, 5-step workflow overview, and 'Reset & Populate Sample Data' button. | [ ] |

---

## 4. MANUAL CAPTURE (ALTERNATIVE METHOD)

If you prefer capturing manually:
1. Launch the application:
   ```powershell
   python main.py
   ```
2. Press **`Windows Key + Shift + S`** (Windows Snipping Tool).
3. Select the application window.
4. Paste and save the screenshots into `screenshots/` with the filenames listed above.
