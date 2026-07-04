# Copyright (c) 2026, Ashutosh and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


def make_library_member(active=True):
	# Library Member.create_user() sends a welcome email; this site has no
	# outgoing email account configured, so mute it for tests.
	frappe.flags.mute_emails = True
	suffix = frappe.generate_hash(length=8)
	member = frappe.get_doc({
		"doctype": "Library Member",
		"first_name": "Test",
		"last_name": suffix,
		"email": f"test.member.{suffix}@example.com",
		"phone": "+14155552671",
	})
	member.insert()
	if active:
		frappe.db.set_value("Library Member", member.name, "membership_expiry", add_days(today(), 30))
	return member


def make_article(status="Issued"):
	suffix = frappe.generate_hash(length=8)
	article = frappe.get_doc({
		"doctype": "Article",
		"article_name": f"Test Article {suffix}",
		"author": "Test Author",
		"status": status,
	})
	article.insert()
	return article


def make_reservation(article, member):
	return frappe.get_doc({
		"doctype": "Books Reservation",
		"article": article.name,
		"member_name": member.name,
		"date": today(),
	})


class TestBooksReservation(FrappeTestCase):
	def test_reservation_blocked_without_active_membership(self):
		member = make_library_member(active=False)
		article = make_article(status="Issued")
		self.assertRaises(frappe.ValidationError, make_reservation(article, member).insert)

	def test_reservation_blocked_if_article_available(self):
		member = make_library_member(active=True)
		article = make_article(status="Available")
		self.assertRaises(frappe.ValidationError, make_reservation(article, member).insert)

	def test_duplicate_pending_reservation_blocked(self):
		member = make_library_member(active=True)
		article = make_article(status="Issued")

		make_reservation(article, member).insert()

		self.assertRaises(frappe.ValidationError, make_reservation(article, member).insert)
