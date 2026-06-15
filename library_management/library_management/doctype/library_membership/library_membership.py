# Copyright (c) 2026, Ashutosh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, today

class LibraryMembership(Document):
	def validate(self):
		# Fetch full name from member
		member = frappe.get_doc("Library Member", self.library_member)
		self.full_name = f"{member.first_name} {member.last_name or ''}".strip()

	def before_submit(self):
		if not self.paid:
			frappe.throw(frappe._("Membership cannot be activated without payment."))
		
		# Calculate to_date based on plan if not already set
		if not self.to_date:
			months = 1
			if self.membership_plan == "Quarterly":
				months = 3
			elif self.membership_plan == "Yearly":
				months = 12
			
			self.to_date = add_months(self.from_date, months)

		self.membership_status = "Active"

	def on_submit(self):
		# Update Library Member's expiry date
		frappe.db.set_value("Library Member", self.library_member, "membership_expiry", self.to_date)
		
		# Assign Role
		self.toggle_library_member_role(add=True)

	def on_cancel(self):
		self.membership_status = "Expired"
		self.toggle_library_member_role(add=False)

	def toggle_library_member_role(self, add=True):
		member = frappe.get_doc("Library Member", self.library_member)
		if member.user:
			user = frappe.get_doc("User", member.user)
			role = "Library Member"
			
			if add:
				user.add_roles(role)
				frappe.msgprint(frappe._("Role 'Library Member' assigned to user {0}").format(user.name))
			else:
				user.remove_roles(role)
				frappe.msgprint(frappe._("Role 'Library Member' removed from user {0}").format(user.name))
