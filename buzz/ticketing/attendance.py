# Copyright (c) 2026, BWH Studios and contributors
# For license information, please see license.txt

import secrets

import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, today


def _generate_token() -> str:
	return secrets.token_urlsafe(32)


def _get_confirm_url(token: str) -> str:
	return f"{frappe.utils.get_url()}/api/method/buzz.api.confirm_attendance?token={token}"


def _send_confirmation_email(ticket, event_doc, is_reminder: bool = False) -> None:
	if not ticket.confirmation_token:
		ticket.db_set("confirmation_token", _generate_token(), update_modified=False)

	confirm_url = _get_confirm_url(ticket.confirmation_token)
	deadline = event_doc.confirmation_deadline

	if is_reminder:
		subject = f"Reminder: Confirm your attendance for {event_doc.title}"
		intro = (
			"<p>This is a friendly reminder to confirm your attendance. "
			f"If we don't hear from you by <strong>{deadline}</strong>, your ticket will be automatically cancelled "
			"to free up the slot for someone else.</p>"
		)
	else:
		subject = f"Please confirm your attendance for {event_doc.title}"
		intro = (
			"<p>We're excited to have you at our upcoming event. "
			"Please confirm your attendance using the button below so we can plan accordingly.</p>"
			f"<p>Confirm by <strong>{deadline}</strong> or your ticket will be automatically cancelled.</p>"
		)

	message = f"""
	<p>Hi {ticket.first_name},</p>
	{intro}
	<p style="margin: 24px 0;">
		<a href="{confirm_url}"
		   style="background:#171717;color:#fff;padding:10px 20px;text-decoration:none;border-radius:6px;display:inline-block;">
			Confirm Attendance
		</a>
	</p>
	<p style="font-size: 12px; color: #6b7280;">
		Or copy this link into your browser:<br>{confirm_url}
	</p>
	<p>See you there!<br>{event_doc.title} Team</p>
	"""

	frappe.sendmail(
		recipients=[ticket.attendee_email],
		subject=subject,
		message=message,
		delayed=False,
	)


@frappe.whitelist()
def trigger_confirmation_emails(event: str) -> dict:
	"""Whitelisted method to manually send confirmation emails for an event."""
	count = send_confirmation_emails_for_event(event)
	return {"sent": count}


@frappe.whitelist()
def send_reminder_to_confirmed(
	event: str,
	email_template: str | None = None,
	subject: str | None = None,
	message: str | None = None,
) -> dict:
	"""Send a reminder email to all confirmed attendees of an event.

	Either provide `email_template` (preferred) OR `subject` + `message`.
	The email body is rendered with Jinja using the ticket/event context.
	"""
	event_doc = frappe.get_cached_doc("Buzz Event", event)

	if email_template:
		template_doc = frappe.get_doc("Email Template", email_template)
		raw_subject = template_doc.subject
		raw_message = template_doc.response_
	else:
		if not subject or not message:
			frappe.throw(_("Either an Email Template or Subject + Message is required"))
		raw_subject = subject
		raw_message = message

	tickets = frappe.get_all(
		"Event Ticket",
		filters={
			"event": event,
			"docstatus": 1,
			"confirmation_status": "Confirmed",
		},
		fields=["name", "first_name", "last_name", "attendee_name", "attendee_email"],
	)

	for ticket in tickets:
		context = {
			"first_name": ticket.first_name or "",
			"last_name": ticket.last_name or "",
			"attendee_name": ticket.attendee_name or "",
			"attendee_email": ticket.attendee_email,
			"event_title": event_doc.title,
			"event_start_date": event_doc.start_date,
			"event_end_date": event_doc.end_date,
			"event_start_time": event_doc.start_time,
			"event_end_time": event_doc.end_time,
			"event_venue": event_doc.venue,
			"event": event_doc,
			"ticket": ticket,
		}
		rendered_subject = frappe.render_template(raw_subject, context)
		rendered_message = frappe.render_template(raw_message, context)

		frappe.sendmail(
			recipients=[ticket.attendee_email],
			subject=rendered_subject,
			message=rendered_message,
			delayed=False,
		)

	return {"sent": len(tickets)}


def send_confirmation_emails_for_event(event: str) -> int:
	"""Send initial confirmation emails for all unconfirmed, unsent tickets of an event."""
	event_doc = frappe.get_cached_doc("Buzz Event", event)
	if not event_doc.require_attendance_confirmation:
		frappe.throw(_("Attendance confirmation is not enabled for this event"))

	tickets = frappe.get_all(
		"Event Ticket",
		filters={
			"event": event,
			"docstatus": 1,
			"confirmation_status": "Pending",
			"confirmation_sent_at": ["is", "not set"],
		},
		pluck="name",
	)

	count = 0
	for ticket_name in tickets:
		ticket = frappe.get_doc("Event Ticket", ticket_name)
		_send_confirmation_email(ticket, event_doc, is_reminder=False)
		ticket.db_set("confirmation_sent_at", now_datetime(), update_modified=False)
		count += 1

	frappe.db.commit()
	return count


def process_attendance_confirmations() -> None:
	"""Daily scheduled job: send reminders, auto-cancel expired tickets."""
	events = frappe.get_all(
		"Buzz Event",
		filters={"require_attendance_confirmation": 1, "is_published": 1},
		fields=[
			"name",
			"title",
			"confirmation_deadline",
			"send_confirmation_reminder_days_before",
		],
	)

	for event in events:
		if not event.confirmation_deadline:
			continue

		deadline = getdate(event.confirmation_deadline)
		today_date = getdate(today())
		event_doc = frappe.get_cached_doc("Buzz Event", event.name)

		# Auto-cancel expired tickets
		if today_date > deadline:
			expired_tickets = frappe.get_all(
				"Event Ticket",
				filters={
					"event": event.name,
					"docstatus": 1,
					"confirmation_status": "Pending",
				},
				pluck="name",
			)
			for ticket_name in expired_tickets:
				try:
					ticket = frappe.get_doc("Event Ticket", ticket_name)
					ticket.confirmation_status = "Declined"
					ticket.flags.ignore_permissions = True
					ticket.cancel()
				except Exception:
					frappe.log_error(
						f"Failed to auto-cancel ticket {ticket_name}",
						"Attendance Auto-Cancel",
					)
			continue

		# Send reminder
		reminder_days = event.send_confirmation_reminder_days_before or 0
		if reminder_days and today_date == add_days(deadline, -reminder_days):
			pending_tickets = frappe.get_all(
				"Event Ticket",
				filters={
					"event": event.name,
					"docstatus": 1,
					"confirmation_status": "Pending",
					"confirmation_reminder_sent_at": ["is", "not set"],
				},
				pluck="name",
			)
			for ticket_name in pending_tickets:
				ticket = frappe.get_doc("Event Ticket", ticket_name)
				_send_confirmation_email(ticket, event_doc, is_reminder=True)
				ticket.db_set(
					"confirmation_reminder_sent_at", now_datetime(), update_modified=False
				)

	frappe.db.commit()
