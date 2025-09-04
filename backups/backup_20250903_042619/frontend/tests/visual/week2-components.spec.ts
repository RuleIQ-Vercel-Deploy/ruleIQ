import { test, expect } from '@playwright/test';

// Visual regression tests for Week 2 components
test.describe('Week 2 Components Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to component showcase page
    await page.goto('/showcase/components');
  });

  test.describe('Form Controls', () => {
    test('Input component states', async ({ page }) => {
      // Default state
      await expect(page.locator('[data-testid="input-default"]')).toHaveScreenshot(
        'input-default.png',
      );

      // Focused state
      await page.locator('[data-testid="input-default"]').focus();
      await expect(page.locator('[data-testid="input-default"]')).toHaveScreenshot(
        'input-focused.png',
      );

      // Error state
      await expect(page.locator('[data-testid="input-error"]')).toHaveScreenshot('input-error.png');

      // Success state
      await expect(page.locator('[data-testid="input-success"]')).toHaveScreenshot(
        'input-success.png',
      );

      // Disabled state
      await expect(page.locator('[data-testid="input-disabled"]')).toHaveScreenshot(
        'input-disabled.png',
      );
    });

    test('Select component states', async ({ page }) => {
      // Closed state
      await expect(page.locator('[data-testid="select-default"]')).toHaveScreenshot(
        'select-closed.png',
      );

      // Open state
      await page.locator('[data-testid="select-default"]').click();
      await expect(page.locator('[role="listbox"]')).toHaveScreenshot('select-open.png');

      // Error state
      await expect(page.locator('[data-testid="select-error"]')).toHaveScreenshot(
        'select-error.png',
      );
    });

    test('Checkbox component states', async ({ page }) => {
      // Unchecked
      await expect(page.locator('[data-testid="checkbox-default"]')).toHaveScreenshot(
        'checkbox-unchecked.png',
      );

      // Checked
      await page.locator('[data-testid="checkbox-default"]').click();
      await expect(page.locator('[data-testid="checkbox-default"]')).toHaveScreenshot(
        'checkbox-checked.png',
      );

      // Focus state
      await page.locator('[data-testid="checkbox-focus"]').focus();
      await expect(page.locator('[data-testid="checkbox-focus"]')).toHaveScreenshot(
        'checkbox-focused.png',
      );

      // Error state
      await expect(page.locator('[data-testid="checkbox-error"]')).toHaveScreenshot(
        'checkbox-error.png',
      );
    });

    test('Radio group component', async ({ page }) => {
      const radioGroup = page.locator('[data-testid="radio-group"]');

      // Default state
      await expect(radioGroup).toHaveScreenshot('radio-group-default.png');

      // Selected state
      await page.locator('[data-testid="radio-option-1"]').click();
      await expect(radioGroup).toHaveScreenshot('radio-group-selected.png');

      // Focus state
      await page.locator('[data-testid="radio-option-2"]').focus();
      await expect(radioGroup).toHaveScreenshot('radio-group-focused.png');
    });
  });

  test.describe('Card Components', () => {
    test('Basic card variations', async ({ page }) => {
      // Default card
      await expect(page.locator('[data-testid="card-default"]')).toHaveScreenshot(
        'card-default.png',
      );

      // Hover state
      await page.locator('[data-testid="card-hover"]').hover();
      await expect(page.locator('[data-testid="card-hover"]')).toHaveScreenshot('card-hover.png');

      // With all sections
      await expect(page.locator('[data-testid="card-complete"]')).toHaveScreenshot(
        'card-complete.png',
      );
    });

    test('Assessment card states', async ({ page }) => {
      // Not started
      await expect(page.locator('[data-testid="assessment-not-started"]')).toHaveScreenshot(
        'assessment-card-not-started.png',
      );

      // In progress
      await expect(page.locator('[data-testid="assessment-in-progress"]')).toHaveScreenshot(
        'assessment-card-in-progress.png',
      );

      // Completed
      await expect(page.locator('[data-testid="assessment-completed"]')).toHaveScreenshot(
        'assessment-card-completed.png',
      );

      // Expired
      await expect(page.locator('[data-testid="assessment-expired"]')).toHaveScreenshot(
        'assessment-card-expired.png',
      );
    });
  });

  test.describe('Table Component', () => {
    test('Table with all features', async ({ page }) => {
      const table = page.locator('[data-testid="table-default"]');

      // Default state
      await expect(table).toHaveScreenshot('table-default.png');

      // Row hover
      await page.locator('tr').nth(2).hover();
      await expect(table).toHaveScreenshot('table-row-hover.png');

      // Selected row
      await page.locator('tr').nth(3).click();
      await expect(table).toHaveScreenshot('table-row-selected.png');
    });

    test('Responsive table - mobile view', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Horizontal scroll table
      await expect(page.locator('[data-testid="table-scroll"]')).toHaveScreenshot(
        'table-mobile-scroll.png',
      );

      // Stacked layout table
      await expect(page.locator('[data-testid="table-stacked"]')).toHaveScreenshot(
        'table-mobile-stacked.png',
      );
    });
  });

  test.describe('Color Contrast', () => {
    test('All components together', async ({ page }) => {
      await expect(page.locator('[data-testid="all-components"]')).toHaveScreenshot(
        'all-components.png',
        {
          animations: 'disabled',
        },
      );
    });
  });

  test.describe('Dark Mode Compatibility', () => {
    test('Components in dark mode', async ({ page }) => {
      // Toggle dark mode
      await page.locator('[data-testid="theme-toggle"]').click();

      // Wait for transition
      await page.waitForTimeout(500);

      // Take screenshots of key components
      await expect(page.locator('[data-testid="dark-form-controls"]')).toHaveScreenshot(
        'dark-form-controls.png',
      );
      await expect(page.locator('[data-testid="dark-cards"]')).toHaveScreenshot('dark-cards.png');
      await expect(page.locator('[data-testid="dark-table"]')).toHaveScreenshot('dark-table.png');
    });
  });

  test.describe('Responsive Breakpoints', () => {
    const breakpoints = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1440, height: 900 },
    ];

    for (const breakpoint of breakpoints) {
      test(`Components at ${breakpoint.name} breakpoint`, async ({ page }) => {
        await page.setViewportSize({ width: breakpoint.width, height: breakpoint.height });

        await expect(page.locator('[data-testid="responsive-showcase"]')).toHaveScreenshot(
          `components-${breakpoint.name}.png`,
          { fullPage: true },
        );
      });
    }
  });
});
