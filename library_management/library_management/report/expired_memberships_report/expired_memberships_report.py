import frappe


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": "Member Name", "fieldname": "member_name", "fieldtype": "Data", "width": 180},
		{"label": "Email", "fieldname": "email", "fieldtype": "Data", "width": 180},
		{"label": "Phone", "fieldname": "phone", "fieldtype": "Data", "width": 120},
		{"label": "Expired On", "fieldname": "to_date", "fieldtype": "Date", "width": 110},
		{"label": "Days Expired", "fieldname": "days_expired", "fieldtype": "Int", "width": 120},
	]


def get_data():
	return frappe.db.sql("""
		SELECT
			m.full_name AS member_name,
			mem.email,
			mem.phone,
			m.to_date,
			DATEDIFF(CURDATE(), m.to_date) AS days_expired
		FROM `tabLibrary Membership` m
		JOIN `tabLibrary Member` mem ON m.library_member = mem.name
		WHERE m.membership_status = 'Expired'
			AND m.docstatus = 1
		ORDER BY days_expired DESC
	""", as_dict=1)
