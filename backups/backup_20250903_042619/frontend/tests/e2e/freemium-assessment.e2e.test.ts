/**
 * End-to-End tests for AI Assessment Freemium Strategy
 *
 * Tests complete user journeys in a real browser environment:
 * - Email capture with UTM tracking
 * - Dynamic assessment flow with AI questions
 * - Results display and conversion tracking
 * - Cross-browser compatibility
 * - Mobile responsiveness
 * - Performance benchmarks
 * - Error recovery scenarios
 *
 * Uses Playwright for reliable, fast E2E testing.
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';
import { faker } from '@faker-js/faker';

/**
 * Test configuration and setup
 */
const TEST_CONFIG = {
  baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
  apiURL: process.env.E2E_API_URL || 'http://localhost:8000',
  timeout: 30000,
  email: `test.${Date.now()}@example.com`,
  utm: {
    source: 'playwright',
    campaign: 'e2e_testing',
    medium: 'automated',
    term: 'freemium_test',
    content: 'test_suite',
  },
};

/**
 * Page Object Model for Freemium Flow
 */
class FreemiumPage {
  constructor(private page: Page) {}

  // Email Capture Page
  async navigateToLanding(utmParams = TEST_CONFIG.utm) {
    const url = new URL('/freemium', TEST_CONFIG.baseURL);
    Object.entries(utmParams).forEach(([key, value]) => {
      url.searchParams.set(`utm_${key}`, value);
    });

    await this.page.goto(url.toString());
    await this.page.waitForLoadState('networkidle');
  }

  async fillEmailCapture(email: string, marketingConsent = true, termsConsent = true) {
    await this.page.fill('[data-testid="email-input"]', email);

    if (marketingConsent) {
      await this.page.check('[data-testid="marketing-consent"]');
    }

    if (termsConsent) {
      await this.page.check('[data-testid="terms-consent"]');
    }
  }

  async submitEmailCapture() {
    await this.page.click('[data-testid="start-assessment-button"]');
    await this.page.waitForLoadState('networkidle');
  }

  // Assessment Flow Page
  async waitForAssessmentToLoad() {
    await this.page.waitForSelector('[data-testid="assessment-question"]', { timeout: 10000 });
  }

  async getCurrentQuestion() {
    return await this.page.textContent('[data-testid="question-text"]');
  }

  async getProgressPercentage() {
    const progressText = await this.page.textContent('[data-testid="progress-indicator"]');
    const match = progressText?.match(/(\d+)%/);
    return match ? parseInt(match[1]) : 0;
  }

  async answerMultipleChoice(answer: string) {
    await this.page.click(`[data-testid="option-${answer.toLowerCase().replace(/\s+/g, '-')}"]`);
  }

  async answerMultiSelect(answers: string[]) {
    for (const answer of answers) {
      await this.page.check(
        `[data-testid="checkbox-${answer.toLowerCase().replace(/\s+/g, '-')}"]`,
      );
    }
  }

  async answerTextInput(answer: string) {
    await this.page.fill('[data-testid="text-input"]', answer);
  }

  async submitAnswer() {
    await this.page.click('[data-testid="next-button"]');
    await this.page.waitForLoadState('networkidle');
  }

  async isAssessmentComplete() {
    return await this.page.isVisible('[data-testid="assessment-complete"]');
  }

  // Results Page
  async waitForResultsToLoad() {
    await this.page.waitForSelector('[data-testid="results-container"]', { timeout: 15000 });
  }

  async getRiskScore() {
    const scoreText = await this.page.textContent('[data-testid="risk-score"]');
    const match = scoreText?.match(/(\d+\.?\d*)/);
    return match ? parseFloat(match[1]) : 0;
  }

  async getRiskLevel() {
    return await this.page.textContent('[data-testid="risk-level"]');
  }

