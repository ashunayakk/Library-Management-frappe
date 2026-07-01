import frappe

PAGE_SIZE = 20

def get_context(context):
	search = frappe.form_dict.get("search", "").strip()
	status = frappe.form_dict.get("status", "")
	page = max(1, frappe.utils.cint(frappe.form_dict.get("page", 1)))

	context.success = ""
	context.error = ""
	context.no_cache = 1
	context.csrf_token = frappe.session.csrf_token

	context.is_logged_in = frappe.session.user != "Guest"
	context.current_member = None
	if context.is_logged_in:
		context.current_member = frappe.db.get_value(
			"Library Member", {"user": frappe.session.user}, "name"
		)

	if frappe.request.method == "POST":
		article = frappe.form_dict.get("article", "").strip()

		if not article:
			context.error = "No book selected."
		elif not context.is_logged_in:
			context.error = "Please log in to reserve a book."
		elif not context.current_member:
			context.error = "No Library Member record found for your account. Please register first."
		else:
			try:
				reservation = frappe.new_doc("Books Reservation")
				reservation.article = article
				reservation.member_name = context.current_member
				reservation.status = "Pending"
				reservation.date = frappe.utils.getdate()
				reservation.insert(ignore_permissions=True)
				frappe.db.commit()
				context.success = f"'{article}' successfully reserved! You are in the queue."
			except frappe.ValidationError as e:
				context.error = str(e)
			except Exception:
				frappe.log_error(frappe.get_traceback(), "Article Reservation Error")
				context.error = "An error occurred. Please try again."

	limit_start = (page - 1) * PAGE_SIZE
	filters = {}
	if status:
		filters["status"] = status

	if search:
		articles = frappe.db.sql("""
			SELECT name, author, publisher, status
			FROM `tabArticle`
			WHERE (name LIKE %(search)s OR author LIKE %(search)s)
			ORDER BY name ASC
			LIMIT %(limit_start)s, %(page_size)s
		""", {"search": f"%{search}%", "limit_start": limit_start, "page_size": PAGE_SIZE}, as_dict=True)

		total_count = frappe.db.sql("""
			SELECT COUNT(*) AS cnt FROM `tabArticle`
			WHERE (name LIKE %(search)s OR author LIKE %(search)s)
		""", {"search": f"%{search}%"}, as_dict=True)[0].cnt
	else:
		articles = frappe.get_list(
			"Article",
			filters=filters,
			fields=["name", "author", "publisher", "status"],
			order_by="name asc",
			limit_start=limit_start,
			limit_page_length=PAGE_SIZE
		)
		total_count = frappe.db.count("Article", filters)

	context.articles = articles
	context.search = search
	context.status = status
	context.total = total_count
	context.page = page
	context.page_size = PAGE_SIZE
	context.total_pages = max(1, -(-total_count // PAGE_SIZE))  # ceiling division
	context.has_prev = page > 1
	context.has_next = page < context.total_pages
