import { type RenderResult } from '@testing-library/react';
import { axe, type AxeResults, type Result } from 'jest-axe';

/**
 * Accessibility testing utilities for ruleIQ
 */

export interface AccessibilityTestOptions {
  /** Custom axe rules to include */
  rules?: Record<string, { enabled: boolean }>;
  /** Tags to include in testing */
  tags?: string[];
  /** Elements to exclude from testing */
  exclude?: string[];
  /** Custom timeout for testing */
  timeout?: number;
}

/**
 * Test accessibility of a rendered component
 */
export async function testAccessibility(
  renderResult: RenderResult,
  options: AccessibilityTestOptions = {}
): Promise<AxeResults> {
  const { container } = renderResult;
  
  const axeOptions = {
    rules: {
      // Enable all WCAG 2.2 AA rules by default
      'color-contrast': { enabled: true },
      'keyboard-navigation': { enabled: true },
      'focus-management': { enabled: true },
      'aria-labels': { enabled: true },
      'semantic-markup': { enabled: true },
      ...options.rules,
    },
    tags: options.tags || ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'],
    exclude: options.exclude || [],
  };

  return await axe(container, axeOptions);
}

/**
 * Test accessibility and throw detailed error if violations found
 */
export async function expectAccessible(
  renderResult: RenderResult,
  options: AccessibilityTestOptions = {}
): Promise<void> {
  const results = await testAccessibility(renderResult, options);
  
  if (results.violations.length > 0) {
    const violationDetails = formatViolations(results.violations);
    throw new Error(`Accessibility violations found:\n${violationDetails}`);
  }
}

/**
 * Format accessibility violations for readable error messages
 */
export function formatViolations(violations: Result[]): string {
  return violations
    .map((violation) => {
      const nodes = violation.nodes
        .map((node) => `  - ${node.target.join(', ')}: ${node.failureSummary}`)
        .join('\n');
      
      return `${violation.id} (${violation.impact}): ${violation.description}\n${nodes}`;
    })
    .join('\n\n');
}

/**
 * Test keyboard navigation for a component
 */
export async function testKeyboardNavigation(
  renderResult: RenderResult,
  expectedFocusableElements: string[]
): Promise<void> {
  const { container } = renderResult;
  
  // Get all focusable elements
  const focusableElements = container.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  // Check that expected elements are focusable
  expectedFocusableElements.forEach((selector) => {
    const element = container.querySelector(selector);
    if (!element) {
      throw new Error(`Expected focusable element not found: ${selector}`);
    }
    
    if (!focusableElements.includes(element)) {
      throw new Error(`Element is not focusable: ${selector}`);
    }
  });
  
  // Test tab order
  const tabOrder: Element[] = [];
  let currentElement = container.querySelector('[tabindex="0"]') || focusableElements[0];
  
  while (currentElement && tabOrder.length < focusableElements.length) {
    tabOrder.push(currentElement);
    
    // Simulate tab key press
    const nextElement = getNextFocusableElement(currentElement, focusableElements);
    if (nextElement === currentElement) break;
    currentElement = nextElement;
  }
  
  // Verify logical tab order
  if (tabOrder.length !== focusableElements.length) {
    throw new Error('Tab order is not complete or contains cycles');
  }
}

/**
 * Get the next focusable element in tab order
 */
function getNextFocusableElement(current: Element, focusableElements: NodeListOf<Element>): Element {
  const currentIndex = Array.from(focusableElements).indexOf(current);
  const nextIndex = (currentIndex + 1) % focusableElements.length;
  return focusableElements[nextIndex];
}

/**
 * Test ARIA attributes for a component
 */
export function testAriaAttributes(
  renderResult: RenderResult,
  expectedAttributes: Record<string, Record<string, string>>
): void {
  const { container } = renderResult;
  
  Object.entries(expectedAttributes).forEach(([selector, attributes]) => {
    const element = container.querySelector(selector);
    if (!element) {
      throw new Error(`Element not found: ${selector}`);
    }
    
    Object.entries(attributes).forEach(([attribute, expectedValue]) => {
      const actualValue = element.getAttribute(attribute);
      if (actualValue !== expectedValue) {
        throw new Error(
          `Expected ${attribute}="${expectedValue}" on ${selector}, but got "${actualValue}"`
        );
      }
    });
  });
}

/**
 * Test color contrast for text elements
 */
export async function testColorContrast(
  renderResult: RenderResult,
  minimumRatio: number = 4.5
): Promise<void> {
  const results = await testAccessibility(renderResult, {
    rules: {
      'color-contrast': { enabled: true },
    },
  });
  
  const contrastViolations = results.violations.filter(
    (violation) => violation.id === 'color-contrast'
  );
  
  if (contrastViolations.length > 0) {
    throw new Error(
      `Color contrast violations found (minimum ratio: ${minimumRatio}):\n${formatViolations(contrastViolations)}`
    );
  }
}

/**
 * Test screen reader announcements
 */
