import frappe
import json

def setup_charts():
    # 1. Membership Status Donut Chart
    if not frappe.db.exists("Dashboard Chart", "Membership Status"):
        doc1 = frappe.get_doc({
            "doctype": "Dashboard Chart",
            "chart_name": "Membership Status",
            "type": "Donut",
            "chart_type": "Group By",
            "document_type": "Library Membership",
            "based_on": "creation",
            "value_based_on": "",
            "group_by_based_on": "membership_status",
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "filters_json": "[]",
            "is_public": 1,
            "is_standard": 1,
            "module": "Library Management"
        })
        doc1.insert(ignore_permissions=True)
        print("Created Dashboard Chart: Membership Status")
        
    # 2. Monthly Issue/Return Trend Line Chart
    if not frappe.db.exists("Dashboard Chart", "Monthly Transaction Trend"):
        doc2 = frappe.get_doc({
            "doctype": "Dashboard Chart",
            "chart_name": "Monthly Transaction Trend",
            "type": "Line",
            "chart_type": "Group By",
            "document_type": "Library Transaction",
            "based_on": "date",
            "value_based_on": "",
            "group_by_based_on": "type",
            "timespan": "Last Year",
            "time_interval": "Monthly",
            "filters_json": "[]",
            "is_public": 1,
            "is_standard": 1,
            "module": "Library Management"
        })
        doc2.insert(ignore_permissions=True)
        print("Created Dashboard Chart: Monthly Transaction Trend")
        
    # Add to Workspace
    ws = frappe.get_doc("Workspace", "Library Dashboard")
    content = json.loads(ws.content)
    
    # Check if charts already added
    has_charts = any(item.get("type") == "chart" for item in content)
    
    if not has_charts:
        content.append({"id": "header_3", "type": "header", "data": {"text": "Analytics", "col": 12}})
        content.append({
            "id": frappe.generate_hash(length=8),
            "type": "chart",
            "data": {"chart_name": "Membership Status"},
            "col": 6
        })
        content.append({
            "id": frappe.generate_hash(length=8),
            "type": "chart",
            "data": {"chart_name": "Monthly Transaction Trend"},
            "col": 6
        })
        
        ws.content = json.dumps(content)
        ws.save(ignore_permissions=True)
        print("Charts added to Workspace layout.")
        
    frappe.db.commit()

if __name__ == "__main__":
    setup_charts()
