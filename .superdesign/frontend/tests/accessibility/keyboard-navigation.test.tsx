import { test, expect } from '@playwright/test';

test.describe('Keyboard Navigation Tests', () => {
  test('Tab order follows logical flow', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Get all tabbable elements
    const tabbableElements = await page.evaluate(() => {
      const selector = 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])';
      const elements = Array.from(document.querySelectorAll(selector));

      return elements
        .filter((el) => {
          const styles = window.getComputedStyle(el);
          return styles.display !== 'none' && styles.visibility !== 'hidden';
        })
        .map((el) => ({
          tag: el.tagName,
          text: el.textContent?.trim().substring(0, 30) || '',
          tabIndex: el.getAttribute('tabindex'),
          position: el.getBoundingClientRect(),
        }));
    });

    // Verify tab order follows visual flow (top to bottom, left to right)
    let lastPosition = { top: 0, left: 0 };
    let violations = 0;

    for (const element of tabbableElements) {
      // Allow some tolerance for elements on the same line
      if (element.position.top < lastPosition.top - 10) {
        violations++;
      }
      lastPosition = element.position;
    }

    expect(violations).toBe(0);
  });

  test('Focus trap in modals', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });

    // Find and click a button that opens a modal
    const modalTrigger = await page.locator('button').first();
    await modalTrigger.click();

    // Wait for modal to appear
    await page.waitForTimeout(500);

    // Check if focus is trapped in modal
    const focusTrapTest = await page.evaluate(async () => {
      const modal = document.querySelector('[role="dialog"], .modal, [aria-modal="true"]');
      if (!modal) return { modalFound: false };

      const focusableInModal = Array.from(
        modal.querySelectorAll(
          'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])',
        ),
      ) as HTMLElement[];

      if (focusableInModal.length === 0) return { modalFound: true, focusTrapped: false };

      // Focus first element
      focusableInModal[0].focus();
      let activeElement = document.activeElement;

      // Tab through all elements
      for (let i = 0; i < focusableInModal.length + 1; i++) {
        const event = new KeyboardEvent('keydown', { key: 'Tab', code: 'Tab' });
        activeElement?.dispatchEvent(event);
        await new Promise((resolve) => setTimeout(resolve, 50));
        activeElement = document.activeElement;
      }

      // Check if focus wrapped back to modal
      const focusInModal = modal.contains(document.activeElement);

      return {
        modalFound: true,
        focusTrapped: focusInModal,
        focusableCount: focusableInModal.length,
      };
    });

    if (focusTrapTest.modalFound) {
      expect(focusTrapTest.focusTrapped).toBe(true);
    }
  });

  test('Keyboard shortcuts accessibility', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });

    // Test common keyboard shortcuts
    const shortcuts = [
      { key: 'Escape', expected: 'close modal or cancel' },
      { key: 'Enter', expected: 'submit or activate' },
      { key: ' ', expected: 'toggle for checkboxes/buttons' },
    ];

    for (const shortcut of shortcuts) {
      await page.keyboard.press(shortcut.key);

      // Check if any action was triggered
      const actionTriggered = await page.evaluate(() => {
        // This would need to be customized based on your app's behavior
        return document.activeElement?.tagName !== 'BODY';
      });

      // Log for debugging
      console.log(`Shortcut ${shortcut.key}: ${actionTriggered ? 'triggered' : 'no action'}`);
    }
  });

  test('Arrow key navigation in menus', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Find navigation menu
    const menuTest = await page.evaluate(async () => {
      const nav = document.querySelector('nav, [role="navigation"]');
      if (!nav) return { menuFound: false };

      const menuItems = Array.from(nav.querySelectorAll('a, [role="menuitem"]')) as HTMLElement[];
      if (menuItems.length === 0) return { menuFound: true, arrowNavWorks: false };

      // Focus first menu item
      menuItems[0].focus();

      // Test arrow key navigation
      const arrowDown = new KeyboardEvent('keydown', { key: 'ArrowDown', code: 'ArrowDown' });
      document.activeElement?.dispatchEvent(arrowDown);

      await new Promise((resolve) => setTimeout(resolve, 100));

      const focusedIndex = menuItems.findIndex((item) => item === document.activeElement);

      return {
        menuFound: true,
        arrowNavWorks: focusedIndex === 1,
        menuItemCount: menuItems.length,
      };
    });

    if (menuTest.menuFound && menuTest.menuItemCount > 1) {
      expect(menuTest.arrowNavWorks).toBe(true);
    }
  });

  test('Form navigation with Tab and Shift+Tab', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle' });

    // Get all form fields
    const formFields = await page.locator('input, select, textarea, button').all();

    if (formFields.length > 0) {
      // Focus first field
      await formFields[0].focus();

      // Tab forward through all fields
      for (let i = 1; i < formFields.length; i++) {
        await page.keyboard.press('Tab');
        const focused = await page.evaluate(() => document.activeElement?.tagName);
        expect(['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON']).toContain(focused);
      }

      // Tab backward with Shift+Tab
      for (let i = formFields.length - 2; i >= 0; i--) {
        await page.keyboard.press('Shift+Tab');
        const focused = await page.evaluate(() => document.activeElement?.tagName);
        expect(['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON']).toContain(focused);
      }
    }
  });

  test('Skip links functionality', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Tab to reveal skip link
    await page.keyboard.press('Tab');

    // Check if skip link is visible
    const skipLinkTest = await page.evaluate(() => {
      const activeElement = document.activeElement as HTMLAnchorElement;
      const isSkipLink =
        activeElement?.textContent?.toLowerCase().includes('skip') ||
        activeElement?.className?.toLowerCase().includes('skip');

      if (isSkipLink && activeElement.href) {
        // Click the skip link
        activeElement.click();

        // Check if focus moved to main content
        const targetId = activeElement.href.split('#')[1];
        const target = document.getElementById(targetId);

        return {
          skipLinkFound: true,
          targetExists: !!target,
          focusMoved: document.activeElement === target,
        };
      }

      return { skipLinkFound: false };
    });

    if (skipLinkTest.skipLinkFound) {
      expect(skipLinkTest.targetExists).toBe(true);
    }
  });

  test('Dropdown navigation with keyboard', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });

    const dropdownTest = await page.evaluate(async () => {
      // Find dropdown triggers
      const dropdowns = Array.from(
        document.querySelectorAll('[aria-haspopup="true"], [data-dropdown]'),
      );
      if (dropdowns.length === 0) return { dropdownFound: false };

      const dropdown = dropdowns[0] as HTMLElement;
      dropdown.focus();

      // Open dropdown with Enter or Space
      const enterEvent = new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter' });
      dropdown.dispatchEvent(enterEvent);

      await new Promise((resolve) => setTimeout(resolve, 200));

      // Check if dropdown opened
      const expanded = dropdown.getAttribute('aria-expanded') === 'true';
      const menu = document.querySelector('[role="menu"], .dropdown-menu:not(.hidden)');

      if (menu) {
        // Test arrow navigation in dropdown
        const menuItems = Array.from(
          menu.querySelectorAll('[role="menuitem"], a, button'),
        ) as HTMLElement[];

        if (menuItems.length > 0) {
          menuItems[0].focus();

          // Navigate with arrow keys
          const arrowDown = new KeyboardEvent('keydown', { key: 'ArrowDown', code: 'ArrowDown' });
          document.activeElement?.dispatchEvent(arrowDown);

          await new Promise((resolve) => setTimeout(resolve, 100));

          return {
            dropdownFound: true,
            opened: expanded || !!menu,
            navigationWorks: document.activeElement === menuItems[1],
          };
        }
      }

      return {
        dropdownFound: true,
        opened: expanded || !!menu,
        navigationWorks: false,
      };
    });

    if (dropdownTest.dropdownFound) {
      expect(dropdownTest.opened).toBe(true);
    }
  });

  test('Focus management on route changes', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Navigate to another route
    await page.click('a[href="/dashboard"]');
    await page.waitForLoadState('networkidle');

    // Check where focus is after navigation
    const focusAfterNav = await page.evaluate(() => {
      const activeElement = document.activeElement;
      const isOnContent =
        activeElement?.tagName !== 'BODY' && !activeElement?.tagName.match(/HTML/);

      // Check if focus is on skip link or main heading
      const isAccessibleFocus =
        activeElement?.textContent?.toLowerCase().includes('skip') ||
        activeElement?.tagName === 'H1' ||
        activeElement?.getAttribute('role') === 'main';

      return {
        hasFocus: isOnContent,
        accessibleFocus: isAccessibleFocus,
        focusedElement: activeElement?.tagName,
        focusedText: activeElement?.textContent?.substring(0, 50),
      };
    });

    expect(focusAfterNav.hasFocus || focusAfterNav.accessibleFocus).toBe(true);
  });

  test('Custom keyboard controls documentation', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });

    // Check for keyboard shortcuts documentation
    const keyboardHelp = await page.evaluate(() => {
      // Look for keyboard help indicators
      const helpIndicators = [
        document.querySelector('[aria-keyshortcuts]'),
        document.querySelector('[title*="keyboard"]'),
        Array.from(document.querySelectorAll('*')).find(
          (el) =>
            el.textContent?.toLowerCase().includes('keyboard shortcuts') ||
            el.textContent?.toLowerCase().includes('press ? for help'),
        ),
      ].filter(Boolean);

      // Check for custom keyboard shortcuts
      const customShortcuts: string[] = [];
      document.querySelectorAll('[aria-keyshortcuts]').forEach((el) => {
        const shortcut = el.getAttribute('aria-keyshortcuts');
        if (shortcut) customShortcuts.push(shortcut);
      });

      return {
        hasHelpIndicator: helpIndicators.length > 0,
        customShortcuts,
      };
    });

    // If custom shortcuts exist, they should be documented
    if (keyboardHelp.customShortcuts.length > 0) {
      expect(keyboardHelp.hasHelpIndicator).toBe(true);
    }
  });

  test('Focus visible on all interactive elements', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Get all interactive elements
    const interactiveElements = await page
      .locator('a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])')
      .all();

    const focusIssues: string[] = [];

    for (const element of interactiveElements.slice(0, 10)) {
      // Test first 10 to avoid timeout
      await element.focus();

      const hasFocusIndicator = await element.evaluate((el) => {
        const styles = window.getComputedStyle(el);
        const hasOutline = styles.outline !== 'none' && styles.outline !== '';
        const hasBoxShadow = styles.boxShadow !== 'none' && styles.boxShadow !== '';
        const hasBorderChange =
          styles.border !== window.getComputedStyle(el, ':not(:focus)').border;

        return hasOutline || hasBoxShadow || hasBorderChange;
      });

      if (!hasFocusIndicator) {
        const elementInfo = await element.evaluate((el) => ({
          tag: el.tagName,
          text: el.textContent?.substring(0, 30),
          class: el.className,
        }));
        focusIssues.push(`${elementInfo.tag}: ${elementInfo.text || elementInfo.class}`);
      }
    }

    expect(focusIssues).toHaveLength(0);
  });

  test('Escape key behavior', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });

    // Test escape key in different contexts
    const escapeTests = await page.evaluate(async () => {
      const results = {
        modalClosed: false,
        dropdownClosed: false,
        tooltipClosed: false,
      };

      // Test modal if exists
      const modalTrigger = document.querySelector('[data-modal-trigger], [onclick*="modal"]');
      if (modalTrigger) {
        (modalTrigger as HTMLElement).click();
        await new Promise((resolve) => setTimeout(resolve, 300));

        const modal = document.querySelector('[role="dialog"], .modal');
        if (modal) {
          document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
          await new Promise((resolve) => setTimeout(resolve, 300));

          results.modalClosed = window.getComputedStyle(modal).display === 'none';
        }
      }

      // Test dropdown if exists
      const dropdown = document.querySelector('[aria-haspopup="true"]');
      if (dropdown) {
        (dropdown as HTMLElement).click();
        await new Promise((resolve) => setTimeout(resolve, 300));

        document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
        await new Promise((resolve) => setTimeout(resolve, 300));

        results.dropdownClosed = dropdown.getAttribute('aria-expanded') !== 'true';
      }

      return results;
    });

    // At least one escape behavior should work
    const anyEscapeWorks = Object.values(escapeTests).some((v) => v);
    expect(anyEscapeWorks).toBe(true);
  });

  test('Grid/table keyboard navigation', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });

    const gridNavTest = await page.evaluate(async () => {
      const table = document.querySelector('table, [role="grid"]');
      if (!table) return { gridFound: false };

      const cells = Array.from(table.querySelectorAll('td, [role="gridcell"]')) as HTMLElement[];
      if (cells.length < 2) return { gridFound: true, navigationWorks: false };

      // Focus first cell
      cells[0].setAttribute('tabindex', '0');
      cells[0].focus();

      // Test arrow key navigation
      const arrowRight = new KeyboardEvent('keydown', { key: 'ArrowRight', code: 'ArrowRight' });
      document.activeElement?.dispatchEvent(arrowRight);

      await new Promise((resolve) => setTimeout(resolve, 100));

      // Check if focus moved
      const focusMoved = document.activeElement !== cells[0];

      return {
        gridFound: true,
        navigationWorks: focusMoved,
        cellCount: cells.length,
      };
    });

    if (gridNavTest.gridFound && gridNavTest.cellCount > 1) {
      // Grid navigation is optional but good to have
      console.log('Grid navigation:', gridNavTest.navigationWorks ? 'supported' : 'not supported');
    }
  });

  test('Focus restoration after dialog close', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });

    const focusRestorationTest = await page.evaluate(async () => {
      // Find a button that might open a dialog
      const triggers = Array.from(document.querySelectorAll('button')).filter(
        (btn) =>
          btn.textContent?.toLowerCase().includes('add') ||
          btn.textContent?.toLowerCase().includes('create') ||
          btn.textContent?.toLowerCase().includes('edit'),
      );

      if (triggers.length === 0) return { tested: false };

      const trigger = triggers[0] as HTMLElement;
      trigger.focus();
      const originalFocus = document.activeElement;

      // Click to open dialog
      trigger.click();
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Find dialog close button
      const dialog = document.querySelector('[role="dialog"], .modal');
      if (!dialog) return { tested: false };

      const closeButton = dialog.querySelector(
        '[aria-label*="close"], .close, button[type="button"]',
      ) as HTMLElement;
      if (closeButton) {
        closeButton.click();
        await new Promise((resolve) => setTimeout(resolve, 500));

        return {
          tested: true,
          focusRestored: document.activeElement === originalFocus,
        };
      }

      return { tested: false };
    });

    if (focusRestorationTest.tested) {
      expect(focusRestorationTest.focusRestored).toBe(true);
    }
  });
});
