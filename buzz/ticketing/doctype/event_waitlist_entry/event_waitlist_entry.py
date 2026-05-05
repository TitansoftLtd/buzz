# Copyright (c) 2026, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class EventWaitlistEntry(Document):
	pass


def _ensure_user(email: str, first_name: str, last_name: str) -> str:
	"""Return the email of an existing or newly-created Website User."""
	email = email.lower().strip()
	if frappe.db.exists("User", email):
		return email

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": first_name or "Attendee",
			"last_name": last_name or "",
			"enabled": 1,
			"user_type": "Website User",
			"send_welcome_email": 0,
		}
	)
	user.insert(ignore_permissions=True, ignore_if_duplicate=True)
	return email


@frappe.whitelist()
def notify_waitlist_entries(entries: list | str, event: str, subject: str, message: str):
	"""Send email notification to selected waitlist entries about an event."""
	if isinstance(entries, str):
		entries = frappe.parse_json(entries)

	if not entries:
		frappe.throw(_("No entries selected"))

	event_doc = frappe.get_cached_doc("Buzz Event", event)

	for entry_name in entries:
		entry = frappe.get_doc("Event Waitlist Entry", entry_name)

		personalized_message = message.replace("{{ full_name }}", entry.full_name)

		frappe.sendmail(
			recipients=[entry.email],
			subject=subject,
			message=personalized_message,
			delayed=False,
		)

		entry.status = "Notified"
		entry.last_notified_on = now_datetime()
		entry.notified_for_event = event
		entry.save(ignore_permissions=True)

	frappe.db.commit()
	frappe.msgprint(
		_("Notification sent to {0} entries").format(len(entries)),
		title=_("Success"),
		indicator="green",
	)


@frappe.whitelist()
def allocate_ticket(entry: str, event: str, ticket_type: str):
	"""Allocate a ticket to a waitlist entry when a slot becomes available."""
	waitlist_entry = frappe.get_doc("Event Waitlist Entry", entry)
	event_doc = frappe.get_cached_doc("Buzz Event", event)
	ticket_type_doc = frappe.get_doc("Event Ticket Type", ticket_type, for_update=True)

	if not ticket_type_doc.are_tickets_available(1):
		frappe.throw(
			_("No tickets available for {0}").format(ticket_type_doc.title)
		)

	name_parts = waitlist_entry.full_name.strip().split(" ", 1)
	first_name = name_parts[0]
	last_name = name_parts[1] if len(name_parts) > 1 else ""

	booking_user = _ensure_user(waitlist_entry.email, first_name, last_name)

	booking = frappe.new_doc("Event Booking")
	booking.event = event
	booking.user = booking_user
	booking.append(
		"attendees",
		{
			"first_name": first_name,
			"last_name": last_name,
			"email": waitlist_entry.email,
			"phone_number": waitlist_entry.phone_number,
			"organization": waitlist_entry.organization,
			"ticket_type": ticket_type,
		},
	)
	booking.flags.ignore_permissions = True
	booking.insert()

	if booking.total_amount == 0:
		booking.submit()

	waitlist_entry.status = "Converted"
	waitlist_entry.save(ignore_permissions=True)

	frappe.sendmail(
		recipients=[waitlist_entry.email],
		subject=f"A spot has opened up — {event_doc.title}",
		message=f"""
		<p>Hi {waitlist_entry.full_name},</p>
		<p>Good news! A ticket has been allocated to you for <strong>{event_doc.title}</strong>.</p>
		<p>We've created a booking under your email. You'll receive a separate ticket confirmation shortly.</p>
		<p>Booking ID: <strong>{booking.name}</strong></p>
		""",
		delayed=False,
	)

	return {
		"booking": booking.name,
		"submitted": booking.total_amount == 0,
	}
