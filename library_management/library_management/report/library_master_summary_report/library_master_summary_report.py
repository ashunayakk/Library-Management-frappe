import frappe


def execute(filters=None):
	return get_columns(), get_data()


def get_columns():
	return [
		{"label": "Metric", "fieldname": "metric", "fieldtype": "Data", "width": 220},
		{"label": "Value", "fieldname": "value", "fieldtype": "Float", "width": 120},
	]


def get_data():
	fine_per_day = frappe.db.get_single_value("Library Settings", "fine_per_day") or 10
	return frappe.db.sql("""
		SELECT 'Total Books' AS metric, COUNT(*) AS value FROM `tabArticle`
		UNION ALL
		SELECT 'Available Books', COUNT(*) FROM `tabArticle` WHERE status = 'Available'
		UNION ALL
		SELECT 'Issued Books', COUNT(*) FROM `tabArticle` WHERE status = 'Issued'
		UNION ALL
		SELECT 'Reserved Books', COUNT(*) FROM `tabArticle` WHERE status = 'Reserved'
		UNION ALL
		SELECT 'Total Members', COUNT(*) FROM `tabLibrary Member`
		UNION ALL
		SELECT 'Active Memberships', COUNT(*)
		FROM `tabLibrary Membership`
		WHERE membership_status = 'Active' AND docstatus = 1
		UNION ALL
		SELECT 'Pending Reservations', COUNT(*)
		FROM `tabBooks Reservation`
		WHERE status = 'Pending'
		UNION ALL
		SELECT 'Total Overdue Fine Outstanding',
			COALESCE(SUM(DATEDIFF(CURDATE(), t.due_date) * %(fine_per_day)s), 0)
		FROM `tabLibrary Transaction` t
		JOIN `tabArticle` a ON t.article = a.name
		WHERE t.type = 'Issue'
			AND t.docstatus = 1
			AND a.status = 'Issued'
			AND t.due_date < CURDATE()
			AND t.fine_paid = 0
	""", {"fine_per_day": fine_per_day}, as_dict=1)
