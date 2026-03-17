import { expect, Locator, Page } from "@playwright/test";

export class CustomFormPage {
	private page: Page;
	private form: Locator;
	private submitButton: Locator;
	private successBanner: Locator;
	private closedBanner: Locator;
	private errorBanner: Locator;

	constructor(page: Page) {
		this.page = page;
		this.form = page.locator("form");
		this.submitButton = page.locator('button[type="submit"]');
		this.successBanner = page.locator(".bg-surface-green-1");
		this.closedBanner = page.locator(".bg-surface-orange-1");
		this.errorBanner = page.locator(".bg-surface-red-1");
	}

	async goto(eventRoute: string, formPath: string): Promise<void> {
		await this.page.goto(`/dashboard/events/${eventRoute}/${formPath}`);
		await this.page.waitForLoadState("networkidle");
	}

	async waitForFormLoad(): Promise<void> {
		await expect(this.form).toBeVisible({ timeout: 15000 });
	}

	async fillField(label: string, value: string): Promise<void> {
		const field = this.page.locator(`label:has-text("${label}")`).locator("..").locator("input, textarea").first();
		await field.fill(value);
	}

	async fillFormControl(placeholder: string, value: string): Promise<void> {
		await this.page.locator(`input[placeholder="${placeholder}"], textarea[placeholder="${placeholder}"]`).first().fill(value);
	}

	async submit(): Promise<void> {
		await this.submitButton.click();
	}

	async expectSuccess(): Promise<void> {
		await expect(this.successBanner).toBeVisible({ timeout: 15000 });
	}

	async expectClosed(): Promise<void> {
		await expect(this.closedBanner).toBeVisible({ timeout: 15000 });
	}

	async expectNotFound(): Promise<void> {
		await expect(this.errorBanner).toBeVisible({ timeout: 15000 });
	}

	async expectFormVisible(): Promise<void> {
		await expect(this.form).toBeVisible();
	}

	async expectFormTitle(title: string): Promise<void> {
		await expect(this.page.locator(`h1:has-text("${title}")`)).toBeVisible();
	}

	async getFieldLabels(): Promise<string[]> {
		const labels = this.page.locator("form label");
		return labels.allTextContents();
	}
}
