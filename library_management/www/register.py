import frappe

no_cache = 1

def get_context(context):
    context.success = False
    context.error = ""
    context.member_name = ""

    if frappe.request.method == "POST":
        try:
            first_name = frappe.form_dict.get("first_name", "")
            last_name = frappe.form_dict.get("last_name", "")
            email = frappe.form_dict.get("email", "")
            country_code = frappe.form_dict.get("country_code", "")
            phone_no = frappe.form_dict.get("phone", "")
            
            # Combine country code and phone number
            full_phone = f"{country_code}{phone_no}"

            if not first_name or not email:
                context.error = "First Name aur Email required hai!"
                return

            # Already exists check
            exists = frappe.db.exists(
                "Library Member", {"email": email}
            )
            if exists:
                context.error = "Yeh email already registered hai!"
                return

            frappe.set_user("Administrator")

            # 1. Library Member banao
            member = frappe.new_doc("Library Member")
            member.first_name = first_name
            member.last_name = last_name
            member.email = email
            member.phone = full_phone
            member.insert(ignore_permissions=True)
            frappe.db.commit()

            # 2. Frappe User banao
            user_exists = frappe.db.exists("User", email)
            if not user_exists:
                user = frappe.new_doc("User")
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.send_welcome_email = 0
                # Role assign karo
                user.append("roles", {
                    "role": "Library Member"
                })
                user.insert(ignore_permissions=True)
                frappe.db.commit()

            context.success = True
            context.member_name = first_name

            # Email notification send karein
            frappe.sendmail(
                recipients=email,
                subject=f"Welcome to Library, {first_name}!",
                message=f"Hi {first_name}, aapka library registration successfully complete ho gaya hai. Aap ab books borrow kar sakte hain."
            )

        except Exception as e:
            context.error = f"Error: {str(e)}"
            