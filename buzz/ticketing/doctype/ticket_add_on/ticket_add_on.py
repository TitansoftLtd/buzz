# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TicketAddon(Document):
	def validate(self):
		self.validate_duplicate_title()
		self.validate_mandatory_ticket_types()

	def validate_duplicate_title(self):
		if frappe.db.exists(
			self.doctype,
			{
				"event": self.event,
				"title": self.title,
				"name": ["!=", self.name],
			},
		):
			frappe.throw(_("Add-on <b>{0}</b> already exists for this event").format(self.title))

	def validate_mandatory_ticket_types(self):
		ticket_types = [row.ticket_type for row in self.mandatory_for_ticket_types]
		if not ticket_types:
			return

		ticket_types_of_event = frappe.get_all(
			"Event Ticket Type",
			filters={"name": ["in", ticket_types], "event": self.event},
			pluck="name",
		)
		ticket_types_of_event = {str(name) for name in ticket_types_of_event}
		for ticket_type in ticket_types:
			if str(ticket_type) not in ticket_types_of_event:
				frappe.throw(
					_("Ticket Type {0} does not belong to event {1}").format(ticket_type, self.event)
				)


def get_mandatory_ticket_types(add_on_names: list) -> dict[str, set[str]]:
	"""Map each add-on name to the set of ticket type names (as strings) that require it."""
	if not add_on_names:
		return {}

	rows = frappe.get_all(
		"Add-on Mandatory Ticket Type",
		filters={"parenttype": "Ticket Add-on", "parent": ["in", add_on_names]},
		fields=["parent", "ticket_type"],
	)
	mandatory_ticket_types = {}
	for row in rows:
		mandatory_ticket_types.setdefault(row.parent, set()).add(str(row.ticket_type))
	return mandatory_ticket_types
