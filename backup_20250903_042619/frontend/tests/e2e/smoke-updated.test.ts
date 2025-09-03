import { test, expect } from '@playwright/test';
import { TestHelpers } from './utils/test-helpers';

test.describe('Smoke Tests - Updated', () => {
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

    // Check for login form elements using more flexible selectors
    await expect(page.locator('form')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    // Check for specific text content
    await expect(page.locator('text=Secure Login')).toBeVisible();
    await expect(page.locator('text=Create account')).toBeVisible();
  });

  test('should load the registration page', async ({ page }) => {
    await helpers.navigateAndWait('/register');

    // Check for registration form elements
    await expect(page.locator('form')).toBeVisible();
    await expect(
      page.locator('input[placeholder*="Full name"], input[placeholder*="full name"]'),
    ).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should have working navigation', async ({ page }) => {
    await helpers.navigateAndWait('/');

    // Test navigation to login page
    const loginLink = page.locator('a[href="/login"], text=Login').first();
    if (await loginLink.isVisible()) {
      await loginLink.click();
      await page.waitForURL('**/login');
      expect(page.url()).toContain('/login');
    }

    // Go back to homepage
    await helpers.navigateAndWait('/');

    // Test navigation to register page
    const registerLink = page
      .locator('a[href="/register"], text=Sign up, text=Get Started')
      .first();
    if (await registerLink.isVisible()) {
      await registerLink.click();
      await page.waitForURL('**/register');
      expect(page.url()).toContain('/register');
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await helpers.navigateAndWait('/');

    // Check that the page still renders properly
    await expect(page.locator('nav')).toBeVisible();

    // Take mobile screenshot
    await helpers.takeScreenshot('homepage-mobile');
  });

  test('should handle 404 pages gracefully', async ({ page }) => {
    await page.goto('/non-existent-page', { waitUntil: 'networkidle' });

    // Should show 404 page or redirect to home
    const is404 = await page.locator('text=/404|not found/i').isVisible();
    const isRedirected = page.url().endsWith('/');

    expect(is404 || isRedirected).toBeTruthy();
  });

  test('should load without critical JavaScript errors', async ({ page }) => {
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

    // Filter out known acceptable errors
    const criticalErrors = errors.filter(
      (error) =>
        !error.includes('favicon.ico') &&
        !error.includes('Extension context invalidated') &&
        !error.includes('ResizeObserver') &&
        !error.includes('Non-Error promise rejection'),
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('should have proper meta tags', async ({ page }) => {
    await helpers.navigateAndWait('/');

    // Check for essential meta tags
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title).toContain('ruleIQ');

    // Check for viewport meta tag
    const viewport = await page.locator('meta[name="viewport"]').getAttribute('content');
    expect(viewport).toContain('width=device-width');
  });

  test('should load CSS and display content properly', async ({ page }) => {
    await helpers.navigateAndWait('/');

    // Check that main content is visible
    const mainContent = page.locator('main, [role="main"], .container').first();
    await expect(mainContent).toBeVisible();

    // Check that styles are applied by checking computed styles
    const body = page.locator('body');
    const backgroundColor = await body.evaluate(
      (el) => window.getComputedStyle(el).backgroundColor,
    );

    // Should not be transparent (indicating CSS loaded)
    expect(backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
  });

  test('should have functional form inputs', async ({ page }) => {
    await helpers.navigateAndWait('/login');

    // Test email input
    const emailInput = page.locator('input[type="email"]');
    await emailInput.fill('test@example.com');
    await expect(emailInput).toHaveValue('test@example.com');

    // Test password input
    const passwordInput = page.locator('input[type="password"]');
    await passwordInput.fill('testpassword');
    await expect(passwordInput).toHaveValue('testpassword');

    // Test password visibility toggle if present
    const toggleButton = page.locator('button:has(svg)').filter({ hasText: '' });
    if (await toggleButton.isVisible()) {
      await toggleButton.click();
      // Password input type might change to text
      await page.waitForTimeout(300);
    }
  });
});
