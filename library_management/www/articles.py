import frappe

def get_context(context):
    search = frappe.form_dict.get("search", "")
    status = frappe.form_dict.get("status", "")
    reserved = frappe.form_dict.get("reserved", "")
    context.success = ""
    context.error = ""
    context.no_cache = 1

    # Reserve karo
    if frappe.request.method == "POST":
        article = frappe.form_dict.get("article", "")
        member_name = frappe.form_dict.get("member_name", "")
        member_email = frappe.form_dict.get("member_email", "")

        try:
            # Check already reserved
            exists = frappe.db.exists("Books Reservation", {
                "article": article,
                "status": "Pending"
            })

            if exists:
                context.error = f"'{article}' already reserved hai!"
            else:
                frappe.set_user("Administrator")
                reservation = frappe.new_doc("Books Reservation")
                reservation.article = article
                reservation.member_name = member_name
                reservation.member_email = member_email
                reservation.status = "Pending"
                reservation.date = frappe.utils.getdate()
                reservation.insert(ignore_permissions=True)
                frappe.db.commit()
                context.success = f"'{article}' successfully reserved!"
        except Exception as e:
            context.error = f"Error: {str(e)}"

    # Articles fetch karo
    filters = {}
    if status:
        filters["status"] = status

    if search:
        context.articles = frappe.db.sql("""
            SELECT name, author, publisher, status
            FROM `tabArticle`
            WHERE (name LIKE %(search)s OR author LIKE %(search)s)
            ORDER BY name ASC
        """, {"search": f"%{search}%"}, as_dict=True)
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
