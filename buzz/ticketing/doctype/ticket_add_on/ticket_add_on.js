// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ticket Add-on", {
	refresh(frm) {
		frm.set_query("ticket_type", "mandatory_for_ticket_types", () => {
			return {
				filters: {
					event: frm.doc.event,
				},
			}
		})
	},
})
