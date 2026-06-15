import frappe
from frappe.utils import today

def create_number_cards():
    cards = [
        {
            "label": "Total Books",
            "document_type": "Article",
            "function": "Count"
        },
        {
            "label": "Total Available Books",
            "document_type": "Article",
            "function": "Count",
            "filters_json": '{"status": "Available"}'
        },
        {
            "label": "Total Issued Books",
            "document_type": "Article",
            "function": "Count",
            "filters_json": '{"status": "Issued"}'
        },
        {
            "label": "Total Members",
            "document_type": "Library Member",
            "function": "Count"
        },
        {
            "label": "Active Memberships",
            "document_type": "Library Membership",
            "function": "Count",
            "filters_json": '{"membership_status": "Active"}'
        },
        {
            "label": "Expired Memberships",
            "document_type": "Library Membership",
            "function": "Count",
            "filters_json": '{"membership_status": "Expired"}'
        },
        {
            "label": "Pending Reservations",
            "document_type": "Books Reservation",
            "function": "Count",
            "filters_json": '{"status": "Pending"}'
        },
        {
            "label": "Overdue Books",
            "document_type": "Library Transaction",
            "function": "Count",
            "filters_json": '[["Library Transaction", "type", "=", "Issue"], ["Library Transaction", "docstatus", "=", 1], ["Library Transaction", "due_date", "<", "{today}"]]'.replace('{today}', today())
        }
    ]

    for card_data in cards:
        if not frappe.db.exists("Number Card", card_data["label"]):
            doc = frappe.new_doc("Number Card")
            doc.update(card_data)
            doc.is_standard = 1
            doc.module = "Library Management"
            doc.insert(ignore_permissions=True)
            print(f"Created Number Card: {doc.label}")
        else:
            print(f"Number Card already exists: {card_data['label']}")

    frappe.db.commit()

if __name__ == "__main__":
    create_number_cards()
