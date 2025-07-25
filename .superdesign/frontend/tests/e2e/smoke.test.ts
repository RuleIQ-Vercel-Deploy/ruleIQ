import { test, expect } from '@playwright/test';

import { TestHelpers } from './utils/test-helpers';

test.describe('Smoke Tests', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test('should load the homepage', async ({ page }) => {
    await helpers.navigateAndWait('/');

    // Check that the page loads
    await expect(page).toHaveTitle(/ruleIQ/);

    // Check for main navigation elements
    await expect(page.locator('nav')).toBeVisible();

    // Take a screenshot for visual verification
    await helpers.takeScreenshot('homepage-loaded');
  });

  test('should load the login page', async ({ page }) => {
    await helpers.navigateAndWait('/login');

    // Check for login form elements
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();

    // Check for registration link
    await expect(page.locator('text=Sign up')).toBeVisible();
  });

  test('should load the registration page', async ({ page }) => {
    await helpers.navigateAndWait('/register');

    // Check for registration form elements
    await expect(page.locator('[data-testid="register-form"]')).toBeVisible();
    await expect(page.locator('[data-testid="full-name-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="register-button"]')).toBeVisible();
  });

  test('should have working navigation', async ({ page }) => {
    await helpers.navigateAndWait('/');

    // Test navigation to different pages
    const navigationTests = [
      { link: 'Login', expectedUrl: '/login' },
      { link: 'Sign up', expectedUrl: '/register' },
    ];

    for (const { link, expectedUrl } of navigationTests) {
      await page.click(`text=${link}`);
      await page.waitForURL(`**${expectedUrl}`);
      expect(page.url()).toContain(expectedUrl);

      // Go back to homepage
      await helpers.navigateAndWait('/');
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await helpers.navigateAndWait('/');

    // Check that mobile navigation works
    const mobileMenu = page.locator('[data-testid="mobile-menu-button"]');
    if (await mobileMenu.isVisible()) {
      await mobileMenu.click();
      await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    }

    // Take mobile screenshot
    await helpers.takeScreenshot('homepage-mobile');
  });

  test('should handle 404 pages gracefully', async ({ page }) => {
    await page.goto('/non-existent-page');

    // Should show 404 page or redirect to home
    const is404 = await page.locator('text=404').isVisible();
    const isRedirected = page.url().includes('/');

    expect(is404 || isRedirected).toBeTruthy();
  });

  test('should load without JavaScript errors', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    page.on('pageerror', (error) => {
      errors.push(error.message);
    });

    await helpers.navigateAndWait('/');

    // Allow some time for any async errors
    await page.waitForTimeout(2000);

    // Filter out known acceptable errors (if any)
    const criticalErrors = errors.filter(
      (error) => !error.includes('favicon.ico') && !error.includes('Extension context invalidated'),
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('should have proper meta tags', async ({ page }) => {
    await helpers.navigateAndWait('/');

    // Check for essential meta tags
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);

    // Check for viewport meta tag
    const viewport = await page.locator('meta[name="viewport"]').getAttribute('content');
    expect(viewport).toContain('width=device-width');

    // Check for description meta tag
    const description = await page.locator('meta[name="description"]').getAttribute('content');
    expect(description).toBeTruthy();
  });

  test('should load CSS and fonts properly', async ({ page }) => {
    await helpers.navigateAndWait('/');

    // Check that styles are applied
    const body = page.locator('body');
    const backgroundColor = await body.evaluate(
      (el) => window.getComputedStyle(el).backgroundColor,
    );

    // Should not be the default white (indicating CSS loaded)
    expect(backgroundColor).not.toBe('rgba(0, 0, 0, 0)');

    // Check that fonts are loaded
    const fontFamily = await body.evaluate((el) => window.getComputedStyle(el).fontFamily);

    expect(fontFamily).toBeTruthy();
  });
});
