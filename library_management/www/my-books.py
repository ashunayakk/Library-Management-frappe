import frappe

no_cache = 1

def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/my-books"
		raise frappe.Redirect

	member = frappe.db.get_value(
		"Library Member",
		{"user": frappe.session.user},
		["name", "first_name", "last_name", "email", "phone", "membership_expiry"],
		as_dict=True
	)

	if not member:
		context.no_member = True
		context.issued_books = []
		context.reservations = []
		context.past_transactions = []
		return

	context.no_member = False
	context.member = member
	context.member.full_name = f"{member.first_name} {member.last_name or ''}".strip()

	membership_expiry = member.membership_expiry
	if membership_expiry and frappe.utils.getdate(membership_expiry) >= frappe.utils.getdate():
		context.membership_active = True
		context.membership_expiry = membership_expiry
	else:
		context.membership_active = False
		context.membership_expiry = membership_expiry

	fine_per_day = frappe.db.get_single_value("Library Settings", "fine_per_day") or 10

	context.issued_books = frappe.db.sql("""
		SELECT
			t.name AS transaction_id,
			t.article,
			t.date AS issue_date,
			t.due_date,
			t.fine_paid,
			CASE
				WHEN t.due_date < CURDATE()
				THEN DATEDIFF(CURDATE(), t.due_date)
				ELSE 0
			END AS days_overdue,
			CASE
				WHEN t.due_date < CURDATE() AND t.fine_paid = 0
				THEN DATEDIFF(CURDATE(), t.due_date) * %(fine_per_day)s
				ELSE 0
			END AS fine_due
		FROM `tabLibrary Transaction` t
		JOIN `tabArticle` a ON t.article = a.name
		WHERE t.library_member = %(member)s
			AND t.type = 'Issue'
			AND t.docstatus = 1
			AND a.status = 'Issued'
		ORDER BY t.due_date ASC
	""", {"member": member.name, "fine_per_day": fine_per_day}, as_dict=1)

	context.reservations = frappe.db.sql("""
		SELECT
			r.name,
			r.article,
			r.date AS reserved_on,
			r.status,
			r.ready_to_issue,
			a.status AS book_status,
			DATEDIFF(CURDATE(), r.date) AS days_waiting
		FROM `tabBooks Reservation` r
		JOIN `tabArticle` a ON r.article = a.name
		WHERE r.member_name = %(member)s
			AND r.status = 'Pending'
		ORDER BY r.date ASC
	""", {"member": member.name}, as_dict=1)

	context.past_transactions = frappe.db.sql("""
		SELECT
			t.name AS transaction_id,
			t.article,
			t.type,
			t.date,
			t.due_date,
			t.fine_amount,
			t.fine_paid
		FROM `tabLibrary Transaction` t
		WHERE t.library_member = %(member)s
			AND t.docstatus = 1
		ORDER BY t.date DESC
		LIMIT 20
	""", {"member": member.name}, as_dict=1)

	context.total_fine_due = sum(b.fine_due for b in context.issued_books)
