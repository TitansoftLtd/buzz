<template>
	<div class="flex flex-col items-center justify-center py-16 px-4">
		<div class="text-center max-w-md">
			<h2 class="text-xl font-semibold text-ink-gray-8 mb-2">
				{{ __("Login Required") }}
			</h2>
			<p class="text-ink-gray-6 mb-6">
				{{ message }}
			</p>
			<Button variant="solid" size="lg" @click="redirectToLogin">{{ __("Log In") }}</Button>
		</div>
	</div>
</template>

<script setup>
import { Button } from "frappe-ui";
import { redirectToLogin } from "@/utils/index";

defineProps({
	message: {
		type: String,
		default: __("Please log in to continue."),
	},
});
</script>
