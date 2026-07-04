# Copyright (c) 2026, Ashutosh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, today


class LibraryMembership(Document):
	def validate(self):
		member = frappe.get_doc("Library Member", self.library_member)
		self.full_name = f"{member.first_name} {member.last_name or ''}".strip()

	def before_submit(self):
		if not self.paid:
			frappe.throw(frappe._("Membership cannot be activated without payment."))

		duplicate = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"membership_status": "Active",
				"docstatus": 1,
				"name": ["!=", self.name],
			},
		)
		if duplicate:
			frappe.throw(
				frappe._("Library Member {0} already has an active membership ({1}).").format(
					self.library_member, duplicate
				)
			)

		if not self.to_date:
			months = 1
			if self.membership_plan == "Quarterly":
				months = 3
			elif self.membership_plan == "Yearly":
				months = 12

			# Extend from current expiry so renewals don't lose remaining time
			current_expiry = frappe.db.get_value(
				"Library Member", self.library_member, "membership_expiry"
			)
			base_date = self.from_date
			if current_expiry and getdate(current_expiry) > getdate(self.from_date):
				base_date = current_expiry

			self.to_date = add_months(base_date, months)

		self.membership_status = "Active"

	def on_submit(self):
		frappe.db.set_value("Library Member", self.library_member, "membership_expiry", self.to_date)
		self.toggle_library_member_role(add=True)

	def on_cancel(self):
		self.membership_status = "Expired"
		self.toggle_library_member_role(add=False)
		self.reset_member_expiry()

	def reset_member_expiry(self):
		"""Recompute Library Member.membership_expiry from any other still-active
		membership, since this cancelled one may have been the source of it."""
		other_expiry = frappe.db.get_value(
			"Library Membership",
			{
				"library_member": self.library_member,
				"membership_status": "Active",
				"docstatus": 1,
				"name": ["!=", self.name],
			},
			"to_date",
			order_by="to_date desc",
		)
		frappe.db.set_value("Library Member", self.library_member, "membership_expiry", other_expiry)

	def toggle_library_member_role(self, add=True):
		member = frappe.get_doc("Library Member", self.library_member)
		if not member.user:
			return

		if not frappe.db.exists("User", member.user):
			return

		user = frappe.get_doc("User", member.user)
		role = "Library Member"

		if add:
			user.add_roles(role)
			frappe.msgprint(frappe._("Role 'Library Member' assigned to user {0}").format(user.name))
		else:
			user.remove_roles(role)
			frappe.msgprint(frappe._("Role 'Library Member' removed from user {0}").format(user.name))