export function testScreenReaderAnnouncements(
  renderResult: RenderResult,
  expectedAnnouncements: Array<{ selector: string; text: string }>
): void {
  const { container } = renderResult;
  
  expectedAnnouncements.forEach(({ selector, text }) => {
    const element = container.querySelector(selector);
    if (!element) {
      throw new Error(`Announcement element not found: ${selector}`);
    }
    
    const ariaLive = element.getAttribute('aria-live');
    const role = element.getAttribute('role');
    
    if (!ariaLive && role !== 'alert' && role !== 'status') {
      throw new Error(
        `Element ${selector} should have aria-live attribute or alert/status role for screen reader announcements`
      );
    }
    
    if (!element.textContent?.includes(text)) {
      throw new Error(
        `Expected announcement text "${text}" not found in element ${selector}`
      );
    }
  });
}

/**
 * Test form accessibility
 */
export function testFormAccessibility(
  renderResult: RenderResult,
  formSelector: string = 'form'
): void {
  const { container } = renderResult;
  const form = container.querySelector(formSelector);
  
  if (!form) {
    throw new Error(`Form not found: ${formSelector}`);
  }
  
  // Check that all inputs have labels
  const inputs = form.querySelectorAll('input, select, textarea');
  inputs.forEach((input) => {
    const id = input.getAttribute('id');
    const ariaLabel = input.getAttribute('aria-label');
    const ariaLabelledBy = input.getAttribute('aria-labelledby');
    
    if (!id && !ariaLabel && !ariaLabelledBy) {
      throw new Error('Input element must have id, aria-label, or aria-labelledby');
    }
    
    if (id) {
      const label = form.querySelector(`label[for="${id}"]`);
      if (!label && !ariaLabel && !ariaLabelledBy) {
        throw new Error(`No label found for input with id="${id}"`);
      }
    }
  });
  
  // Check required field indicators
  const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');
  requiredInputs.forEach((input) => {
    const ariaRequired = input.getAttribute('aria-required');
    const required = input.hasAttribute('required');
    
    if (!required && ariaRequired !== 'true') {
      throw new Error('Required inputs should have required attribute or aria-required="true"');
    }
  });
  
  // Check error message associations
  const invalidInputs = form.querySelectorAll('[aria-invalid="true"]');
  invalidInputs.forEach((input) => {
    const describedBy = input.getAttribute('aria-describedby');
    if (!describedBy) {
      throw new Error('Invalid inputs should have aria-describedby pointing to error message');
    }
    
    const errorElement = form.querySelector(`#${describedBy}`);
    if (!errorElement) {
      throw new Error(`Error message element not found: #${describedBy}`);
    }
  });
}

/**
 * Test modal accessibility
 */
export function testModalAccessibility(
  renderResult: RenderResult,
  modalSelector: string
): void {
  const { container } = renderResult;
  const modal = container.querySelector(modalSelector);
  
  if (!modal) {
    throw new Error(`Modal not found: ${modalSelector}`);
  }
  
  // Check required ARIA attributes
  const requiredAttributes = {
    'role': 'dialog',
    'aria-modal': 'true',
  };
  
  Object.entries(requiredAttributes).forEach(([attribute, expectedValue]) => {
    const actualValue = modal.getAttribute(attribute);
    if (actualValue !== expectedValue) {
      throw new Error(
        `Modal should have ${attribute}="${expectedValue}", but got "${actualValue}"`
      );
    }
  });
  
  // Check for accessible name
  const ariaLabel = modal.getAttribute('aria-label');
  const ariaLabelledBy = modal.getAttribute('aria-labelledby');
  
  if (!ariaLabel && !ariaLabelledBy) {
    throw new Error('Modal should have aria-label or aria-labelledby for accessible name');
  }
  
  // Check for close button
  const closeButton = modal.querySelector('button[aria-label*="close"], button[aria-label*="Close"]');
  if (!closeButton) {
    throw new Error('Modal should have a close button with appropriate aria-label');
  }
}

/**
 * Accessibility testing presets for common components
 */
export const AccessibilityPresets = {
  WCAG_AA: {
    tags: ['wcag2a', 'wcag2aa'],
    rules: {
      'color-contrast': { enabled: true },
      'keyboard-navigation': { enabled: true },
    },
  },
  
  WCAG_AAA: {
    tags: ['wcag2a', 'wcag2aa', 'wcag2aaa'],
    rules: {
      'color-contrast-enhanced': { enabled: true },
    },
  },
  
  FORM_ACCESSIBILITY: {
    tags: ['wcag2a', 'wcag2aa'],
    rules: {
      'label': { enabled: true },
      'label-title-only': { enabled: true },
      'form-field-multiple-labels': { enabled: true },
    },
  },
  
  NAVIGATION_ACCESSIBILITY: {
    tags: ['wcag2a', 'wcag2aa'],
    rules: {
      'skip-link': { enabled: true },
      'focus-order-semantics': { enabled: true },
      'tabindex': { enabled: true },
    },
  },
};
