// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Buzz Coupon Code", {
	refresh(frm) {
		frm.set_query("ticket_type", () => {
			return {
				filters: {
					event: frm.doc.event,
				},
			}
		})

		frm.set_query("add_on", "free_add_ons", () => {
			return {
				filters: {
					event: frm.doc.event,
				},
			}
		})

		frm.trigger("coupon_type")
		frm.trigger("applies_to")
	},

	coupon_type(frm) {
		if (frm.doc.coupon_type === "Free Tickets") {
			setValueIfChanged(frm, "applies_to", "Event")
		}
	},

	applies_to(frm) {
		if (frm.doc.applies_to === "Event") {
			clearValue(frm, "event_category")
		} else if (frm.doc.applies_to === "Event Category") {
			clearValue(frm, "event")
		} else {
			clearValue(frm, "event")
			clearValue(frm, "event_category")
		}
	},
})

// Only touch the field when the value actually differs, so loading a saved
// coupon doesn't mark the form dirty ("Not Saved").
function setValueIfChanged(frm, fieldname, value) {
	if (frm.doc[fieldname] !== value) {
		frm.set_value(fieldname, value)
	}
}

function clearValue(frm, fieldname) {
	if (!is_null(frm.doc[fieldname])) {
		frm.set_value(fieldname, null)
	}
}
