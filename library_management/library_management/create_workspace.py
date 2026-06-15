import frappe
import json

def fix_workspace():
    workspace_name = "Library Dashboard"
    
    if frappe.db.exists("Workspace", workspace_name):
        doc = frappe.get_doc("Workspace", workspace_name)
        
        # Clean up legacy tables
        doc.set("links", [])
        doc.set("number_cards", [])
        doc.set("charts", [])
        doc.set("shortcuts", [])

        content = []
        
        # 1. Number Cards
        content.append({"id": frappe.generate_hash(length=8), "type": "header", "data": {"text": "<span class=\"h4\">Key Metrics</span>", "col": 12}})
        
        cards = [
            "Total Books", "Total Available Books", "Total Issued Books", "Total Members",
            "Active Memberships", "Expired Memberships", "Pending Reservations", "Overdue Books"
        ]
        for card_name in cards:
            if frappe.db.exists("Number Card", card_name):
                doc.append("number_cards", {
                    "number_card_name": card_name,
                    "label": card_name
                })
                content.append({
                    "id": frappe.generate_hash(length=8),
                    "type": "number_card",
                    "data": {"number_card_name": card_name},
                    "col": 3
                })
                print(f"Added Number Card to doc: {card_name}")

        # 2. Reports (Shortcuts)
        content.append({"id": frappe.generate_hash(length=8), "type": "header", "data": {"text": "<span class=\"h4\">Reports</span>", "col": 12}})
        
        reports = [
            "Active Memberships Report", "Expired Memberships Report", 
            "Membership Expiring Soon Report", "Pending Reservations Report", 
            "Books to Issue Report", "Overdue Books Report", "Library Master Summary Report"
        ]
        for report_name in reports:
            if frappe.db.exists("Report", report_name):
                doc.append("shortcuts", {
                    "label": report_name,
                    "type": "Report",
                    "link_to": report_name
                })
                content.append({
                    "id": frappe.generate_hash(length=8),
                    "type": "shortcut",
                    "data": {"shortcut_name": report_name},
                    "col": 3
                })
                print(f"Added Report Shortcut to doc: {report_name}")

        # 2.1 Custom URL Shortcuts
        content.append({"id": frappe.generate_hash(length=8), "type": "header", "data": {"text": "<span class=\"h4\">Quick Actions</span>", "col": 12}})
        
        custom_shortcuts = [
            {"label": "📚 Add Book", "type": "URL", "link_to": "/app/article/new-article-1"},
            {"label": "👤 Add Member", "type": "URL", "link_to": "/app/library-member/new-library-member-1"},
            {"label": "🎫 Add Membership", "type": "URL", "link_to": "/app/library-membership/new-library-membership-1"},
            {"label": "🔄 Issue / Return Book", "type": "URL", "link_to": "/app/library-transaction/new-library-transaction-1"},
        ]
        
        for s in custom_shortcuts:
            doc.append("shortcuts", {
                "label": s["label"],
                "type": "URL",
                "url": s["link_to"]
            })
            content.append({
                "id": frappe.generate_hash(length=8),
                "type": "shortcut",
                "data": {"shortcut_name": s["label"]},
                "col": 3
            })
            print(f"Added URL Shortcut to doc: {s['label']}")

        # 3. Charts
        content.append({"id": frappe.generate_hash(length=8), "type": "header", "data": {"text": "<span class=\"h4\">Analytics</span>", "col": 12}})
        
        chart_names = ["Membership Status", "Monthly Transaction Trend"]
        for c in chart_names:
            if frappe.db.exists("Dashboard Chart", c):
                doc.append("charts", {
                    "chart_name": c,
                    "label": c
                })
                content.append({
                    "id": frappe.generate_hash(length=8),
                    "type": "chart",
                    "data": {"chart_name": c},
                    "col": 6
                })
                print(f"Added Chart to doc: {c}")

        doc.content = json.dumps(content)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()
        print(f"Workspace '{workspace_name}' saved and cache cleared.")
    else:
        print("Workspace not found.")

if __name__ == "__main__":
    fix_workspace()
