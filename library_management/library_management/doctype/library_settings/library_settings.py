# Copyright (c) 2026, Ashutosh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LibrarySettings(Document):
	def validate(self):
		if self.fine_per_day is not None and self.fine_per_day < 0:
			frappe.throw(frappe._("Fine Per Day cannot be negative."))

		if self.loan_period_days is not None and self.loan_period_days <= 0:
			frappe.throw(frappe._("Loan Period (Days) must be greater than zero."))
