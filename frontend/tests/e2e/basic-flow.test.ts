import { test, expect } from '@playwright/test';
import { TestHelpers } from './utils/test-helpers';

/**
 * Basic E2E test to verify the setup is working correctly
 * This test suite uses flexible selectors that work with the current app structure
 */
test.describe('Basic Application Flow', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test('should navigate through main pages', async ({ page }) => {
    // Start at homepage
    await helpers.navigateAndWait('/');
    
    // Verify homepage loaded
    await expect(page).toHaveTitle(/ruleIQ/);
    
    // Check for navigation - handle responsive design
    const desktopNav = page.locator('nav.md\\:flex').first();
    const mobileMenuButton = page.locator('button[aria-label*="menu" i]').first();
    
    // On desktop, nav should be visible; on mobile, menu button should be visible
    const isDesktop = await desktopNav.isVisible().catch(() => false);
    const isMobile = await mobileMenuButton.isVisible().catch(() => false);
    
    expect(isDesktop || isMobile).toBeTruthy();
    
    // Screenshot for reference
    await helpers.takeScreenshot('01-homepage');
  });

  test('should display login page correctly', async ({ page }) => {
    await helpers.navigateAndWait('/login');
    
    // Check for essential login elements
    const form = page.locator('form').first();
    await expect(form).toBeVisible();
    
    // Check for email input
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible();
    await expect(emailInput).toBeEnabled();
    
    // Check for password input
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeVisible();
    await expect(passwordInput).toBeEnabled();
    
    // Check for submit button
    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toBeVisible();
    await expect(submitButton).toContainText(/sign in/i);
    
    await helpers.takeScreenshot('02-login-page');
  });

  test('should display registration page correctly', async ({ page }) => {
    await helpers.navigateAndWait('/register');
    
    // Check for registration form
    const form = page.locator('form').first();
    await expect(form).toBeVisible();
    
    // Check for required fields
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]').first()).toBeVisible();
    
    // Check for password confirmation field (register page has two password inputs)
    const passwordInputs = page.locator('input[type="password"]');
    await expect(passwordInputs).toHaveCount(2);
    
    await helpers.takeScreenshot('03-register-page');
  });

  test('should validate form inputs', async ({ page }) => {
    await helpers.navigateAndWait('/login');
    
    // Test email validation
    const emailInput = page.locator('input[type="email"]');
    await emailInput.fill('invalid-email');
    await emailInput.blur();
    
    // Test password field
    const passwordInput = page.locator('input[type="password"]');
    await passwordInput.fill('test');
    
    // Try to submit
    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();
    
    // Should stay on login page due to validation
    await expect(page).toHaveURL(/\/login/);
    
    await helpers.takeScreenshot('04-form-validation');
  });

  test('should handle responsive design', async ({ page }) => {
    // Desktop view
    await helpers.navigateAndWait('/');
    
    // Check for responsive navigation elements
    const checkNavigation = async () => {
      const desktopNav = page.locator('nav.md\\:flex, nav:not(.mobile-nav)').first();
      const mobileMenuButton = page.locator('button[aria-label*="menu" i], button.mobile-menu-toggle').first();
      
      const isDesktopVisible = await desktopNav.isVisible().catch(() => false);
      const isMobileVisible = await mobileMenuButton.isVisible().catch(() => false);
      
      return isDesktopVisible || isMobileVisible;
    };
    
    // Verify navigation exists in desktop view
    expect(await checkNavigation()).toBeTruthy();
    
    // Tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500); // Allow for responsive adjustments
    await helpers.takeScreenshot('05-tablet-view');
    expect(await checkNavigation()).toBeTruthy();
    
    // Mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    await helpers.takeScreenshot('06-mobile-view');
    expect(await checkNavigation()).toBeTruthy();
    
    // On mobile, the layout should still have essential elements
    // Just verify the page loads without errors and has content
    const bodyContent = await page.locator('body').textContent();
    expect(bodyContent).toBeTruthy();
    expect(bodyContent?.length).toBeGreaterThan(100); // Has substantial content
    
    // Verify no layout breaking - check if main content areas exist
    const hasMainContent = await page.locator('main, [role="main"], .container, #__next').count() > 0;
    expect(hasMainContent).toBeTruthy();
  });

  test('should load without critical errors', async ({ page }) => {
    const consoleErrors: string[] = [];
    
    // Capture console errors
    page.on('console', message => {
      if (message.type() === 'error') {
        consoleErrors.push(message.text());
      }
    });
    
    // Navigate to main pages
    const pages = ['/', '/login', '/register'];
    
    for (const path of pages) {
      await helpers.navigateAndWait(path);
      await page.waitForTimeout(1000); // Wait for any async operations
    }
    
    // Filter out acceptable errors
    const criticalErrors = consoleErrors.filter(error => {
      const acceptableErrors = [
        'favicon.ico',
        'Extension context invalidated',
        'ResizeObserver',
        'Non-Error promise rejection',
        'Firebase',
        'Stripe',
        '404 (Not Found)',  // Missing resources are acceptable in dev
        'Failed to load resource',
        'manifest.json'  // PWA manifest might be missing in dev
      ];
      
      return !acceptableErrors.some(acceptable => error.includes(acceptable));
    });
    
    // Log any critical errors for debugging
    if (criticalErrors.length > 0) {
      console.log('Critical errors found:', criticalErrors);
    }
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should have proper SEO meta tags', async ({ page }) => {
    await helpers.navigateAndWait('/');
    
    // Check title
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title).toContain('ruleIQ');
    
    // Check viewport meta
    const viewport = await page.locator('meta[name="viewport"]').getAttribute('content');
    expect(viewport).toContain('width=device-width');
    
    // Check for description (if exists)
    const description = await page.locator('meta[name="description"]').count();
    if (description > 0) {
      const content = await page.locator('meta[name="description"]').getAttribute('content');
      expect(content).toBeTruthy();
    }
  });
});

// Run with: pnpm exec playwright test tests/e2e/basic-flow.test.ts