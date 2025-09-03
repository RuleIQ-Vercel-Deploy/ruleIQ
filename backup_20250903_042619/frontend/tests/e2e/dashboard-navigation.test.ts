import { test, expect } from '@playwright/test';
import { TEST_USERS, DASHBOARD_DATA } from './fixtures/test-data';
import { TestSelectors } from './fixtures/test-selectors';

test.describe('Dashboard Navigation and Responsive Behavior', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill(TestSelectors.auth.emailInput, TEST_USERS.VALID_USER.email);
    await page.fill(TestSelectors.auth.passwordInput, TEST_USERS.VALID_USER.password);
    await page.click(TestSelectors.auth.submitButton);
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Desktop Navigation', () => {
    test('should display main navigation items', async ({ page }) => {
      // Check main navigation is visible
      await expect(page.locator(TestSelectors.navigation.mainNav)).toBeVisible();

      // Check key navigation links
      await expect(page.getByRole('link', { name: /dashboard/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /assessments/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /evidence/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /policies/i })).toBeVisible();
    });

    test('should navigate between main sections', async ({ page }) => {
      // Navigate to assessments
      await page.getByRole('link', { name: /assessments/i }).click();
      await expect(page).toHaveURL(/.*assessments/);

      // Navigate to evidence
      await page.getByRole('link', { name: /evidence/i }).click();
      await expect(page).toHaveURL(/.*evidence/);

      // Navigate back to dashboard
      await page.getByRole('link', { name: /dashboard/i }).click();
      await expect(page).toHaveURL(/.*dashboard/);
    });

    test('should display dashboard widgets', async ({ page }) => {
      // Check dashboard container
      await expect(page.locator(TestSelectors.dashboard.container)).toBeVisible();

      // Check welcome message
      await expect(page.locator(TestSelectors.dashboard.welcomeMessage)).toContainText(/welcome/i);

      // Check stats cards
      await expect(page.locator(TestSelectors.dashboard.statsCards).first()).toBeVisible();

      // Check quick actions
      await expect(page.locator(TestSelectors.dashboard.quickActions).first()).toBeVisible();
    });
  });

  test.describe('Mobile Responsive Behavior', () => {
    test('should show mobile menu on small screens', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Check mobile menu button is visible
      await expect(page.locator(TestSelectors.navigation.mobileMenuButton)).toBeVisible();

      // Open mobile menu
      await page.click(TestSelectors.navigation.mobileMenuButton);

      // Check mobile navigation items
      await expect(page.getByRole('link', { name: /dashboard/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /assessments/i })).toBeVisible();
    });

    test('should hide desktop navigation on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      // Desktop navigation should be hidden
      const desktopNav = page.locator(TestSelectors.navigation.mainNav);
      await expect(desktopNav).toBeHidden();

      // Mobile menu button should be visible
      await expect(page.locator(TestSelectors.navigation.mobileMenuButton)).toBeVisible();
    });

    test('should stack dashboard widgets on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      // Check widgets are responsive
      const statsCards = page.locator(TestSelectors.dashboard.statsCards);
      const cardCount = await statsCards.count();
      expect(cardCount).toBeGreaterThan(0);

      // Check widgets don't overlap
      const firstCard = statsCards.first();
      const lastCard = statsCards.last();

      const firstBox = await firstCard.boundingBox();
      const lastBox = await lastCard.boundingBox();

      if (firstBox && lastBox) {
        expect(firstBox.y).toBeLessThan(lastBox.y); // Stacked vertically
      }
    });
  });

  test.describe('Dashboard Widgets', () => {
    test('should display compliance score widget', async ({ page }) => {
      const scoreWidget = page.locator('[class*="compliance-score"], [class*="score-widget"]');
      await expect(scoreWidget).toBeVisible();

      // Check score is displayed
      await expect(scoreWidget.locator('[class*="score"], [class*="percentage"]')).toBeVisible();
    });

    test('should display pending tasks widget', async ({ page }) => {
      const tasksWidget = page.locator('[class*="pending-tasks"], [class*="tasks-widget"]');
      await expect(tasksWidget).toBeVisible();

      // Check tasks are listed
      await expect(tasksWidget.locator('[class*="task-item"], li')).toBeVisible();
    });

    test('should display recent activity widget', async ({ page }) => {
      const activityWidget = page.locator('[class*="recent-activity"], [class*="activity-widget"]');
      await expect(activityWidget).toBeVisible();

      // Check activity items
      await expect(activityWidget.locator('[class*="activity-item"], li')).toBeVisible();
    });

    test('should display upcoming deadlines widget', async ({ page }) => {
      const deadlinesWidget = page.locator(
        '[class*="upcoming-deadlines"], [class*="deadlines-widget"]',
      );
      await expect(deadlinesWidget).toBeVisible();

      // Check deadline items
      await expect(deadlinesWidget.locator('[class*="deadline-item"], li')).toBeVisible();
    });
  });

  test.describe('Widget Interactions', () => {
    test('should navigate to assessment from quick action', async ({ page }) => {
      // Find quick action for new assessment
      const newAssessmentAction = page
        .locator(TestSelectors.dashboard.quickActions)
        .filter({ hasText: /new assessment|start assessment/i });

      await newAssessmentAction.click();

      // Should navigate to assessments page
      await expect(page).toHaveURL(/.*assessments/);
    });

    test('should navigate to evidence upload from quick action', async ({ page }) => {
      const uploadEvidenceAction = page
        .locator(TestSelectors.dashboard.quickActions)
        .filter({ hasText: /upload evidence|add evidence/i });

      await uploadEvidenceAction.click();

      // Should navigate to evidence page
      await expect(page).toHaveURL(/.*evidence/);
    });

    test('should show task details on click', async ({ page }) => {
      const tasksWidget = page.locator('[class*="pending-tasks"], [class*="tasks-widget"]');
      const firstTask = tasksWidget.locator('[class*="task-item"], li').first();

      await firstTask.click();

      // Should show task details (modal or navigation)
      await expect(page.locator('text=Task Details')).toBeVisible();
    });
  });

  test.describe('User Menu and Profile', () => {
    test('should open user menu', async ({ page }) => {
      await page.click(TestSelectors.navigation.userMenu);

      // Check menu items
      await expect(page.getByRole('link', { name: /profile/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /settings/i })).toBeVisible();
      await expect(page.locator(TestSelectors.navigation.logoutButton)).toBeVisible();
    });

    test('should navigate to settings', async ({ page }) => {
      await page.click(TestSelectors.navigation.userMenu);
      await page.getByRole('link', { name: /settings/i }).click();

      await expect(page).toHaveURL(/.*settings/);
    });

    test('should navigate to profile', async ({ page }) => {
      await page.click(TestSelectors.navigation.userMenu);
      await page.getByRole('link', { name: /profile/i }).click();

      await expect(page).toHaveURL(/.*profile/);
    });
  });

  test.describe('Loading States', () => {
    test('should show loading spinner while data loads', async ({ page }) => {
      // Reload page to trigger loading
      await page.reload();

      // Check loading spinner appears
      await expect(page.locator(TestSelectors.common.loadingSpinner)).toBeVisible();

      // Wait for content to load
      await expect(page.locator(TestSelectors.common.loadingSpinner)).toBeHidden();
    });

    test('should show skeleton loaders for widgets', async ({ page }) => {
      // Reload page to trigger loading
      await page.reload();

      // Check skeleton loaders appear
      await expect(page.locator(TestSelectors.common.skeletonLoader)).toBeVisible();

      // Wait for content to load
      await expect(page.locator(TestSelectors.common.skeletonLoader)).toBeHidden();
    });
  });

  test.describe('Error Handling', () => {
    test('should show error message on API failure', async ({ page }) => {
      // Simulate API failure by blocking requests
      await page.route('**/api/dashboard**', (route) => route.abort());

      await page.reload();

      // Should show error message
      await expect(page.locator(TestSelectors.common.errorMessage)).toBeVisible();
    });

    test('should show retry option on error', async ({ page }) => {
      await page.route('**/api/dashboard**', (route) => route.abort());

      await page.reload();

      // Should show retry button
      await expect(page.getByRole('button', { name: /retry/i })).toBeVisible();
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should navigate with keyboard', async ({ page }) => {
      // Focus on first interactive element
      await page.keyboard.press('Tab');

      // Navigate through menu items
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');

      // Should navigate to focused link
      await expect(page).toHaveURL(/.*assessments|.*evidence/);
    });

    test('should support keyboard shortcuts', async ({ page }) => {
      // Test keyboard shortcuts (if implemented)
      await page.keyboard.press('Control+K'); // Command palette

      // Should open command palette or search
      await expect(
        page.locator('[class*="command-palette"], [class*="search-overlay"]'),
      ).toBeVisible();
    });
  });
});
