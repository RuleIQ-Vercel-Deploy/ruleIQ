import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y, getViolations } from 'axe-playwright';

// WCAG 2.2 AA compliance levels
const WCAG_LEVELS = {
  A: ['wcag2a', 'wcag21a', 'wcag22a'],
  AA: ['wcag2aa', 'wcag21aa', 'wcag22aa']
};

test.describe('WCAG 2.2 AA Compliance Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Inject axe-core for accessibility testing
    await injectAxe(page);
  });

  test('Homepage WCAG 2.2 AA compliance', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });
    
    // Run comprehensive WCAG 2.2 AA checks
    const violations = await getViolations(page, undefined, {
      runOnly: {
        type: 'tag',
        values: WCAG_LEVELS.AA
      }
    });

    // Log violations for debugging
    if (violations.length > 0) {
      console.log('WCAG 2.2 AA Violations:', JSON.stringify(violations, null, 2));
    }

    expect(violations.length).toBe(0);
  });

  test('All main routes WCAG compliance', async ({ page }) => {
    const routes = [
      '/',
      '/dashboard',
      '/assessments',
      '/policies',
      '/evidence',
      '/chat',
      '/login',
      '/register'
    ];

    for (const route of routes) {
      await page.goto(route, { waitUntil: 'networkidle' });
      
      const violations = await getViolations(page, undefined, {
        runOnly: {
          type: 'tag',
          values: WCAG_LEVELS.AA
        }
      });

      expect(violations.length).toBe(0);
    }
  });

  test('Color contrast validation', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Check color contrast ratios
    const contrastIssues = await page.evaluate(() => {
      const issues: any[] = [];
      const elements = document.querySelectorAll('*');

      elements.forEach(element => {
        const style = window.getComputedStyle(element);
        const backgroundColor = style.backgroundColor;
        const color = style.color;

        // Skip if colors are not set or transparent
        if (backgroundColor === 'rgba(0, 0, 0, 0)' || color === 'rgba(0, 0, 0, 0)') {
          return;
        }

        // Convert RGB to relative luminance
        const getLuminance = (rgb: string) => {
          const values = rgb.match(/\d+/g);
          if (!values || values.length < 3) return 0;

          const [r, g, b] = values.map(v => {
            const val = parseInt(v) / 255;
            return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
          });

          return 0.2126 * r + 0.7152 * g + 0.0722 * b;
        };

        const bgLuminance = getLuminance(backgroundColor);
        const fgLuminance = getLuminance(color);

        const contrast = (Math.max(bgLuminance, fgLuminance) + 0.05) / 
                        (Math.min(bgLuminance, fgLuminance) + 0.05);

        // WCAG AA requires 4.5:1 for normal text, 3:1 for large text
        const fontSize = parseFloat(style.fontSize);
        const fontWeight = style.fontWeight;
        const isLargeText = fontSize >= 18 || (fontSize >= 14 && fontWeight === 'bold');
        const requiredContrast = isLargeText ? 3 : 4.5;

        if (contrast < requiredContrast && element.textContent?.trim()) {
          issues.push({
            element: element.tagName,
            text: element.textContent.substring(0, 50),
            contrast: contrast.toFixed(2),
            required: requiredContrast,
            colors: { background: backgroundColor, foreground: color }
          });
        }
      });

      return issues;
    });

    expect(contrastIssues.length).toBe(0);
  });

  test('Screen reader compatibility - landmarks', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const landmarks = await page.evaluate(() => {
      const results = {
        main: document.querySelector('main') !== null,
        nav: document.querySelector('nav') !== null,
        header: document.querySelector('header') !== null,
        footer: document.querySelector('footer') !== null,
        aside: document.querySelector('aside')?.getAttribute('aria-label') || null,
        regions: [] as string[]
      };

      // Check for properly labeled regions
      document.querySelectorAll('[role="region"]').forEach(region => {
        const label = region.getAttribute('aria-label') || region.getAttribute('aria-labelledby');
        if (label) {
          results.regions.push(label);
        }
      });

      return results;
    });

    // Verify essential landmarks exist
    expect(landmarks.main).toBe(true);
    expect(landmarks.nav).toBe(true);
    expect(landmarks.header).toBe(true);
  });

  test('Screen reader compatibility - headings structure', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const headingStructure = await page.evaluate(() => {
      const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
      const issues: string[] = [];
      let lastLevel = 0;

      headings.forEach((heading, index) => {
        const level = parseInt(heading.tagName[1]);
        
        // Check for multiple h1s
        if (level === 1 && headings.filter(h => h.tagName === 'H1').length > 1) {
          issues.push('Multiple H1 elements found');
        }

        // Check for skipped levels
        if (lastLevel && level > lastLevel + 1) {
          issues.push(`Heading level skipped: H${lastLevel} → H${level}`);
        }

        lastLevel = level;
      });

      return {
        headings: headings.map(h => ({
          level: h.tagName,
          text: h.textContent?.trim().substring(0, 50)
        })),
        issues
      };
    });

    expect(headingStructure.issues.length).toBe(0);
  });

  test('ARIA attributes validation', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const ariaIssues = await page.evaluate(() => {
      const issues: any[] = [];

      // Check for valid ARIA roles
      document.querySelectorAll('[role]').forEach(element => {
        const role = element.getAttribute('role');
        const validRoles = [
          'button', 'link', 'menuitem', 'tab', 'navigation', 'main',
          'complementary', 'contentinfo', 'banner', 'search', 'form',
          'region', 'alert', 'dialog', 'alertdialog', 'progressbar'
        ];

        if (role && !validRoles.includes(role)) {
          issues.push({
            type: 'invalid-role',
            element: element.tagName,
            role
          });
        }
      });

      // Check for required ARIA properties
      document.querySelectorAll('[role="button"]').forEach(button => {
        if (!button.hasAttribute('aria-label') && !button.textContent?.trim()) {
          issues.push({
            type: 'missing-label',
            element: 'button',
            text: 'Button without accessible label'
          });
        }
      });

      // Check for aria-describedby references
      document.querySelectorAll('[aria-describedby]').forEach(element => {
        const id = element.getAttribute('aria-describedby');
        if (id && !document.getElementById(id)) {
          issues.push({
            type: 'broken-reference',
            element: element.tagName,
            reference: id
          });
        }
      });

      return issues;
    });

    expect(ariaIssues.length).toBe(0);
  });

  test('Form accessibility', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle' });

    const formIssues = await page.evaluate(() => {
      const issues: any[] = [];

      // Check all form inputs
      document.querySelectorAll('input, select, textarea').forEach(input => {
        const id = input.id;
        const name = input.getAttribute('name');
        const type = input.getAttribute('type');
        
        // Check for labels
        const label = document.querySelector(`label[for="${id}"]`);
        const ariaLabel = input.getAttribute('aria-label');
        const ariaLabelledby = input.getAttribute('aria-labelledby');
        
        if (!label && !ariaLabel && !ariaLabelledby && type !== 'hidden') {
          issues.push({
            type: 'missing-label',
            element: input.tagName,
            name: name || 'unnamed',
            inputType: type
          });
        }

        // Check for error messages association
        if (input.getAttribute('aria-invalid') === 'true') {
          const errorId = input.getAttribute('aria-describedby');
          if (!errorId || !document.getElementById(errorId)) {
            issues.push({
              type: 'missing-error-association',
              element: input.tagName,
              name: name || 'unnamed'
            });
          }
        }

        // Check for required fields indication
        if (input.hasAttribute('required') && !input.getAttribute('aria-required')) {
          issues.push({
            type: 'missing-aria-required',
            element: input.tagName,
            name: name || 'unnamed'
          });
        }
      });

      // Check for fieldset/legend for grouped inputs
      document.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(input => {
        const fieldset = input.closest('fieldset');
        if (!fieldset || !fieldset.querySelector('legend')) {
          issues.push({
            type: 'missing-fieldset-legend',
            element: 'input',
            inputType: input.getAttribute('type')
          });
        }
      });

      return issues;
    });

    expect(formIssues.length).toBe(0);
  });

  test('Image accessibility', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const imageIssues = await page.evaluate(() => {
      const issues: any[] = [];

      // Check all images
      document.querySelectorAll('img').forEach(img => {
        const alt = img.getAttribute('alt');
        const src = img.getAttribute('src');
        const role = img.getAttribute('role');

        // Check for alt text
        if (alt === null && role !== 'presentation') {
          issues.push({
            type: 'missing-alt',
            src: src?.substring(0, 50)
          });
        }

        // Check for empty alt on decorative images
        if (alt === '' && !role) {
          issues.push({
            type: 'decorative-image-without-role',
            src: src?.substring(0, 50)
          });
        }
      });

      // Check for SVGs
      document.querySelectorAll('svg').forEach(svg => {
        const title = svg.querySelector('title');
        const ariaLabel = svg.getAttribute('aria-label');
        const role = svg.getAttribute('role');

        if (!title && !ariaLabel && role !== 'presentation') {
          issues.push({
            type: 'inaccessible-svg',
            element: 'svg'
          });
        }
      });

      return issues;
    });

    expect(imageIssues.length).toBe(0);
  });

  test('Link accessibility', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const linkIssues = await page.evaluate(() => {
      const issues: any[] = [];

      document.querySelectorAll('a').forEach(link => {
        const href = link.getAttribute('href');
        const text = link.textContent?.trim();
        const ariaLabel = link.getAttribute('aria-label');

        // Check for link text
        if (!text && !ariaLabel) {
          issues.push({
            type: 'missing-link-text',
            href: href || 'no-href'
          });
        }

        // Check for generic link text
        const genericTexts = ['click here', 'read more', 'learn more', 'more', 'link'];
        if (text && genericTexts.includes(text.toLowerCase()) && !ariaLabel) {
          issues.push({
            type: 'generic-link-text',
            text,
            href: href || 'no-href'
          });
        }

        // Check for links that open in new window
        if (link.getAttribute('target') === '_blank') {
          const hasWarning = ariaLabel?.includes('opens in new') || 
                           text?.includes('opens in new');
          if (!hasWarning) {
            issues.push({
              type: 'new-window-without-warning',
              text: text?.substring(0, 30),
              href: href || 'no-href'
            });
          }
        }
      });

      return issues;
    });

    expect(linkIssues.length).toBe(0);
  });

  test('Focus indicators visibility', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const focusIssues = await page.evaluate(async () => {
      const issues: any[] = [];
      const focusableElements = document.querySelectorAll(
        'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      for (const element of Array.from(focusableElements)) {
        // Focus the element
        (element as HTMLElement).focus();
        
        // Check if focus is visible
        const styles = window.getComputedStyle(element);
        const outline = styles.outline;
        const boxShadow = styles.boxShadow;
        const border = styles.border;
        
        // Get styles before focus for comparison
        (element as HTMLElement).blur();
        const blurredStyles = window.getComputedStyle(element);
        
        const hasVisibleFocus = 
          outline !== 'none' || 
          boxShadow !== blurredStyles.boxShadow ||
          border !== blurredStyles.border;

        if (!hasVisibleFocus) {
          issues.push({
            element: element.tagName,
            class: element.className,
            text: element.textContent?.substring(0, 30)
          });
        }
      }

      return issues;
    });

    expect(focusIssues.length).toBe(0);
  });

  test('Table accessibility', async ({ page }) => {
    await page.goto('/dashboard', { waitUntil: 'networkidle' });

    const tableIssues = await page.evaluate(() => {
      const issues: any[] = [];

      document.querySelectorAll('table').forEach(table => {
        // Check for caption or aria-label
        const caption = table.querySelector('caption');
        const ariaLabel = table.getAttribute('aria-label');
        if (!caption && !ariaLabel) {
          issues.push({
            type: 'missing-table-caption',
            element: 'table'
          });
        }

        // Check for header cells
        const headers = table.querySelectorAll('th');
        if (headers.length === 0) {
          issues.push({
            type: 'missing-table-headers',
            element: 'table'
          });
        }

        // Check for scope attributes on headers
        headers.forEach(header => {
          if (!header.hasAttribute('scope')) {
            issues.push({
              type: 'missing-header-scope',
              text: header.textContent?.substring(0, 30)
            });
          }
        });
      });

      return issues;
    });

    expect(tableIssues.length).toBe(0);
  });

  test('Media accessibility', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const mediaIssues = await page.evaluate(() => {
      const issues: any[] = [];

      // Check video elements
      document.querySelectorAll('video').forEach(video => {
        // Check for captions
        const tracks = video.querySelectorAll('track[kind="captions"]');
        if (tracks.length === 0) {
          issues.push({
            type: 'missing-captions',
            element: 'video'
          });
        }

        // Check for audio description
        const audioDesc = video.querySelector('track[kind="descriptions"]');
        if (!audioDesc) {
          issues.push({
            type: 'missing-audio-description',
            element: 'video'
          });
        }
      });

      // Check audio elements
      document.querySelectorAll('audio').forEach(audio => {
        // Check for transcript
        const transcriptId = audio.getAttribute('aria-describedby');
        if (!transcriptId || !document.getElementById(transcriptId)) {
          issues.push({
            type: 'missing-transcript',
            element: 'audio'
          });
        }
      });

      return issues;
    });

    expect(mediaIssues.length).toBe(0);
  });

  test('Page language declaration', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const languageCheck = await page.evaluate(() => {
      const html = document.documentElement;
      const lang = html.getAttribute('lang');
      
      return {
        hasLang: !!lang,
        lang: lang,
        validLang: lang ? /^[a-z]{2}(-[A-Z]{2})?$/.test(lang) : false
      };
    });

    expect(languageCheck.hasLang).toBe(true);
    expect(languageCheck.validLang).toBe(true);
  });

  test('Skip navigation links', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const skipLinks = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a')).filter(link => 
        link.textContent?.toLowerCase().includes('skip') ||
        link.className.toLowerCase().includes('skip')
      );

      return links.map(link => ({
        text: link.textContent,
        href: link.getAttribute('href'),
        visible: window.getComputedStyle(link).position === 'absolute' &&
                 window.getComputedStyle(link).left.includes('-')
      }));
    });

    expect(skipLinks.length).toBeGreaterThan(0);
    expect(skipLinks[0].href).toContain('#');
  });
});