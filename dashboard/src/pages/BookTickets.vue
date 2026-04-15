<template>
	<div>
		<div v-if="eventBookingResource.loading" class="flex justify-center py-16">
			<Spinner class="w-8 h-8" />
		</div>
		<div
			v-else-if="eventNotFound"
			class="flex flex-col items-center justify-center py-16 px-4"
		>
			<div class="text-center max-w-md">
				<h2 class="text-xl font-semibold text-ink-gray-8 mb-2">
					{{ __("Event Not Found") }}
				</h2>
				<p class="text-ink-gray-6 mb-6">
					{{
						__(
							"The event you are looking for does not exist or may have been removed."
						)
					}}
				</p>
				<Button variant="solid" size="lg" @click="$router.push('/')">{{
					__("Go to Home")
				}}</Button>
			</div>
		</div>
		<div
			v-else-if="registrationsClosed"
			class="flex flex-col items-center justify-center py-16 px-4"
		>
			<div class="text-center max-w-md">
				<img
					v-if="eventBookingData.eventDetails?.banner_image"
					:src="eventBookingData.eventDetails.banner_image"
					:alt="eventBookingData.eventDetails.title"
					class="w-full rounded-lg mb-6 object-cover max-h-48"
				/>
				<h2 class="text-xl font-semibold text-ink-gray-8 mb-2">
					{{ __("Registrations Closed") }}
				</h2>
				<p class="text-ink-gray-6 mb-6">
					{{ __("Registrations for this event are closed.") }}
				</p>
				<Button variant="solid" size="lg" @click="goToHome">{{
					__("Browse Other Events")
				}}</Button>
			</div>
		</div>
		<div
			v-else-if="registrationsFull"
			class="flex flex-col items-center justify-center py-12 px-4"
		>
			<div class="w-full max-w-md">
				<img
					v-if="eventBookingData.eventDetails?.banner_image"
					:src="eventBookingData.eventDetails.banner_image"
					:alt="eventBookingData.eventDetails.title"
					class="w-full rounded-lg mb-6 object-cover max-h-48"
				/>
				<div class="text-center mb-6">
					<div
						class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-50"
					>
						<LucideTicketX class="h-6 w-6 text-red-500" />
					</div>
					<h2 class="text-xl font-semibold text-ink-gray-8 mb-2">
						{{ __("Event Full") }}
					</h2>
					<p class="text-ink-gray-6 mb-1">
						{{ __("All slots for this event are fully booked.") }}
					</p>
					<p class="text-sm text-ink-gray-5">
						{{ __("Leave your details below and we'll notify you about future events.") }}
					</p>
				</div>

				<!-- Success state -->
				<div
					v-if="waitlistRegistered"
					class="bg-surface-green-1 border border-outline-green-1 rounded-lg p-6 text-center"
				>
					<LucideCheckCircle class="w-12 h-12 text-ink-green-2 mx-auto mb-3" />
					<h3 class="text-lg font-semibold text-ink-green-3 mb-1">
						{{ __("You're on the list!") }}
					</h3>
					<p class="text-ink-green-2 text-sm">
						{{ __("We'll reach out to you about upcoming events.") }}
					</p>
				</div>

				<!-- Waitlist form -->
				<div
					v-else
					class="bg-surface-white border border-outline-gray-3 rounded-xl p-6"
				>
					<div class="grid grid-cols-1 gap-4">
						<FormControl
							v-model="waitlistForm.full_name"
							:label="__('Full Name')"
							:placeholder="__('Enter your full name')"
							required
							type="text"
						/>
						<FormControl
							v-model="waitlistForm.email"
							:label="__('Email')"
							:placeholder="__('Enter your email address')"
							required
							type="email"
						/>
						<FormControl
							v-model="waitlistForm.phone_number"
							:label="__('Phone Number')"
							:placeholder="__('Enter your phone number')"
							required
							type="text"
						/>
						<FormControl
							v-model="waitlistForm.organization"
							:label="__('Organization')"
							:placeholder="__('Enter your organization')"
							required
							type="text"
						/>
					</div>
					<Button
						variant="solid"
						size="lg"
						class="w-full mt-6"
						:loading="waitlistResource.loading"
						@click="submitWaitlist"
					>
						{{ __("Notify Me") }}
					</Button>
					<p v-if="waitlistError" class="text-red-600 text-sm mt-3 text-center">
						{{ waitlistError }}
					</p>
				</div>
			</div>
		</div>
		<div v-else>
			<BookingForm
				v-if="eventBookingData.availableAddOns && eventBookingData.availableTicketTypes"
				:availableAddOns="eventBookingData.availableAddOns"
				:availableTicketTypes="eventBookingData.availableTicketTypes"
				:taxSettings="eventBookingData.taxSettings"
				:eventDetails="eventBookingData.eventDetails"
				:customFields="eventBookingData.customFields"
				:eventRoute="eventRoute"
				:paymentGateways="eventBookingData.paymentGateways"
				:isGuestMode="isGuest"
				:offlineMethods="eventBookingData.offlineMethods"
			/>
		</div>
	</div>
