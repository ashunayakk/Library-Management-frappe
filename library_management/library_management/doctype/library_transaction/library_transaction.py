import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils import getdate, add_days, date_diff


class LibraryTransaction(WebsiteGenerator):
	def get_route(self):
		return f"transactions/{self.name}"

	def get_feed(self):
		return _("Transaction {0} for {1}").format(self.type, self.library_member)

	def validate(self):
		if not self.date:
			frappe.throw(frappe._("Please set the Transaction Date."))
		if not self.article:
			frappe.throw(frappe._("Please select an Article."))
		if not self.library_member:
			frappe.throw(frappe._("Please select a Library Member."))

		if self.type == "Issue" and not self.due_date:
			loan_days = frappe.db.get_single_value("Library Settings", "loan_period_days") or 15
			self.due_date = add_days(self.date, loan_days)

		self.validate_membership()

	def validate_membership(self):
		member_expiry = frappe.db.get_value("Library Member", self.library_member, "membership_expiry")

		if not member_expiry or getdate(member_expiry) < getdate(self.date):
			frappe.throw(frappe._("Member does not have an active membership or it has expired."))

	def before_submit(self):
		if self.type == "Issue":
			self.validate_article_available()
			self.validate_reservation()
		elif self.type == "Return":
			self.validate_article_issued()
			self.calculate_fine()

	def validate_reservation(self):
		reservations = frappe.get_all(
			"Books Reservation",
			filters={"article": self.article, "status": "Pending"},
			fields=["name", "member_name"],
			order_by="creation asc"
		)

		if reservations and reservations[0].member_name != self.library_member:
			frappe.throw(
				frappe._("Article {0} is reserved by {1}. They are first in the queue!").format(
					self.article, reservations[0].member_name
				)
			)

	def on_submit(self):
		if self.type == "Issue":
			frappe.db.set_value("Article", self.article, "status", "Issued")
			self.update_reservation_status()
		elif self.type == "Return":
			self.handle_return()

	def handle_return(self):
		reservations = frappe.get_all(
			"Books Reservation",
			filters={"article": self.article, "status": "Pending"},
			fields=["name", "member_name", "member_email"],
			order_by="creation asc"
		)

		if reservations:
			frappe.db.set_value("Article", self.article, "status", "Reserved")
			self.notify_next_in_queue(reservations[0])
		else:
			frappe.db.set_value("Article", self.article, "status", "Available")

	def notify_next_in_queue(self, reservation):
		frappe.db.set_value("Books Reservation", reservation.name, {
			"notification_date": frappe.utils.today(),
			"ready_to_issue": 1
		})

		frappe.msgprint(
			frappe._("ALERT: Book '{0}' is reserved by {1} ({2}). Please issue it to them now!")
			.format(self.article, reservation.member_name, reservation.member_email),
			indicator="orange",
			alert=True
		)

		frappe.sendmail(
			recipients=[reservation.member_email],
			subject=frappe._("Article Available: {0}").format(self.article),
			message=frappe._(
				"Hi {0},<br><br>The article <b>{1}</b> you reserved is now available for pickup. "
				"Please collect it within 48 hours."
			).format(reservation.member_name, self.article)
		)

	def update_reservation_status(self):
		reservation = frappe.db.get_value(
			"Books Reservation",
			{"article": self.article, "member_name": self.library_member, "status": "Pending"},
			"name"
		)
		if reservation:
			frappe.db.set_value("Books Reservation", reservation, {
				"status": "Confirmed",
				"ready_to_issue": 0
			})

	def validate_article_available(self):
		article_status = frappe.db.get_value("Article", self.article, "status")
		if article_status == "Issued":
			frappe.throw(frappe._("Article {0} is already issued.").format(self.article))

	def validate_article_issued(self):
		article_status = frappe.db.get_value("Article", self.article, "status")
		if article_status == "Available":
			frappe.throw(frappe._("Article {0} is not issued and cannot be returned.").format(self.article))

	def calculate_fine(self):
		if not self.due_date:
			return

		if getdate(self.date) > getdate(self.due_date):
			late_days = date_diff(self.date, self.due_date)
			fine_per_day = frappe.db.get_single_value("Library Settings", "fine_per_day") or 10
			self.fine_amount = late_days * fine_per_day
			frappe.msgprint(
				frappe._("Late return! Fine of {0} calculated for {1} days delay.")
				.format(self.fine_amount, late_days),
				indicator="orange"
			)
