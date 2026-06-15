import frappe
from frappe.utils import today, add_days, getdate

def check_expired_memberships():
	# Find all active memberships that have expired
	expired_memberships = frappe.get_all("Library Membership", 
		filters={
			"membership_status": "Active",
			"to_date": ("<", today())
		}
	)

	for m in expired_memberships:
		doc = frappe.get_doc("Library Membership", m.name)
		doc.membership_status = "Expired"
		doc.save()
		doc.toggle_library_member_role(add=False)
		frappe.db.commit()

def cancel_expired_reservations():
	# Find reservations where notification was sent > 48 hours ago and still pending
	expiry_date = add_days(today(), -2)
	
	expired_reservations = frappe.get_all(
		"Books Reservation",
		filters={
			"status": "Pending",
			"notification_date": ("<", expiry_date)
		},
		fields=["name", "article"]
	)

	for res in expired_reservations:
		# Cancel the reservation
		frappe.db.set_value("Books Reservation", res.name, "status", "Cancelled")
		
		# Process the next person in queue for this article
		handle_next_reservation(res.article)
		
		frappe.db.commit()

def handle_next_reservation(article):
	# Check if there are other pending reservations
	reservations = frappe.get_all(
		"Books Reservation",
		filters={"article": article, "status": "Pending"},
		fields=["name", "member_name", "member_email"],
		order_by="creation asc"
	)

	if reservations:
		# Notify the next person
		next_res = reservations[0]
		frappe.db.set_value("Books Reservation", next_res.name, "notification_date", today())
		frappe.db.set_value("Article", article, "status", "Reserved")
		
		frappe.sendmail(
			recipients=[next_res.member_email],
			subject=frappe._("Article Available (Reserved for you): {0}").format(article),
			message=frappe._("Hi {0},<br><br>The article <b>{1}</b> is now available for you as the previous reservation expired. Please collect it within 48 hours.").format(next_res.member_name, article)
		)
	else:
		# No one left in queue
		frappe.db.set_value("Article", article, "status", "Available")
