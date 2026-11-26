"""
Automated Test Suite
Blood Bank Donor Directory & Stock Tracker
Student: Baire Gowda (25PG00157) - MCA 3rd Semester
Tests database CRUD, transactions, validations, stock integrity, and edge cases.
"""

import unittest
import os
import sqlite3
import tempfile
from datetime import date, timedelta

import validators
from database import DatabaseManager
import config


class TestBloodBankSystem(unittest.TestCase):
    """Full test suite covering database operations, validations, and inventory logic."""

    def setUp(self):
        # Create a temporary SQLite database for isolated test execution
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        self.db = DatabaseManager(db_path=self.temp_db_path)

    def tearDown(self):
        # Clean up temporary database file
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except PermissionError:
                pass

    # =========================================================================
    # 1. DATABASE SCHEMA & TABLE INTEGRITY
    # =========================================================================

    def test_tables_created(self):
        """Verifies that exactly the three required tables exist in SQLite."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row["name"] for row in cursor.fetchall()]

            self.assertIn("DONORS", tables)
            self.assertIn("BLOOD_STOCK", tables)
            self.assertIn("REQUESTS", tables)

    def test_stock_initialization(self):
        """Verifies that all 8 blood groups are initialized with records."""
        stock = self.db.get_all_stock()
        self.assertEqual(len(stock), 8)
        groups = [r["blood_group"] for r in stock]
        for bg in config.BLOOD_GROUPS:
            self.assertIn(bg, groups)

    # =========================================================================
    # 2. VALIDATOR TESTS
    # =========================================================================

    def test_name_validation(self):
        """Tests donor name validation rules."""
        valid, val = validators.validate_name("Baire Gowda")
        self.assertTrue(valid)
        self.assertEqual(val, "Baire Gowda")

        valid, _ = validators.validate_name("Dr. A. P. J. Abdul-Kalam")
        self.assertTrue(valid)

        # Invalid cases
        valid, _ = validators.validate_name("")
        self.assertFalse(valid)
        valid, _ = validators.validate_name("A")  # Too short
        self.assertFalse(valid)
        valid, _ = validators.validate_name("John123")  # Contains numbers
        self.assertFalse(valid)

    def test_phone_validation(self):
        """Tests 10-digit phone number regex validation."""
        valid, val = validators.validate_phone("9845123456")
        self.assertTrue(valid)
        self.assertEqual(val, "9845123456")

        # Invalid formats
        valid, _ = validators.validate_phone("12345")  # Too short
        self.assertFalse(valid)
        valid, _ = validators.validate_phone("98451234567")  # 11 digits
        self.assertFalse(valid)
        valid, _ = validators.validate_phone("98451ABC56")  # Alphabetic
        self.assertFalse(valid)

    def test_date_validation(self):
        """Tests calendar date validation and future date restriction."""
        today_str = date.today().strftime("%Y-%m-%d")
        valid, _ = validators.validate_date(today_str, allow_future=False)
        self.assertTrue(valid)

        # Future date rejected when allow_future=False
        tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        valid, _ = validators.validate_date(tomorrow_str, allow_future=False)
        self.assertFalse(valid)

        # Future date allowed for expiry
        valid, _ = validators.validate_expiry_date(tomorrow_str)
        self.assertTrue(valid)

        # Invalid calendar date
        valid, _ = validators.validate_date("2026-02-30", allow_future=True)
        self.assertFalse(valid)

    def test_units_validation(self):
        """Tests unit count validation."""
        valid, val = validators.validate_units(5)
        self.assertTrue(valid)
        self.assertEqual(val, 5)

        # Zero and negative units rejected
        valid, _ = validators.validate_units(0)
        self.assertFalse(valid)
        valid, _ = validators.validate_units(-3)
        self.assertFalse(valid)
        valid, _ = validators.validate_units("abc")
        self.assertFalse(valid)

    # =========================================================================
    # 3. DONOR CRUD TESTS
    # =========================================================================

    def test_donor_crud_operations(self):
        """Tests adding, reading, updating, and deleting donor records."""
        # Add donor
        donor_id = self.db.add_donor(
            name="Rohan Murthy",
            blood_group="O+",
            phone="9876543210",
            last_donation_date="2026-01-10",
            eligibility="Eligible"
        )
        self.assertIsInstance(donor_id, int)
        self.assertGreater(donor_id, 0)

        # Read donor
        donor = self.db.get_donor_by_id(donor_id)
        self.assertIsNotNone(donor)
        self.assertEqual(donor["name"], "Rohan Murthy")
        self.assertEqual(donor["blood_group"], "O+")

        # Update donor
        updated = self.db.update_donor(
            donor_id=donor_id,
            name="Rohan Murthy Senior",
            blood_group="O+",
            phone="9876543210",
            last_donation_date="2026-03-15",
            eligibility="Not Eligible"
        )
        self.assertTrue(updated)
        donor = self.db.get_donor_by_id(donor_id)
        self.assertEqual(donor["name"], "Rohan Murthy Senior")
        self.assertEqual(donor["eligibility"], "Not Eligible")

        # Delete donor
        deleted = self.db.delete_donor(donor_id)
        self.assertTrue(deleted)
        self.assertIsNone(self.db.get_donor_by_id(donor_id))

    # =========================================================================
    # 4. BLOOD DONATION TRANSACTION TEST
    # =========================================================================

    def test_record_donation_transaction(self):
        """
        Tests atomic donation intake:
        Updates donor's last donation date AND increases blood stock in a transaction.
        """
        # Register a donor
        donor_id = self.db.add_donor(
            name="Suresh Rao",
            blood_group="B+",
            phone="9845112233",
            last_donation_date="2025-10-01",
            eligibility="Eligible"
        )

        initial_stock = self.db.get_stock_by_group("B+")
        initial_units = initial_stock["units_available"]

        # Record a donation of 2 units
        donation_date = date.today().strftime("%Y-%m-%d")
        expiry_date = (date.today() + timedelta(days=42)).strftime("%Y-%m-%d")

        success, msg = self.db.record_donation(
            donor_id=donor_id,
            units=2,
            donation_date=donation_date,
            expiry_date=expiry_date
        )
        self.assertTrue(success)

        # Verify donor last donation date was updated
        donor = self.db.get_donor_by_id(donor_id)
        self.assertEqual(donor["last_donation_date"], donation_date)

        # Verify stock increased by exactly 2
        updated_stock = self.db.get_stock_by_group("B+")
        self.assertEqual(updated_stock["units_available"], initial_units + 2)

    # =========================================================================
    # 5. EMERGENCY REQUEST & SAFE INVENTORY LOGIC TESTS
    # =========================================================================

    def test_emergency_request_stock_deduction(self):
        """
        Tests safe inventory deduction on request fulfillment:
        - Pending requests do NOT deduct stock.
        - Fulfilling deducts stock.
        - Cannot fulfill if stock is insufficient.
        """
        # Set stock for A+ to 5 units
        stock = self.db.get_stock_by_group("A+")
        self.db.update_stock_record(stock["stock_id"], 5, "2026-12-31")

        # Create a Pending request for 3 units
        success, msg, req_id = self.db.add_request(
            hospital_name="City General Hospital",
            blood_group="A+",
            units_needed=3,
            req_status="Pending"
        )
        self.assertTrue(success)

        # Verify stock was NOT deducted for Pending
        stock = self.db.get_stock_by_group("A+")
        self.assertEqual(stock["units_available"], 5)

        # Now fulfill the request
        success, msg = self.db.update_request(
            req_id=req_id,
            hospital_name="City General Hospital",
            blood_group="A+",
            units_needed=3,
            req_status="Fulfilled"
        )
        self.assertTrue(success)

        # Verify stock is now 5 - 3 = 2 units
        stock = self.db.get_stock_by_group("A+")
        self.assertEqual(stock["units_available"], 2)

        # Try to fulfill another request needing 4 units (more than available 2)
        success2, msg2, req_id2 = self.db.add_request(
            hospital_name="Trauma Care",
            blood_group="A+",
            units_needed=4,
            req_status="Fulfilled"
        )
        # Must fail because only 2 units are available!
        self.assertFalse(success2)
        self.assertIn("Insufficient stock", msg2)

        # Stock must remain 2 (negative stock prevented!)
        stock = self.db.get_stock_by_group("A+")
        self.assertEqual(stock["units_available"], 2)

    def test_prevent_duplicate_deduction_on_update(self):
        """
        Tests that editing an already-fulfilled request does NOT repeatedly deduct stock.
        """
        # Set stock for O- to 10 units
        stock = self.db.get_stock_by_group("O-")
        self.db.update_stock_record(stock["stock_id"], 10, "2026-12-31")

        # Create and fulfill request for 3 units (stock becomes 7)
        success, msg, req_id = self.db.add_request("Govt Hospital", "O-", 3, "Fulfilled")
        self.assertTrue(success)
        stock = self.db.get_stock_by_group("O-")
        self.assertEqual(stock["units_available"], 7)

        # Update the hospital name only, leaving units at 3 and status at Fulfilled
        success, msg = self.db.update_request(req_id, "Govt Hospital New Wing", "O-", 3, "Fulfilled")
        self.assertTrue(success)

        # Stock MUST STILL be 7, not 4!
        stock = self.db.get_stock_by_group("O-")
        self.assertEqual(stock["units_available"], 7)

    def test_stock_restoration_on_revert_or_delete(self):
        """
        Tests that if a fulfilled request is changed back to Pending/Rejected
        or deleted, the stock is safely restored.
        """
        # Set stock for AB+ to 6 units
        stock = self.db.get_stock_by_group("AB+")
        self.db.update_stock_record(stock["stock_id"], 6, "2026-12-31")

        # Fulfill request for 2 units (stock becomes 4)
        success, msg, req_id = self.db.add_request("Apex Hospital", "AB+", 2, "Fulfilled")
        self.assertTrue(success)
        stock = self.db.get_stock_by_group("AB+")
        self.assertEqual(stock["units_available"], 4)

        # Revert request to 'Rejected' (patient no longer needs blood)
        success, msg = self.db.update_request(req_id, "Apex Hospital", "AB+", 2, "Rejected")
        self.assertTrue(success)

        # Stock must be restored back to 6!
        stock = self.db.get_stock_by_group("AB+")
        self.assertEqual(stock["units_available"], 6)

        # Fulfill again (stock becomes 4)
        self.db.update_request(req_id, "Apex Hospital", "AB+", 2, "Fulfilled")
        stock = self.db.get_stock_by_group("AB+")
        self.assertEqual(stock["units_available"], 4)

        # Delete fulfilled request -> stock must be restored to 6!
        self.db.delete_request(req_id, restore_if_fulfilled=True)
        stock = self.db.get_stock_by_group("AB+")
        self.assertEqual(stock["units_available"], 6)

    # =========================================================================
    # 6. CONNECTION LIFECYCLE & TRANSACTION ROLLBACK TESTS
    # =========================================================================

    def test_connection_lifecycle_closed(self):
        """Verifies that connection_scope properly closes the connection upon exit."""
        captured_conn = None
        with self.db.connection_scope() as conn:
            captured_conn = conn
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            self.assertEqual(cursor.fetchone()[0], 1)
            cursor.close()

        # Outside the context manager, the connection must be closed
        # Executing a query on a closed connection raises sqlite3.ProgrammingError
        with self.assertRaises(sqlite3.ProgrammingError):
            captured_conn.execute("SELECT 1;")

    def test_transaction_rollback_on_failure(self):
        """
        Verifies that multi-step transactions roll back completely if an error
        occurs AFTER an initial modification within the transaction.
        """
        donor_id = self.db.add_donor(
            name="Rollback Test Donor",
            blood_group="O+",
            phone="9876543211",
            last_donation_date="2026-01-01",
            eligibility="Eligible"
        )
        initial_stock = self.db.get_stock_by_group("O+")["units_available"]

        # Execute a transaction that modifies the donor, but then triggers a failure
        try:
            with self.db.connection_scope() as conn:
                cursor = conn.cursor()
                # 1. First modification: update donor name
                cursor.execute("UPDATE DONORS SET name = 'Modified Name' WHERE donor_id = ?;", (donor_id,))
                
                # 2. Simulated failure after initial modification: invalid table query
                cursor.execute("INSERT INTO NON_EXISTENT_TABLE VALUES (1);")
                cursor.close()
        except sqlite3.OperationalError:
            pass  # Expected simulated failure

        # Verify that the first modification was completely rolled back!
        donor = self.db.get_donor_by_id(donor_id)
        self.assertEqual(donor["name"], "Rollback Test Donor")

        # Confirm stock was unchanged
        current_stock = self.db.get_stock_by_group("O+")["units_available"]
        self.assertEqual(current_stock, initial_stock)

    def test_fulfilled_blood_group_change_insufficient_stock_rollback(self):
        """
        REGRESSION TEST:
        When an already Fulfilled request is changed to a different blood group,
        if the new blood group has insufficient stock:
        - The update must fail (return False).
        - The old blood group's stock must NOT be restored or changed.
        - The new blood group's stock must NOT be changed.
        - The original request record must remain unchanged.
        """
        # 1. Setup exact scenario: O+ has 5 units, A+ has 0 units
        o_stock = self.db.get_stock_by_group("O+")
        a_stock = self.db.get_stock_by_group("A+")
        self.db.update_stock_record(o_stock["stock_id"], 5, "2026-12-31")
        self.db.update_stock_record(a_stock["stock_id"], 0, "2026-12-31")

        # 2. Fulfill a request for 2 units of O+ -> O+ stock becomes 3
        success, msg, req_id = self.db.add_request("City Hospital", "O+", 2, "Fulfilled")
        self.assertTrue(success)
        self.assertEqual(self.db.get_stock_by_group("O+")["units_available"], 3)
        self.assertEqual(self.db.get_stock_by_group("A+")["units_available"], 0)

        # 3. Attempt to change the fulfilled request to A+ (2 units) when A+ has 0 units
        update_success, update_msg = self.db.update_request(req_id, "City Hospital", "A+", 2, "Fulfilled")

        # 4. Verification:
        # a) Update must return False
        self.assertFalse(update_success)
        self.assertIn("Cannot fulfill updated group A+", update_msg)

        # b) O+ stock MUST REMAIN AT 3 (must NOT be restored to 5!)
        self.assertEqual(self.db.get_stock_by_group("O+")["units_available"], 3)

        # c) A+ stock MUST REMAIN AT 0
        self.assertEqual(self.db.get_stock_by_group("A+")["units_available"], 0)

        # d) Original request in REQUESTS table must remain unchanged (O+, 2 units, Fulfilled)
        req = self.db.get_request_by_id(req_id)
        self.assertEqual(req["blood_group"], "O+")
        self.assertEqual(req["units_needed"], 2)
        self.assertEqual(req["req_status"], "Fulfilled")

    def test_parameterized_query_safety(self):
        """
        Verifies parameterized SQL query safety against injection payloads.
        """
        injection_name = "Robert'); DROP TABLE DONORS;--"
        donor_id = self.db.add_donor(
            name=injection_name,
            blood_group="A+",
            phone="9812345678",
            last_donation_date="2026-02-01",
            eligibility="Eligible"
        )
        self.assertGreater(donor_id, 0)

        # Table DONORS must still exist!
        donors = self.db.get_all_donors()
        self.assertGreaterEqual(len(donors), 1)

        # Search with SQL injection payload should return safely
        search_res = self.db.search_donors(query="Robert'); DROP TABLE")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["name"], injection_name)

        # Clean up
        self.db.delete_donor(donor_id)


if __name__ == "__main__":
    unittest.main()
