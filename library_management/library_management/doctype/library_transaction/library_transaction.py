import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class LibraryTransaction(Document):

    def validate(self):
        # Basic validation on Save
        if not self.date:
            frappe.throw("Please set the Transaction Date.")
        if not self.article:
            frappe.throw("Please select an Article.")
        if not self.library_member:
            frappe.throw("Please select a Library Member.")

    def before_submit(self):
        if self.type == "Issue":
            self.validate_membership()
            self.validate_article_available()
        elif self.type == "Return":
            self.validate_article_issued()

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
            frappe.throw("❌ Member does not have an active membership!")

    def validate_article_available(self):
        article_status = frappe.db.get_value(
            "Article", self.article, "status"
        )
        if article_status == "Issued":
            frappe.throw("❌ This book is already issued!")
        frappe.db.set_value("Article", self.article, "status", "Issued")

    def validate_article_issued(self):
        article_status = frappe.db.get_value(
            "Article", self.article, "status"
        )
        if article_status == "Available":
            frappe.throw("❌ This book is not issued yet. Cannot return!")
        frappe.db.set_value("Article", self.article, "status", "Available")