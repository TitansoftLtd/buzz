frappe.ui.form.on("Event Waitlist Entry", {
	refresh(frm) {
		if (frm.is_new()) return;

		if (frm.doc.status !== "Converted") {
			frm.add_custom_button(
				__("Allocate Ticket"),
				() => {
					const dialog = new frappe.ui.Dialog({
						title: __("Allocate Ticket to {0}", [frm.doc.full_name]),
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
								onchange() {
									const event = dialog.get_value("event");
									dialog.set_value("ticket_type", "");
									if (!event) return;

									frappe.db
										.get_value("Buzz Event", event, "default_ticket_type")
										.then((r) => {
											if (r.message?.default_ticket_type) {
												dialog.set_value(
													"ticket_type",
													r.message.default_ticket_type
												);
											}
										});
								},
							},
							{
								fieldname: "ticket_type",
								fieldtype: "Link",
								label: __("Ticket Type"),
								options: "Event Ticket Type",
								reqd: 1,
								get_query: () => ({
									filters: {
										event: dialog.get_value("event"),
										is_published: 1,
									},
								}),
							},
						],
						primary_action_label: __("Allocate"),
						primary_action(values) {
							frappe.call({
								method: "buzz.ticketing.doctype.event_waitlist_entry.event_waitlist_entry.allocate_ticket",
								args: {
									entry: frm.doc.name,
									event: values.event,
									ticket_type: values.ticket_type,
								},
								freeze: true,
								freeze_message: __("Allocating ticket..."),
								callback(r) {
									if (r.message) {
										dialog.hide();
										frappe.show_alert(
											{
												message: __("Ticket allocated. Booking: {0}", [
													r.message.booking,
												]),
												indicator: "green",
											},
											7
										);
										frm.reload_doc();
									}
								},
							});
						},
					});
					dialog.show();
				},
				__("Actions")
			);
		}

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
	},
});
