"""
Database Layer Module
Blood Bank Donor Directory & Stock Tracker
Student: Baire Gowda (25PG00157) - MCA 3rd Semester

Manages SQLite connection, exact professor schema tables, parameterized CRUD operations,
and safe atomic transactions for donations and emergency hospital fulfillment.
"""

import sqlite3
import os
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import config


class DatabaseManager:
    """Encapsulates all SQLite database interactions with robust error handling and transactions."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.DATABASE_PATH
        # Ensure database directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Creates and returns a connection with foreign keys enabled and row factory set."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self) -> None:
        """
        Creates exactly the three primary assigned tables:
        1. DONORS
        2. BLOOD_STOCK
        3. REQUESTS
        Initializes default blood group inventory rows if table is empty.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # TABLE 1: DONORS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS DONORS (
                    donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    blood_group TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    last_donation_date TEXT,
                    eligibility TEXT NOT NULL
                );
            """)

            # TABLE 2: BLOOD_STOCK
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS BLOOD_STOCK (
                    stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    blood_group TEXT NOT NULL,
                    units_available INTEGER NOT NULL DEFAULT 0,
                    expiry_date TEXT
                );
            """)

            # TABLE 3: REQUESTS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS REQUESTS (
                    req_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hospital_name TEXT NOT NULL,
                    blood_group TEXT NOT NULL,
                    units_needed INTEGER NOT NULL,
                    req_status TEXT NOT NULL
                );
            """)

            # Create performance and search indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_donors_bg ON DONORS(blood_group);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_donors_phone ON DONORS(phone);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_bg ON BLOOD_STOCK(blood_group);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_req_status ON REQUESTS(req_status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_req_bg ON REQUESTS(blood_group);")

            # Check if BLOOD_STOCK has entries; initialize all 8 blood groups if empty
            cursor.execute("SELECT COUNT(*) as count FROM BLOOD_STOCK;")
            if cursor.fetchone()["count"] == 0:
                default_expiry = (date.today() + timedelta(days=config.SHELF_LIFE_DAYS)).strftime("%Y-%m-%d")
                for bg in config.BLOOD_GROUPS:
                    cursor.execute("""
                        INSERT INTO BLOOD_STOCK (blood_group, units_available, expiry_date)
                        VALUES (?, 0, ?);
                    """, (bg, default_expiry))

            conn.commit()

    # =========================================================================
    # DONOR CRUD OPERATIONS
    # =========================================================================

    def add_donor(self, name: str, blood_group: str, phone: str,
                  last_donation_date: str, eligibility: str) -> int:
        """Inserts a new donor record and returns the new donor_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO DONORS (name, blood_group, phone, last_donation_date, eligibility)
                VALUES (?, ?, ?, ?, ?);
            """, (name.strip(), blood_group.strip(), phone.strip(),
                  last_donation_date.strip() if last_donation_date else None,
                  eligibility.strip()))
            conn.commit()
            return cursor.lastrowid

    def get_all_donors(self) -> List[Dict[str, Any]]:
        """Retrieves all donors ordered by donor_id descending."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DONORS ORDER BY donor_id DESC;")
            return [dict(row) for row in cursor.fetchall()]

    def get_donor_by_id(self, donor_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single donor by donor_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DONORS WHERE donor_id = ?;", (donor_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_donor(self, donor_id: int, name: str, blood_group: str,
                     phone: str, last_donation_date: str, eligibility: str) -> bool:
        """Updates an existing donor record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE DONORS
                SET name = ?, blood_group = ?, phone = ?, last_donation_date = ?, eligibility = ?
                WHERE donor_id = ?;
            """, (name.strip(), blood_group.strip(), phone.strip(),
                  last_donation_date.strip() if last_donation_date else None,
                  eligibility.strip(), donor_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_donor(self, donor_id: int) -> bool:
        """Deletes a donor by donor_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM DONORS WHERE donor_id = ?;", (donor_id,))
            conn.commit()
            return cursor.rowcount > 0

    def search_donors(self, query: Optional[str] = None,
                      blood_group: Optional[str] = None,
                      eligibility: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Searches and filters donors dynamically using parameterized queries.
        Supports matching on name or phone, plus group and eligibility filters.
        """
        sql = "SELECT * FROM DONORS WHERE 1=1"
        params: List[Any] = []

        if query and query.strip():
            clean_q = f"%{query.strip()}%"
            sql += " AND (name LIKE ? OR phone LIKE ?)"
            params.extend([clean_q, clean_q])

        if blood_group and blood_group.strip() and blood_group != "All Groups":
            sql += " AND blood_group = ?"
            params.append(blood_group.strip())

        if eligibility and eligibility.strip() and eligibility != "All Statuses":
            sql += " AND eligibility = ?"
            params.append(eligibility.strip())

        sql += " ORDER BY donor_id DESC;"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # BLOOD STOCK OPERATIONS
    # =========================================================================

    def get_all_stock(self) -> List[Dict[str, Any]]:
        """Retrieves all blood stock entries ordered by blood_group."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM BLOOD_STOCK ORDER BY blood_group ASC;")
            return [dict(row) for row in cursor.fetchall()]

    def get_stock_by_group(self, blood_group: str) -> Optional[Dict[str, Any]]:
        """Retrieves stock information for a specific blood group."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM BLOOD_STOCK WHERE blood_group = ?;", (blood_group.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_stock_record(self, stock_id: int, units_available: int, expiry_date: str) -> bool:
        """Updates units and expiry date for a specific stock record."""
        if units_available < 0:
            raise ValueError("Blood stock units cannot be negative.")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE BLOOD_STOCK
                SET units_available = ?, expiry_date = ?
                WHERE stock_id = ?;
            """, (units_available, expiry_date.strip(), stock_id))
            conn.commit()
            return cursor.rowcount > 0

    def add_direct_stock(self, blood_group: str, units_to_add: int, expiry_date: str) -> bool:
        """
        Increases stock for a blood group by units_to_add and updates expiry date.
        If a record does not exist for this blood group, inserts one.
        """
        if units_to_add <= 0:
            raise ValueError("Units to add must be greater than zero.")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM BLOOD_STOCK WHERE blood_group = ?;", (blood_group.strip(),))
            row = cursor.fetchone()
            if row:
                new_units = row["units_available"] + units_to_add
                cursor.execute("""
                    UPDATE BLOOD_STOCK
                    SET units_available = ?, expiry_date = ?
                    WHERE stock_id = ?;
                """, (new_units, expiry_date.strip(), row["stock_id"]))
            else:
                cursor.execute("""
                    INSERT INTO BLOOD_STOCK (blood_group, units_available, expiry_date)
                    VALUES (?, ?, ?);
                """, (blood_group.strip(), units_to_add, expiry_date.strip()))
            conn.commit()
            return True

    def record_donation(self, donor_id: int, units: int,
                        donation_date: str, expiry_date: str) -> Tuple[bool, str]:
        """
        ATOMIC TRANSACTION:
        1. Validates donor exists.
        2. Validates units > 0.
        3. Updates donor's last_donation_date.
        4. Increases corresponding blood stock in BLOOD_STOCK.
        5. Commits both together. Rolls back on any failure.
        """
        if units <= 0:
            return False, "Donated units must be greater than zero."

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # 1. Fetch donor
            cursor.execute("SELECT * FROM DONORS WHERE donor_id = ?;", (donor_id,))
            donor = cursor.fetchone()
            if not donor:
                conn.rollback()
                return False, f"Donor ID {donor_id} not found."

            blood_group = donor["blood_group"]

            # 2. Update donor's last donation date
            cursor.execute("""
                UPDATE DONORS
                SET last_donation_date = ?
                WHERE donor_id = ?;
            """, (donation_date.strip(), donor_id))

            # 3. Increase blood stock
            cursor.execute("SELECT * FROM BLOOD_STOCK WHERE blood_group = ?;", (blood_group,))
            stock = cursor.fetchone()
            if stock:
                new_units = stock["units_available"] + units
                cursor.execute("""
                    UPDATE BLOOD_STOCK
                    SET units_available = ?, expiry_date = ?
                    WHERE stock_id = ?;
                """, (new_units, expiry_date.strip(), stock["stock_id"]))
            else:
                cursor.execute("""
                    INSERT INTO BLOOD_STOCK (blood_group, units_available, expiry_date)
                    VALUES (?, ?, ?);
                """, (blood_group, units, expiry_date.strip()))

            conn.commit()
            return True, f"Successfully recorded {units} unit(s) of {blood_group} from {donor['name']}."
        except Exception as e:
            conn.rollback()
            return False, f"Transaction error during donation: {str(e)}"
        finally:
            conn.close()

    # =========================================================================
    # EMERGENCY REQUEST OPERATIONS (WITH SAFE INVENTORY DEDUCTION)
    # =========================================================================

    def get_all_requests(self) -> List[Dict[str, Any]]:
        """Retrieves all hospital requests ordered by req_id descending."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM REQUESTS ORDER BY req_id DESC;")
            return [dict(row) for row in cursor.fetchall()]

    def get_request_by_id(self, req_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single request by req_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM REQUESTS WHERE req_id = ?;", (req_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_request(self, hospital_name: str, blood_group: str,
                    units_needed: int, req_status: str) -> Tuple[bool, str, Optional[int]]:
        """
        Creates a new hospital request.
        If status is 'Fulfilled' right at creation, checks stock availability and
        deducts units within an atomic transaction.
        """
        if units_needed <= 0:
            return False, "Units needed must be greater than zero.", None

        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            if req_status == "Fulfilled":
                cursor.execute("SELECT * FROM BLOOD_STOCK WHERE blood_group = ?;", (blood_group.strip(),))
                stock = cursor.fetchone()
                current_units = stock["units_available"] if stock else 0
                if current_units < units_needed:
                    conn.rollback()
                    return False, (f"Insufficient stock for {blood_group}: "
                                  f"requested {units_needed} units, but only {current_units} available."), None

                # Deduct stock
                cursor.execute("""
                    UPDATE BLOOD_STOCK
                    SET units_available = units_available - ?
                    WHERE blood_group = ?;
                """, (units_needed, blood_group.strip()))

            # Insert Request
            cursor.execute("""
                INSERT INTO REQUESTS (hospital_name, blood_group, units_needed, req_status)
                VALUES (?, ?, ?, ?);
            """, (hospital_name.strip(), blood_group.strip(), units_needed, req_status.strip()))

            new_id = cursor.lastrowid
            conn.commit()
            return True, f"Request #{new_id} created successfully.", new_id
        except Exception as e:
            conn.rollback()
            return False, f"Failed to create request: {str(e)}", None
        finally:
            conn.close()

    def update_request(self, req_id: int, hospital_name: str, blood_group: str,
                       units_needed: int, req_status: str) -> Tuple[bool, str]:
        """
        SAFE INVENTORY UPDATE TRANSACTION:
        Prevents duplicate stock deductions and prevents negative stock.
        Handles transition between old_status and new req_status:
        - Non-Fulfilled -> Fulfilled: checks stock availability and deducts units.
        - Fulfilled -> Non-Fulfilled: restores previously deducted units to stock.
        - Fulfilled -> Fulfilled: adjusts difference safely (deducts net increase or restores net decrease).
        - Non-Fulfilled -> Non-Fulfilled: only metadata updated.
        """
        if units_needed <= 0:
            return False, "Units needed must be greater than zero."

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM REQUESTS WHERE req_id = ?;", (req_id,))
            old_req = cursor.fetchone()
            if not old_req:
                conn.rollback()
                return False, f"Request ID {req_id} not found."

            old_status = old_req["req_status"]
            old_group = old_req["blood_group"]
            old_units = old_req["units_needed"]

            new_status = req_status.strip()
            new_group = blood_group.strip()
            new_units = units_needed

            # Case 1: Was NOT Fulfilled, now transitioning to Fulfilled
            if old_status != "Fulfilled" and new_status == "Fulfilled":
                cursor.execute("SELECT * FROM BLOOD_STOCK WHERE blood_group = ?;", (new_group,))
                stock = cursor.fetchone()
                current_units = stock["units_available"] if stock else 0
                if current_units < new_units:
                    conn.rollback()
                    return False, (f"Cannot fulfill request: Available {new_group} stock ({current_units}) "
                                  f"is less than requested units ({new_units}).")
                # Deduct units
                cursor.execute("""
                    UPDATE BLOOD_STOCK
                    SET units_available = units_available - ?
                    WHERE blood_group = ?;
                """, (new_units, new_group))

            # Case 2: WAS Fulfilled, now changed back to Non-Fulfilled (e.g. Cancelled/Rejected/Pending)
            elif old_status == "Fulfilled" and new_status != "Fulfilled":
                # Restore old units back to stock
                cursor.execute("""
                    UPDATE BLOOD_STOCK
                    SET units_available = units_available + ?
                    WHERE blood_group = ?;
                """, (old_units, old_group))

            # Case 3: WAS Fulfilled, and REMAINS Fulfilled (quantity or blood group changed)
            elif old_status == "Fulfilled" and new_status == "Fulfilled":
                if old_group == new_group:
                    diff = new_units - old_units
                    if diff > 0:
                        # Need more units
                        cursor.execute("SELECT * FROM BLOOD_STOCK WHERE blood_group = ?;", (new_group,))
                        stock = cursor.fetchone()
                        current_units = stock["units_available"] if stock else 0
                        if current_units < diff:
                            conn.rollback()
                            return False, (f"Cannot increase fulfillment by {diff} units: "
                                          f"only {current_units} additional units of {new_group} available.")
                        cursor.execute("""
                            UPDATE BLOOD_STOCK
                            SET units_available = units_available - ?
                            WHERE blood_group = ?;
                        """, (diff, new_group))
                    elif diff < 0:
                        # Returned units
                        restore_qty = abs(diff)
                        cursor.execute("""
                            UPDATE BLOOD_STOCK
                            SET units_available = units_available + ?
                            WHERE blood_group = ?;
                        """, (restore_qty, new_group))
                else:
                    # Blood group changed while fulfilled! Return old, check and deduct new
                    cursor.execute("""
                        UPDATE BLOOD_STOCK
                        SET units_available = units_available + ?
                        WHERE blood_group = ?;
                    """, (old_units, old_group))

                    cursor.execute("SELECT * FROM BLOOD_STOCK WHERE blood_group = ?;", (new_group,))
                    stock = cursor.fetchone()
                    current_units = stock["units_available"] if stock else 0
                    if current_units < new_units:
                        conn.rollback()
                        return False, (f"Cannot fulfill updated group {new_group}: "
                                      f"only {current_units} units available, needed {new_units}.")

                    cursor.execute("""
                        UPDATE BLOOD_STOCK
                        SET units_available = units_available - ?
                        WHERE blood_group = ?;
                    """, (new_units, new_group))

            # Case 4: Neither old nor new was fulfilled -> No stock change needed.

            # Update the REQUESTS table
            cursor.execute("""
                UPDATE REQUESTS
                SET hospital_name = ?, blood_group = ?, units_needed = ?, req_status = ?
                WHERE req_id = ?;
            """, (hospital_name.strip(), new_group, new_units, new_status, req_id))

            conn.commit()
            return True, f"Request #{req_id} successfully updated."
        except Exception as e:
            conn.rollback()
            return False, f"Failed to update request: {str(e)}"
        finally:
            conn.close()

    def delete_request(self, req_id: int, restore_if_fulfilled: bool = True) -> Tuple[bool, str]:
        """
        Deletes a hospital request. If it was fulfilled, restores the units
        back into BLOOD_STOCK to maintain accurate inventory accounting.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM REQUESTS WHERE req_id = ?;", (req_id,))
            req = cursor.fetchone()
            if not req:
                conn.rollback()
                return False, f"Request ID {req_id} not found."

            if req["req_status"] == "Fulfilled" and restore_if_fulfilled:
                cursor.execute("""
                    UPDATE BLOOD_STOCK
                    SET units_available = units_available + ?
                    WHERE blood_group = ?;
                """, (req["units_needed"], req["blood_group"]))

            cursor.execute("DELETE FROM REQUESTS WHERE req_id = ?;", (req_id,))
            conn.commit()
            return True, f"Request #{req_id} deleted successfully."
        except Exception as e:
            conn.rollback()
            return False, f"Failed to delete request: {str(e)}"
        finally:
            conn.close()

    def search_requests(self, query: Optional[str] = None,
                        status_filter: Optional[str] = None,
                        blood_group: Optional[str] = None) -> List[Dict[str, Any]]:
        """Searches hospital requests by name, status, or blood group."""
        sql = "SELECT * FROM REQUESTS WHERE 1=1"
        params: List[Any] = []

        if query and query.strip():
            clean_q = f"%{query.strip()}%"
            sql += " AND hospital_name LIKE ?"
            params.append(clean_q)

        if status_filter and status_filter.strip() and status_filter != "All Statuses":
            sql += " AND req_status = ?"
            params.append(status_filter.strip())

        if blood_group and blood_group.strip() and blood_group != "All Groups":
            sql += " AND blood_group = ?"
            params.append(blood_group.strip())

        sql += " ORDER BY req_id DESC;"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # DASHBOARD STATISTICS & ALERTS
    # =========================================================================

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Computes real-time statistics from SQLite:
        - Total Donors
        - Total Blood Units Available (non-expired)
        - Pending Requests
        - Approved Requests
        - Fulfilled Requests
        - Active Blood Groups In Stock
        - Low-Stock and Expiry Alerts
        - Recent Donors & Requests
        """
        stats: Dict[str, Any] = {}
        today_str = date.today().strftime("%Y-%m-%d")
        warn_expiry_str = (date.today() + timedelta(days=config.EXPIRY_WARN_DAYS)).strftime("%Y-%m-%d")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Total Donors
            cursor.execute("SELECT COUNT(*) AS total FROM DONORS;")
            stats["total_donors"] = cursor.fetchone()["total"]

            # 2. Eligible Donors
            cursor.execute("SELECT COUNT(*) AS total FROM DONORS WHERE eligibility = 'Eligible';")
            stats["eligible_donors"] = cursor.fetchone()["total"]

            # 3. Blood Stock Stats
            cursor.execute("SELECT * FROM BLOOD_STOCK ORDER BY blood_group ASC;")
            stock_rows = [dict(r) for r in cursor.fetchall()]
            stats["stock_rows"] = stock_rows

            total_units = 0
            groups_available = 0
            low_stock_alerts = []
            expiry_alerts = []

            for item in stock_rows:
                units = item["units_available"]
                bg = item["blood_group"]
                exp = item["expiry_date"]

                # Is expired?
                is_expired = False
                if exp:
                    try:
                        exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
                        if exp_date < date.today():
                            is_expired = True
                    except ValueError:
                        pass

                # Only non-expired stock counts as usable available units
                if not is_expired:
                    total_units += units
                    if units > 0:
                        groups_available += 1

                # Alerts
                if is_expired and units > 0:
                    expiry_alerts.append({
                        "blood_group": bg,
                        "units": units,
                        "expiry_date": exp,
                        "status": "EXPIRED"
                    })
                elif exp and exp <= warn_expiry_str and units > 0:
                    expiry_alerts.append({
                        "blood_group": bg,
                        "units": units,
                        "expiry_date": exp,
                        "status": "EXPIRING SOON"
                    })

                if units < config.LOW_STOCK_THRESHOLD:
                    low_stock_alerts.append({
                        "blood_group": bg,
                        "units": units,
                        "status": "CRITICAL" if units <= config.CRITICAL_STOCK_THRESHOLD else "LOW"
                    })

            stats["total_blood_units"] = total_units
            stats["groups_available"] = groups_available
            stats["low_stock_alerts"] = low_stock_alerts
            stats["expiry_alerts"] = expiry_alerts

            # 4. Request statistics
            cursor.execute("SELECT req_status, COUNT(*) AS count FROM REQUESTS GROUP BY req_status;")
            req_counts = {row["req_status"]: row["count"] for row in cursor.fetchall()}
            stats["pending_requests"] = req_counts.get("Pending", 0)
            stats["approved_requests"] = req_counts.get("Approved", 0)
            stats["fulfilled_requests"] = req_counts.get("Fulfilled", 0)
            stats["rejected_requests"] = req_counts.get("Rejected", 0)
            stats["total_requests"] = sum(req_counts.values())

            # 5. Recent Donors (Last 5 unique donors)
            cursor.execute("""
                SELECT * FROM DONORS 
                WHERE donor_id IN (
                    SELECT MAX(donor_id) FROM DONORS GROUP BY phone
                ) 
                ORDER BY donor_id DESC LIMIT 5;
            """)
            stats["recent_donors"] = [dict(r) for r in cursor.fetchall()]

            # 6. Recent Requests (Last 5 unique hospital requisitions)
            cursor.execute("""
                SELECT * FROM REQUESTS 
                WHERE req_id IN (
                    SELECT MAX(req_id) FROM REQUESTS GROUP BY hospital_name, blood_group
                ) 
                ORDER BY req_id DESC LIMIT 5;
            """)
            stats["recent_requests"] = [dict(r) for r in cursor.fetchall()]

        return stats

    # =========================================================================
    # SAMPLE DATA SEEDING (FOR VIVA / PRESENTATION)
    # =========================================================================

    def seed_sample_data(self, force: bool = False) -> bool:
        """
        Seeds realistic presentation demo data if database is empty or if forced.
        Will NOT overwrite existing donor records unless force=True.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM DONORS;")
            if cursor.fetchone()["count"] > 0 and not force:
                return False  # Already has data

            # Clear if forced
            if force:
                cursor.execute("DELETE FROM DONORS;")
                cursor.execute("DELETE FROM REQUESTS;")
                cursor.execute("DELETE FROM BLOOD_STOCK;")

            # 1. Seed Donors
            today = date.today()
            sample_donors = [
                ("Ramesh Kumar", "O+", "9845123456", (today - timedelta(days=95)).strftime("%Y-%m-%d"), "Eligible"),
                ("Sneha Patil", "A+", "9741234567", (today - timedelta(days=40)).strftime("%Y-%m-%d"), "Not Eligible"),
                ("Mohammed Irfan", "B+", "9988776655", (today - timedelta(days=120)).strftime("%Y-%m-%d"), "Eligible"),
                ("Priya Sharma", "AB+", "9876543210", (today - timedelta(days=15)).strftime("%Y-%m-%d"), "Not Eligible"),
                ("Anand Gowda", "O-", "9448123789", (today - timedelta(days=180)).strftime("%Y-%m-%d"), "Eligible"),
                ("Kavya Nair", "A-", "9123456780", (today - timedelta(days=110)).strftime("%Y-%m-%d"), "Eligible"),
                ("Vikramaditya Rao", "B-", "9654321870", (today - timedelta(days=60)).strftime("%Y-%m-%d"), "Pending Verification"),
                ("Divya Lakshmi", "AB-", "9532147890", (today - timedelta(days=150)).strftime("%Y-%m-%d"), "Eligible"),
                ("Manjunath Reddy", "O+", "9880123456", (today - timedelta(days=200)).strftime("%Y-%m-%d"), "Eligible"),
                ("Deepika Hegde", "B+", "9731234567", (today - timedelta(days=30)).strftime("%Y-%m-%d"), "Pending Verification"),
            ]
            cursor.executemany("""
                INSERT INTO DONORS (name, blood_group, phone, last_donation_date, eligibility)
                VALUES (?, ?, ?, ?, ?);
            """, sample_donors)

            # 2. Seed Stock (Ensure all 8 groups have realistic initial units)
            sample_stock = [
                ("A+", 14, (today + timedelta(days=28)).strftime("%Y-%m-%d")),
                ("A-", 4, (today + timedelta(days=18)).strftime("%Y-%m-%d")),
                ("B+", 18, (today + timedelta(days=35)).strftime("%Y-%m-%d")),
                ("B-", 3, (today + timedelta(days=12)).strftime("%Y-%m-%d")),
                ("AB+", 6, (today + timedelta(days=22)).strftime("%Y-%m-%d")),
                ("AB-", 2, (today + timedelta(days=5)).strftime("%Y-%m-%d")),    # Low & Expiring soon
                ("O+", 22, (today + timedelta(days=32)).strftime("%Y-%m-%d")),
                ("O-", 5, (today + timedelta(days=25)).strftime("%Y-%m-%d")),
            ]
            cursor.execute("DELETE FROM BLOOD_STOCK;")
            cursor.executemany("""
                INSERT INTO BLOOD_STOCK (blood_group, units_available, expiry_date)
                VALUES (?, ?, ?);
            """, sample_stock)

            # 3. Seed Requests
            sample_requests = [
                ("Apollo Multispeciality Hospital", "O+", 3, "Fulfilled"),
                ("Manipal Hospital Trauma Center", "A+", 2, "Pending"),
                ("Fortis Healthcare Emergency", "B-", 1, "Approved"),
                ("St. John's Medical College Hospital", "AB-", 2, "Pending"),
                ("Victoria Government Hospital", "O-", 4, "Pending"),
                ("Columbia Asia Referral Hospital", "B+", 3, "Fulfilled"),
            ]
            cursor.executemany("""
                INSERT INTO REQUESTS (hospital_name, blood_group, units_needed, req_status)
                VALUES (?, ?, ?, ?);
            """, sample_requests)

            conn.commit()
            return True
