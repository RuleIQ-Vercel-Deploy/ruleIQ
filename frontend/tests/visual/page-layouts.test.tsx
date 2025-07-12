import { test, expect } from '@playwright/test';
import { TestHelpers } from '../e2e/utils/test-helpers';

/**
 * Visual regression tests for complete page layouts
 * Tests full page rendering across different viewports and browsers
 */

test.describe('Page Layout Visual Regression Tests', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test.describe('Public Pages', () => {
    test('landing page - full layout', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000); // Allow animations to complete
      
      await expect(page).toHaveScreenshot(`landing-page-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
        maxDiffPixels: 100,
      });
    });

    test('marketing page sections', async ({ page }) => {
      await helpers.navigateAndWait('/marketing');
      
      // Hero section
      const heroSection = page.locator('[data-testid="hero-section"]');
      await expect(heroSection).toHaveScreenshot('marketing-hero.png');
      
      // Features section
      const featuresSection = page.locator('[data-testid="features-section"]');
      await expect(featuresSection).toHaveScreenshot('marketing-features.png');
      
      // Pricing section
      const pricingSection = page.locator('[data-testid="pricing-section"]');
      await expect(pricingSection).toHaveScreenshot('marketing-pricing.png');
      
      // CTA section
      const ctaSection = page.locator('[data-testid="cta-section"]');
      await expect(ctaSection).toHaveScreenshot('marketing-cta.png');
    });

    test('pricing page - complete layout', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/pricing');
      await page.waitForLoadState('networkidle');
      
      await expect(page).toHaveScreenshot(`pricing-page-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
      });
    });
  });

  test.describe('Authentication Pages', () => {
    test('login page - all states', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/login');
      
      // Default state
      await expect(page).toHaveScreenshot(`login-page-default-${browserName}.png`, {
        fullPage: true,
      });
      
      // With validation errors
      await page.click('[data-testid="login-button"]');
      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot(`login-page-errors-${browserName}.png`, {
        fullPage: true,
      });
      
      // Filled form
      await helpers.fillField('[data-testid="email-input"]', 'test@example.com');
      await helpers.fillField('[data-testid="password-input"]', 'password123');
      await expect(page).toHaveScreenshot(`login-page-filled-${browserName}.png`, {
        fullPage: true,
      });
    });

    test('registration page - multi-step flow', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/register');
      
      // Step 1
      await expect(page).toHaveScreenshot(`register-step1-${browserName}.png`, {
        fullPage: true,
      });
      
      // Fill step 1
      await helpers.fillField('[data-testid="email-input"]', 'newuser@example.com');
      await helpers.fillField('[data-testid="password-input"]', 'SecurePass123!');
      await helpers.fillField('[data-testid="confirm-password-input"]', 'SecurePass123!');
      await page.click('[data-testid="next-button"]');
      
      // Step 2
      await page.waitForTimeout(300);
      await expect(page).toHaveScreenshot(`register-step2-${browserName}.png`, {
        fullPage: true,
      });
    });
  });

  test.describe('Dashboard Pages', () => {
    test.beforeEach(async ({ page }) => {
      // Mock authentication
      await page.goto('/login');
      await page.evaluate(() => {
        localStorage.setItem('auth-token', 'mock-token');
        localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));
      });
    });

    test('main dashboard - complete layout', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/dashboard');
      await helpers.waitForLoadingToComplete();
      
      await expect(page).toHaveScreenshot(`dashboard-main-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
        mask: [
          page.locator('[data-testid="current-time"]'),
          page.locator('[data-testid="dynamic-data"]'),
        ],
      });
    });

    test('analytics dashboard', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/analytics');
      await helpers.waitForLoadingToComplete();
      
      await expect(page).toHaveScreenshot(`analytics-dashboard-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
        mask: [
          page.locator('[data-testid="chart-data"]'),
          page.locator('[data-testid="date-range"]'),
        ],
      });
    });

    test('assessments page - list view', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/assessments');
      await helpers.waitForLoadingToComplete();
      
      await expect(page).toHaveScreenshot(`assessments-list-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('assessment wizard - multi-step', async ({ page }) => {
      await helpers.navigateAndWait('/assessments/new');
      
      // Step 1: Framework Selection
      await expect(page).toHaveScreenshot('assessment-wizard-step1.png', {
        fullPage: true,
      });
      
      // Select framework and proceed
      await page.click('[data-testid="framework-gdpr"]');
      await page.click('[data-testid="next-button"]');
      await page.waitForTimeout(300);
      
      // Step 2: Questions
      await expect(page).toHaveScreenshot('assessment-wizard-step2.png', {
        fullPage: true,
      });
      
      // Answer questions and proceed
      await page.click('[data-testid="answer-yes-1"]');
      await page.click('[data-testid="next-button"]');
      await page.waitForTimeout(300);
      
      // Step 3: Review
      await expect(page).toHaveScreenshot('assessment-wizard-step3.png', {
        fullPage: true,
      });
    });

    test('evidence management page', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/evidence');
      await helpers.waitForLoadingToComplete();
      
      await expect(page).toHaveScreenshot(`evidence-page-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('policies page - grid view', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/policies');
      await helpers.waitForLoadingToComplete();
      
      await expect(page).toHaveScreenshot(`policies-grid-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('chat interface', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/chat');
      await helpers.waitForLoadingToComplete();
      
      await expect(page).toHaveScreenshot(`chat-interface-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('business profile page', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/business-profile');
      await helpers.waitForLoadingToComplete();
      
      await expect(page).toHaveScreenshot(`business-profile-${browserName}.png`, {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('settings pages', async ({ page }) => {
      // Team settings
      await helpers.navigateAndWait('/settings/team');
      await helpers.waitForLoadingToComplete();
      await expect(page).toHaveScreenshot('settings-team.png', {
        fullPage: true,
      });
      
      // Billing settings
      await helpers.navigateAndWait('/settings/billing');
      await helpers.waitForLoadingToComplete();
      await expect(page).toHaveScreenshot('settings-billing.png', {
        fullPage: true,
      });
      
      // Integrations settings
      await helpers.navigateAndWait('/settings/integrations');
      await helpers.waitForLoadingToComplete();
      await expect(page).toHaveScreenshot('settings-integrations.png', {
        fullPage: true,
      });
    });
  });

  test.describe('Responsive Layouts', () => {
    const viewports = [
      { name: 'mobile-portrait', width: 375, height: 667 },
      { name: 'mobile-landscape', width: 667, height: 375 },
      { name: 'tablet-portrait', width: 768, height: 1024 },
      { name: 'tablet-landscape', width: 1024, height: 768 },
      { name: 'desktop', width: 1440, height: 900 },
      { name: 'wide-desktop', width: 1920, height: 1080 },
    ];

    for (const viewport of viewports) {
      test(`dashboard layout - ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        
        // Mock authentication
        await page.goto('/login');
        await page.evaluate(() => {
          localStorage.setItem('auth-token', 'mock-token');
        });
        
        await helpers.navigateAndWait('/dashboard');
        await helpers.waitForLoadingToComplete();
        
        await expect(page).toHaveScreenshot(`dashboard-${viewport.name}.png`, {
          fullPage: true,
          animations: 'disabled',
          mask: [
            page.locator('[data-testid="current-time"]'),
            page.locator('[data-testid="dynamic-data"]'),
          ],
        });
      });

      test(`landing page - ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await helpers.navigateAndWait('/');
        
        await expect(page).toHaveScreenshot(`landing-${viewport.name}.png`, {
          fullPage: true,
          animations: 'disabled',
        });
      });
    }
  });

  test.describe('Cross-Browser Testing', () => {
    test('dashboard consistency across browsers', async ({ page, browserName }) => {
      // Mock authentication
      await page.goto('/login');
      await page.evaluate(() => {
        localStorage.setItem('auth-token', 'mock-token');
      });
      
      await helpers.navigateAndWait('/dashboard');
      await helpers.waitForLoadingToComplete();
      
      // Take screenshots of specific components for cross-browser comparison
      const header = page.locator('[data-testid="dashboard-header"]');
      await expect(header).toHaveScreenshot(`dashboard-header-${browserName}.png`);
      
      const sidebar = page.locator('[data-testid="dashboard-sidebar"]');
      await expect(sidebar).toHaveScreenshot(`dashboard-sidebar-${browserName}.png`);
      
      const mainContent = page.locator('[data-testid="dashboard-main"]');
      await expect(mainContent).toHaveScreenshot(`dashboard-main-content-${browserName}.png`, {
        mask: [
          mainContent.locator('[data-testid="dynamic-data"]'),
        ],
      });
    });

    test('form rendering across browsers', async ({ page, browserName }) => {
      await helpers.navigateAndWait('/forms');
      
      const formContainer = page.locator('[data-testid="form-showcase"]');
      await expect(formContainer).toHaveScreenshot(`forms-showcase-${browserName}.png`);
    });

    test('chart rendering across browsers', async ({ page, browserName }) => {
      // Mock authentication
      await page.goto('/login');
      await page.evaluate(() => {
        localStorage.setItem('auth-token', 'mock-token');
      });
      
      await helpers.navigateAndWait('/analytics');
      await helpers.waitForLoadingToComplete();
      
      const chartContainer = page.locator('[data-testid="charts-container"]');
      await expect(chartContainer).toHaveScreenshot(`charts-${browserName}.png`, {
        mask: [
          chartContainer.locator('[data-testid="dynamic-data"]'),
        ],
      });
    });
  });

  test.describe('Dark Mode Layouts', () => {
    test('dashboard pages in dark mode', async ({ page }) => {
      await page.emulateMedia({ colorScheme: 'dark' });
      
      // Mock authentication
      await page.goto('/login');
      await page.evaluate(() => {
        localStorage.setItem('auth-token', 'mock-token');
      });
      
      // Main dashboard
      await helpers.navigateAndWait('/dashboard');
      await helpers.waitForLoadingToComplete();
      await expect(page).toHaveScreenshot('dashboard-dark-mode.png', {
        fullPage: true,
        animations: 'disabled',
        mask: [
          page.locator('[data-testid="current-time"]'),
        ],
      });
      
      // Assessments
      await helpers.navigateAndWait('/assessments');
      await helpers.waitForLoadingToComplete();
      await expect(page).toHaveScreenshot('assessments-dark-mode.png', {
        fullPage: true,
      });
      
      // Evidence
      await helpers.navigateAndWait('/evidence');
      await helpers.waitForLoadingToComplete();
      await expect(page).toHaveScreenshot('evidence-dark-mode.png', {
        fullPage: true,
      });
    });

    test('public pages in dark mode', async ({ page }) => {
      await page.emulateMedia({ colorScheme: 'dark' });
      
      // Landing page
      await helpers.navigateAndWait('/');
      await expect(page).toHaveScreenshot('landing-dark-mode.png', {
        fullPage: true,
        animations: 'disabled',
      });
      
      // Login page
      await helpers.navigateAndWait('/login');
      await expect(page).toHaveScreenshot('login-dark-mode.png', {
        fullPage: true,
      });
      
      // Pricing page
      await helpers.navigateAndWait('/pricing');
      await expect(page).toHaveScreenshot('pricing-dark-mode.png', {
        fullPage: true,
      });
    });
  });

  test.describe('Loading and Error States', () => {
    test('loading states across pages', async ({ page }) => {
      // Intercept API calls to simulate loading
      await page.route('**/api/**', route => {
        setTimeout(() => route.continue(), 3000);
      });
      
      // Dashboard loading
      await helpers.navigateAndWait('/dashboard');
      await expect(page).toHaveScreenshot('dashboard-loading-state.png', {
        fullPage: true,
      });
      
      // Assessments loading
      await helpers.navigateAndWait('/assessments');
      await expect(page).toHaveScreenshot('assessments-loading-state.png', {
        fullPage: true,
      });
    });

    test('error states across pages', async ({ page }) => {
      // Intercept API calls to simulate errors
      await page.route('**/api/**', route => {
        route.abort('failed');
      });
      
      // Dashboard error
      await helpers.navigateAndWait('/dashboard');
      await page.waitForTimeout(1000);
      await expect(page).toHaveScreenshot('dashboard-error-state.png', {
        fullPage: true,
      });
      
      // 404 page
      await page.goto('/non-existent-page');
      await expect(page).toHaveScreenshot('404-error-page.png', {
        fullPage: true,
      });
    });
  });

  test.describe('Print Layouts', () => {
    test('dashboard print layout', async ({ page }) => {
      // Mock authentication
      await page.goto('/login');
      await page.evaluate(() => {
        localStorage.setItem('auth-token', 'mock-token');
      });
      
      await helpers.navigateAndWait('/dashboard');
      await helpers.waitForLoadingToComplete();
      
      // Emulate print media
      await page.emulateMedia({ media: 'print' });
      
      await expect(page).toHaveScreenshot('dashboard-print.png', {
        fullPage: true,
      });
    });

    test('assessment results print layout', async ({ page }) => {
      // Mock authentication
      await page.goto('/login');
      await page.evaluate(() => {
        localStorage.setItem('auth-token', 'mock-token');
      });
      
      await helpers.navigateAndWait('/assessments/123/results');
      await helpers.waitForLoadingToComplete();
      
      // Emulate print media
      await page.emulateMedia({ media: 'print' });
      
      await expect(page).toHaveScreenshot('assessment-results-print.png', {
        fullPage: true,
      });
    });
  });
});