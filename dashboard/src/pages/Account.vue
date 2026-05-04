<template>
	<ProfileView />

	<!-- Mobile: Select dropdown for navigation -->
	<div class="sm:hidden">
		<FormControl
			type="select"
			:modelValue="currentTabRoute"
			:options="selectOptions"
			@update:modelValue="onSelectChange"
		/>
	</div>

	<!-- Desktop: Tabs for navigation -->
	<div class="hidden sm:block">
		<Tabs as="div" v-model="tabIndex" :tabs="tabs">
			<template #tab-panel>
				<div></div>
			</template>
		</Tabs>
	</div>

	<div class="py-5">
		<router-view></router-view>
	</div>
</template>

<script setup>
import ProfileView from "@/components/ProfileView.vue";
import { Tabs } from "frappe-ui";
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import LucideCalendarDays from "~icons/lucide/calendar-days";
import LucideCircleDollarSign from "~icons/lucide/circle-dollar-sign";
import LucideMegaphone from "~icons/lucide/megaphone";
import LucideTicket from "~icons/lucide/ticket";

const route = useRoute();
const router = useRouter();

const tabs = [
	{
		label: __("My Bookings"),
		route: "/account/bookings",
		icon: LucideCalendarDays,
	},
	{ label: __("My Tickets"), route: "/account/tickets", icon: LucideTicket },
	{
		label: __("Talk Proposals"),
		route: "/account/proposals",
		icon: LucideMegaphone,
	},
	{
		label: __("Sponsorships"),
		route: "/account/sponsorships",
		icon: LucideCircleDollarSign,
	},
];

const selectOptions = tabs.map((tab) => ({
	label: tab.label,
	value: tab.route,
}));

const currentTabRoute = computed(() => {
	const tab = tabs.find((tab) => route.path.startsWith(tab.route));
	return tab ? tab.route : tabs[0].route;
});

function onSelectChange(value) {
	router.push(value);
}

// Find the tab index based on current route path
const getTabIndexFromRoute = () => {
	const currentPath = route.path;
	const index = tabs.findIndex((tab) => currentPath.startsWith(tab.route));
	return index >= 0 ? index : 0;
};

const tabIndex = ref(getTabIndexFromRoute());

// Watch for route changes and update tab index
watch(
	() => route.path,
	() => {
		tabIndex.value = getTabIndexFromRoute();
	}
);
</script>
