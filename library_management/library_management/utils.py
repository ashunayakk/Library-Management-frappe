import frappe

def create_member_for_user(user, method):
	"""Create a Library Member when a Website User is registered."""
	if user.user_type != "Website User":
		return

	if frappe.db.exists("Library Member", {"email": user.email}):
		return

	member = frappe.get_doc({
		"doctype": "Library Member",
		"email": user.email,
		"first_name": user.first_name,
		"last_name": user.last_name,
		"user": user.name
	})
	member.insert(ignore_permissions=True)