</template>

<script setup>
import { session } from "@/data/session";
import { FormControl, Spinner, createResource } from "frappe-ui";
import { computed, reactive, ref } from "vue";
import BookingForm from "../components/BookingForm.vue";
import LucideTicketX from "~icons/lucide/ticket-x";
import LucideCheckCircle from "~icons/lucide/check-circle";

const eventBookingData = reactive({
	availableAddOns: null,
	availableTicketTypes: null,
	taxSettings: null,
	eventDetails: null,
	customFields: null,
	paymentGateways: [],
	offlineMethods: [],
});

const eventNotFound = ref(false);
const registrationsClosed = ref(false);
const registrationsFull = ref(false);

const props = defineProps({
	eventRoute: {
		type: String,
		required: true,
	},
});

const isGuest = computed(() => !session.isLoggedIn);

const goToHome = () => {
	window.location.href = "/";
};

// Waitlist form
const waitlistForm = reactive({
	full_name: "",
	email: "",
	phone_number: "",
	organization: "",
});
const waitlistRegistered = ref(false);
const waitlistError = ref(null);

const waitlistResource = createResource({
	url: "buzz.api.register_event_waitlist",
	onSuccess: () => {
		waitlistRegistered.value = true;
		waitlistError.value = null;
	},
	onError: (error) => {
		waitlistError.value = error.messages?.[0] || __("Failed to register. Please try again.");
	},
});

function submitWaitlist() {
	if (!waitlistForm.full_name || !waitlistForm.email || !waitlistForm.phone_number || !waitlistForm.organization) {
		waitlistError.value = __("Please fill in all fields.");
		return;
	}
	waitlistError.value = null;
	waitlistResource.submit({
		full_name: waitlistForm.full_name,
		email: waitlistForm.email,
		phone_number: waitlistForm.phone_number,
		organization: waitlistForm.organization,
	});
}

const eventBookingResource = createResource({
	url: "buzz.api.get_event_booking_data",
	params: {
		event_route: props.eventRoute,
	},
	auto: true,
	onSuccess: (data) => {
		eventBookingData.availableAddOns = data.available_add_ons || [];
		eventBookingData.availableTicketTypes = data.available_ticket_types || [];
		eventBookingData.taxSettings = data.tax_settings || {
			apply_tax: false,
			tax_inclusive: false,
			tax_label: "Tax",
			tax_percentage: 0,
		};
		eventBookingData.eventDetails = data.event_details || {};
		eventBookingData.customFields = data.custom_fields || [];
		eventBookingData.paymentGateways = data.payment_gateways || [];
		eventBookingData.offlineMethods = data.offline_methods || [];
		registrationsClosed.value = data.registrations_closed || false;
		registrationsFull.value = data.registrations_full || false;
	},
	onError: (error) => {
		if (error.message?.includes("DoesNotExistError")) {
			eventNotFound.value = true;
		}
	},
});
</script>
