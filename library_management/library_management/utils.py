import frappe

def create_member_for_user(user, method):
	"""Automatically create a Library Member when a new User is created."""
	if not frappe.db.exists("Library Member", {"email": user.email}):
		member = frappe.get_doc({
			"doctype": "Library Member",
			"email": user.email,
			"first_name": user.first_name,
			"last_name": user.last_name,
			"user": user.name
		})
		member.insert(ignore_permissions=True)
		# We don't need a commit here as Frappe handles it in the transaction
