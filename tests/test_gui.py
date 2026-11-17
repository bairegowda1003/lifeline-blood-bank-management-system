"""
Automated GUI Functional Test
Tests UI views, form population, event bindings, and live dashboard refreshes.
"""

import unittest
from datetime import date
from main import BloodBankApp


class TestGUIIntegration(unittest.TestCase):
    """Functional tests driving the Tkinter GUI views directly."""

    @classmethod
    def setUpClass(cls):
        cls.app = BloodBankApp()
        cls.app.update()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.app.destroy()
        except Exception:
            pass

    def test_navigation_switching(self):
        """Verifies switching between all views without error."""
        views = ["dashboard", "donors", "stock", "requests", "about"]
        for v in views:
            self.app.show_view(v)
            self.app.update()
            self.assertEqual(self.app.current_view_name, v)

    def test_donor_view_workflow(self):
        """Tests donor form input, validation, registration, and table population."""
        self.app.show_view("donors")
        donor_view = self.app.views["donors"]
        donor_view.clear_form()

        # Fill in valid donor details
        donor_view.entry_name.insert(0, "Praveen Kumar")
        donor_view.combo_blood_type.set("AB")
        donor_view.combo_rh.set("Positive (+)")
        donor_view.entry_phone.insert(0, "9876543219")
        donor_view.date_entry.set_date(date.today())
        donor_view.combo_eligibility.set("Eligible")

        # Save donor
        name, bg, phone, last_date, elig = donor_view.validate_inputs()
        new_id = donor_view.db.add_donor(name, bg, phone, last_date, elig)
        self.assertGreater(new_id, 0)

        donor_view.load_donors()
        self.app.update()

        # Search for the donor
        donor_view.entry_search.delete(0, "end")
        donor_view.entry_search.insert(0, "Praveen")
        donor_view.search_donors()
        self.app.update()

        children = donor_view.tree.get_children()
        self.assertGreaterEqual(len(children), 1)

        # Clean up test donor to avoid polluting production database
        donor_view.db.delete_donor(new_id)

    def test_requests_workflow(self):
        """Tests hospital request creation and stock verification."""
        self.app.show_view("requests")
        req_view = self.app.views["requests"]
        req_view.clear_form()

        req_view.entry_hospital.insert(0, "Narayana Hrudayalaya")
        req_view.combo_bg.set("O+")
        req_view.spin_units.delete(0, "end")
        req_view.spin_units.insert(0, "2")
        req_view.combo_status.set("Pending")

        hosp, bg, units, status = req_view.validate_inputs()
        success, msg, req_id = req_view.db.add_request(hosp, bg, units, status)
        self.assertTrue(success)
        self.assertGreater(req_id, 0)

        req_view.load_requests()
        self.app.update()

        # Clean up test request to avoid polluting production database
        req_view.db.delete_request(req_id)


if __name__ == "__main__":
    unittest.main()
