# VIVA VOCE QUESTIONS & MODEL ANSWERS

**Project:** Blood Bank Donor Directory & Stock Tracker  
**Student:** Baire Gowda (25PG00157)  
**Degree:** MCA, 3rd Semester  
**Target Date:** 25 November 2026  

---

## 1. PROJECT OVERVIEW & CONCEPTUAL QUESTIONS

### Q1: What is the primary purpose of your project?
**Answer:**
"Sir/Madam, the **Blood Bank Donor Directory & Stock Tracker** is a Python desktop GUI application designed to manage blood bank operations. It addresses four core workflows:
1. Registering and tracking volunteer blood donors.
2. Managing the inventory of all eight standard blood groups (A+, A-, B+, B-, AB+, AB-, O+, O-).
3. Recording blood donations atomically by updating both donor records and inventory in a single transaction.
4. Handling emergency hospital requisitions while enforcing strict stock safety rules—preventing negative inventory, preventing duplicate deductions, and alerting staff to low stock and expired batches."

---

### Q2: Why did you build a desktop application using Tkinter instead of a web app?
**Answer:**
"Sir/Madam, in medical environments such as hospital blood banks and trauma centers, internet connectivity or remote server downtime can disrupt critical operations. A desktop application built with Python Tkinter and a local SQLite database provides:
- Zero external server latency and offline capability.
- Instant responsiveness on local workstations without browser overhead.
- Direct operating-system level reliability without network vulnerability."

---

### Q3: What is the architectural pattern used in your code?
**Answer:**
"The project follows a **Layered Architecture (MVC-Style)** separating concerns into three tiers:
1. **Presentation Layer (View):** `main.py`, `dashboard.py`, `donor.py`, `blood_stock.py`, `requests.py`—handling user interaction, `pack()` and `grid()` layouts, forms, and `ttk.Treeview` tables.
2. **Business Logic & Validation Layer (Controller):** `validators.py` and `config.py`—handling regex validation, date logic, unit constraints, and workflow rules.
3. **Data Access Layer (Model):** `database.py`—executing parameterized SQL queries and managing database connections and transactions in SQLite 3."

---

## 2. DATABASE & SQL QUESTIONS

### Q4: Explain your database schema. How many tables did you create?
**Answer:**
"I created exactly **three primary tables** as assigned by the professor:
1. `DONORS` (Columns: `donor_id`, `name`, `blood_group`, `phone`, `last_donation_date`, `eligibility`).
2. `BLOOD_STOCK` (Columns: `stock_id`, `blood_group`, `units_available`, `expiry_date`).
3. `REQUESTS` (Columns: `req_id`, `hospital_name`, `blood_group`, `units_needed`, `req_status`).

All primary keys use `INTEGER PRIMARY KEY AUTOINCREMENT`. I also created indices on `blood_group`, `phone`, and `req_status` to optimize search performance."

---

### Q5: How do you prevent SQL Injection in your application?
**Answer:**
"We use **parameterized queries** everywhere using the `?` placeholder in `sqlite3`. For example:
```python
cursor.execute("SELECT * FROM DONORS WHERE blood_group = ? AND name LIKE ?;", (bg, query))
```
We never concatenate user inputs directly into SQL strings. This ensures that the SQLite database engine compiles the query structure first, treating all user inputs strictly as literal values rather than executable code."

---

### Q6: What is an ACID transaction and where did you implement it?
**Answer:**
"An **ACID transaction** guarantees Atomicity, Consistency, Isolation, and Durability.
I implemented transactions in two critical workflows:
1. **Donation Intake:** When a donor donates blood, two tables must be updated simultaneously:
   - Update `DONORS.last_donation_date`
   - Increment `BLOOD_STOCK.units_available`
   Both statements run within a single transaction. If either fails, `conn.rollback()` is executed so that no partial update is committed.
2. **Hospital Request Fulfillment:** When dispensing blood, we check available stock and deduct units atomically before marking the request `Fulfilled`."

---

### Q7: Why does `BLOOD_STOCK` have a single expiry date per blood group?
**Answer:**
"In an industrial commercial blood bank, each physical blood bag has an individual RFID/barcode and unique expiry date. However, to strictly comply with the allocated three-table schema without creating unauthorized child tables, our application implements a **batch inventory model** where the recorded expiry date represents the earliest expiration date of the current batch for that blood group."

