import frappe

def get_context(context):
    # Total books
    context.total_books = frappe.db.count("Article")
    
    # Available books
    context.available_books = frappe.db.count(
        "Article", {"status": "Available"}
    )
    
    # Issued books
    context.issued_books = frappe.db.count(
        "Article", {"status": "Issued"}
    )
    
    # Total members
    context.total_members = frappe.db.count("Library Member")
    
    # Latest available books
    context.latest_books = frappe.get_list(
        "Article",
        filters={"status": "Available"},
        fields=["name", "author", "publisher", "status"],
        limit=6,
        order_by="creation desc"
    )