import { test, expect } from '@playwright/test';
import { TEST_USERS, EVIDENCE_DATA } from './fixtures/test-data';
import { TestSelectors } from './fixtures/test-selectors';
import path from 'path';

test.describe('Evidence Upload Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill(TestSelectors.auth.emailInput, TEST_USERS.VALID_USER.email);
    await page.fill(TestSelectors.auth.passwordInput, TEST_USERS.VALID_USER.password);
    await page.click(TestSelectors.auth.submitButton);
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Evidence Upload', () => {
    test('should upload PDF document successfully', async ({ page }) => {
      // Navigate to evidence page
      await page.getByRole('link', { name: /evidence/i }).click();
      await expect(page).toHaveURL(/.*evidence/);

      // Start upload process
      await page.click(TestSelectors.evidence.uploadButton);

      // Fill upload form
      await page.fill(TestSelectors.evidence.titleInput, EVIDENCE_DATA.POLICY_DOCUMENT.title);
      await page.fill(
        TestSelectors.evidence.descriptionInput,
        EVIDENCE_DATA.POLICY_DOCUMENT.description,
      );

      // Upload file
      const filePath = path.join(__dirname, '../fixtures/test-document.pdf');
      await page.setInputFiles(TestSelectors.evidence.fileInput, filePath);

      // Submit form
      await page.click(TestSelectors.evidence.submitButton);

      // Verify upload success
      await expect(page.locator('text=Evidence uploaded successfully')).toBeVisible();
      await expect(page.locator(`text=${EVIDENCE_DATA.POLICY_DOCUMENT.title}`)).toBeVisible();
    });

    test('should upload Excel spreadsheet', async ({ page }) => {
      await page.goto('/evidence');
      await page.click(TestSelectors.evidence.uploadButton);

      await page.fill(TestSelectors.evidence.titleInput, EVIDENCE_DATA.TRAINING_RECORD.title);
      await page.fill(
        TestSelectors.evidence.descriptionInput,
        EVIDENCE_DATA.TRAINING_RECORD.description,
      );

      // Create a temporary Excel file for testing
      const excelBuffer = Buffer.from('test,excel,data\nrow1,col1,col2\nrow2,col1,col2');
      await page.setInputFiles(TestSelectors.evidence.fileInput, {
        name: 'training-records.xlsx',
        mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        buffer: excelBuffer,
      });

      await page.click(TestSelectors.evidence.submitButton);

      await expect(page.locator('text=Evidence uploaded successfully')).toBeVisible();
    });

    test('should validate file type restrictions', async ({ page }) => {
      await page.goto('/evidence');
      await page.click(TestSelectors.evidence.uploadButton);

      // Try to upload invalid file type
      await page.setInputFiles(TestSelectors.evidence.fileInput, {
        name: 'malicious.exe',
        mimeType: 'application/x-msdownload',
        buffer: Buffer.from('fake executable'),
      });

      // Should show validation error
      await expect(page.locator('text=Invalid file type')).toBeVisible();
    });

    test('should validate file size limits', async ({ page }) => {
      await page.goto('/evidence');
      await page.click(TestSelectors.evidence.uploadButton);

      // Create a large file (simulate > 10MB)
      const largeBuffer = Buffer.alloc(11 * 1024 * 1024); // 11MB
      await page.setInputFiles(TestSelectors.evidence.fileInput, {
        name: 'large-file.pdf',
        mimeType: 'application/pdf',
        buffer: largeBuffer,
      });

      // Should show file size error
      await expect(page.locator('text=file too large')).toBeVisible();
    });

    test('should require title and description', async ({ page }) => {
      await page.goto('/evidence');
      await page.click(TestSelectors.evidence.uploadButton);

      // Try to submit without required fields
      const filePath = path.join(__dirname, '../fixtures/test-document.pdf');
      await page.setInputFiles(TestSelectors.evidence.fileInput, filePath);

      await page.click(TestSelectors.evidence.submitButton);

      // Should show validation errors
      await expect(page.locator('text=required')).toBeVisible();
    });
  });

  test.describe('Evidence Management', () => {
    test('should display evidence list', async ({ page }) => {
      await page.goto('/evidence');

      // Should show evidence list container
      await expect(page.locator(TestSelectors.evidence.evidenceList)).toBeVisible();

      // Should show evidence cards/items
      const evidenceCards = page.locator(TestSelectors.evidence.evidenceCard);
      await expect(evidenceCards.first()).toBeVisible();
    });

    test('should search evidence', async ({ page }) => {
      await page.goto('/evidence');

      // Search functionality
      const searchInput = page.locator('input[placeholder*="search" i]');
      await searchInput.fill('policy');

      // Should filter results
      await expect(page.locator('text=policy')).toBeVisible();
    });

    test('should filter evidence by category', async ({ page }) => {
      await page.goto('/evidence');

      // Filter by category
      await page.getByRole('button', { name: /filter/i }).click();
      await page.getByRole('checkbox', { name: /policy/i }).check();

      // Should show filtered results
      await expect(page.locator('text=Policy')).toBeVisible();
    });

    test('should sort evidence', async ({ page }) => {
      await page.goto('/evidence');

      // Sort functionality
      await page.getByRole('button', { name: /sort/i }).click();
      await page.getByRole('option', { name: /date|newest/i }).click();

      // Should maintain sort order
      const firstEvidence = page.locator(TestSelectors.evidence.evidenceCard).first();
      await expect(firstEvidence).toBeVisible();
    });
  });

  test.describe('Evidence Details', () => {
    test('should view evidence details', async ({ page }) => {
      await page.goto('/evidence');

      // Click on first evidence item
      await page.locator(TestSelectors.evidence.evidenceCard).first().click();

      // Should show evidence details
      await expect(page.locator('text=Evidence Details')).toBeVisible();
      await expect(page.locator('text=Download')).toBeVisible();
    });

    test('should download evidence', async ({ page }) => {
      await page.goto('/evidence');

      // Click on evidence item
      await page.locator(TestSelectors.evidence.evidenceCard).first().click();

      // Download file
      const downloadPromise = page.waitForEvent('download');
      await page.getByRole('button', { name: /download/i }).click();
      const download = await downloadPromise;

      expect(download.suggestedFilename()).toMatch(/\.pdf$/);
    });

    test('should edit evidence metadata', async ({ page }) => {
      await page.goto('/evidence');

      // Click on evidence item
      await page.locator(TestSelectors.evidence.evidenceCard).first().click();

      // Edit metadata
      await page.getByRole('button', { name: /edit/i }).click();

      const newTitle = 'Updated Evidence Title';
      await page.fill(TestSelectors.evidence.titleInput, newTitle);
      await page.click(TestSelectors.evidence.submitButton);

      // Verify update
      await expect(page.locator(`text=${newTitle}`)).toBeVisible();
    });

    test('should delete evidence', async ({ page }) => {
      await page.goto('/evidence');

      // Get initial count
      const initialCount = await page.locator(TestSelectors.evidence.evidenceCard).count();

      // Click on evidence item
      await page.locator(TestSelectors.evidence.evidenceCard).first().click();

      // Delete evidence
      await page.getByRole('button', { name: /delete/i }).click();
      await page.getByRole('button', { name: /confirm/i }).click();

      // Verify deletion
      await expect(page.locator('text=Evidence deleted')).toBeVisible();
      const newCount = await page.locator(TestSelectors.evidence.evidenceCard).count();
      expect(newCount).toBeLessThan(initialCount);
    });
  });

  test.describe('Evidence Tags and Categories', () => {
    test('should add tags to evidence', async ({ page }) => {
      await page.goto('/evidence');
      await page.click(TestSelectors.evidence.uploadButton);

      await page.fill(TestSelectors.evidence.titleInput, 'Test Evidence');
      await page.fill(TestSelectors.evidence.descriptionInput, 'Test Description');

      const filePath = path.join(__dirname, '../fixtures/test-document.pdf');
      await page.setInputFiles(TestSelectors.evidence.fileInput, filePath);

      // Add tags
      const tagsInput = page.locator('input[placeholder*="tag" i]');
      await tagsInput.fill('compliance, policy, test');
      await tagsInput.press('Enter');

      await page.click(TestSelectors.evidence.submitButton);

      // Verify tags are displayed
      await expect(page.locator('text=compliance')).toBeVisible();
      await expect(page.locator('text=policy')).toBeVisible();
    });

    test('should filter by multiple tags', async ({ page }) => {
      await page.goto('/evidence');

      // Add tag filter
      await page.getByRole('button', { name: /filter/i }).click();
      await page.getByRole('checkbox', { name: /compliance/i }).check();
      await page.getByRole('checkbox', { name: /policy/i }).check();

      // Should show evidence with both tags
      await expect(page.locator('text=compliance')).toBeVisible();
      await expect(page.locator('text=policy')).toBeVisible();
    });
  });
});
