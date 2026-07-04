# Copyright (c) 2026, Ashutosh and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestLibrarySettings(FrappeTestCase):
	def setUp(self):
		settings = frappe.get_single("Library Settings")
		self._fine_per_day = settings.fine_per_day
		self._loan_period_days = settings.loan_period_days

	def tearDown(self):
		settings = frappe.get_single("Library Settings")
		settings.fine_per_day = self._fine_per_day
		settings.loan_period_days = self._loan_period_days
		settings.save()

	def test_negative_fine_per_day_rejected(self):
		settings = frappe.get_single("Library Settings")
		settings.fine_per_day = -5
		self.assertRaises(frappe.ValidationError, settings.save)

	def test_non_positive_loan_period_rejected(self):
		settings = frappe.get_single("Library Settings")
		settings.loan_period_days = 0
		self.assertRaises(frappe.ValidationError, settings.save)

	def test_valid_settings_saved(self):
		settings = frappe.get_single("Library Settings")
		settings.fine_per_day = 5
		settings.loan_period_days = 10
		settings.save()
		self.assertEqual(frappe.db.get_single_value("Library Settings", "fine_per_day"), 5)
		self.assertEqual(frappe.db.get_single_value("Library Settings", "loan_period_days"), 10)
