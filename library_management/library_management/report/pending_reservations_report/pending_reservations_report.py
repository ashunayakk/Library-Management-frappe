import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data

def get_columns():
	return [{'label': 'Article', 'fieldname': 'article', 'fieldtype': 'Link', 'options': 'Article', 'width': 150}, {'label': 'Member Name', 'fieldname': 'member_name', 'fieldtype': 'Data', 'width': 150}, {'label': 'Email', 'fieldname': 'member_email', 'fieldtype': 'Data', 'width': 180}, {'label': 'Reservation Date', 'fieldname': 'reservation_date', 'fieldtype': 'Date', 'width': 120}, {'label': 'Current Status', 'fieldname': 'current_book_status', 'fieldtype': 'Data', 'width': 120}, {'label': 'Days Waiting', 'fieldname': 'days_waiting', 'fieldtype': 'Int', 'width': 100}]

def get_data():
	return frappe.db.sql("""SELECT 
            r.article, 
            r.member_name as member_id,
            mem.full_name as member_name,
            r.member_email, 
            r.date as reservation_date, 
            a.status as current_book_status,
            DATEDIFF(CURDATE(), r.date) as days_waiting
        FROM `tabBooks Reservation` r
        JOIN `tabArticle` a ON r.article = a.name
        JOIN `tabLibrary Member` mem ON r.member_name = mem.name
        WHERE r.status = 'Pending'
        ORDER BY r.date ASC""", as_dict=1)
