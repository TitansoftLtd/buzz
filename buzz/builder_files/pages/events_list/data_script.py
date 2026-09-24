def to_card(event):
	# Sibling functions are not visible to each other in the safe_exec sandbox.
	def format_day(value):
		# Script-level names are not visible inside functions in the safe_exec sandbox.
		months = ["January", "February", "March", "April", "May", "June", "July",
			"August", "September", "October", "November", "December"]
		value = frappe.utils.getdate(value)
		return str(value.day) + " " + months[value.month - 1] + " " + str(value.year)

	start_date = frappe.utils.getdate(event.start_date)
	end_date = frappe.utils.getdate(event.end_date) if event.end_date else start_date
	if end_date == start_date:
		date_label = format_day(start_date)
	elif start_date.month == end_date.month and start_date.year == end_date.year:
		date_label = str(start_date.day) + " - " + format_day(end_date)
	else:
		date_label = format_day(start_date) + " - " + format_day(end_date)
	return {
		"title": event.title,
		"image": event.card_image or event.banner_image or "",
		"date_label": date_label,
		"place": event.venue or event.medium or "",
		"url": "/events/" + event.route,
	}

events = frappe.get_all(
	"Buzz Event",
	filters={"is_published": 1, "route": ["is", "set"]},
	fields=["title", "route", "card_image", "banner_image", "start_date", "end_date", "venue", "medium"],
	order_by="start_date asc",
)
today = frappe.utils.getdate(frappe.utils.today())
upcoming = []
past = []
for event in events:
	last_day = frappe.utils.getdate(event.end_date or event.start_date)
	if last_day >= today:
		upcoming.append(to_card(event))
	else:
		past.insert(0, to_card(event))

data.title = "Events"
data.page_title = "Events"
data.upcoming = upcoming
data.past = past