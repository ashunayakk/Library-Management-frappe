import frappe

def create_query_report(report_name, query):
    if not frappe.db.exists("Report", report_name):
        report = frappe.new_doc("Report")
        report.report_name = report_name
        report.ref_doctype = "Library Transaction" # Default ref, will adjust per report
        report.is_standard = "Yes"
        report.module = "Library Management"
        report.report_type = "Query Report"
        report.query = query
        report.insert(ignore_permissions=True)
        print(f"Created Report: {report_name}")
    else:
        # Update existing report query if it was NULL or incorrect
        report = frappe.get_doc("Report", report_name)
        report.query = query
        report.save(ignore_permissions=True)
        print(f"Updated Report Query: {report_name}")

def setup_all_reports():
    # 1. Active Memberships Report
    create_query_report(
        "Active Memberships Report",
        """SELECT 
            m.full_name as `Member Name`, 
            mem.email as `Email`, 
            mem.phone as `Phone`, 
            m.from_date as `From Date:Date:100`, 
            m.to_date as `To Date:Date:100`, 
            DATEDIFF(m.to_date, CURDATE()) as `Days Remaining:Int:120`
        FROM `tabLibrary Membership` m
        JOIN `tabLibrary Member` mem ON m.library_member = mem.name
        WHERE CURDATE() <= m.to_date
        ORDER BY DATEDIFF(m.to_date, CURDATE()) ASC"""
    )

    # 2. Expired Memberships Report
    create_query_report(
        "Expired Memberships Report",
        """SELECT 
            m.full_name as `Member Name`, 
            mem.email as `Email`, 
            mem.phone as `Phone`, 
            m.to_date as `To Date:Date:100`, 
            DATEDIFF(CURDATE(), m.to_date) as `Days Expired:Int:120`
        FROM `tabLibrary Membership` m
        JOIN `tabLibrary Member` mem ON m.library_member = mem.name
        WHERE m.to_date < CURDATE()
        ORDER BY DATEDIFF(CURDATE(), m.to_date) DESC"""
    )

    # 3. Membership Expiring Soon Report
    create_query_report(
        "Membership Expiring Soon Report",
        """SELECT 
            m.full_name as `Member Name`, 
            mem.email as `Email`, 
            mem.phone as `Phone`, 
            m.to_date as `To Date:Date:100`, 
            DATEDIFF(m.to_date, CURDATE()) as `Days Remaining:Int:120`
        FROM `tabLibrary Membership` m
        JOIN `tabLibrary Member` mem ON m.library_member = mem.name
        WHERE CURDATE() <= m.to_date
        AND DATEDIFF(m.to_date, CURDATE()) <= 7
        ORDER BY DATEDIFF(m.to_date, CURDATE()) ASC"""
    )

    # 4. Pending Reservations Report
    create_query_report(
        "Pending Reservations Report",
        """SELECT 
            r.article as `Article:Link/Article:150`, 
            CONCAT(mem.first_name, " ", IFNULL(mem.last_name, "")) as `Member Name`,
            r.member_email as `Email`, 
            r.date as `Reservation Date:Date:120`, 
            a.status as `Current Book Status`,
            DATEDIFF(CURDATE(), r.date) as `Days Waiting:Int:100`
        FROM `tabBooks Reservation` r
        JOIN `tabArticle` a ON r.article = a.name
        JOIN `tabLibrary Member` mem ON r.member_name = mem.name
        WHERE r.status = 'Pending'
        ORDER BY r.date ASC"""
    )

    # 5. Books to Issue (Reserved + Returned) Report
    create_query_report(
        "Books to Issue Report",
        """SELECT 
            r.article as `Article:Link/Article:150`, 
            CONCAT(mem.first_name, " ", IFNULL(mem.last_name, "")) as `Reserved For`,
            r.member_email as `Email`, 
            r.date as `Reservation Date:Date:120`, 
            DATEDIFF(CURDATE(), r.date) as `Days Waited:Int:100`,
            'ISSUE NOW' as `Action Required`
        FROM `tabBooks Reservation` r
        JOIN `tabArticle` a ON r.article = a.name
        JOIN `tabLibrary Member` mem ON r.member_name = mem.name
        WHERE r.status = 'Pending' 
        AND (a.status IN ('Available', 'Reserved') OR r.ready_to_issue = 1)
        ORDER BY r.date ASC"""
    )

    # 6. Overdue Books Report
    create_query_report(
        "Overdue Books Report",
        """SELECT 
            t.name as `Transaction ID:Link/Library Transaction:120`, 
            t.article as `Book Name`, 
            CONCAT(mem.first_name, " ", IFNULL(mem.last_name, "")) as `Member Name`, 
            mem.email as `Email`, 
            mem.phone as `Phone`, 
            t.date as `Issue Date:Date:100`, 
            t.due_date as `Due Date:Date:100`, 
            DATEDIFF(CURDATE(), t.due_date) as `Days Overdue:Int:100`,
            (DATEDIFF(CURDATE(), t.due_date) * 10) as `Fine Amount:Currency:100`
        FROM `tabLibrary Transaction` t
        JOIN `tabLibrary Member` mem ON t.library_member = mem.name
        JOIN `tabArticle` a ON t.article = a.name
        WHERE t.type = 'Issue' 
        AND t.docstatus = 1 
        AND a.status = 'Issued'
        AND t.due_date < CURDATE()
        ORDER BY DATEDIFF(CURDATE(), t.due_date) DESC"""
    )

    # 7. Library Master Summary Report
    create_query_report(
        "Library Master Summary Report",
        """SELECT 'Total Books' as `Metric`, count(*) as `Value:Float:120` FROM `tabArticle`
        UNION ALL
        SELECT 'Available Books', count(*) FROM `tabArticle` WHERE status = 'Available'
        UNION ALL
        SELECT 'Issued Books', count(*) FROM `tabArticle` WHERE status = 'Issued'
        UNION ALL
        SELECT 'Total Members', count(*) FROM `tabLibrary Member`
        UNION ALL
        SELECT 'Active Memberships', count(*) FROM `tabLibrary Membership` WHERE CURDATE() <= to_date
        UNION ALL
        SELECT 'Pending Reservations', count(*) FROM `tabBooks Reservation` WHERE status = 'Pending'
        UNION ALL
        SELECT 'Overdue Fine Total', SUM(DATEDIFF(CURDATE(), due_date) * 10) 
        FROM `tabLibrary Transaction` t
        JOIN `tabArticle` a ON t.article = a.name
        WHERE t.type = 'Issue' AND t.docstatus = 1 AND a.status = 'Issued' AND t.due_date < CURDATE()"""
    )

    frappe.db.commit()

if __name__ == "__main__":
    setup_all_reports()
