import frappe


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": "Article", "fieldname": "article", "fieldtype": "Link",
		 "options": "Article", "width": 180},
		{"label": "Reserved For", "fieldname": "member_name", "fieldtype": "Data", "width": 150},
		{"label": "Email", "fieldname": "member_email", "fieldtype": "Data", "width": 180},
		{"label": "Reservation Date", "fieldname": "reservation_date", "fieldtype": "Date", "width": 120},
		{"label": "Days Waited", "fieldname": "days_waited", "fieldtype": "Int", "width": 100},
		{"label": "Action", "fieldname": "action_required", "fieldtype": "Data", "width": 120},
	]


def get_data():
	return frappe.db.sql("""
		SELECT
			r.article,
			CONCAT(mem.first_name, ' ', COALESCE(mem.last_name, '')) AS member_name,
			r.member_email,
			r.date AS reservation_date,
			DATEDIFF(CURDATE(), r.date) AS days_waited,
			'ISSUE NOW' AS action_required
		FROM `tabBooks Reservation` r
		JOIN `tabArticle` a ON r.article = a.name
		JOIN `tabLibrary Member` mem ON r.member_name = mem.name
		WHERE r.status = 'Pending'
			AND (a.status = 'Available' OR r.ready_to_issue = 1)
		ORDER BY r.date ASC
	""", as_dict=1)
