def format_day(value):
	# Script-level names are not visible inside functions in the safe_exec sandbox.
	months = ["January", "February", "March", "April", "May", "June", "July",
		"August", "September", "October", "November", "December"]
	value = frappe.utils.getdate(value)
	return str(value.day) + " " + months[value.month - 1] + " " + str(value.year)

def format_clock(value):
	if not value:
		return ""
	total_minutes = int(frappe.utils.flt(frappe.utils.to_timedelta(value).total_seconds())) // 60
	hours = (total_minutes // 60) % 24
	minutes = total_minutes % 60
	suffix = "AM" if hours < 12 else "PM"
	display_hours = hours % 12 or 12
	return str(display_hours).zfill(2) + ":" + str(minutes).zfill(2) + " " + suffix

route = frappe.form_dict.route
if not route:
	# The Builder editor previews this page without a route; show the latest published event.
	route = frappe.db.get_value(
		"Buzz Event", {"is_published": 1, "route": ["is", "set"]}, "route", order_by="start_date desc"
	)

event = frappe.db.get_value(
	"Buzz Event",
	{"route": route, "is_published": 1},
	["name", "title", "route", "banner_image", "about", "short_description", "start_date", "end_date",
		"start_time", "end_time", "time_zone_label", "venue", "host", "medium"],
	as_dict=True,
)
if not event:
	frappe.throw("Event not found", frappe.DoesNotExistError)

start_date = frappe.utils.getdate(event.start_date)
end_date = frappe.utils.getdate(event.end_date) if event.end_date else start_date
if end_date == start_date:
	date_label = format_day(start_date)
elif start_date.month == end_date.month and start_date.year == end_date.year:
	date_label = str(start_date.day) + " - " + format_day(end_date)
else:
	date_label = format_day(start_date) + " - " + format_day(end_date)

time_label = format_clock(event.start_time)
if event.end_time:
	time_label = time_label + " - " + format_clock(event.end_time)
if time_label and event.time_zone_label:
	time_label = time_label + " (" + event.time_zone_label + ")"

venue = {}
if event.venue:
	venue = {"name": event.venue, "address": frappe.db.get_value("Event Venue", event.venue, "address") or ""}
elif event.medium == "Online":
	venue = {"name": "Online", "address": ""}

host = {}
if event.host:
	host_details = frappe.db.get_value("Event Host", event.host, ["logo", "by_line"], as_dict=True) or {}
	host = {"name": event.host, "logo": host_details.get("logo") or "", "by_line": host_details.get("by_line") or ""}

speaker_names = frappe.get_all(
	"Event Featured Speaker", filters={"parent": event.name, "parenttype": "Buzz Event"}, pluck="speaker", order_by="idx"
)
speakers = []
if speaker_names:
	speakers = frappe.get_all(
		"Speaker Profile",
		filters={"name": ["in", speaker_names]},
		fields=["display_name", "designation", "company", "display_image"],
	)

sponsors = frappe.get_all(
	"Event Sponsor",
	filters={"event": event.name},
	fields=["company_name", "company_logo", "website"],
	order_by="creation",
)
for sponsor in sponsors:
	sponsor.website = sponsor.website or "#"

# Builder applies page_title as the tab title only when a `title` key is also present.
data.title = event.title
data.page_title = event.title
data.metatags = {
	"title": event.title,
	"description": event.short_description or "",
	"image": event.banner_image or "",
}
data.event = event
data.event.date_label = date_label
data.event.time_label = time_label
data.event.register_url = "/b/register/" + event.route
data.venue = venue
data.host = host
data.speakers = speakers
data.sponsors = sponsors