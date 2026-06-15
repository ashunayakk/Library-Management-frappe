import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class BooksReservation(Document):
	def validate(self):
		self.set_member_email()
		self.validate_membership()
		self.validate_article_status()
		self.validate_duplicate_reservation()

	def set_member_email(self):
		if not self.member_email:
			self.member_email = frappe.db.get_value("Library Member", self.member_name, "email")

	def validate_membership(self):
		# Check if member exists and has an active membership
		member_expiry = frappe.db.get_value("Library Member", self.member_name, "membership_expiry")
		
		if not member_expiry or getdate(member_expiry) < getdate(frappe.utils.today()):
			frappe.throw(frappe._("Member {0} does not have an active membership.").format(self.member_name))

	def validate_article_status(self):
		article_status = frappe.db.get_value("Article", self.article, "status")
		if article_status == "Available":
			frappe.throw(
				frappe._("Article {0} is currently Available. Please issue it directly instead of reserving.").format(self.article)
			)

	def validate_duplicate_reservation(self):
		# Prevent the same member from reserving the same article twice if it's already pending
		existing_reservation = frappe.db.exists(
			"Books Reservation",
			{
				"article": self.article,
				"member_name": self.member_name,
				"status": "Pending",
				"name": ["!=", self.name]
			}
		)
		if existing_reservation:
			frappe.throw(frappe._("You already have a pending reservation for this article."))
