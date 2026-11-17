# USER GUIDE & OPERATING MANUAL

**LIFELINE | Blood Bank Donor Directory & Stock Tracker**  
*Student: Baire Gowda (25PG00157) — MCA 3rd Semester*  
*Healthcare SaaS-Inspired Desktop Application*

---

## 1. GETTING STARTED

### 1.1 Launching the Application
1. Open PowerShell or Command Prompt in the project folder.
2. Ensure dependencies are installed:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run:
   ```powershell
   python main.py
   ```
4. The main application window will open at `1320x820` with the **LIFELINE** dark teal sidebar, clean white cards, and the new healthcare SaaS layout.

---

## 2. NAVIGATION WALKTHROUGH

The left sidebar provides clean healthcare navigation:
1. **📊 Overview:** Live dashboard, statistics KPI cards, alerts, and 8-group stock status.
2. **👥 Donor Directory:** Register, edit, search, filter, and delete blood donors.
3. **🩸 Blood Inventory:** View 8-group stock status, record donations, or make manual adjustments.
4. **🏥 Hospital Requests:** Manage hospital emergency requisitions and dispense blood safely.
5. **ℹ️ About & Help:** Review academic project info and re-seed sample demo data.
6. **🚪 Exit System:** Closes the application with confirmation.

---

## 3. STEP-BY-STEP OPERATION MANUAL

### 3.1 Using the Overview Dashboard
- **Live KPI Cards:** The 4 top cards reflect current database totals:
  - *Total Registered Donors*
  - *Available Blood Units*
  - *Pending Requests*
  - *Blood Groups in Stock*
- **Warning Banners:** If any blood group falls below 5 units, a yellow warning banner appears. If 2 units or fewer, it is flagged as *CRITICAL*. If stock exceeds 42 days, an *EXPIRED* banner appears.
- **Stock Grid:** Displays unit counts and health status pills for all 8 standard blood groups at a glance.
- **Refresh:** Click `🔄 Refresh Overview` at any time to re-query the SQLite database.

---

### 3.2 Managing the Donor Directory
#### To Register a New Donor:
1. Click **👥 Donor Directory** in the sidebar.
2. Enter the donor's **Full Name** (e.g., `Suresh Kumar`).
3. Select **Blood Group** (e.g., `O`) and **Rh Factor** (e.g., `Positive (+)`).
4. Enter a **10-Digit Mobile Phone** (e.g., `9845123456`).
5. Pick the **Last Donation Date** using the calendar dropdown (`DateEntry`).
6. Select **Eligibility Status** (`Eligible`, `Not Eligible`, or `Pending Verification`).
7. Click `➕ Register Donor`. A confirmation dialog will display the assigned Donor ID.

#### To Edit or Update a Donor:
1. In the donor directory table on the right, click on any donor's row.
2. Their details will immediately populate the form on the left, and the mode will switch to *Editing Donor #ID*.
3. Modify the required fields and click `✏️ Update Profile`.

#### To Delete a Donor:
1. Select the donor from the table.
2. Click `🗑️ Delete Donor`.
3. Confirm the deletion prompt.

#### To Search or Filter Donors:
- Type a partial name or phone number in the `🔍 Search:` box and click `Search` or press `Enter`.
- Use the `Group:` dropdown to filter by specific blood group (e.g., `A+`, `O-`).
- Use the `Status:` dropdown to filter by eligibility.
- Click `Reset` to clear filters and view all donors.

---

### 3.3 Recording Blood Donations & Managing Inventory
1. Click **🩸 Blood Inventory** in the sidebar.
2. In the left panel, select the **Record Donation Intake** tab.
3. Choose a registered donor from the dropdown (e.g., `#1 - Ramesh Kumar (O+)`).
4. Select the **Units Donated** using the Spinbox (1 to 10 units; default is 1).
5. Pick the **Donation Date** (defaults to today).
6. The system automatically computes the standard 42-day RBC shelf life and sets the **Batch Expiry Date**.
7. Click `💉 Record Donation & Update Inventory`.
8. Both the donor's last donation date and the blood group inventory will update together in one atomic SQLite transaction.

#### Direct Stock Adjustment:
1. Switch to the **Direct Stock Update** tab.
2. Select the blood group.
3. Adjust the units or expiry date.
4. Click `💾 Save Stock Changes`.

---

### 3.4 Managing Hospital Requisitions & Safe Dispensing
1. Click **🏥 Hospital Requests** in the sidebar.
2. Enter the **Hospital Name** (e.g., `Columbia Asia Trauma Center`).
3. Select the required **Blood Group** and **Units Needed**.
4. The live indicator will show whether the blood bank has enough units in stock.
5. Select status:
   - `Pending`: Request is logged; no blood is deducted.
   - `Approved`: Request is authorized; blood is not yet deducted.
   - `Fulfilled`: Dispenses blood; units are deducted from inventory.
6. Click `➕ Submit Request`.

#### Quick Dispensing:
- To immediately fulfill an approved or pending request from the table, select its row and click `⚡ Dispense Blood & Fulfil Selected`. Confirm the prompt, and the units will be deducted from inventory.

---

### 3.5 Loading Presentation Sample Data
If you need to reset the database and load realistic demo data for presentation:
1. Click **ℹ️ About & Help** in the sidebar (or click `✨ Load Demo Data` on the top bar).
2. Click `✨ Reset & Populate Presentation Sample Data`.
3. Confirm the prompt. The system loads 10 donors, 8 stock records, and 6 hospital requests.
