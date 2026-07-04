import frappe
from frappe.utils import validate_email_address

no_cache = 1

def get_context(context):
	context.success = False
	context.error = ""
	context.member_name = ""
	context.csrf_token = frappe.session.csrf_token

	if frappe.request.method == "POST":
		try:
			first_name = frappe.form_dict.get("first_name", "").strip()
			last_name = frappe.form_dict.get("last_name", "").strip()
			email = frappe.form_dict.get("email", "").strip().lower()
			country_code = frappe.form_dict.get("country_code", "")
			phone_no = frappe.form_dict.get("phone", "")
			full_phone = f"{country_code}{phone_no}"

			if not first_name or not email:
				context.error = "First Name and Email are required."
				return

			validate_email_address(email, throw=True)

			if frappe.db.exists("Library Member", {"email": email}):
				context.error = "This email is already registered."
				return

			if frappe.db.exists("User", email):
				context.error = "An account with this email already exists. Please log in instead."
				return

			member = frappe.new_doc("Library Member")
			member.first_name = first_name
			member.last_name = last_name
			member.email = email
			member.phone = full_phone
			member.insert(ignore_permissions=True)
			frappe.db.commit()

			context.success = True
			context.member_name = first_name

			frappe.sendmail(
				recipients=email,
				subject=f"Welcome to the Library, {first_name}!",
				message=(
					f"Hi {first_name},<br><br>"
					"Your library registration is complete. "
					"Please visit the library to activate your membership and start borrowing books."
				)
			)

		except frappe.ValidationError:
			context.error = "Please enter a valid email address."
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Library Registration Error")
			context.error = "Registration failed. Please try again later."
