import { test, expect } from '@playwright/test';

test.describe('Homepage Smoke Test', () => {
  test('should load the homepage and display the main heading', async ({ page }) => {
    // Navigate to the homepage
    await page.goto('/');

    // Wait for the main heading to be visible to ensure the page has loaded.
    // This selector will likely need to be updated to match your actual heading element.
    const mainHeading = page.locator('h1');

    // Assert that the heading is visible
    await expect(mainHeading).toBeVisible({ timeout: 10000 });

    // Optional: Assert that the heading contains specific text
    // This is a good check to ensure the correct content is loading.
    // Replace 'Welcome to ruleIQ' with the actual text of your main heading.
    await expect(mainHeading).toContainText(/Welcome to ruleIQ/i);
  });

  test('should have a title', async ({ page }) => {
    await page.goto('/');

    // Assert that the page has the correct title.
    // Replace 'ruleIQ' with your application's actual title.
    await expect(page).toHaveTitle(/ruleIQ/);
  });
});
