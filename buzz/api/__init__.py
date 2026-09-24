import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import now_datetime, validate_email_address


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
@rate_limit(key="ip", limit=10, seconds=3600)
def register_event_waitlist(full_name: str, email: str, phone_number: str, organization: str) -> dict:
	"""Register interest to be notified about future events."""
	validate_email_address(email, throw=True)

	existing = frappe.db.exists("Event Waitlist Entry", {"email": email.strip().lower()})
	if existing:
		frappe.throw(_("You are already registered"))

	entry = frappe.get_doc(
		{
			"doctype": "Event Waitlist Entry",
			"full_name": full_name.strip(),
			"email": email.strip().lower(),
			"phone_number": phone_number.strip(),
			"organization": organization.strip(),
		}
	)
	entry.insert(ignore_permissions=True)

	return {"success": True}


@frappe.whitelist(allow_guest=True)  # nosemgrep: frappe-semgrep-rules.rules.security.guest-whitelisted-method
def confirm_attendance(token: str) -> None:
	"""Mark a ticket as Confirmed via a one-time token. Redirects to a confirmation page."""
	if not token:
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/dashboard?confirmation=invalid"
		return

	ticket_name = frappe.db.get_value("Event Ticket", {"confirmation_token": token}, "name")
	if not ticket_name:
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/dashboard?confirmation=invalid"
		return

	ticket = frappe.get_doc("Event Ticket", ticket_name)

	if ticket.confirmation_status == "Confirmed":
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/dashboard?confirmation=already"
		return

	if ticket.docstatus != 1:
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/dashboard?confirmation=invalid"
		return

	ticket.confirmation_status = "Confirmed"
	ticket.confirmed_at = now_datetime()
	ticket.flags.ignore_permissions = True
	ticket.save()
	frappe.db.commit()

	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = "/dashboard?confirmation=success"