---

## 3. SAFE INVENTORY ALGORITHM & BUSINESS LOGIC

### Q8: How does your application prevent negative stock?
**Answer:**
"In `database.py`, before fulfilling any request or deducting units, we execute:
```python
cursor.execute("SELECT units_available FROM BLOOD_STOCK WHERE blood_group = ?;", (group,))
stock = cursor.fetchone()
if stock['units_available'] < units_needed:
    conn.rollback()
    return False, "Cannot fulfill: Insufficient blood stock."
```
If the requested units exceed available stock, the transaction is rejected, no stock is deducted, and the user receives a warning alert."

---

### Q9: How do you prevent duplicate stock deduction when a request is edited?
**Answer:**
"When `update_request()` is called, our code queries the current database state first to examine `old_status`, `old_units`, and `old_blood_group`:
- If the status was already `Fulfilled` and remains `Fulfilled` with the same units, **zero** stock change is made.
- If the quantity changed, we only adjust the net difference ($\Delta = \text{new\_units} - \text{old\_units}$).
- If a fulfilled request is changed back to `Pending` or `Rejected`, the previously deducted units are added back into inventory.
- If a fulfilled request is deleted, units are restored to inventory."

---

### Q10: How is donor eligibility handled?
**Answer:**
"Eligibility status is categorized as:
- `Eligible`
- `Not Eligible`
- `Pending Verification`

Per medical regulations, eligibility is a **human-in-the-loop medical verification**, not an automated assumption. If a staff member attempts to record a donation from a donor marked 'Not Eligible' or 'Pending Verification', the system alerts them with a warning prompt to verify medical clearance."

---

## 4. PYTHON, TKINTER & VALIDATION QUESTIONS

### Q11: Which regular expressions did you use?
**Answer:**
"In `validators.py`:
1. **Phone Validation:** `^[6-9]\d{9}$` ensures exactly 10 digits starting with valid mobile prefix digits 6, 7, 8, or 9.
2. **Donor Name Validation:** `^[A-Za-z\s\.\-']{2,70}$` validates human names containing alphabets, spaces, dots, or hyphens while rejecting numbers and special symbols.
3. **Hospital Name Validation:** `^[A-Za-z0-9\s\.\-',&()]{3,100}$` validates healthcare institution titles."

---

### Q12: Why did you use `tkcalendar.DateEntry` instead of a plain Entry widget?
**Answer:**
"A plain `Entry` widget accepts arbitrary text, requiring users to manually format dates, which frequently leads to syntax and calendar errors (such as entering February 30th). `tkcalendar.DateEntry` provides:
- A calendar drop-down widget for intuitive date selection.
- Automatic constraint enforcement using `maxdate=date.today()` to prevent future dates for past donations.
- Automatic formatting in standard ISO `YYYY-MM-DD` representation for reliable SQLite date comparisons."

---

### Q13: What is the difference between `pack()` and `grid()` in Tkinter?
**Answer:**
"- `pack()` positions widgets in blocks relative to sides (`top`, `bottom`, `left`, `right`) and is ideal for linear toolbars, headers, and footers.
- `grid()` organizes widgets into a structured 2D table of rows and columns with `rowspan`, `columnspan`, and `weight` options for responsive form alignment.
- A critical rule in Tkinter is that **`pack()` and `grid()` must never be mixed within the exact same parent container**, as this causes geometry manager conflicts and freezes the window."

---

### Q14: How does `ttk.Treeview` work with dynamic data?
**Answer:**
"`ttk.Treeview` displays multi-column tabular data. When refreshing:
1. We iterate through `tree.get_children()` and call `tree.delete(item)` to clear existing rows.
2. We iterate over rows returned by SQLite and insert each row with `tree.insert('', 'end', values=(...))`.
3. We bind `<<TreeviewSelect>>` to populate entry forms when the user clicks any row."

---

### Q15: How did you test your application?
**Answer:**
"We wrote an automated test suite using Python's standard `unittest` framework:
- `tests/test_app.py`: Contains 11 unit tests covering table creation, regex validations, donor CRUD operations, atomic donation transactions, request fulfillment, stock deduction, and duplicate deduction prevention.
- `tests/test_gui.py`: Contains 3 integration tests verifying window initialization, view switching, and form interaction.
All tests passed with zero failures."
