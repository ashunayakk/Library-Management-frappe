# Copyright (c) 2026, Ashutosh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LibraryMember(Document):
	def after_insert(self):
		self.create_user()

	def create_user(self):
		if frappe.db.exists("User", self.email):
			frappe.msgprint(frappe._("User with email {0} already exists").format(self.email))
			# Link existing user if found
			self.db_set("user", self.email)
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
