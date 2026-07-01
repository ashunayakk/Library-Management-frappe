import frappe


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": "Article", "fieldname": "article", "fieldtype": "Link",
		 "options": "Article", "width": 180},
		{"label": "Member Name", "fieldname": "member_name", "fieldtype": "Data", "width": 150},
		{"label": "Email", "fieldname": "member_email", "fieldtype": "Data", "width": 180},
		{"label": "Reservation Date", "fieldname": "reservation_date", "fieldtype": "Date", "width": 120},
		{"label": "Book Status", "fieldname": "current_book_status", "fieldtype": "Data", "width": 100},
		{"label": "Days Waiting", "fieldname": "days_waiting", "fieldtype": "Int", "width": 100},
	]


def get_data():
	return frappe.db.sql("""
		SELECT
			r.article,
			CONCAT(mem.first_name, ' ', COALESCE(mem.last_name, '')) AS member_name,
			r.member_email,
			r.date AS reservation_date,
			a.status AS current_book_status,
			DATEDIFF(CURDATE(), r.date) AS days_waiting
		FROM `tabBooks Reservation` r
		JOIN `tabArticle` a ON r.article = a.name
		JOIN `tabLibrary Member` mem ON r.member_name = mem.name
		WHERE r.status = 'Pending'
		ORDER BY r.date ASC
	""", as_dict=1)
