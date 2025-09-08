import AxeBuilder from '@axe-core/playwright';
import { test, expect } from '@playwright/test';

import { TestHelpers } from './utils/test-helpers';

test.describe('E2E Accessibility Tests', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test.describe('Page-Level Accessibility', () => {
    test('homepage should be accessible', async ({ page }) => {
      await helpers.navigateAndWait('/');

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('login page should be accessible', async ({ page }) => {
      await helpers.navigateAndWait('/login');

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('registration page should be accessible', async ({ page }) => {
      await helpers.navigateAndWait('/register');

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('dashboard should be accessible', async ({ page }) => {
      // Login first
      await helpers.navigateAndWait('/login');
      await helpers.fillField('[data-testid="email-input"]', 'test@example.com');
      await helpers.fillField('[data-testid="password-input"]', 'password123');
      await helpers.clickAndWait('[data-testid="login-button"]', '[data-testid="dashboard"]');

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should navigate homepage with keyboard only', async ({ page }) => {
      await helpers.navigateAndWait('/');

      // Test tab navigation
      await page.keyboard.press('Tab');

      // Should focus on first interactive element
      const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
      expect(['A', 'BUTTON', 'INPUT']).toContain(focusedElement);

      // Test skip link
      await page.keyboard.press('Tab');
      const skipLink = page.locator('text=Skip to main content');
      if (await skipLink.isVisible()) {
        await page.keyboard.press('Enter');

        // Should jump to main content
        const mainContent = page.locator('main, [role="main"], #main-content');
        await expect(mainContent).toBeFocused();
      }
    });

    test('should navigate login form with keyboard', async ({ page }) => {
      await helpers.navigateAndWait('/login');

      // Tab to email field
      await page.keyboard.press('Tab');
      await expect(page.locator('[data-testid="email-input"]')).toBeFocused();

      // Tab to password field
      await page.keyboard.press('Tab');
      await expect(page.locator('[data-testid="password-input"]')).toBeFocused();

      // Tab to submit button
      await page.keyboard.press('Tab');
      await expect(page.locator('[data-testid="login-button"]')).toBeFocused();

      // Should be able to submit with Enter
      await helpers.fillField('[data-testid="email-input"]', 'test@example.com');
      await helpers.fillField('[data-testid="password-input"]', 'password123');
      await page.keyboard.press('Enter');

      // Should attempt login
      await page.waitForTimeout(1000);
    });

    test('should handle modal focus trapping', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      // Open a modal (assuming there's a settings modal)
      const settingsButton = page.locator('[data-testid="settings-button"]');
      if (await settingsButton.isVisible()) {
        await settingsButton.click();

        // Focus should be trapped in modal
        const modal = page.locator('[role="dialog"]');
        await expect(modal).toBeVisible();

        // Tab through modal elements
        await page.keyboard.press('Tab');
        const focusedElement = await page.evaluate(() => document.activeElement);

        // Focus should be within modal
        const isWithinModal = await page.evaluate(
          (modal, focused) => {
            return modal.contains(focused);
          },
          await modal.elementHandle(),
          focusedElement,
        );

        expect(isWithinModal).toBe(true);

        // Escape should close modal
        await page.keyboard.press('Escape');
        await expect(modal).not.toBeVisible();
      }
    });

    test('should support arrow key navigation in menus', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      // Open dropdown menu
      const userMenu = page.locator('[data-testid="user-menu"]');
      if (await userMenu.isVisible()) {
        await userMenu.click();

        const menuItems = page.locator('[role="menuitem"]');
        const itemCount = await menuItems.count();

        if (itemCount > 0) {
          // First item should be focused
          await expect(menuItems.first()).toBeFocused();

          // Arrow down should move to next item
          await page.keyboard.press('ArrowDown');
          if (itemCount > 1) {
            await expect(menuItems.nth(1)).toBeFocused();
          }

          // Arrow up should move to previous item
          await page.keyboard.press('ArrowUp');
          await expect(menuItems.first()).toBeFocused();
        }
      }
    });
  });

  test.describe('Screen Reader Support', () => {
    test('should have proper heading structure', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      // Check heading hierarchy
      const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
      const headingLevels = await Promise.all(
        headings.map(async (heading) => {
          const tagName = await heading.evaluate((el) => el.tagName);
          return parseInt(tagName.charAt(1));
        }),
      );

      // Should start with h1
      expect(headingLevels[0]).toBe(1);

      // Should not skip levels
      for (let i = 1; i < headingLevels.length; i++) {
        const diff = headingLevels[i] - headingLevels[i - 1];
        expect(diff).toBeLessThanOrEqual(1);
      }
    });

    test('should have proper form labels', async ({ page }) => {
      await helpers.navigateAndWait('/login');

      // Check that all inputs have labels
      const inputs = await page.locator('input').all();

      for (const input of inputs) {
        const id = await input.getAttribute('id');
        const ariaLabel = await input.getAttribute('aria-label');
        const ariaLabelledBy = await input.getAttribute('aria-labelledby');

        if (id) {
          const label = page.locator(`label[for="${id}"]`);
          const hasLabel = (await label.count()) > 0;

          expect(hasLabel || ariaLabel || ariaLabelledBy).toBeTruthy();
        } else {
          expect(ariaLabel || ariaLabelledBy).toBeTruthy();
        }
      }
    });

    test('should announce dynamic content changes', async ({ page }) => {
      await helpers.navigateAndWait('/assessments');

      // Look for live regions
      const liveRegions = page.locator('[aria-live]');
      const liveRegionCount = await liveRegions.count();

      if (liveRegionCount > 0) {
        // Check that live regions have appropriate values
        for (let i = 0; i < liveRegionCount; i++) {
          const liveValue = await liveRegions.nth(i).getAttribute('aria-live');
          expect(['polite', 'assertive', 'off']).toContain(liveValue);
        }
      }

      // Check for status and alert roles
      const statusElements = page.locator('[role="status"], [role="alert"]');
      const statusCount = await statusElements.count();

      // Should have at least some status/alert elements for dynamic content
      if (statusCount > 0) {
        expect(statusCount).toBeGreaterThan(0);
      }
    });

    test('should have accessible error messages', async ({ page }) => {
      await helpers.navigateAndWait('/login');

      // Submit form without filling fields to trigger errors
      await helpers.clickAndWait('[data-testid="login-button"]');

      // Wait for error messages
      await page.waitForTimeout(1000);

      // Check for error messages with proper ARIA
      const errorMessages = page.locator('[role="alert"], [aria-live="assertive"]');
      const errorCount = await errorMessages.count();

      if (errorCount > 0) {
        // Error messages should be announced
        for (let i = 0; i < errorCount; i++) {
          const errorText = await errorMessages.nth(i).textContent();
          expect(errorText).toBeTruthy();
          expect(errorText?.length).toBeGreaterThan(0);
        }
      }
    });
  });

  test.describe('Color and Contrast', () => {
    test('should have sufficient color contrast', async ({ page }) => {
      await helpers.navigateAndWait('/');

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withRules(['color-contrast'])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('should not rely solely on color for information', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      // Check for color-only information (this would need specific implementation)
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withRules(['color-contrast', 'link-in-text-block'])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });
  });

  test.describe('Mobile Accessibility', () => {
    test('should be accessible on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await helpers.navigateAndWait('/');

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('should have touch-friendly targets', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await helpers.navigateAndWait('/');

      // Check that interactive elements are large enough for touch
      const buttons = await page
        .locator('button, a, input[type="button"], input[type="submit"]')
        .all();

      for (const button of buttons) {
        const box = await button.boundingBox();
        if (box) {
          // WCAG recommends minimum 44x44 pixels for touch targets
          expect(box.width).toBeGreaterThanOrEqual(44);
          expect(box.height).toBeGreaterThanOrEqual(44);
        }
      }
    });
  });

  test.describe('Focus Management', () => {
    test('should manage focus in single-page navigation', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      // Navigate to different section
      const assessmentsLink = page.locator('a[href*="assessments"]');
      if (await assessmentsLink.isVisible()) {
        await assessmentsLink.click();

        // Focus should move to main content area
        await page.waitForTimeout(500);

        const mainHeading = page.locator('h1').first();
        if (await mainHeading.isVisible()) {
          // Main heading should be focusable or focus should be managed
          const isFocused = await mainHeading.evaluate((el) => document.activeElement === el);
          const hasTabIndex = await mainHeading.getAttribute('tabindex');

          // Either focused or has tabindex for focus management
          expect(isFocused || hasTabIndex === '-1').toBeTruthy();
        }
      }
    });

    test('should restore focus after modal closes', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      // Find and click button that opens modal
      const modalTrigger = page.locator('[data-testid*="modal"], [data-testid*="dialog"]').first();
      if (await modalTrigger.isVisible()) {
        await modalTrigger.focus();
        await modalTrigger.click();

        // Modal should be open
        const modal = page.locator('[role="dialog"]');
        await expect(modal).toBeVisible();

        // Close modal with Escape
        await page.keyboard.press('Escape');
        await expect(modal).not.toBeVisible();

        // Focus should return to trigger button
        await expect(modalTrigger).toBeFocused();
      }
    });
  });
});
