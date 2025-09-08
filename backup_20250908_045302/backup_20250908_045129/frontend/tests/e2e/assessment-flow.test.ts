import { test, expect } from '@playwright/test';
import { TEST_USERS, ASSESSMENT_DATA } from './fixtures/test-data';
import { TestSelectors } from './fixtures/test-selectors';

test.describe('Assessment Wizard Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill(TestSelectors.auth.emailInput, TEST_USERS.VALID_USER.email);
    await page.fill(TestSelectors.auth.passwordInput, TEST_USERS.VALID_USER.password);
    await page.click(TestSelectors.auth.submitButton);
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Assessment Creation', () => {
    test('should create new GDPR assessment', async ({ page }) => {
      // Navigate to assessments
      await page.getByRole('link', { name: /assessments/i }).click();
      await expect(page).toHaveURL(/.*assessments/);

      // Start new assessment
      await page.click(TestSelectors.assessments.newAssessmentButton);

      // Select GDPR framework
      await page.getByRole('button', { name: /gdpr/i }).click();

      // Verify assessment started
      await expect(page).toHaveURL(/.*assessments\/new/);
      await expect(page.locator('text=GDPR Assessment')).toBeVisible();
    });

    test('should complete basic GDPR assessment', async ({ page }) => {
      // Navigate to new assessment
      await page.goto('/assessments/new');

      // Select GDPR framework
      await page.getByRole('button', { name: /gdpr/i }).click();

      // Complete assessment questions
      for (const question of ASSESSMENT_DATA.GDPR_BASIC.questions) {
        const questionElement = page.locator(`text=${question.question}`);
        await expect(questionElement).toBeVisible();

        // Select answer based on question type
        if (question.answer === 'yes') {
          await page.getByRole('radio', { name: /yes/i }).check();
        } else if (question.answer === 'no') {
          await page.getByRole('radio', { name: /no/i }).check();
        }

        // Navigate to next question
        const nextButton = page.getByRole('button', { name: /next|continue/i });
        if (await nextButton.isVisible()) {
          await nextButton.click();
        }
      }

      // Submit assessment
      await page.click(TestSelectors.assessments.submitAssessmentButton);

      // Verify completion
      await expect(page).toHaveURL(/.*results/);
      await expect(page.locator('text=Assessment Complete')).toBeVisible();
    });

    test('should save assessment progress', async ({ page }) => {
      await page.goto('/assessments/new');
      await page.getByRole('button', { name: /gdpr/i }).click();

      // Answer first question
      await page.getByRole('radio', { name: /yes/i }).first().check();

      // Navigate away and back
      await page.goto('/dashboard');
      await page.goBack();

      // Verify progress is saved (implementation depends on auto-save)
      await expect(page.getByRole('radio', { name: /yes/i }).first()).toBeChecked();
    });

    test('should handle assessment cancellation', async ({ page }) => {
      await page.goto('/assessments/new');
      await page.getByRole('button', { name: /gdpr/i }).click();

      // Start answering questions
      await page.getByRole('radio', { name: /yes/i }).first().check();

      // Cancel assessment
      await page.getByRole('button', { name: /cancel|exit/i }).click();

      // Confirm cancellation
      await page.getByRole('button', { name: /confirm|yes/i }).click();

      // Should redirect to assessments page
      await expect(page).toHaveURL(/.*assessments/);
    });
  });

  test.describe('Assessment Navigation', () => {
    test('should navigate between questions', async ({ page }) => {
      await page.goto('/assessments/new');
      await page.getByRole('button', { name: /iso 27001/i }).click();

      // Answer first question
      await page.getByRole('radio', { name: /yes/i }).first().check();

      // Go to next question
      await page.getByRole('button', { name: /next/i }).click();

      // Verify we're on question 2
      await expect(page.locator('text=2 of')).toBeVisible();

      // Go back to previous question
      await page.getByRole('button', { name: /previous|back/i }).click();

      // Verify we're back on question 1
      await expect(page.locator('text=1 of')).toBeVisible();
    });

    test('should show progress indicator', async ({ page }) => {
      await page.goto('/assessments/new');
      await page.getByRole('button', { name: /gdpr/i }).click();

      // Check progress bar exists
      await expect(page.locator('[class*="progress"]')).toBeVisible();

      // Check progress updates
      const progressText = await page.locator('[class*="progress"]').textContent();
      expect(progressText).toContain('1');
    });
  });

  test.describe('Assessment Validation', () => {
    test('should validate required questions', async ({ page }) => {
      await page.goto('/assessments/new');
      await page.getByRole('button', { name: /gdpr/i }).click();

      // Try to proceed without answering
      await page.getByRole('button', { name: /next/i }).click();

      // Should show validation error
      await expect(page.locator('text=required')).toBeVisible();
    });

    test('should allow skipping optional questions', async ({ page }) => {
      await page.goto('/assessments/new');
      await page.getByRole('button', { name: /iso 27001/i }).click();

      // Skip optional question
      await page.getByRole('button', { name: /next|skip/i }).click();

      // Should proceed to next question
      await expect(page.locator('text=2 of')).toBeVisible();
    });
  });

  test.describe('Assessment Results', () => {
    test('should display results after completion', async ({ page }) => {
      await page.goto('/assessments/new');
      await page.getByRole('button', { name: /gdpr/i }).click();

      // Complete all questions
      for (const question of ASSESSMENT_DATA.GDPR_BASIC.questions) {
        if (question.answer === 'yes') {
          await page.getByRole('radio', { name: /yes/i }).check();
        }

        const nextButton = page.getByRole('button', { name: /next|continue|submit/i });
        if (await nextButton.isVisible()) {
          await nextButton.click();
        }
      }

      // Verify results page
      await expect(page).toHaveURL(/.*results/);
      await expect(page.locator('text=Assessment Results')).toBeVisible();
      await expect(page.locator('[class*="score"]')).toBeVisible();
    });

    test('should allow downloading results', async ({ page }) => {
      // Complete an assessment first
      await page.goto('/assessments/new');
      await page.getByRole('button', { name: /gdpr/i }).click();

      for (const question of ASSESSMENT_DATA.GDPR_BASIC.questions) {
        if (question.answer === 'yes') {
          await page.getByRole('radio', { name: /yes/i }).check();
        }

        const nextButton = page.getByRole('button', { name: /next|continue|submit/i });
        if (await nextButton.isVisible()) {
          await nextButton.click();
        }
      }

      // Download results
      const downloadPromise = page.waitForEvent('download');
      await page.getByRole('button', { name: /download|export/i }).click();
      const download = await downloadPromise;

      expect(download.suggestedFilename()).toMatch(/assessment-results.*\.pdf/);
    });
  });

  test.describe('Assessment History', () => {
    test('should display completed assessments', async ({ page }) => {
      await page.goto('/assessments');

      // Should show assessment list
      await expect(
        page.locator('[class*="assessment-card"], [class*="assessment-item"]'),
      ).toBeVisible();

      // Should show assessment status
      await expect(page.locator('text=Completed')).toBeVisible();
    });

    test('should allow viewing assessment details', async ({ page }) => {
      await page.goto('/assessments');

      // Click on first assessment
      await page.locator('[class*="assessment-card"]').first().click();

      // Should show assessment details
      await expect(page).toHaveURL(/.*assessments\/[a-f0-9-]+/);
      await expect(page.locator('text=Assessment Details')).toBeVisible();
    });
  });
});
