frappe.ui.form.on("Event Waitlist Entry", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Send Notification"), () => {
				const dialog = new frappe.ui.Dialog({
					title: __("Notify {0}", [frm.doc.full_name]),
					fields: [
						{
							fieldname: "event",
							fieldtype: "Link",
							label: __("Event"),
							options: "Buzz Event",
							reqd: 1,
							get_query: () => ({
								filters: { is_published: 1 },
							}),
						},
						{
							fieldname: "subject",
							fieldtype: "Data",
							label: __("Email Subject"),
							reqd: 1,
							default: "You're Invited! New Event Announcement",
						},
						{
							fieldname: "message",
							fieldtype: "Text Editor",
							label: __("Email Message"),
							reqd: 1,
							description: __(
								"Use {{ full_name }} to personalize the message."
							),
						},
					],
					primary_action_label: __("Send"),
					primary_action(values) {
						frappe.call({
							method: "buzz.ticketing.doctype.event_waitlist_entry.event_waitlist_entry.notify_waitlist_entries",
							args: {
								entries: [frm.doc.name],
								event: values.event,
								subject: values.subject,
								message: values.message,
							},
							freeze: true,
							freeze_message: __("Sending notification..."),
							callback() {
								dialog.hide();
								frm.reload_doc();
							},
						});
					},
				});

				dialog.show();
			});
		}
	},
});
