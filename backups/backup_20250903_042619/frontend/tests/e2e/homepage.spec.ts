import { test, expect } from '@playwright/test';

test.describe('Homepage Smoke Test', () => {
  test('should load the homepage and display the main heading', async ({ page }) => {
    await page.goto('/');

    // Check main heading
    const mainHeading = page.locator('h1');
    await expect(mainHeading).toBeVisible({ timeout: 10000 });
    await expect(mainHeading).toContainText(/TransformYour Compliance/i);

    // Check navigation
    await expect(page.getByRole('link', { name: /sign in|login/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /sign up|register/i })).toBeVisible();
  });

  test('should have correct title and meta tags', async ({ page }) => {
    await page.goto('/');

    await expect(page).toHaveTitle(/ruleIQ/);
    await expect(page.locator('meta[name="description"]')).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Check mobile-specific elements
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.getByRole('button', { name: /menu/i })).toBeVisible();
  });

  test('should load all critical resources', async ({ page }) => {
    await page.goto('/');

    // Check for critical CSS/JS loading
    await expect(page.locator('link[rel="stylesheet"]')).toBeVisible();
    await expect(page.locator('script[src]')).toBeVisible();

    // Check for images
    await expect(page.locator('img')).toBeVisible();
  });
});
