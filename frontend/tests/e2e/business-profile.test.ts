import { test, expect } from '@playwright/test';

import { BUSINESS_PROFILES } from './fixtures/test-data';
import { AuthHelpers, BusinessProfileHelpers } from './utils/test-helpers';

test.describe('Business Profile Management', () => {
  let authHelpers: AuthHelpers;
  let profileHelpers: BusinessProfileHelpers;

  test.beforeEach(async ({ page }) => {
    authHelpers = new AuthHelpers(page);
    profileHelpers = new BusinessProfileHelpers(page);
    
    // Login before each test
    await authHelpers.login();
  });

  test.describe('Profile Setup Wizard', () => {
    test('should complete business profile setup successfully', async ({ page }) => {
      await profileHelpers.completeProfileSetup(BUSINESS_PROFILES.TECH_STARTUP);
      
      // Should be redirected to dashboard
      await expect(page).toHaveURL(/\/dashboard/);
      
      // Should show success message
      await profileHelpers.waitForToast('Business profile created successfully');
      
      // Should show profile completion status
      await expect(page.locator('[data-testid="profile-complete-badge"]')).toBeVisible();
    });

    test('should validate required fields in each step', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Step 1: Try to proceed without filling required fields
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      // Should show validation errors
      await expect(page.locator('[data-testid="company-name-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="industry-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="employee-count-error"]')).toBeVisible();
    });

    test('should allow navigation between wizard steps', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Fill step 1 and proceed
      await profileHelpers.fillField('[data-testid="company-name-input"]', BUSINESS_PROFILES.TECH_STARTUP.companyName);
      await page.selectOption('[data-testid="industry-select"]', BUSINESS_PROFILES.TECH_STARTUP.industry);
      await page.selectOption('[data-testid="employee-count-select"]', BUSINESS_PROFILES.TECH_STARTUP.employeeCount);
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      // Should be on step 2
      await expect(page.locator('[data-testid="step-2"]')).toBeVisible();
      
      // Go back to step 1
      await profileHelpers.clickAndWait('[data-testid="back-button"]');
      
      // Should be on step 1 with data preserved
      await expect(page.locator('[data-testid="step-1"]')).toBeVisible();
      await expect(page.locator('[data-testid="company-name-input"]')).toHaveValue(BUSINESS_PROFILES.TECH_STARTUP.companyName);
    });

    test('should save progress and allow resuming later', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Fill partial data
      await profileHelpers.fillField('[data-testid="company-name-input"]', BUSINESS_PROFILES.TECH_STARTUP.companyName);
      await page.selectOption('[data-testid="industry-select"]', BUSINESS_PROFILES.TECH_STARTUP.industry);
      
      // Navigate away
      await page.goto('/dashboard');
      
      // Return to setup
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Data should be preserved
      await expect(page.locator('[data-testid="company-name-input"]')).toHaveValue(BUSINESS_PROFILES.TECH_STARTUP.companyName);
    });

    test('should show progress indicator', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Should show step 1 as active
      await expect(page.locator('[data-testid="step-indicator-1"]')).toHaveClass(/active/);
      await expect(page.locator('[data-testid="step-indicator-2"]')).not.toHaveClass(/active/);
      
      // Complete step 1
      await profileHelpers.fillField('[data-testid="company-name-input"]', BUSINESS_PROFILES.TECH_STARTUP.companyName);
      await page.selectOption('[data-testid="industry-select"]', BUSINESS_PROFILES.TECH_STARTUP.industry);
      await page.selectOption('[data-testid="employee-count-select"]', BUSINESS_PROFILES.TECH_STARTUP.employeeCount);
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      // Should show step 2 as active
      await expect(page.locator('[data-testid="step-indicator-2"]')).toHaveClass(/active/);
      await expect(page.locator('[data-testid="step-indicator-1"]')).toHaveClass(/completed/);
    });
  });

  test.describe('Profile Management', () => {
    test.beforeEach(async ({ page }) => {
      // Complete profile setup first
      await profileHelpers.completeProfileSetup(BUSINESS_PROFILES.TECH_STARTUP);
    });

    test('should view existing business profile', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile');
      
      // Should show profile information
      await expect(page.locator('[data-testid="company-name"]')).toContainText(BUSINESS_PROFILES.TECH_STARTUP.companyName);
      await expect(page.locator('[data-testid="industry"]')).toContainText(BUSINESS_PROFILES.TECH_STARTUP.industry);
      await expect(page.locator('[data-testid="employee-count"]')).toContainText(BUSINESS_PROFILES.TECH_STARTUP.employeeCount);
    });

    test('should edit business profile', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile');
      
      // Click edit button
      await profileHelpers.clickAndWait('[data-testid="edit-profile-button"]');
      
      // Should show edit form
      await expect(page.locator('[data-testid="edit-profile-form"]')).toBeVisible();
      
      // Update company name
      const newCompanyName = 'Updated Company Name';
      await profileHelpers.fillField('[data-testid="company-name-input"]', newCompanyName);
      
      // Save changes
      await profileHelpers.clickAndWait('[data-testid="save-button"]');
      
      // Should show success message
      await profileHelpers.waitForToast('Profile updated successfully');
      
      // Should show updated information
      await expect(page.locator('[data-testid="company-name"]')).toContainText(newCompanyName);
    });

    test('should handle multiple business profiles', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile');
      
      // Create additional profile
      await profileHelpers.clickAndWait('[data-testid="add-profile-button"]');
      
      await profileHelpers.completeProfileSetup(BUSINESS_PROFILES.FINANCIAL_SERVICES);
      
      // Should show profile selector
      await expect(page.locator('[data-testid="profile-selector"]')).toBeVisible();
      
      // Should list both profiles
      await expect(page.locator('[data-testid="profile-list"]')).toContainText(BUSINESS_PROFILES.TECH_STARTUP.companyName);
      await expect(page.locator('[data-testid="profile-list"]')).toContainText(BUSINESS_PROFILES.FINANCIAL_SERVICES.companyName);
    });

    test('should switch between business profiles', async ({ page }) => {
      // Assuming multiple profiles exist
      await profileHelpers.navigateAndWait('/business-profile');
      
      // Switch to different profile
      await page.click('[data-testid="profile-selector"]');
      await page.click('[data-testid="profile-option-2"]');
      
      // Should update dashboard context
      await profileHelpers.navigateAndWait('/dashboard');
      
      // Should show data for selected profile
      await expect(page.locator('[data-testid="active-profile-name"]')).toBeVisible();
    });

    test('should delete business profile', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile');
      
      // Click delete button
      await profileHelpers.clickAndWait('[data-testid="delete-profile-button"]');
      
      // Should show confirmation dialog
      await expect(page.locator('[data-testid="delete-confirmation-dialog"]')).toBeVisible();
      
      // Confirm deletion
      await profileHelpers.clickAndWait('[data-testid="confirm-delete-button"]');
      
      // Should show success message
      await profileHelpers.waitForToast('Profile deleted successfully');
      
      // Should redirect to profile setup or dashboard
      await expect(page).toHaveURL(/\/(business-profile\/setup|dashboard)/);
    });
  });

  test.describe('Data Types and Compliance', () => {
    test('should configure data types and show relevant frameworks', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Complete step 1
      await profileHelpers.fillField('[data-testid="company-name-input"]', BUSINESS_PROFILES.HEALTHCARE.companyName);
      await page.selectOption('[data-testid="industry-select"]', BUSINESS_PROFILES.HEALTHCARE.industry);
      await page.selectOption('[data-testid="employee-count-select"]', BUSINESS_PROFILES.HEALTHCARE.employeeCount);
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      // Step 2: Select health data
      await page.check('[data-testid="data-type-health_data"]');
      await page.check('[data-testid="data-type-personal_data"]');
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      // Should show relevant compliance frameworks
      await expect(page.locator('[data-testid="recommended-frameworks"]')).toContainText('GDPR');
      await expect(page.locator('[data-testid="recommended-frameworks"]')).toContainText('HIPAA');
    });

    test('should show industry-specific recommendations', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Select financial services industry
      await profileHelpers.fillField('[data-testid="company-name-input"]', BUSINESS_PROFILES.FINANCIAL_SERVICES.companyName);
      await page.selectOption('[data-testid="industry-select"]', BUSINESS_PROFILES.FINANCIAL_SERVICES.industry);
      await page.selectOption('[data-testid="employee-count-select"]', BUSINESS_PROFILES.FINANCIAL_SERVICES.employeeCount);
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      // Should show financial data options
      await expect(page.locator('[data-testid="data-type-financial_data"]')).toBeVisible();
      await expect(page.locator('[data-testid="data-type-payment_data"]')).toBeVisible();
      
      // Select financial data types
      await page.check('[data-testid="data-type-financial_data"]');
      await page.check('[data-testid="data-type-payment_data"]');
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      // Should recommend financial compliance frameworks
      await expect(page.locator('[data-testid="recommended-frameworks"]')).toContainText('PCI DSS');
      await expect(page.locator('[data-testid="recommended-frameworks"]')).toContainText('SOX');
    });
  });

  test.describe('Profile Validation', () => {
    test('should validate company name format', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Try invalid company name
      await profileHelpers.fillField('[data-testid="company-name-input"]', 'a'); // Too short
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      await expect(page.locator('[data-testid="company-name-error"]')).toContainText('Company name must be at least 2 characters');
    });

    test('should validate employee count selection', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      await profileHelpers.fillField('[data-testid="company-name-input"]', BUSINESS_PROFILES.TECH_STARTUP.companyName);
      await page.selectOption('[data-testid="industry-select"]', BUSINESS_PROFILES.TECH_STARTUP.industry);
      // Don't select employee count
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      await expect(page.locator('[data-testid="employee-count-error"]')).toBeVisible();
    });

    test('should require at least one data type selection', async ({ page }) => {
      await profileHelpers.navigateAndWait('/business-profile/setup');
      
      // Complete step 1
      await profileHelpers.fillField('[data-testid="company-name-input"]', BUSINESS_PROFILES.TECH_STARTUP.companyName);
      await page.selectOption('[data-testid="industry-select"]', BUSINESS_PROFILES.TECH_STARTUP.industry);
      await page.selectOption('[data-testid="employee-count-select"]', BUSINESS_PROFILES.TECH_STARTUP.employeeCount);
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      // Try to proceed without selecting data types
      await profileHelpers.clickAndWait('[data-testid="next-button"]');
      
      await expect(page.locator('[data-testid="data-types-error"]')).toContainText('Please select at least one data type');
    });
  });
});
