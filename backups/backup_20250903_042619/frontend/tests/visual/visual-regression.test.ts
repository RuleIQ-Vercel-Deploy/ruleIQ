import { test, expect } from '@playwright/test';

import { TestHelpers } from '../e2e/utils/test-helpers';

test.describe('Visual Regression Tests', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test.describe('Page Screenshots', () => {
    test('homepage should match visual baseline', async ({ page }) => {
      await helpers.navigateAndWait('/');

      // Wait for all content to load
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000); // Allow for animations

      // Take full page screenshot
      await expect(page).toHaveScreenshot('homepage.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('login page should match visual baseline', async ({ page }) => {
      await helpers.navigateAndWait('/login');

      await expect(page).toHaveScreenshot('login-page.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('registration page should match visual baseline', async ({ page }) => {
      await helpers.navigateAndWait('/register');

      await expect(page).toHaveScreenshot('register-page.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('dashboard should match visual baseline', async ({ page }) => {
      // Login first
      await helpers.navigateAndWait('/login');
      await helpers.fillField('[data-testid="email-input"]', 'test@example.com');
      await helpers.fillField('[data-testid="password-input"]', 'password123');
      await helpers.clickAndWait('[data-testid="login-button"]', '[data-testid="dashboard"]');

      // Wait for dashboard to fully load
      await helpers.waitForLoadingToComplete();

      await expect(page).toHaveScreenshot('dashboard.png', {
        fullPage: true,
        animations: 'disabled',
        mask: [
          page.locator('[data-testid="current-time"]'), // Mask dynamic time
          page.locator('[data-testid="user-avatar"]'), // Mask user-specific content
        ],
      });
    });
  });

  test.describe('Component Screenshots', () => {
    test('navigation component should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      const navigation = page.locator('[data-testid="main-navigation"]');
      await expect(navigation).toHaveScreenshot('navigation-component.png');
    });

    test('user menu should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      // Open user menu
      await page.click('[data-testid="user-menu-trigger"]');

      const userMenu = page.locator('[data-testid="user-menu"]');
      await expect(userMenu).toHaveScreenshot('user-menu.png');
    });

    test('compliance score widget should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      const scoreWidget = page.locator('[data-testid="compliance-score-widget"]');
      await expect(scoreWidget).toHaveScreenshot('compliance-score-widget.png', {
        mask: [
          scoreWidget.locator('[data-testid="score-value"]'), // Mask dynamic score
        ],
      });
    });

    test('assessment card should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/assessments');

      const assessmentCard = page.locator('[data-testid="assessment-card"]').first();
      await expect(assessmentCard).toHaveScreenshot('assessment-card.png');
    });

    test('evidence upload component should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/evidence');
      await page.click('[data-testid="upload-evidence-button"]');

      const uploadComponent = page.locator('[data-testid="evidence-upload-modal"]');
      await expect(uploadComponent).toHaveScreenshot('evidence-upload.png');
    });
  });

  test.describe('Form States', () => {
    test('login form states should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/login');

      // Empty state
      await expect(page.locator('[data-testid="login-form"]')).toHaveScreenshot(
        'login-form-empty.png',
      );

      // Filled state
      await helpers.fillField('[data-testid="email-input"]', 'test@example.com');
      await helpers.fillField('[data-testid="password-input"]', 'password123');
      await expect(page.locator('[data-testid="login-form"]')).toHaveScreenshot(
        'login-form-filled.png',
      );

      // Error state
      await helpers.fillField('[data-testid="email-input"]', 'invalid-email');
      await page.click('[data-testid="login-button"]');
      await page.waitForTimeout(500);
      await expect(page.locator('[data-testid="login-form"]')).toHaveScreenshot(
        'login-form-error.png',
      );
    });

    test('business profile wizard should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/business-profile/setup');

      // Step 1
      await expect(page.locator('[data-testid="profile-wizard"]')).toHaveScreenshot(
        'profile-wizard-step1.png',
      );

      // Fill step 1 and proceed
      await helpers.fillField('[data-testid="company-name-input"]', 'Test Company');
      await page.selectOption('[data-testid="industry-select"]', 'Technology');
      await page.selectOption('[data-testid="employee-count-select"]', '10-50');
      await page.click('[data-testid="next-button"]');

      // Step 2
      await expect(page.locator('[data-testid="profile-wizard"]')).toHaveScreenshot(
        'profile-wizard-step2.png',
      );
    });
  });

  test.describe('Responsive Design', () => {
    test('mobile homepage should match baseline', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await helpers.navigateAndWait('/');

      await expect(page).toHaveScreenshot('homepage-mobile.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('tablet dashboard should match baseline', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await helpers.navigateAndWait('/dashboard');

      await expect(page).toHaveScreenshot('dashboard-tablet.png', {
        fullPage: true,
        animations: 'disabled',
        mask: [page.locator('[data-testid="current-time"]')],
      });
    });

    test('mobile navigation should match baseline', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await helpers.navigateAndWait('/dashboard');

      // Open mobile menu
      await page.click('[data-testid="mobile-menu-button"]');

      const mobileMenu = page.locator('[data-testid="mobile-menu"]');
      await expect(mobileMenu).toHaveScreenshot('mobile-navigation.png');
    });
  });

  test.describe('Interactive States', () => {
    test('button hover states should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/');

      const primaryButton = page.locator('[data-testid="primary-button"]').first();

      // Normal state
      await expect(primaryButton).toHaveScreenshot('button-normal.png');

      // Hover state
      await primaryButton.hover();
      await expect(primaryButton).toHaveScreenshot('button-hover.png');

      // Focus state
      await primaryButton.focus();
      await expect(primaryButton).toHaveScreenshot('button-focus.png');
    });

    test('form input states should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/login');

      const emailInput = page.locator('[data-testid="email-input"]');

      // Empty state
      await expect(emailInput).toHaveScreenshot('input-empty.png');

      // Focused state
      await emailInput.focus();
      await expect(emailInput).toHaveScreenshot('input-focused.png');

      // Filled state
      await emailInput.fill('test@example.com');
      await expect(emailInput).toHaveScreenshot('input-filled.png');

      // Error state
      await emailInput.fill('invalid-email');
      await page.click('[data-testid="login-button"]');
      await page.waitForTimeout(500);
      await expect(emailInput).toHaveScreenshot('input-error.png');
    });

    test('dropdown menu states should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/business-profile/setup');

      const dropdown = page.locator('[data-testid="industry-select"]');

      // Closed state
      await expect(dropdown).toHaveScreenshot('dropdown-closed.png');

      // Open state
      await dropdown.click();
      await expect(page.locator('[data-testid="industry-options"]')).toHaveScreenshot(
        'dropdown-open.png',
      );
    });
  });

  test.describe('Data Visualization', () => {
    test('compliance score chart should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      const scoreChart = page.locator('[data-testid="compliance-score-chart"]');
      await expect(scoreChart).toHaveScreenshot('compliance-score-chart.png', {
        mask: [
          scoreChart.locator('[data-testid="score-percentage"]'), // Mask dynamic values
        ],
      });
    });

    test('framework progress bars should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/dashboard');

      const progressBars = page.locator('[data-testid="framework-progress"]');
      await expect(progressBars).toHaveScreenshot('framework-progress.png', {
        mask: [
          progressBars.locator('[data-testid="progress-percentage"]'), // Mask dynamic values
        ],
      });
    });

    test('assessment results chart should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/assessments/123/results');

      const resultsChart = page.locator('[data-testid="assessment-results-chart"]');
      await expect(resultsChart).toHaveScreenshot('assessment-results-chart.png');
    });
  });

  test.describe('Loading States', () => {
    test('dashboard loading state should match baseline', async ({ page }) => {
      // Intercept API calls to simulate loading
      await page.route('**/api/dashboard/**', (route) => {
        setTimeout(() => route.continue(), 2000);
      });

      await helpers.navigateAndWait('/dashboard');

      // Capture loading state
      await expect(page.locator('[data-testid="dashboard-loading"]')).toHaveScreenshot(
        'dashboard-loading.png',
      );
    });

    test('assessment loading state should match baseline', async ({ page }) => {
      await page.route('**/api/assessments/**', (route) => {
        setTimeout(() => route.continue(), 1000);
      });

      await helpers.navigateAndWait('/assessments');

      await expect(page.locator('[data-testid="assessments-loading"]')).toHaveScreenshot(
        'assessments-loading.png',
      );
    });

    test('evidence upload progress should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/evidence');
      await page.click('[data-testid="upload-evidence-button"]');

      // Simulate file upload with progress
      await page.setInputFiles('[data-testid="file-input"]', {
        name: 'test-document.pdf',
        mimeType: 'application/pdf',
        buffer: Buffer.from('test content'),
      });

      const uploadProgress = page.locator('[data-testid="upload-progress"]');
      await expect(uploadProgress).toHaveScreenshot('upload-progress.png');
    });
  });

  test.describe('Error States', () => {
    test('404 page should match baseline', async ({ page }) => {
      await page.goto('/non-existent-page');

      await expect(page).toHaveScreenshot('404-page.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('network error state should match baseline', async ({ page }) => {
      // Simulate network error
      await page.route('**/api/**', (route) => {
        route.abort('failed');
      });

      await helpers.navigateAndWait('/dashboard');

      const errorState = page.locator('[data-testid="network-error"]');
      await expect(errorState).toHaveScreenshot('network-error.png');
    });

    test('form validation errors should match baseline', async ({ page }) => {
      await helpers.navigateAndWait('/register');

      // Submit form without filling required fields
      await page.click('[data-testid="register-button"]');
      await page.waitForTimeout(500);

      const formErrors = page.locator('[data-testid="register-form"]');
      await expect(formErrors).toHaveScreenshot('form-validation-errors.png');
    });
  });

  test.describe('Dark Mode', () => {
    test('homepage dark mode should match baseline', async ({ page }) => {
      // Enable dark mode
      await page.emulateMedia({ colorScheme: 'dark' });
      await helpers.navigateAndWait('/');

      await expect(page).toHaveScreenshot('homepage-dark.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('dashboard dark mode should match baseline', async ({ page }) => {
      await page.emulateMedia({ colorScheme: 'dark' });
      await helpers.navigateAndWait('/dashboard');

      await expect(page).toHaveScreenshot('dashboard-dark.png', {
        fullPage: true,
        animations: 'disabled',
        mask: [page.locator('[data-testid="current-time"]')],
      });
    });
  });
});
