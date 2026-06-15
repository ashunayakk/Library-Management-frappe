import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data

def get_columns():
	return [{'label': 'Member Name', 'fieldname': 'member_name', 'fieldtype': 'Data', 'width': 150}, {'label': 'Email', 'fieldname': 'email', 'fieldtype': 'Data', 'width': 180}, {'label': 'Phone', 'fieldname': 'phone', 'fieldtype': 'Data', 'width': 120}, {'label': 'From Date', 'fieldname': 'from_date', 'fieldtype': 'Date', 'width': 100}, {'label': 'To Date', 'fieldname': 'to_date', 'fieldtype': 'Date', 'width': 100}, {'label': 'Days Remaining', 'fieldname': 'days_remaining', 'fieldtype': 'Int', 'width': 120}]

def get_data():
	return frappe.db.sql("""SELECT 
            m.full_name as member_name, 
            mem.email, mem.phone, 
            m.from_date, m.to_date, 
            DATEDIFF(m.to_date, CURDATE()) as days_remaining
        FROM `tabLibrary Membership` m
        JOIN `tabLibrary Member` mem ON m.library_member = mem.name
        WHERE m.membership_status = 'Active' 
        AND m.docstatus = 1
        ORDER BY days_remaining ASC""", as_dict=1)
