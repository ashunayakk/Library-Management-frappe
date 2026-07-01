import frappe


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": "Transaction ID", "fieldname": "transaction_id", "fieldtype": "Link",
		 "options": "Library Transaction", "width": 140},
		{"label": "Book Name", "fieldname": "book_name", "fieldtype": "Data", "width": 180},
		{"label": "Member Name", "fieldname": "member_name", "fieldtype": "Data", "width": 150},
		{"label": "Email", "fieldname": "email", "fieldtype": "Data", "width": 180},
		{"label": "Issue Date", "fieldname": "issue_date", "fieldtype": "Date", "width": 100},
		{"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 100},
		{"label": "Days Overdue", "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
		{"label": "Fine Amount", "fieldname": "fine_amount", "fieldtype": "Currency", "width": 110},
		{"label": "Fine Paid", "fieldname": "fine_paid", "fieldtype": "Check", "width": 80},
	]


def get_data():
	fine_per_day = frappe.db.get_single_value("Library Settings", "fine_per_day") or 10
	return frappe.db.sql("""
		SELECT
			t.name AS transaction_id,
			t.article AS book_name,
			CONCAT(mem.first_name, ' ', COALESCE(mem.last_name, '')) AS member_name,
			mem.email,
			t.date AS issue_date,
			t.due_date,
			DATEDIFF(CURDATE(), t.due_date) AS days_overdue,
			(DATEDIFF(CURDATE(), t.due_date) * %(fine_per_day)s) AS fine_amount,
			t.fine_paid
		FROM `tabLibrary Transaction` t
		JOIN `tabLibrary Member` mem ON t.library_member = mem.name
		JOIN `tabArticle` a ON t.article = a.name
		WHERE t.type = 'Issue'
			AND t.docstatus = 1
			AND a.status = 'Issued'
			AND t.due_date < CURDATE()
		ORDER BY days_overdue DESC
	""", {"fine_per_day": fine_per_day}, as_dict=1)
