import frappe

def get_context(context):
    # Search query
    search = frappe.form_dict.get("search", "")
    status = frappe.form_dict.get("status", "")

    # Filters
    filters = {}
    if status:
        filters["status"] = status

    # Articles fetch karo
    if search:
        context.articles = frappe.db.sql("""
            SELECT name, author, publisher, status
            FROM `tabArticle`
            WHERE (name LIKE %(search)s 
            OR author LIKE %(search)s)
            {status_filter}
            ORDER BY name ASC
        """.format(
            status_filter=f"AND status = '{status}'" if status else ""
        ), {
            "search": f"%{search}%"
        }, as_dict=True)
    else:
        context.articles = frappe.get_list(
            "Article",
            filters=filters,
            fields=["name", "author", "publisher", "status"],
            order_by="name asc"
        )

    context.search = search
    context.status = status
    context.total = len(context.articles)