import frappe

no_cache = 1

def get_context(context):
	stats = frappe.db.sql("""
		SELECT
			COUNT(*) AS total_books,
			SUM(status = 'Available') AS available_books,
			SUM(status = 'Issued') AS issued_books,
			SUM(status = 'Reserved') AS reserved_books
		FROM `tabArticle`
	""", as_dict=1)[0]

	context.total_books = stats.total_books or 0
	context.available_books = stats.available_books or 0
	context.issued_books = stats.issued_books or 0
	context.reserved_books = stats.reserved_books or 0
	context.total_members = frappe.db.count("Library Member")

	context.latest_books = frappe.get_list(
		"Article",
		filters={"status": "Available"},
		fields=["name", "author", "publisher", "status"],
		limit=6,
		order_by="creation desc"
	)
