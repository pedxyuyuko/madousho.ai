import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should display the main heading', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/Vite App/);
  });

  test('should navigate to login when not authenticated', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveURL(/.*login/);
  });
});