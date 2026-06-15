import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data

def get_columns():
	return [{'label': 'Metric', 'fieldname': 'metric', 'fieldtype': 'Data', 'width': 200}, {'label': 'Value', 'fieldname': 'value', 'fieldtype': 'Float', 'width': 120}]

def get_data():
	return frappe.db.sql("""SELECT 'Total Books' as metric, count(*) as value FROM `tabArticle`
        UNION ALL
        SELECT 'Available Books', count(*) FROM `tabArticle` WHERE status = 'Available'
        UNION ALL
        SELECT 'Issued Books', count(*) FROM `tabArticle` WHERE status = 'Issued'
        UNION ALL
        SELECT 'Total Members', count(*) FROM `tabLibrary Member`
        UNION ALL
        SELECT 'Active Memberships', count(*) FROM `tabLibrary Membership` WHERE membership_status = 'Active' AND docstatus = 1
        UNION ALL
        SELECT 'Pending Reservations', count(*) FROM `tabBooks Reservation` WHERE status = 'Pending'
        UNION ALL
        SELECT 'Overdue Fine Total', SUM(DATEDIFF(CURDATE(), due_date) * 10) 
        FROM `tabLibrary Transaction` t
        JOIN `tabArticle` a ON t.article = a.name
        WHERE t.type = 'Issue' AND t.docstatus = 1 AND a.status = 'Issued' AND t.due_date < CURDATE()""", as_dict=1)