  async getComplianceGaps() {
    const gaps = await this.page.$$('[data-testid^="compliance-gap-"]');
    const gapData = [];

    for (const gap of gaps) {
      const framework = await gap.getAttribute('data-framework');
      const severity = await gap.getAttribute('data-severity');
      const description = await gap.textContent();
      gapData.push({ framework, severity, description });
    }

    return gapData;
  }

  async getRecommendations() {
    const recommendations = await this.page.$$('[data-testid^="recommendation-"]');
    return await Promise.all(recommendations.map((rec) => rec.textContent()));
  }

  async clickConversionCTA() {
    await this.page.click('[data-testid="conversion-cta"]');
  }

  async shareResults() {
    await this.page.click('[data-testid="share-button"]');
    await this.page.waitForSelector('[data-testid="share-success"]');
  }

  async downloadPDF() {
    const downloadPromise = this.page.waitForEvent('download');
    await this.page.click('[data-testid="download-pdf"]');
    return await downloadPromise;
  }

  // Utility methods
  async takeScreenshot(name: string) {
    await this.page.screenshot({
      path: `test-results/screenshots/${name}-${Date.now()}.png`,
      fullPage: true,
    });
  }

  async checkAccessibility() {
    // Basic accessibility checks
    const violations = await this.page.evaluate(() => {
      const issues = [];

      // Check for alt text on images
      const images = document.querySelectorAll('img');
      images.forEach((img, index) => {
        if (!img.alt && !img.getAttribute('aria-label')) {
          issues.push(`Image ${index} missing alt text`);
        }
      });

      // Check for form labels
      const inputs = document.querySelectorAll('input, select, textarea');
      inputs.forEach((input, index) => {
        const hasLabel =
          input.getAttribute('aria-label') ||
          input.getAttribute('aria-labelledby') ||
          document.querySelector(`label[for="${input.id}"]`);
        if (!hasLabel) {
          issues.push(`Form field ${index} missing label`);
        }
      });

      // Check heading hierarchy
      const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      let prevLevel = 0;
      headings.forEach((heading, index) => {
        const level = parseInt(heading.tagName.substring(1));
        if (level > prevLevel + 1) {
          issues.push(`Heading level skip at heading ${index}: ${heading.textContent}`);
        }
        prevLevel = level;
      });

      return issues;
    });

    return violations;
  }
}

/**
 * Test Suite: Complete Freemium Flow
 */
