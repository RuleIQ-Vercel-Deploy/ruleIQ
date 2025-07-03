import { type Page, Locator, expect } from '@playwright/test';

/**
 * Test utilities for ruleIQ E2E tests
 */

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Navigate to a specific page and wait for it to load
   */
  async navigateAndWait(path: string, waitForSelector?: string) {
    await this.page.goto(path);
    if (waitForSelector) {
      await this.page.waitForSelector(waitForSelector);
    }
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Fill a form field and wait for it to be updated
   */
  async fillField(selector: string, value: string) {
    await this.page.fill(selector, value);
    await this.page.waitForTimeout(100); // Small delay for UI updates
  }

  /**
   * Click a button and wait for navigation or loading
   */
  async clickAndWait(selector: string, waitForSelector?: string) {
    await this.page.click(selector);
    if (waitForSelector) {
      await this.page.waitForSelector(waitForSelector);
    }
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for a toast notification to appear
   */
  async waitForToast(message?: string) {
    const toast = this.page.locator('[data-testid="toast"]').first();
    await expect(toast).toBeVisible();
    
    if (message) {
      await expect(toast).toContainText(message);
    }
    
    return toast;
  }

  /**
   * Wait for loading states to complete
   */
  async waitForLoadingToComplete() {
    // Wait for any loading spinners to disappear
    await this.page.waitForSelector('[data-testid="loading-spinner"]', { 
      state: 'hidden',
      timeout: 10000 
    }).catch(() => {
      // Ignore if no loading spinner exists
    });
    
    // Wait for skeleton loaders to disappear
    await this.page.waitForSelector('[data-testid="skeleton-loader"]', { 
      state: 'hidden',
      timeout: 10000 
    }).catch(() => {
      // Ignore if no skeleton loader exists
    });
  }

  /**
   * Check if an element is visible and enabled
   */
  async isElementReady(selector: string): Promise<boolean> {
    try {
      const element = this.page.locator(selector);
      await expect(element).toBeVisible();
      await expect(element).toBeEnabled();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Take a screenshot with a descriptive name
   */
  async takeScreenshot(name: string) {
    await this.page.screenshot({ 
      path: `test-results/screenshots/${name}-${Date.now()}.png`,
      fullPage: true 
    });
  }

  /**
   * Scroll to an element and ensure it's visible
   */
  async scrollToElement(selector: string) {
    await this.page.locator(selector).scrollIntoViewIfNeeded();
    await this.page.waitForTimeout(500); // Allow scroll animation
  }

  /**
   * Check accessibility of the current page
   */
  async checkAccessibility() {
    // This would integrate with axe-core for accessibility testing
    // Implementation depends on your accessibility testing setup
    console.log('Accessibility check for:', await this.page.url());
  }

  /**
   * Mock API responses for testing
   */
  async mockApiResponse(url: string, response: any) {
    await this.page.route(url, route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  /**
   * Wait for API call to complete
   */
  async waitForApiCall(urlPattern: string) {
    return this.page.waitForResponse(response => 
      response.url().includes(urlPattern) && response.status() === 200
    );
  }
}

/**
 * Authentication helpers
 */
export class AuthHelpers extends TestHelpers {
  /**
   * Login with test credentials
   */
  async login(email: string = 'test@example.com', password: string = 'TestPassword123!') {
    await this.navigateAndWait('/login');
    
    await this.fillField('[data-testid="email-input"]', email);
    await this.fillField('[data-testid="password-input"]', password);
    
    await this.clickAndWait('[data-testid="login-button"]', '[data-testid="dashboard"]');
    
    // Verify we're logged in
    await expect(this.page.locator('[data-testid="user-menu"]')).toBeVisible();
  }

  /**
   * Logout from the application
   */
  async logout() {
    await this.page.click('[data-testid="user-menu"]');
    await this.clickAndWait('[data-testid="logout-button"]', '[data-testid="login-form"]');
  }

  /**
   * Register a new user
   */
  async register(userData: {
    email: string;
    password: string;
    fullName: string;
    company?: string;
  }) {
    await this.navigateAndWait('/register');
    
    await this.fillField('[data-testid="full-name-input"]', userData.fullName);
    await this.fillField('[data-testid="email-input"]', userData.email);
    await this.fillField('[data-testid="password-input"]', userData.password);
    
    if (userData.company) {
      await this.fillField('[data-testid="company-input"]', userData.company);
    }
    
    await this.clickAndWait('[data-testid="register-button"]');
    
    // Wait for success message or redirect
    await this.waitForToast('Registration successful');
  }
}

/**
 * Business Profile helpers
 */
export class BusinessProfileHelpers extends TestHelpers {
  /**
   * Complete business profile setup
   */
  async completeProfileSetup(profileData: {
    companyName: string;
    industry: string;
    employeeCount: string;
    dataTypes: string[];
  }) {
    await this.navigateAndWait('/business-profile/setup');
    
    // Step 1: Company Information
    await this.fillField('[data-testid="company-name-input"]', profileData.companyName);
    await this.page.selectOption('[data-testid="industry-select"]', profileData.industry);
    await this.page.selectOption('[data-testid="employee-count-select"]', profileData.employeeCount);
    await this.clickAndWait('[data-testid="next-button"]');
    
    // Step 2: Data Types
    for (const dataType of profileData.dataTypes) {
      await this.page.check(`[data-testid="data-type-${dataType}"]`);
    }
    await this.clickAndWait('[data-testid="next-button"]');
    
    // Step 3: Review and Submit
    await this.clickAndWait('[data-testid="submit-button"]', '[data-testid="dashboard"]');
    
    await this.waitForToast('Business profile created successfully');
  }
}

/**
 * Assessment helpers
 */
export class AssessmentHelpers extends TestHelpers {
  /**
   * Start a new assessment
   */
  async startAssessment(frameworkName: string) {
    await this.navigateAndWait('/assessments');
    await this.clickAndWait('[data-testid="new-assessment-button"]');
    
    // Select framework
    await this.page.click(`[data-testid="framework-${frameworkName}"]`);
    await this.clickAndWait('[data-testid="start-assessment-button"]');
    
    // Wait for assessment to load
    await this.page.waitForSelector('[data-testid="assessment-question"]');
  }

  /**
   * Answer assessment questions
   */
  async answerQuestions(answers: { questionId: string; answer: string }[]) {
    for (const { questionId, answer } of answers) {
      await this.page.click(`[data-testid="question-${questionId}-answer-${answer}"]`);
      await this.page.waitForTimeout(500); // Allow UI to update
    }
  }

  /**
   * Submit assessment
   */
  async submitAssessment() {
    await this.clickAndWait('[data-testid="submit-assessment-button"]');
    await this.waitForToast('Assessment submitted successfully');
    
    // Wait for results page
    await this.page.waitForSelector('[data-testid="assessment-results"]');
  }
}

/**
 * Evidence helpers
 */
export class EvidenceHelpers extends TestHelpers {
  /**
   * Upload evidence file
   */
  async uploadEvidence(filePath: string, title: string, description?: string) {
    await this.navigateAndWait('/evidence');
    await this.clickAndWait('[data-testid="upload-evidence-button"]');
    
    // Upload file
    await this.page.setInputFiles('[data-testid="file-input"]', filePath);
    
    // Fill metadata
    await this.fillField('[data-testid="evidence-title-input"]', title);
    if (description) {
      await this.fillField('[data-testid="evidence-description-input"]', description);
    }
    
    await this.clickAndWait('[data-testid="upload-button"]');
    await this.waitForToast('Evidence uploaded successfully');
  }
}
