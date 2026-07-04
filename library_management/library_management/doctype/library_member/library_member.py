# Copyright (c) 2026, Ashutosh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LibraryMember(Document):
	def validate(self):
		if self.email:
			self.email = self.email.strip().lower()

	def after_insert(self):
		self.create_user()

	def create_user(self):
		if frappe.db.exists("User", self.email):
			# An account with this email already exists. Do not silently link an
			# unverified Library Member to it - that would let anyone claim an
			# existing account just by knowing its email address.
			frappe.msgprint(
				frappe._(
					"A user with email {0} already exists. Please ask them to link "
					"this Library Member from their User record if needed."
				).format(self.email)
			)
			return

		user = frappe.get_doc({
			"doctype": "User",
			"email": self.email,
			"first_name": self.first_name,
			"last_name": self.last_name,
			"send_welcome_email": 1,
			"enabled": 1,
			"roles": [] # Roles will be assigned on membership activation
		})
		user.insert(ignore_permissions=True)
		
		# Link user to library member
		self.db_set("user", user.name)
		frappe.msgprint(frappe._("User {0} created for Library Member").format(user.name))
