import { test, expect } from '@playwright/test';

const APP_URL = process.env.NEXT_APP_URL;

(APP_URL ? test : test.skip)('lead form submit', async ({ page }) => {
  await page.goto(APP_URL!);
  await page.fill('input[type="text"]', 'Test User');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.click('text=Submit');
  await expect(page.getByText('Thanks!')).toBeVisible();
});