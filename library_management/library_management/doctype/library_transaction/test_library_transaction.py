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


def make_article(status="Available"):
	suffix = frappe.generate_hash(length=8)
	article = frappe.get_doc({
		"doctype": "Article",
		"article_name": f"Test Article {suffix}",
		"author": "Test Author",
		"status": status,
	})
	article.insert()
	return article


class TestLibraryTransaction(FrappeTestCase):
	def test_issue_blocked_without_active_membership(self):
		member = make_library_member(active=False)
		article = make_article(status="Available")

		txn = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"type": "Issue",
			"library_member": member.name,
			"date": today(),
		})
		self.assertRaises(frappe.ValidationError, txn.insert)

	def test_issue_blocked_if_article_already_issued(self):
		member = make_library_member(active=True)
		article = make_article(status="Issued")

		txn = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"type": "Issue",
			"library_member": member.name,
			"date": today(),
		})
		txn.insert()
		self.assertRaises(frappe.ValidationError, txn.submit)

	def test_return_calculates_fine_for_late_return(self):
		member = make_library_member(active=True)
		article = make_article(status="Issued")

		txn = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"type": "Return",
			"library_member": member.name,
			"date": today(),
			"due_date": add_days(today(), -5),
		})
		txn.insert()
		txn.submit()
		fine_per_day = frappe.db.get_single_value("Library Settings", "fine_per_day") or 10
		self.assertEqual(txn.fine_amount, 5 * fine_per_day)

	def test_return_has_no_fine_when_on_time(self):
		member = make_library_member(active=True)
		article = make_article(status="Issued")

		txn = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"type": "Return",
			"library_member": member.name,
			"date": today(),
			"due_date": add_days(today(), 5),
		})
		txn.insert()
		txn.submit()
		self.assertFalse(txn.fine_amount)

	def test_cancel_issue_reverts_article_to_available(self):
		member = make_library_member(active=True)
		article = make_article(status="Available")

		txn = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"type": "Issue",
			"library_member": member.name,
			"date": today(),
		})
		txn.insert()
		txn.submit()
		self.assertEqual(frappe.db.get_value("Article", article.name, "status"), "Issued")

		txn.cancel()
		self.assertEqual(frappe.db.get_value("Article", article.name, "status"), "Available")