test.describe('Freemium Assessment E2E', () => {
  let freemiumPage: FreemiumPage;

  test.beforeEach(async ({ page }) => {
    freemiumPage = new FreemiumPage(page);
  });

  test('completes full freemium journey successfully', async ({ page }) => {
    test.setTimeout(60000);

    const testEmail = `success.${Date.now()}@example.com`;

    // Step 1: Landing page with UTM parameters
    await freemiumPage.navigateToLanding();

    // Verify page loads and UTM parameters are captured
    await expect(page.locator('[data-testid="freemium-landing"]')).toBeVisible();
    await expect(page.locator('text=Start Your Free Compliance Assessment')).toBeVisible();

    // Step 2: Email capture
    await freemiumPage.fillEmailCapture(testEmail, true, true);
    await freemiumPage.submitEmailCapture();

    // Verify navigation to assessment
    await expect(page).toHaveURL(/\/freemium\/assessment/);

    // Step 3: Assessment flow
    await freemiumPage.waitForAssessmentToLoad();

    // Answer assessment questions
    const questions = [
      { type: 'multiple_choice', answer: 'SaaS' },
      { type: 'multiple_choice', answer: '11-50' },
      { type: 'multi_select', answers: ['Customer personal data', 'Payment information'] },
      { type: 'multiple_choice', answer: 'Partially compliant' },
      { type: 'multi_select', answers: ['GDPR', 'ISO 27001'] },
    ];

    for (let i = 0; i < questions.length; i++) {
      const question = questions[i];

      // Verify question loads
      await expect(page.locator('[data-testid="question-text"]')).toBeVisible();

      // Check progress
      const progress = await freemiumPage.getProgressPercentage();
      expect(progress).toBeGreaterThanOrEqual(i * 20);

      // Answer based on type
      if (question.type === 'multiple_choice') {
        await freemiumPage.answerMultipleChoice(question.answer);
      } else if (question.type === 'multi_select') {
        await freemiumPage.answerMultiSelect(question.answers);
      }

      // Submit answer
      await freemiumPage.submitAnswer();

      // Wait for next question or completion
      if (i < questions.length - 1) {
        await page.waitForTimeout(1000); // Allow for question transition
      }
    }

    // Step 4: Results page
    await expect(page).toHaveURL(/\/freemium\/results/);
    await freemiumPage.waitForResultsToLoad();

    // Verify results display
    await expect(page.locator('text=Your Compliance Assessment Results')).toBeVisible();

    const riskScore = await freemiumPage.getRiskScore();
    expect(riskScore).toBeGreaterThan(0);
    expect(riskScore).toBeLessThanOrEqual(10);

    const riskLevel = await freemiumPage.getRiskLevel();
    expect(['low', 'medium', 'high']).toContain(riskLevel?.toLowerCase());

    // Verify compliance gaps
    const gaps = await freemiumPage.getComplianceGaps();
    expect(gaps.length).toBeGreaterThan(0);

    // Verify recommendations
    const recommendations = await freemiumPage.getRecommendations();
    expect(recommendations.length).toBeGreaterThan(0);

    // Step 5: Conversion CTA
    await expect(page.locator('[data-testid="conversion-cta"]')).toBeVisible();
    await expect(page.locator('text=Get Compliant Now')).toBeVisible();

    // Click CTA (but don't navigate away in test)
    await freemiumPage.clickConversionCTA();

    // Take final screenshot
    await freemiumPage.takeScreenshot('complete-journey-success');
  });

  test('handles email validation errors', async ({ page }) => {
    await freemiumPage.navigateToLanding();

    // Try invalid email
    await freemiumPage.fillEmailCapture('invalid-email', false, true);
    await freemiumPage.submitEmailCapture();

    // Should show validation error
    await expect(page.locator('text=please enter a valid email')).toBeVisible();

    // Should not navigate away
    await expect(page).toHaveURL(/\/freemium$/);
  });

  test('requires terms of service consent', async ({ page }) => {
    await freemiumPage.navigateToLanding();

    // Try without terms consent
    await freemiumPage.fillEmailCapture('valid@example.com', true, false);
    await freemiumPage.submitEmailCapture();

    // Should show consent error
    await expect(page.locator('text=you must agree to the terms')).toBeVisible();

    // Should not navigate away
    await expect(page).toHaveURL(/\/freemium$/);
  });

  test('handles API errors gracefully', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/v1/freemium/capture-email', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });

    await freemiumPage.navigateToLanding();
    await freemiumPage.fillEmailCapture('error@example.com', true, true);
    await freemiumPage.submitEmailCapture();

    // Should show error message
    await expect(page.locator('text=failed to start assessment')).toBeVisible();
    await expect(page.locator('text=please try again')).toBeVisible();
  });

  test('supports keyboard navigation', async ({ page }) => {
    await freemiumPage.navigateToLanding();

    // Navigate through form with keyboard
    await page.keyboard.press('Tab'); // Email input
    await page.keyboard.type('keyboard@example.com');

    await page.keyboard.press('Tab'); // Marketing consent
    await page.keyboard.press('Space'); // Check

    await page.keyboard.press('Tab'); // Terms consent
    await page.keyboard.press('Space'); // Check

    await page.keyboard.press('Tab'); // Submit button
    await page.keyboard.press('Enter'); // Submit

    // Should navigate to assessment
    await expect(page).toHaveURL(/\/freemium\/assessment/);
  });

  test('works on mobile devices', async ({ page, browserName }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await freemiumPage.navigateToLanding();

    // Verify mobile layout
    await expect(page.locator('[data-testid="mobile-layout"]')).toBeVisible();

    // Complete mobile flow
    await freemiumPage.fillEmailCapture('mobile@example.com', true, true);
    await freemiumPage.submitEmailCapture();

    await expect(page).toHaveURL(/\/freemium\/assessment/);

    await freemiumPage.takeScreenshot(`mobile-${browserName}`);
  });

  test('maintains session across page refreshes', async ({ page }) => {
    const testEmail = `session.${Date.now()}@example.com`;

    await freemiumPage.navigateToLanding();
    await freemiumPage.fillEmailCapture(testEmail, true, true);
    await freemiumPage.submitEmailCapture();

    await freemiumPage.waitForAssessmentToLoad();

    // Answer first question
    await freemiumPage.answerMultipleChoice('SaaS');
    await freemiumPage.submitAnswer();

    // Refresh page
    await page.reload();
    await freemiumPage.waitForAssessmentToLoad();

    // Should resume from where left off
    const progress = await freemiumPage.getProgressPercentage();
    expect(progress).toBeGreaterThan(0);
  });

  test('tracks UTM parameters correctly', async ({ page }) => {
    const customUTM = {
      source: 'facebook',
      campaign: 'retargeting_q1',
      medium: 'social',
      term: 'compliance_automation',
      content: 'video_cta',
    };

    await freemiumPage.navigateToLanding(customUTM);

    // Check if UTM parameters are captured in localStorage
    const utmData = await page.evaluate(() => {
      return localStorage.getItem('freemium-utm');
    });

    expect(utmData).toBeTruthy();
    const parsedUTM = JSON.parse(utmData);
    expect(parsedUTM.utm_source).toBe('facebook');
    expect(parsedUTM.utm_campaign).toBe('retargeting_q1');
  });

  test('shares results successfully', async ({ page, context }) => {
    // Complete assessment first (abbreviated)
    await freemiumPage.navigateToLanding();
    await freemiumPage.fillEmailCapture('share@example.com', true, true);
    await freemiumPage.submitEmailCapture();

    // Mock completed assessment
    await page.goto('/freemium/results?token=mock-completed-token');
    await freemiumPage.waitForResultsToLoad();

    // Test share functionality
    await freemiumPage.shareResults();

    // Verify share success
    await expect(page.locator('text=link copied to clipboard')).toBeVisible();
  });

  test('downloads PDF results', async ({ page }) => {
    // Navigate to results page
    await page.goto('/freemium/results?token=mock-completed-token');
    await freemiumPage.waitForResultsToLoad();

    // Test PDF download
    const download = await freemiumPage.downloadPDF();
    expect(download.suggestedFilename()).toContain('compliance-assessment');
  });

  test('meets accessibility standards', async ({ page }) => {
    await freemiumPage.navigateToLanding();

    // Run accessibility checks
    const violations = await freemiumPage.checkAccessibility();

    // Should have no critical accessibility violations
    expect(violations).toHaveLength(0);

    // Verify ARIA attributes
    await expect(page.locator('[role="main"]')).toBeVisible();
    await expect(page.locator('[aria-label]')).toHaveCount(4); // Expected labeled elements
  });

  test('performs within acceptable limits', async ({ page }) => {
    // Start performance monitoring
    await page.addInitScript(() => {
      window.performance.mark('test-start');
    });

    await freemiumPage.navigateToLanding();

    // Measure page load time
    const loadTime = await page.evaluate(() => {
      return performance.timing.loadEventEnd - performance.timing.navigationStart;
    });

    expect(loadTime).toBeLessThan(3000); // Under 3 seconds

    // Measure assessment transition time
    await freemiumPage.fillEmailCapture('perf@example.com', true, true);

    const startTime = Date.now();
    await freemiumPage.submitEmailCapture();
    await freemiumPage.waitForAssessmentToLoad();
    const transitionTime = Date.now() - startTime;

    expect(transitionTime).toBeLessThan(2000); // Under 2 seconds
  });

  test('handles concurrent users', async ({ browser }) => {
    // Create multiple browser contexts to simulate concurrent users
    const contexts = await Promise.all([
      browser.newContext(),
      browser.newContext(),
      browser.newContext(),
    ]);

    const pages = await Promise.all(contexts.map((ctx) => ctx.newPage()));

    // Run concurrent assessment flows
    const promises = pages.map(async (page, index) => {
      const freemium = new FreemiumPage(page);
      await freemium.navigateToLanding();
      await freemium.fillEmailCapture(`concurrent${index}@example.com`, true, true);
      await freemium.submitEmailCapture();
      return page.url();
    });

    const results = await Promise.all(promises);

    // All should successfully navigate to assessment
    results.forEach((url) => {
      expect(url).toContain('/freemium/assessment');
    });

    // Cleanup
    await Promise.all(contexts.map((ctx) => ctx.close()));
  });
});

