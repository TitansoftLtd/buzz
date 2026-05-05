# Copyright (c) 2026, BWH Studios and contributors
# For license information, please see license.txt
"""Custom permission rules so users can see records linked to them
even when they are not the document owner (e.g. records created by an admin
during waitlist allocation, or by a guest checkout)."""

import frappe


def event_booking_query(user: str | None = None):
	"""Allow users to see Event Bookings where they are the linked user."""
	user = user or frappe.session.user
	if user == "Administrator":
		return ""
	escaped = frappe.db.escape(user)
	return f"(`tabEvent Booking`.user = {escaped} OR `tabEvent Booking`.owner = {escaped})"


def event_booking_has_permission(doc, ptype, user):
	if user == "Administrator":
		return True
	if ptype not in ("read", "write", "cancel"):
		return None
	if doc.user == user or doc.owner == user:
		return True
	return None


def event_ticket_query(user: str | None = None):
	"""Allow users to see Event Tickets where they are the attendee."""
	user = user or frappe.session.user
	if user == "Administrator":
		return ""
	escaped = frappe.db.escape(user)
	return (
		f"(`tabEvent Ticket`.attendee_email = {escaped} "
		f"OR `tabEvent Ticket`.owner = {escaped})"
	)


def event_ticket_has_permission(doc, ptype, user):
	if user == "Administrator":
		return True
	if ptype not in ("read", "write"):
		return None
	if doc.attendee_email == user or doc.owner == user:
		return True
	return None
