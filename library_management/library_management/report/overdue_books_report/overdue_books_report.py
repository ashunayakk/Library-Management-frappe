import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data

def get_columns():
	return [{'label': 'Transaction ID', 'fieldname': 'transaction_id', 'fieldtype': 'Link', 'options': 'Library Transaction', 'width': 120}, {'label': 'Book Name', 'fieldname': 'book_name', 'fieldtype': 'Data', 'width': 150}, {'label': 'Member Name', 'fieldname': 'member_name', 'fieldtype': 'Data', 'width': 150}, {'label': 'Email', 'fieldname': 'email', 'fieldtype': 'Data', 'width': 180}, {'label': 'Due Date', 'fieldname': 'due_date', 'fieldtype': 'Date', 'width': 100}, {'label': 'Days Overdue', 'fieldname': 'days_overdue', 'fieldtype': 'Int', 'width': 100}, {'label': 'Fine Amount', 'fieldname': 'fine_amount', 'fieldtype': 'Currency', 'width': 100}]

def get_data():
	return frappe.db.sql("""SELECT 
            t.name as transaction_id, 
            t.article as book_name, 
            mem.full_name as member_name, 
            mem.email, mem.phone, 
            t.date as issue_date, 
            t.due_date, 
            DATEDIFF(CURDATE(), t.due_date) as days_overdue,
            (DATEDIFF(CURDATE(), t.due_date) * 10) as fine_amount
        FROM `tabLibrary Transaction` t
        JOIN `tabLibrary Member` mem ON t.library_member = mem.name
        JOIN `tabArticle` a ON t.article = a.name
        WHERE t.type = 'Issue' 
        AND t.docstatus = 1 
        AND a.status = 'Issued'
        AND t.due_date < CURDATE()
        ORDER BY days_overdue DESC""", as_dict=1)
