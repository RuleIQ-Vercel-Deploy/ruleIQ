import { test, expect } from '@playwright/test';
import { TestHelpers } from '../e2e/utils/test-helpers';

/**
 * Visual regression tests for individual components
 * Tests component variants, states, and responsive behavior
 */

test.describe('Component Visual Regression Tests', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test.describe('Button Component Variants', () => {
    const buttonVariants = ['primary', 'secondary', 'destructive', 'outline', 'ghost', 'link'];
    const buttonSizes = ['default', 'sm', 'lg', 'icon'];

    for (const variant of buttonVariants) {
      for (const size of buttonSizes) {
        test(`button - ${variant} variant - ${size} size`, async ({ page }) => {
          await helpers.navigateAndWait('/components');
          
          const button = page.locator(`[data-testid="button-${variant}-${size}"]`);
          
          // Normal state
          await expect(button).toHaveScreenshot(`button-${variant}-${size}-normal.png`);
          
          // Skip hover/focus for icon size as it might not be interactive
          if (size !== 'icon') {
            // Hover state
            await button.hover();
            await expect(button).toHaveScreenshot(`button-${variant}-${size}-hover.png`);
            
            // Focus state
            await button.focus();
            await expect(button).toHaveScreenshot(`button-${variant}-${size}-focus.png`);
          }
          
          // Disabled state
          const disabledButton = page.locator(`[data-testid="button-${variant}-${size}-disabled"]`);
          await expect(disabledButton).toHaveScreenshot(`button-${variant}-${size}-disabled.png`);
        });
      }
    }

    test('button with loading state', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const loadingButton = page.locator('[data-testid="button-loading"]');
      await expect(loadingButton).toHaveScreenshot('button-loading.png');
    });

    test('button with icon', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const iconButton = page.locator('[data-testid="button-with-icon"]');
      await expect(iconButton).toHaveScreenshot('button-with-icon.png');
    });
  });

  test.describe('Form Components', () => {
    test('input field variants', async ({ page }) => {
      await helpers.navigateAndWait('/forms');
      
      // Text input
      const textInput = page.locator('[data-testid="input-text"]');
      await expect(textInput).toHaveScreenshot('input-text-empty.png');
      
      await textInput.focus();
      await expect(textInput).toHaveScreenshot('input-text-focused.png');
      
      await textInput.fill('Test content');
      await expect(textInput).toHaveScreenshot('input-text-filled.png');
      
      // Error state
      const errorInput = page.locator('[data-testid="input-error"]');
      await expect(errorInput).toHaveScreenshot('input-error.png');
      
      // Disabled state
      const disabledInput = page.locator('[data-testid="input-disabled"]');
      await expect(disabledInput).toHaveScreenshot('input-disabled.png');
    });

    test('select dropdown', async ({ page }) => {
      await helpers.navigateAndWait('/forms');
      
      const select = page.locator('[data-testid="select-framework"]');
      
      // Closed state
      await expect(select).toHaveScreenshot('select-closed.png');
      
      // Open state
      await select.click();
      await page.waitForTimeout(300); // Wait for animation
      await expect(page.locator('[data-testid="select-options"]')).toHaveScreenshot('select-open.png');
    });

    test('checkbox states', async ({ page }) => {
      await helpers.navigateAndWait('/forms');
      
      const checkbox = page.locator('[data-testid="checkbox-default"]');
      
      // Unchecked
      await expect(checkbox).toHaveScreenshot('checkbox-unchecked.png');
      
      // Checked
      await checkbox.click();
      await expect(checkbox).toHaveScreenshot('checkbox-checked.png');
      
      // Disabled
      const disabledCheckbox = page.locator('[data-testid="checkbox-disabled"]');
      await expect(disabledCheckbox).toHaveScreenshot('checkbox-disabled.png');
    });

    test('radio group', async ({ page }) => {
      await helpers.navigateAndWait('/forms');
      
      const radioGroup = page.locator('[data-testid="radio-group"]');
      await expect(radioGroup).toHaveScreenshot('radio-group.png');
      
      // Select an option
      await page.locator('[data-testid="radio-option-1"]').click();
      await expect(radioGroup).toHaveScreenshot('radio-group-selected.png');
    });

    test('switch component', async ({ page }) => {
      await helpers.navigateAndWait('/forms');
      
      const switchComponent = page.locator('[data-testid="switch-default"]');
      
      // Off state
      await expect(switchComponent).toHaveScreenshot('switch-off.png');
      
      // On state
      await switchComponent.click();
      await expect(switchComponent).toHaveScreenshot('switch-on.png');
      
      // Disabled
      const disabledSwitch = page.locator('[data-testid="switch-disabled"]');
      await expect(disabledSwitch).toHaveScreenshot('switch-disabled.png');
    });

    test('textarea', async ({ page }) => {
      await helpers.navigateAndWait('/forms');
      
      const textarea = page.locator('[data-testid="textarea-default"]');
      
      // Empty
      await expect(textarea).toHaveScreenshot('textarea-empty.png');
      
      // Focused
      await textarea.focus();
      await expect(textarea).toHaveScreenshot('textarea-focused.png');
      
      // With content
      await textarea.fill('This is a multi-line\ntext content\nfor testing purposes.');
      await expect(textarea).toHaveScreenshot('textarea-filled.png');
    });
  });

  test.describe('Card Components', () => {
    test('basic card', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const card = page.locator('[data-testid="card-basic"]');
      await expect(card).toHaveScreenshot('card-basic.png');
    });

    test('interactive card', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const card = page.locator('[data-testid="card-interactive"]');
      
      // Normal state
      await expect(card).toHaveScreenshot('card-interactive-normal.png');
      
      // Hover state
      await card.hover();
      await expect(card).toHaveScreenshot('card-interactive-hover.png');
    });

    test('card with header and footer', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const card = page.locator('[data-testid="card-complex"]');
      await expect(card).toHaveScreenshot('card-complex.png');
    });
  });

  test.describe('Badge Component', () => {
    const badgeVariants = ['default', 'secondary', 'destructive', 'outline'];
    
    for (const variant of badgeVariants) {
      test(`badge - ${variant} variant`, async ({ page }) => {
        await helpers.navigateAndWait('/components');
        
        const badge = page.locator(`[data-testid="badge-${variant}"]`);
        await expect(badge).toHaveScreenshot(`badge-${variant}.png`);
      });
    }
  });

  test.describe('Alert Components', () => {
    const alertVariants = ['default', 'destructive'];
    
    for (const variant of alertVariants) {
      test(`alert - ${variant} variant`, async ({ page }) => {
        await helpers.navigateAndWait('/components');
        
        const alert = page.locator(`[data-testid="alert-${variant}"]`);
        await expect(alert).toHaveScreenshot(`alert-${variant}.png`);
      });
    }
  });

  test.describe('Dialog Component', () => {
    test('dialog closed and open states', async ({ page }) => {
      await helpers.navigateAndWait('/modals');
      
      // Trigger button
      const triggerButton = page.locator('[data-testid="dialog-trigger"]');
      await expect(triggerButton).toHaveScreenshot('dialog-trigger.png');
      
      // Open dialog
      await triggerButton.click();
      await page.waitForTimeout(300); // Wait for animation
      
      const dialog = page.locator('[data-testid="dialog-content"]');
      await expect(dialog).toHaveScreenshot('dialog-open.png');
      
      // Dialog with overlay
      await expect(page).toHaveScreenshot('dialog-with-overlay.png');
    });
  });

  test.describe('Toast Notifications', () => {
    const toastTypes = ['success', 'error', 'warning', 'info'];
    
    for (const type of toastTypes) {
      test(`toast - ${type} type`, async ({ page }) => {
        await helpers.navigateAndWait('/components');
        
        // Trigger toast
        await page.click(`[data-testid="trigger-${type}-toast"]`);
        await page.waitForTimeout(300); // Wait for animation
        
        const toast = page.locator(`[data-testid="toast-${type}"]`);
        await expect(toast).toHaveScreenshot(`toast-${type}.png`);
      });
    }
  });

  test.describe('Progress Components', () => {
    test('progress bar states', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      // 0% progress
      const progress0 = page.locator('[data-testid="progress-0"]');
      await expect(progress0).toHaveScreenshot('progress-0.png');
      
      // 50% progress
      const progress50 = page.locator('[data-testid="progress-50"]');
      await expect(progress50).toHaveScreenshot('progress-50.png');
      
      // 100% progress
      const progress100 = page.locator('[data-testid="progress-100"]');
      await expect(progress100).toHaveScreenshot('progress-100.png');
      
      // Indeterminate progress
      const progressIndeterminate = page.locator('[data-testid="progress-indeterminate"]');
      await expect(progressIndeterminate).toHaveScreenshot('progress-indeterminate.png');
    });
  });

  test.describe('Tabs Component', () => {
    test('tabs navigation', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const tabs = page.locator('[data-testid="tabs-container"]');
      
      // Default state (first tab active)
      await expect(tabs).toHaveScreenshot('tabs-default.png');
      
      // Click second tab
      await page.click('[data-testid="tab-2"]');
      await page.waitForTimeout(200); // Wait for animation
      await expect(tabs).toHaveScreenshot('tabs-second-active.png');
      
      // Click third tab
      await page.click('[data-testid="tab-3"]');
      await page.waitForTimeout(200); // Wait for animation
      await expect(tabs).toHaveScreenshot('tabs-third-active.png');
    });
  });

  test.describe('Accordion Component', () => {
    test('accordion states', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const accordion = page.locator('[data-testid="accordion"]');
      
      // All collapsed
      await expect(accordion).toHaveScreenshot('accordion-collapsed.png');
      
      // First item expanded
      await page.click('[data-testid="accordion-item-1-trigger"]');
      await page.waitForTimeout(300); // Wait for animation
      await expect(accordion).toHaveScreenshot('accordion-first-expanded.png');
      
      // Multiple items expanded
      await page.click('[data-testid="accordion-item-2-trigger"]');
      await page.waitForTimeout(300); // Wait for animation
      await expect(accordion).toHaveScreenshot('accordion-multiple-expanded.png');
    });
  });

  test.describe('Table Component', () => {
    test('data table', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const table = page.locator('[data-testid="data-table"]');
      
      // Default state
      await expect(table).toHaveScreenshot('table-default.png');
      
      // Sorted state
      await page.click('[data-testid="table-sort-name"]');
      await expect(table).toHaveScreenshot('table-sorted.png');
      
      // Row selected
      await page.click('[data-testid="table-row-1-checkbox"]');
      await expect(table).toHaveScreenshot('table-row-selected.png');
      
      // Row hover
      await page.hover('[data-testid="table-row-2"]');
      await expect(table).toHaveScreenshot('table-row-hover.png');
    });
  });

  test.describe('Tooltip Component', () => {
    test('tooltip positions', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const positions = ['top', 'right', 'bottom', 'left'];
      
      for (const position of positions) {
        const trigger = page.locator(`[data-testid="tooltip-${position}-trigger"]`);
        await trigger.hover();
        await page.waitForTimeout(300); // Wait for tooltip to appear
        
        const tooltip = page.locator(`[data-testid="tooltip-${position}"]`);
        await expect(tooltip).toHaveScreenshot(`tooltip-${position}.png`);
      }
    });
  });

  test.describe('Skeleton Loaders', () => {
    test('skeleton variants', async ({ page }) => {
      await helpers.navigateAndWait('/loading-states');
      
      // Text skeleton
      const textSkeleton = page.locator('[data-testid="skeleton-text"]');
      await expect(textSkeleton).toHaveScreenshot('skeleton-text.png');
      
      // Card skeleton
      const cardSkeleton = page.locator('[data-testid="skeleton-card"]');
      await expect(cardSkeleton).toHaveScreenshot('skeleton-card.png');
      
      // Table skeleton
      const tableSkeleton = page.locator('[data-testid="skeleton-table"]');
      await expect(tableSkeleton).toHaveScreenshot('skeleton-table.png');
    });
  });

  test.describe('Custom Components', () => {
    test('compliance gauge', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      // Different score levels
      const scores = [0, 25, 50, 75, 100];
      
      for (const score of scores) {
        const gauge = page.locator(`[data-testid="compliance-gauge-${score}"]`);
        await expect(gauge).toHaveScreenshot(`compliance-gauge-${score}.png`);
      }
    });

    test('AI guidance panel', async ({ page }) => {
      await helpers.navigateAndWait('/components');
      
      const panel = page.locator('[data-testid="ai-guidance-panel"]');
      
      // Collapsed state
      await expect(panel).toHaveScreenshot('ai-guidance-panel-collapsed.png');
      
      // Expanded state
      await page.click('[data-testid="ai-panel-toggle"]');
      await page.waitForTimeout(300); // Wait for animation
      await expect(panel).toHaveScreenshot('ai-guidance-panel-expanded.png');
    });

    test('file upload component', async ({ page }) => {
      await helpers.navigateAndWait('/demo/file-upload');
      
      const uploader = page.locator('[data-testid="file-uploader"]');
      
      // Default state
      await expect(uploader).toHaveScreenshot('file-uploader-default.png');
      
      // Drag over state
      const dropZone = page.locator('[data-testid="drop-zone"]');
      await dropZone.dispatchEvent('dragenter');
      await expect(uploader).toHaveScreenshot('file-uploader-dragover.png');
    });
  });

  test.describe('Responsive Component Behavior', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1440, height: 900 },
    ];

    for (const viewport of viewports) {
      test(`navigation component - ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await helpers.navigateAndWait('/dashboard');
        
        const navigation = page.locator('[data-testid="main-navigation"]');
        await expect(navigation).toHaveScreenshot(`navigation-${viewport.name}.png`);
      });

      test(`card grid - ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await helpers.navigateAndWait('/components');
        
        const cardGrid = page.locator('[data-testid="card-grid"]');
        await expect(cardGrid).toHaveScreenshot(`card-grid-${viewport.name}.png`);
      });

      test(`form layout - ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await helpers.navigateAndWait('/forms');
        
        const formLayout = page.locator('[data-testid="form-layout"]');
        await expect(formLayout).toHaveScreenshot(`form-layout-${viewport.name}.png`);
      });
    }
  });

  test.describe('Theme Variations', () => {
    const themes = ['light', 'dark'];
    
    for (const theme of themes) {
      test(`button component - ${theme} theme`, async ({ page }) => {
        await page.emulateMedia({ colorScheme: theme as 'light' | 'dark' });
        await helpers.navigateAndWait('/components');
        
        const buttonSection = page.locator('[data-testid="button-showcase"]');
        await expect(buttonSection).toHaveScreenshot(`buttons-${theme}.png`);
      });

      test(`card component - ${theme} theme`, async ({ page }) => {
        await page.emulateMedia({ colorScheme: theme as 'light' | 'dark' });
        await helpers.navigateAndWait('/components');
        
        const cardSection = page.locator('[data-testid="card-showcase"]');
        await expect(cardSection).toHaveScreenshot(`cards-${theme}.png`);
      });

      test(`form components - ${theme} theme`, async ({ page }) => {
        await page.emulateMedia({ colorScheme: theme as 'light' | 'dark' });
        await helpers.navigateAndWait('/forms');
        
        const formSection = page.locator('[data-testid="form-showcase"]');
        await expect(formSection).toHaveScreenshot(`forms-${theme}.png`);
      });
    }
  });
});