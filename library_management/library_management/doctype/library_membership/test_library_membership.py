# Copyright (c) 2026, Ashutosh and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_months, today


def make_library_member():
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
	return member


class TestLibraryMembership(FrappeTestCase):
	def make_membership(self, member, paid=1, membership_plan="Monthly"):
		# to_date is a mandatory field, so it must be supplied up front - the
		# before_submit auto-calculation only fills it in when it's left blank,
		# which can't happen through a normal insert().
		return frappe.get_doc({
			"doctype": "Library Membership",
			"library_member": member.name,
			"membership_plan": membership_plan,
			"from_date": today(),
			"to_date": add_months(today(), 1),
			"paid": paid,
		})

	def test_cannot_submit_without_payment(self):
		member = make_library_member()
		membership = self.make_membership(member, paid=0)
		membership.insert()
		self.assertRaises(frappe.ValidationError, membership.submit)

	def test_submit_sets_expiry_and_role(self):
		member = make_library_member()
		membership = self.make_membership(member, paid=1)
		membership.insert()
		membership.submit()

		expiry = frappe.db.get_value("Library Member", member.name, "membership_expiry")
		self.assertEqual(str(expiry), str(add_months(today(), 1)))

		user = frappe.db.get_value("Library Member", member.name, "user")
		roles = [r.role for r in frappe.get_doc("User", user).roles]
		self.assertIn("Library Member", roles)

	def test_cancel_reverts_expiry_and_role(self):
		member = make_library_member()
		membership = self.make_membership(member, paid=1)
		membership.insert()
		membership.submit()
		membership.cancel()

		expiry = frappe.db.get_value("Library Member", member.name, "membership_expiry")
		self.assertIsNone(expiry)

		user = frappe.db.get_value("Library Member", member.name, "user")
		roles = [r.role for r in frappe.get_doc("User", user).roles]
		self.assertNotIn("Library Member", roles)

	def test_duplicate_active_membership_blocked(self):
		member = make_library_member()
		first = self.make_membership(member, paid=1)
		first.insert()
		first.submit()

		second = self.make_membership(member, paid=1)
		second.insert()
		self.assertRaises(frappe.ValidationError, second.submit)
