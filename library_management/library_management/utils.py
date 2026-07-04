import frappe


def get_member_full_name(library_member):
	"""Library Member link fields (e.g. Books Reservation.member_name) store the
	doc ID, not a display name - use this wherever that ID is shown to a human."""
	member = frappe.db.get_value(
		"Library Member", library_member, ["first_name", "last_name"], as_dict=True
	)
	if not member:
		return library_member
	return f"{member.first_name} {member.last_name or ''}".strip()


def create_member_for_user(user, method):
	"""Create a Library Member when a Website User is registered."""
	if user.user_type != "Website User":
		return

	email = (user.email or "").strip().lower()
	if not email or frappe.db.exists("Library Member", {"email": email}):
		return

	member = frappe.get_doc({
		"doctype": "Library Member",
		"email": email,
		"first_name": user.first_name,
		"last_name": user.last_name,
		"user": user.name
	})
	try:
		member.insert(ignore_permissions=True)
	except Exception:
		# Don't let auto-provisioning a Library Member (e.g. missing phone, a
		# mandatory field this hook can't always fill in) break User creation
		# itself - this hook fires for every Website User site-wide.
		frappe.log_error(frappe.get_traceback(), f"Failed to auto-create Library Member for {email}")
