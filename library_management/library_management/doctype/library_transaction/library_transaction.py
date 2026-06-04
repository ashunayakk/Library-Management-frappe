import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, date_diff

class LibraryTransaction(Document):

    def validate(self):
        if not self.date:
            frappe.throw("Please set the Transaction Date.")
        if not self.article:
            frappe.throw("Please select an Article.")
        if not self.library_member:
            frappe.throw("Please select a Library Member.")
        # Transaction date se 15 din baad due date set karo
        if self.type == "Issue" and not self.due_date:
            self.due_date = add_days(self.date, 15)

    def before_submit(self):
        if self.type == "Issue":
            self.validate_membership()
            self.validate_article_available()
        elif self.type == "Return":
            self.validate_article_issued()
            self.calculate_fine()

    def calculate_fine(self):
        if not self.due_date:
            return
        today = getdate()
        due_date = getdate(self.due_date)
        if today > due_date:
            late_days = date_diff(today, due_date)
            fine = late_days * 5
            self.fine_amount = fine
            frappe.msgprint(
                f"Late! Fine: {fine} ({late_days} days)",
                title="Fine Alert",
                indicator="red"
            )
        else:
            frappe.msgprint(
                "Time Pe Return! Shukriya",
                title="Success",
                indicator="green"
            )

    def validate_membership(self):
        today = getdate()
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "from_date": ("<=", today),
                "to_date": (">=", today),
            }
        )
        if not valid_membership:
            frappe.throw("Member does not have an active membership.")

    def validate_article_available(self):
        article_status = frappe.db.get_value(
            "Article", self.article, "status"
        )
        if article_status == "Issued":
            frappe.throw("This book is already issued!")
        frappe.db.set_value(
            "Article", self.article, "status", "Issued"
        )

    def validate_article_issued(self):
        article_status = frappe.db.get_value(
            "Article", self.article, "status"
        )
        if article_status == "Available":
            frappe.throw("This book is not issued. Cannot return!")
        frappe.db.set_value(
            "Article", self.article, "status", "Available"
        )