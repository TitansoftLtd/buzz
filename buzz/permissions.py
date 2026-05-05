# Copyright (c) 2026, BWH Studios and contributors
# For license information, please see license.txt
"""Custom permission rules so users can see records linked to them."""

import frappe

PRIVILEGED_ROLES = {"System Manager", "Event Manager"}


def _is_privileged(user: str) -> bool:
	if user == "Administrator":
		return True
	user_roles = set(frappe.get_roles(user) or [])
	return bool(user_roles & PRIVILEGED_ROLES)


def event_booking_query(user: str | None = None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	escaped = frappe.db.escape(user)
	return f"(`tabEvent Booking`.user = {escaped} OR `tabEvent Booking`.owner = {escaped})"


def event_booking_has_permission(doc, ptype, user):
	if _is_privileged(user):
		return True
	if ptype not in ("read", "write", "cancel"):
		return None
	if getattr(doc, "user", None) == user or doc.owner == user:
		return True
	return None


def event_ticket_query(user: str | None = None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	escaped = frappe.db.escape(user)
	return (
		f"(`tabEvent Ticket`.attendee_email = {escaped} "
		f"OR `tabEvent Ticket`.owner = {escaped})"
	)


def event_ticket_has_permission(doc, ptype, user):
	if _is_privileged(user):
		return True
	if ptype not in ("read", "write"):
		return None
	if getattr(doc, "attendee_email", None) == user or doc.owner == user:
		return True
	return None
