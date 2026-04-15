frappe.listview_settings["Event Waitlist Entry"] = {
	get_indicator(doc) {
		if (doc.status === "Converted") {
			return [__("Converted"), "green", "status,=,Converted"];
		} else if (doc.status === "Notified") {
			return [__("Notified"), "blue", "status,=,Notified"];
		}
		return [__("New"), "orange", "status,=,New"];
	},

	onload(listview) {
		listview.page.add_action_item(__("Notify About Event"), () => {
			const selected = listview.get_checked_items();
			if (!selected.length) {
				frappe.msgprint(__("Please select at least one entry"));
				return;
			}

			const dialog = new frappe.ui.Dialog({
				title: __("Notify About Event"),
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
							"Use {{ full_name }} to personalize the message with the recipient's name."
						),
					},
				],
				primary_action_label: __("Send Notification"),
				primary_action(values) {
					const entryNames = selected.map((entry) => entry.name);

					frappe.call({
						method: "buzz.ticketing.doctype.event_waitlist_entry.event_waitlist_entry.notify_waitlist_entries",
						args: {
							entries: entryNames,
							event: values.event,
							subject: values.subject,
							message: values.message,
						},
						freeze: true,
						freeze_message: __("Sending notifications..."),
						callback() {
							dialog.hide();
							listview.refresh();
						},
					});
				},
			});

			dialog.show();
		});
	},
};
