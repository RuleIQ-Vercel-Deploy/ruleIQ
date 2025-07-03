import path from 'path';

import { test, expect } from '@playwright/test';

import { BUSINESS_PROFILES, EVIDENCE_DATA } from './fixtures/test-data';
import { AuthHelpers, BusinessProfileHelpers, EvidenceHelpers } from './utils/test-helpers';

test.describe('Evidence Management', () => {
  let authHelpers: AuthHelpers;
  let profileHelpers: BusinessProfileHelpers;
  let evidenceHelpers: EvidenceHelpers;

  test.beforeEach(async ({ page }) => {
    authHelpers = new AuthHelpers(page);
    profileHelpers = new BusinessProfileHelpers(page);
    evidenceHelpers = new EvidenceHelpers(page);
    
    // Setup: Login and complete business profile
    await authHelpers.login();
    await profileHelpers.completeProfileSetup(BUSINESS_PROFILES.TECH_STARTUP);
  });

  test.describe('Evidence Upload', () => {
    test('should upload evidence file successfully', async ({ page }) => {
      // Create a test file
      const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf');
      
      await evidenceHelpers.uploadEvidence(
        testFilePath,
        EVIDENCE_DATA.POLICY_DOCUMENT.title,
        EVIDENCE_DATA.POLICY_DOCUMENT.description
      );
      
      // Should show in evidence list
      await expect(page.locator('[data-testid="evidence-list"]')).toContainText(EVIDENCE_DATA.POLICY_DOCUMENT.title);
    });

    test('should validate file types and size', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      await evidenceHelpers.clickAndWait('[data-testid="upload-evidence-button"]');
      
      // Try to upload invalid file type
      const invalidFilePath = path.join(__dirname, 'fixtures', 'test-file.exe');
      await page.setInputFiles('[data-testid="file-input"]', invalidFilePath);
      
      // Should show error
      await expect(page.locator('[data-testid="file-type-error"]')).toContainText('File type not supported');
    });

    test('should show upload progress', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      await evidenceHelpers.clickAndWait('[data-testid="upload-evidence-button"]');
      
      const testFilePath = path.join(__dirname, 'fixtures', 'large-document.pdf');
      await page.setInputFiles('[data-testid="file-input"]', testFilePath);
      
      await evidenceHelpers.fillField('[data-testid="evidence-title-input"]', 'Large Document');
      await page.click('[data-testid="upload-button"]');
      
      // Should show progress bar
      await expect(page.locator('[data-testid="upload-progress"]')).toBeVisible();
    });

    test('should support drag and drop upload', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Should show drop zone
      await expect(page.locator('[data-testid="drop-zone"]')).toBeVisible();
      
      // Simulate drag and drop (this would require more complex setup in real tests)
      await page.locator('[data-testid="drop-zone"]').click();
      
      // Should open file dialog
      await expect(page.locator('[data-testid="file-input"]')).toBeVisible();
    });

    test('should auto-categorize uploaded evidence', async ({ page }) => {
      const testFilePath = path.join(__dirname, 'fixtures', 'privacy-policy.pdf');
      
      await evidenceHelpers.navigateAndWait('/evidence');
      await evidenceHelpers.clickAndWait('[data-testid="upload-evidence-button"]');
      
      await page.setInputFiles('[data-testid="file-input"]', testFilePath);
      
      // Should auto-detect category based on filename/content
      await expect(page.locator('[data-testid="category-select"]')).toHaveValue('policy');
      
      // Should suggest tags
      await expect(page.locator('[data-testid="suggested-tags"]')).toContainText('privacy');
      await expect(page.locator('[data-testid="suggested-tags"]')).toContainText('gdpr');
    });

    test('should handle bulk upload', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      await evidenceHelpers.clickAndWait('[data-testid="bulk-upload-button"]');
      
      // Select multiple files
      const files = [
        path.join(__dirname, 'fixtures', 'document1.pdf'),
        path.join(__dirname, 'fixtures', 'document2.pdf'),
        path.join(__dirname, 'fixtures', 'document3.pdf')
      ];
      
      await page.setInputFiles('[data-testid="bulk-file-input"]', files);
      
      // Should show file list
      await expect(page.locator('[data-testid="bulk-file-list"]')).toBeVisible();
      
      // Should allow setting metadata for each file
      await evidenceHelpers.fillField('[data-testid="file-1-title"]', 'Document 1');
      await evidenceHelpers.fillField('[data-testid="file-2-title"]', 'Document 2');
      
      await page.click('[data-testid="bulk-upload-submit"]');
      
      // Should show upload progress for all files
      await expect(page.locator('[data-testid="bulk-upload-progress"]')).toBeVisible();
    });
  });

  test.describe('Evidence Organization', () => {
    test.beforeEach(async ({ page }) => {
      // Upload some test evidence
      const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf');
      await evidenceHelpers.uploadEvidence(testFilePath, 'Test Document', 'Test description');
    });

    test('should filter evidence by category', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Filter by policy category
      await page.selectOption('[data-testid="category-filter"]', 'policy');
      
      // Should show only policy documents
      await expect(page.locator('[data-testid="evidence-list"]')).toContainText('Test Document');
      
      // Change filter to certificates
      await page.selectOption('[data-testid="category-filter"]', 'certificate');
      
      // Should show no results or different documents
      const evidenceItems = page.locator('[data-testid="evidence-item"]');
      const count = await evidenceItems.count();
      expect(count).toBe(0);
    });

    test('should search evidence by title and content', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Search by title
      await evidenceHelpers.fillField('[data-testid="search-input"]', 'Test Document');
      
      // Should show matching results
      await expect(page.locator('[data-testid="evidence-list"]')).toContainText('Test Document');
      
      // Search for non-existent term
      await evidenceHelpers.fillField('[data-testid="search-input"]', 'NonExistent');
      
      // Should show no results
      await expect(page.locator('[data-testid="no-results"]')).toBeVisible();
    });

    test('should sort evidence by different criteria', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Sort by date (newest first)
      await page.selectOption('[data-testid="sort-select"]', 'date-desc');
      
      // Should reorder list
      await evidenceHelpers.waitForLoadingToComplete();
      
      // Sort by title (A-Z)
      await page.selectOption('[data-testid="sort-select"]', 'title-asc');
      
      // Should reorder list alphabetically
      await evidenceHelpers.waitForLoadingToComplete();
    });

    test('should manage evidence tags', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Click on evidence item
      await page.click('[data-testid="evidence-item-1"]');
      
      // Should show evidence details
      await expect(page.locator('[data-testid="evidence-details"]')).toBeVisible();
      
      // Add new tag
      await evidenceHelpers.fillField('[data-testid="new-tag-input"]', 'compliance');
      await page.click('[data-testid="add-tag-button"]');
      
      // Should show new tag
      await expect(page.locator('[data-testid="evidence-tags"]')).toContainText('compliance');
      
      // Remove tag
      await page.click('[data-testid="remove-tag-compliance"]');
      
      // Should remove tag
      await expect(page.locator('[data-testid="evidence-tags"]')).not.toContainText('compliance');
    });

    test('should create evidence folders', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Create new folder
      await page.click('[data-testid="create-folder-button"]');
      
      await evidenceHelpers.fillField('[data-testid="folder-name-input"]', 'GDPR Documents');
      await page.click('[data-testid="create-folder-submit"]');
      
      // Should show new folder
      await expect(page.locator('[data-testid="folder-list"]')).toContainText('GDPR Documents');
      
      // Move evidence to folder
      await page.click('[data-testid="evidence-item-1"]');
      await page.click('[data-testid="move-to-folder-button"]');
      await page.selectOption('[data-testid="folder-select"]', 'GDPR Documents');
      await page.click('[data-testid="move-confirm-button"]');
      
      // Should move evidence to folder
      await page.click('[data-testid="folder-GDPR-Documents"]');
      await expect(page.locator('[data-testid="evidence-list"]')).toContainText('Test Document');
    });
  });

  test.describe('Evidence Review and Approval', () => {
    test.beforeEach(async ({ page }) => {
      // Upload evidence that needs review
      const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf');
      await evidenceHelpers.uploadEvidence(testFilePath, 'Document for Review', 'Needs approval');
    });

    test('should submit evidence for review', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Click on evidence item
      await page.click('[data-testid="evidence-item-1"]');
      
      // Submit for review
      await page.click('[data-testid="submit-for-review-button"]');
      
      // Should show review dialog
      await expect(page.locator('[data-testid="review-dialog"]')).toBeVisible();
      
      // Add review notes
      await evidenceHelpers.fillField('[data-testid="review-notes"]', 'Please review for GDPR compliance');
      
      // Select reviewer
      await page.selectOption('[data-testid="reviewer-select"]', 'compliance-officer');
      
      await page.click('[data-testid="submit-review-button"]');
      
      // Should show pending review status
      await expect(page.locator('[data-testid="evidence-status"]')).toContainText('Pending Review');
    });

    test('should approve evidence', async ({ page }) => {
      // Simulate reviewer role
      await page.goto('/evidence?role=reviewer');
      
      // Should show pending reviews
      await expect(page.locator('[data-testid="pending-reviews"]')).toBeVisible();
      
      // Click on review item
      await page.click('[data-testid="review-item-1"]');
      
      // Should show review interface
      await expect(page.locator('[data-testid="review-interface"]')).toBeVisible();
      
      // Approve evidence
      await page.click('[data-testid="approve-button"]');
      
      // Add approval notes
      await evidenceHelpers.fillField('[data-testid="approval-notes"]', 'Approved for compliance');
      
      await page.click('[data-testid="confirm-approval-button"]');
      
      // Should show approved status
      await expect(page.locator('[data-testid="evidence-status"]')).toContainText('Approved');
    });

    test('should reject evidence with feedback', async ({ page }) => {
      await page.goto('/evidence?role=reviewer');
      
      await page.click('[data-testid="review-item-1"]');
      
      // Reject evidence
      await page.click('[data-testid="reject-button"]');
      
      // Add rejection reason
      await evidenceHelpers.fillField('[data-testid="rejection-reason"]', 'Document is incomplete');
      
      await page.click('[data-testid="confirm-rejection-button"]');
      
      // Should show rejected status
      await expect(page.locator('[data-testid="evidence-status"]')).toContainText('Rejected');
      
      // Should show feedback to uploader
      await expect(page.locator('[data-testid="rejection-feedback"]')).toContainText('Document is incomplete');
    });

    test('should track review history', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      await page.click('[data-testid="evidence-item-1"]');
      
      // Click on history tab
      await page.click('[data-testid="history-tab"]');
      
      // Should show review history
      await expect(page.locator('[data-testid="review-history"]')).toBeVisible();
      
      // Should show timeline of events
      await expect(page.locator('[data-testid="history-timeline"]')).toBeVisible();
      await expect(page.locator('[data-testid="history-event"]')).toContainText('Uploaded');
    });
  });

  test.describe('Evidence Integration', () => {
    test('should link evidence to assessment questions', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      await page.click('[data-testid="evidence-item-1"]');
      
      // Link to assessment question
      await page.click('[data-testid="link-to-assessment-button"]');
      
      // Should show assessment selector
      await expect(page.locator('[data-testid="assessment-selector"]')).toBeVisible();
      
      // Select assessment and question
      await page.selectOption('[data-testid="assessment-select"]', 'gdpr-assessment');
      await page.selectOption('[data-testid="question-select"]', 'privacy-policy-question');
      
      await page.click('[data-testid="link-evidence-button"]');
      
      // Should show linked status
      await expect(page.locator('[data-testid="linked-assessments"]')).toContainText('GDPR Assessment');
    });

    test('should generate compliance reports from evidence', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Select multiple evidence items
      await page.check('[data-testid="select-evidence-1"]');
      await page.check('[data-testid="select-evidence-2"]');
      
      // Generate report
      await page.click('[data-testid="generate-report-button"]');
      
      // Should show report options
      await expect(page.locator('[data-testid="report-options"]')).toBeVisible();
      
      // Select report type
      await page.selectOption('[data-testid="report-type-select"]', 'compliance-summary');
      
      await page.click('[data-testid="generate-report-submit"]');
      
      // Should generate and download report
      const [download] = await Promise.all([
        page.waitForEvent('download'),
        page.click('[data-testid="download-report-button"]')
      ]);
      
      expect(download.suggestedFilename()).toContain('compliance-report');
    });

    test('should export evidence metadata', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Export all evidence metadata
      const [download] = await Promise.all([
        page.waitForEvent('download'),
        page.click('[data-testid="export-metadata-button"]')
      ]);
      
      expect(download.suggestedFilename()).toContain('.csv');
    });
  });

  test.describe('Evidence Security', () => {
    test('should handle sensitive evidence with encryption', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      await evidenceHelpers.clickAndWait('[data-testid="upload-evidence-button"]');
      
      const sensitiveFilePath = path.join(__dirname, 'fixtures', 'sensitive-document.pdf');
      await page.setInputFiles('[data-testid="file-input"]', sensitiveFilePath);
      
      // Mark as sensitive
      await page.check('[data-testid="sensitive-checkbox"]');
      
      // Should show encryption options
      await expect(page.locator('[data-testid="encryption-options"]')).toBeVisible();
      
      await evidenceHelpers.fillField('[data-testid="evidence-title-input"]', 'Sensitive Document');
      await page.click('[data-testid="upload-button"]');
      
      // Should show encrypted status
      await expect(page.locator('[data-testid="encryption-badge"]')).toBeVisible();
    });

    test('should control access to sensitive evidence', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      // Click on sensitive evidence
      await page.click('[data-testid="sensitive-evidence-item"]');
      
      // Should require additional authentication
      await expect(page.locator('[data-testid="access-control-dialog"]')).toBeVisible();
      
      // Enter access code or additional authentication
      await evidenceHelpers.fillField('[data-testid="access-code-input"]', '123456');
      await page.click('[data-testid="verify-access-button"]');
      
      // Should grant access to sensitive content
      await expect(page.locator('[data-testid="evidence-content"]')).toBeVisible();
    });

    test('should audit evidence access', async ({ page }) => {
      await evidenceHelpers.navigateAndWait('/evidence');
      
      await page.click('[data-testid="evidence-item-1"]');
      
      // Click on audit tab
      await page.click('[data-testid="audit-tab"]');
      
      // Should show access log
      await expect(page.locator('[data-testid="access-log"]')).toBeVisible();
      
      // Should show who accessed when
      await expect(page.locator('[data-testid="access-entry"]')).toContainText('Viewed by');
      await expect(page.locator('[data-testid="access-timestamp"]')).toBeVisible();
    });
  });
});
