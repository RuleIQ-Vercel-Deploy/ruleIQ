/**
 * Test selectors for E2E tests
 * These provide consistent selectors across all E2E tests
 */

export const TestSelectors = {
  // Auth pages
  auth: {
    loginForm: 'form',
    registerForm: 'form',
    emailInput: 'input[type="email"]',
    passwordInput: 'input[type="password"]',
    fullNameInput: 'input[placeholder*="name" i], input[id*="name" i]',
    submitButton: 'button[type="submit"]',
    rememberMeCheckbox: 'input[type="checkbox"]',
    forgotPasswordLink: 'a[href="/forgot-password"]',
    signUpLink: 'a[href="/register"]',
    loginLink: 'a[href="/login"]',
  },

  // Navigation
  navigation: {
    mainNav: 'nav',
    mobileMenuButton: 'button[aria-label*="menu" i]',
    userMenu: '[aria-label*="user" i], [aria-label*="account" i]',
    logoutButton: 'button:has-text("Logout"), button:has-text("Sign out")',
  },

  // Dashboard
  dashboard: {
    container: 'main, [role="main"]',
    welcomeMessage: 'h1, h2',
    statsCards: '[class*="card"], [class*="stat"]',
    quickActions: '[class*="quick-action"], [class*="action-card"]',
  },

  // Business Profile
  businessProfile: {
    setupForm: 'form',
    companyNameInput: 'input[name*="company" i], input[placeholder*="company" i]',
    industrySelect: 'select[name*="industry" i], [role="combobox"]',
    employeeCountSelect: 'select[name*="employee" i], [role="combobox"]',
    dataTypeCheckboxes: 'input[type="checkbox"]',
    nextButton: 'button:has-text("Next"), button:has-text("Continue")',
    submitButton: 'button:has-text("Submit"), button:has-text("Complete")',
  },

  // Assessments
  assessments: {
    newAssessmentButton: 'button:has-text("New Assessment"), button:has-text("Start Assessment")',
    frameworkCards: '[class*="framework-card"], [role="button"]',
    assessmentQuestion: '[class*="question"], form',
    answerOptions: 'input[type="radio"], label',
    submitAssessmentButton: 'button:has-text("Submit"), button:has-text("Complete")',
    assessmentResults: '[class*="results"], [class*="score"]',
  },

  // Evidence
  evidence: {
    uploadButton: 'button:has-text("Upload"), button:has-text("Add Evidence")',
    fileInput: 'input[type="file"]',
    titleInput: 'input[name*="title" i], input[placeholder*="title" i]',
    descriptionInput: 'textarea, input[name*="description" i]',
    evidenceList: '[class*="evidence-list"], [role="list"]',
    evidenceCard: '[class*="evidence-card"], [class*="evidence-item"]',
    submitButton:
      'button[type="submit"], button:has-text("Submit"), button:has-text("Upload Evidence")',
  },

  // Common UI elements
  common: {
    toast: '[role="alert"], [class*="toast"], [class*="notification"]',
    loadingSpinner: '[class*="spinner"], [class*="loading"], svg[class*="animate-spin"]',
    skeletonLoader: '[class*="skeleton"], [class*="placeholder"]',
    errorMessage: '[class*="error"], [role="alert"]',
    successMessage: '[class*="success"], [role="status"]',
    modal: '[role="dialog"], [class*="modal"]',
    modalClose: 'button[aria-label*="close" i]',
  },
} as const;

/**
 * Helper function to wait for an element with multiple possible selectors
 */
export async function waitForAnySelector(page: any, selectors: string[]) {
  const promises = selectors.map((selector) =>
    page.waitForSelector(selector, { timeout: 5000 }).catch(() => null),
  );

  const element = await Promise.race(promises);
  if (!element) {
    throw new Error(`None of the selectors were found: ${selectors.join(', ')}`);
  }

  return element;
}

/**
 * Helper function to check if any of the selectors exist
 */
export async function hasAnySelector(page: any, selectors: string[]) {
  for (const selector of selectors) {
    const element = await page.$(selector);
    if (element) return true;
  }
  return false;
}