/**
 * Test Suite: Cross-Browser Compatibility
 */
test.describe('Cross-Browser Compatibility', () => {
  test('works in Chrome', async ({ page, browserName }) => {
    test.skip(browserName !== 'chromium', 'Chrome-specific test');

    const freemiumPage = new FreemiumPage(page);
    await freemiumPage.navigateToLanding();

    await expect(page.locator('[data-testid="freemium-landing"]')).toBeVisible();
    await freemiumPage.takeScreenshot('chrome-compatibility');
  });

  test('works in Firefox', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox', 'Firefox-specific test');

    const freemiumPage = new FreemiumPage(page);
    await freemiumPage.navigateToLanding();

    await expect(page.locator('[data-testid="freemium-landing"]')).toBeVisible();
    await freemiumPage.takeScreenshot('firefox-compatibility');
  });

  test('works in Safari', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit', 'Safari-specific test');

    const freemiumPage = new FreemiumPage(page);
    await freemiumPage.navigateToLanding();

    await expect(page.locator('[data-testid="freemium-landing"]')).toBeVisible();
    await freemiumPage.takeScreenshot('safari-compatibility');
  });
});

/**
 * Test Suite: Performance Benchmarks
 */
test.describe('Performance Benchmarks', () => {
  test('measures Core Web Vitals', async ({ page }) => {
    await page.goto('/freemium');

    // Measure Largest Contentful Paint (LCP)
    const lcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });
      });
    });

    expect(lcp).toBeLessThan(2500); // Good LCP is under 2.5s

    // Measure Cumulative Layout Shift (CLS)
    await page.waitForLoadState('networkidle');
    const cls = await page.evaluate(() => {
      return new Promise((resolve) => {
        let clsValue = 0;
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
          resolve(clsValue);
        }).observe({ entryTypes: ['layout-shift'] });

        setTimeout(() => resolve(clsValue), 5000);
      });
    });

    expect(cls).toBeLessThan(0.1); // Good CLS is under 0.1
  });

  test('measures API response times', async ({ page }) => {
    const apiTimes: number[] = [];

    page.on('response', (response) => {
      if (response.url().includes('/api/v1/freemium/')) {
        const timing = response.timing();
        if (timing) {
          apiTimes.push(timing.responseEnd - timing.requestStart);
        }
      }
    });

    const freemiumPage = new FreemiumPage(page);
    await freemiumPage.navigateToLanding();
    await freemiumPage.fillEmailCapture('perf@example.com', true, true);
    await freemiumPage.submitEmailCapture();

    // Check API response times
    expect(apiTimes.length).toBeGreaterThan(0);
    const avgTime = apiTimes.reduce((a, b) => a + b, 0) / apiTimes.length;
    expect(avgTime).toBeLessThan(200); // Under 200ms average
  });
});
