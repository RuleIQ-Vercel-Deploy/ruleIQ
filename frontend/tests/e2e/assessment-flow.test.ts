import { test, expect } from '@playwright/test';

import { BUSINESS_PROFILES, ASSESSMENT_DATA } from './fixtures/test-data';
import { AuthHelpers, BusinessProfileHelpers, AssessmentHelpers } from './utils/test-helpers';

test.describe('Assessment Flow', () => {
  let authHelpers: AuthHelpers;
  let profileHelpers: BusinessProfileHelpers;
  let assessmentHelpers: AssessmentHelpers;

  test.beforeEach(async ({ page }) => {
    authHelpers = new AuthHelpers(page);
    profileHelpers = new BusinessProfileHelpers(page);
    assessmentHelpers = new AssessmentHelpers(page);
    
    // Setup: Login and complete business profile
    await authHelpers.login();
    await profileHelpers.completeProfileSetup(BUSINESS_PROFILES.TECH_STARTUP);
  });

  test.describe('Framework Selection', () => {
    test('should display available frameworks based on business profile', async ({ page }) => {
      await assessmentHelpers.navigateAndWait('/assessments');
      
      // Should show framework recommendations
      await expect(page.locator('[data-testid="recommended-frameworks"]')).toBeVisible();
      
      // Should show GDPR for tech startup with personal data
      await expect(page.locator('[data-testid="framework-GDPR"]')).toBeVisible();
      await expect(page.locator('[data-testid="framework-ISO27001"]')).toBeVisible();
    });

    test('should show framework details on selection', async ({ page }) => {
      await assessmentHelpers.navigateAndWait('/assessments');
      
      // Click on GDPR framework
      await page.click('[data-testid="framework-GDPR"]');
      
      // Should show framework details
      await expect(page.locator('[data-testid="framework-details"]')).toBeVisible();
      await expect(page.locator('[data-testid="framework-description"]')).toContainText('General Data Protection Regulation');
      await expect(page.locator('[data-testid="estimated-time"]')).toBeVisible();
      await expect(page.locator('[data-testid="question-count"]')).toBeVisible();
    });

    test('should allow framework filtering and search', async ({ page }) => {
      await assessmentHelpers.navigateAndWait('/assessments');
      
      // Filter by category
      await page.selectOption('[data-testid="category-filter"]', 'privacy');
      
      // Should show only privacy frameworks
      await expect(page.locator('[data-testid="framework-GDPR"]')).toBeVisible();
      await expect(page.locator('[data-testid="framework-ISO27001"]')).not.toBeVisible();
      
      // Search for specific framework
      await assessmentHelpers.fillField('[data-testid="framework-search"]', 'ISO');
      
      // Should show ISO frameworks
      await expect(page.locator('[data-testid="framework-ISO27001"]')).toBeVisible();
    });

    test('should show assessment mode options', async ({ page }) => {
      await assessmentHelpers.navigateAndWait('/assessments');
      await page.click('[data-testid="framework-GDPR"]');
      
      // Should show assessment mode options
      await expect(page.locator('[data-testid="mode-quick"]')).toBeVisible();
      await expect(page.locator('[data-testid="mode-comprehensive"]')).toBeVisible();
      
      // Select comprehensive mode
      await page.click('[data-testid="mode-comprehensive"]');
      
      // Should show mode details
      await expect(page.locator('[data-testid="mode-description"]')).toContainText('comprehensive');
    });
  });

  test.describe('Assessment Execution', () => {
    test('should start and complete a basic assessment', async ({ page }) => {
      await assessmentHelpers.startAssessment('GDPR');
      
      // Should show assessment interface
      await expect(page.locator('[data-testid="assessment-progress"]')).toBeVisible();
      await expect(page.locator('[data-testid="question-counter"]')).toBeVisible();
      
      // Answer questions
      await assessmentHelpers.answerQuestions(ASSESSMENT_DATA.GDPR_BASIC.questions);
      
      // Submit assessment
      await assessmentHelpers.submitAssessment();
      
      // Should show results
      await expect(page.locator('[data-testid="assessment-results"]')).toBeVisible();
      await expect(page.locator('[data-testid="compliance-score"]')).toBeVisible();
    });

    test('should show progress indicator during assessment', async ({ page }) => {
      await assessmentHelpers.startAssessment('GDPR');
      
      // Should show initial progress
      await expect(page.locator('[data-testid="progress-bar"]')).toHaveAttribute('aria-valuenow', '0');
      
      // Answer first question
      await page.click('[data-testid="question-1-answer-yes"]');
      await page.click('[data-testid="next-question-button"]');
      
      // Progress should update
      const progress = await page.locator('[data-testid="progress-bar"]').getAttribute('aria-valuenow');
      expect(parseInt(progress || '0')).toBeGreaterThan(0);
    });

    test('should allow navigation between questions', async ({ page }) => {
      await assessmentHelpers.startAssessment('GDPR');
      
      // Answer first question
      await page.click('[data-testid="question-1-answer-yes"]');
      await page.click('[data-testid="next-question-button"]');
      
      // Should be on question 2
      await expect(page.locator('[data-testid="question-2"]')).toBeVisible();
      
      // Go back to question 1
      await page.click('[data-testid="previous-question-button"]');
      
      // Should be on question 1 with answer preserved
      await expect(page.locator('[data-testid="question-1"]')).toBeVisible();
      await expect(page.locator('[data-testid="question-1-answer-yes"]')).toBeChecked();
    });

    test('should save progress and allow resuming', async ({ page }) => {
      await assessmentHelpers.startAssessment('GDPR');
      
      // Answer some questions
      await page.click('[data-testid="question-1-answer-yes"]');
      await page.click('[data-testid="next-question-button"]');
      await page.click('[data-testid="question-2-answer-no"]');
      
      // Navigate away
      await page.goto('/dashboard');
      
      // Return to assessments
      await assessmentHelpers.navigateAndWait('/assessments');
      
      // Should show option to resume
      await expect(page.locator('[data-testid="resume-assessment"]')).toBeVisible();
      
      // Resume assessment
      await page.click('[data-testid="resume-assessment"]');
      
      // Should be on question 2 with answer preserved
      await expect(page.locator('[data-testid="question-2"]')).toBeVisible();
      await expect(page.locator('[data-testid="question-2-answer-no"]')).toBeChecked();
    });

    test('should handle conditional questions', async ({ page }) => {
      await assessmentHelpers.startAssessment('GDPR');
      
      // Answer question that triggers conditional logic
      await page.click('[data-testid="question-1-answer-yes"]');
      await page.click('[data-testid="next-question-button"]');
      
      // Should show follow-up question
      await expect(page.locator('[data-testid="conditional-question"]')).toBeVisible();
      
      // Change answer to skip conditional
      await page.click('[data-testid="previous-question-button"]');
      await page.click('[data-testid="question-1-answer-no"]');
      await page.click('[data-testid="next-question-button"]');
      
      // Should skip conditional question
      await expect(page.locator('[data-testid="conditional-question"]')).not.toBeVisible();
    });

    test('should validate required questions', async ({ page }) => {
      await assessmentHelpers.startAssessment('GDPR');
      
      // Try to proceed without answering
      await page.click('[data-testid="next-question-button"]');
      
      // Should show validation error
      await expect(page.locator('[data-testid="question-error"]')).toContainText('Please select an answer');
      
      // Should not advance to next question
      await expect(page.locator('[data-testid="question-1"]')).toBeVisible();
    });
  });

  test.describe('Assessment Results', () => {
    test.beforeEach(async ({ page }) => {
      // Complete an assessment before each test
      await assessmentHelpers.startAssessment('GDPR');
      await assessmentHelpers.answerQuestions(ASSESSMENT_DATA.GDPR_BASIC.questions);
      await assessmentHelpers.submitAssessment();
    });

    test('should display comprehensive results', async ({ page }) => {
      // Should show overall score
      await expect(page.locator('[data-testid="overall-score"]')).toBeVisible();
      
      // Should show category breakdown
      await expect(page.locator('[data-testid="category-scores"]')).toBeVisible();
      
      // Should show recommendations
      await expect(page.locator('[data-testid="recommendations"]')).toBeVisible();
      
      // Should show action items
      await expect(page.locator('[data-testid="action-items"]')).toBeVisible();
    });

    test('should show detailed gap analysis', async ({ page }) => {
      // Click on gap analysis tab
      await page.click('[data-testid="gap-analysis-tab"]');
      
      // Should show gaps by category
      await expect(page.locator('[data-testid="gaps-by-category"]')).toBeVisible();
      
      // Should show priority levels
      await expect(page.locator('[data-testid="high-priority-gaps"]')).toBeVisible();
      await expect(page.locator('[data-testid="medium-priority-gaps"]')).toBeVisible();
      
      // Should show implementation timeline
      await expect(page.locator('[data-testid="implementation-timeline"]')).toBeVisible();
    });

    test('should generate action plan', async ({ page }) => {
      // Click generate action plan
      await page.click('[data-testid="generate-action-plan-button"]');
      
      // Should show action plan
      await expect(page.locator('[data-testid="action-plan"]')).toBeVisible();
      
      // Should show prioritized tasks
      await expect(page.locator('[data-testid="priority-tasks"]')).toBeVisible();
      
      // Should show estimated effort
      await expect(page.locator('[data-testid="estimated-effort"]')).toBeVisible();
    });

    test('should export results in multiple formats', async ({ page }) => {
      // Test PDF export
      const [pdfDownload] = await Promise.all([
        page.waitForEvent('download'),
        page.click('[data-testid="export-pdf-button"]')
      ]);
      
      expect(pdfDownload.suggestedFilename()).toContain('.pdf');
      
      // Test Excel export
      const [excelDownload] = await Promise.all([
        page.waitForEvent('download'),
        page.click('[data-testid="export-excel-button"]')
      ]);
      
      expect(excelDownload.suggestedFilename()).toContain('.xlsx');
    });

    test('should allow sharing results', async ({ page }) => {
      // Click share button
      await page.click('[data-testid="share-results-button"]');
      
      // Should show sharing options
      await expect(page.locator('[data-testid="share-dialog"]')).toBeVisible();
      
      // Should show link sharing
      await expect(page.locator('[data-testid="share-link"]')).toBeVisible();
      
      // Should show email sharing
      await expect(page.locator('[data-testid="share-email"]')).toBeVisible();
    });
  });

  test.describe('Assessment History', () => {
    test('should show assessment history', async ({ page }) => {
      await assessmentHelpers.navigateAndWait('/assessments/history');
      
      // Should show list of completed assessments
      await expect(page.locator('[data-testid="assessment-history-list"]')).toBeVisible();
      
      // Should show assessment details
      await expect(page.locator('[data-testid="assessment-date"]')).toBeVisible();
      await expect(page.locator('[data-testid="assessment-score"]')).toBeVisible();
      await expect(page.locator('[data-testid="assessment-framework"]')).toBeVisible();
    });

    test('should allow viewing historical results', async ({ page }) => {
      await assessmentHelpers.navigateAndWait('/assessments/history');
      
      // Click on historical assessment
      await page.click('[data-testid="view-assessment-1"]');
      
      // Should show historical results
      await expect(page.locator('[data-testid="historical-results"]')).toBeVisible();
      await expect(page.locator('[data-testid="assessment-date"]')).toBeVisible();
    });

    test('should compare assessments', async ({ page }) => {
      await assessmentHelpers.navigateAndWait('/assessments/history');
      
      // Select multiple assessments for comparison
      await page.check('[data-testid="select-assessment-1"]');
      await page.check('[data-testid="select-assessment-2"]');
      
      // Click compare button
      await page.click('[data-testid="compare-assessments-button"]');
      
      // Should show comparison view
      await expect(page.locator('[data-testid="assessment-comparison"]')).toBeVisible();
      await expect(page.locator('[data-testid="score-comparison"]')).toBeVisible();
      await expect(page.locator('[data-testid="improvement-trends"]')).toBeVisible();
    });
  });
});
