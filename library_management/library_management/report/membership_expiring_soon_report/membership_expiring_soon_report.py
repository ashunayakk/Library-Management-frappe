import frappe


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": "Member Name", "fieldname": "member_name", "fieldtype": "Data", "width": 180},
		{"label": "Email", "fieldname": "email", "fieldtype": "Data", "width": 180},
		{"label": "Phone", "fieldname": "phone", "fieldtype": "Data", "width": 120},
		{"label": "Expires On", "fieldname": "to_date", "fieldtype": "Date", "width": 110},
		{"label": "Days Remaining", "fieldname": "days_remaining", "fieldtype": "Int", "width": 120},
	]


def get_data():
	return frappe.db.sql("""
		SELECT
			m.full_name AS member_name,
			mem.email,
			mem.phone,
			m.to_date,
			DATEDIFF(m.to_date, CURDATE()) AS days_remaining
		FROM `tabLibrary Membership` m
		JOIN `tabLibrary Member` mem ON m.library_member = mem.name
		WHERE m.membership_status = 'Active'
			AND m.docstatus = 1
			AND DATEDIFF(m.to_date, CURDATE()) <= 7
		ORDER BY days_remaining ASC
	""", as_dict=1)
