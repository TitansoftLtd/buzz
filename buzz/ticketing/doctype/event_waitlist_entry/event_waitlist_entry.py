# Copyright (c) 2026, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class EventWaitlistEntry(Document):
	pass


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
