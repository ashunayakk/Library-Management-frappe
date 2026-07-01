import frappe
from frappe.utils import today, add_days


def check_expired_memberships():
	expired_memberships = frappe.get_all(
		"Library Membership",
		filters={
			"membership_status": "Active",
			"docstatus": 1,
			"to_date": ("<", today())
		},
		fields=["name", "library_member"]
	)

	for m in expired_memberships:
		frappe.db.set_value("Library Membership", m.name, "membership_status", "Expired")
		member_user = frappe.db.get_value("Library Member", m.library_member, "user")
		if member_user and frappe.db.exists("User", member_user):
			frappe.get_doc("User", member_user).remove_roles("Library Member")

	if expired_memberships:
		frappe.db.commit()


def cancel_expired_reservations():
	expiry_date = add_days(today(), -2)

	expired_reservations = frappe.get_all(
		"Books Reservation",
		filters=[
			["status", "=", "Pending"],
			["notification_date", "is", "set"],
			["notification_date", "<", expiry_date]
		],
		fields=["name", "article"]
	)

	for res in expired_reservations:
		frappe.db.set_value("Books Reservation", res.name, "status", "Cancelled")
		handle_next_reservation(res.article)

	if expired_reservations:
		frappe.db.commit()


def handle_next_reservation(article):
	reservations = frappe.get_all(
		"Books Reservation",
		filters={"article": article, "status": "Pending"},
		fields=["name", "member_name", "member_email"],
		order_by="creation asc"
	)

	if reservations:
		next_res = reservations[0]
		frappe.db.set_value("Books Reservation", next_res.name, "notification_date", today())
		frappe.db.set_value("Article", article, "status", "Reserved")

		frappe.sendmail(
			recipients=[next_res.member_email],
			subject=frappe._("Article Available: {0}").format(article),
			message=frappe._(
				"Hi {0},<br><br>The article <b>{1}</b> is now available for you. "
				"Please collect it within 48 hours."
			).format(next_res.member_name, article)
		)
	else:
		frappe.db.set_value("Article", article, "status", "Available")
