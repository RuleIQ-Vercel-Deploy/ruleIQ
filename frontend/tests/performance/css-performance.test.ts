import { test, expect } from '@playwright/test';
import { join } from 'path';
import { readFileSync } from 'fs';

test.describe('CSS Performance Tests', () => {
  test('CSS loading performance - critical CSS should load quickly', async ({ page }) => {
    const cssLoadTimes: { [url: string]: number } = {};

    // Monitor CSS resource timing
    page.on('response', async (response) => {
      if (response.url().includes('.css')) {
        const timing = await page.evaluate((url) => {
          const entry = performance.getEntriesByName(url)[0] as PerformanceResourceTiming;
          return entry ? entry.duration : 0;
        }, response.url());

        cssLoadTimes[response.url()] = timing;
      }
    });

    await page.goto('/', { waitUntil: 'networkidle' });

    // Check CSS load times
    for (const [url, duration] of Object.entries(cssLoadTimes)) {
      expect(duration).toBeLessThan(500); // CSS should load in under 500ms
    // TODO: Replace with proper logging
    }

    // Verify critical CSS is inlined or loaded first
    const criticalCSSLoaded = await page.evaluate(() => {
      // Check if critical styles are present
      const styles = window.getComputedStyle(document.body);
      return styles.display !== 'none' && styles.visibility !== 'hidden';
    });

    expect(criticalCSSLoaded).toBe(true);
  });

  test('Unused CSS detection', async ({ page }) => {
    // Start CSS coverage
    await page.coverage.startCSSCoverage();

    // Navigate through main routes to maximize CSS usage
    const routes = ['/', '/dashboard', '/assessments', '/policies', '/evidence'];

    for (const route of routes) {
      await page.goto(route, { waitUntil: 'networkidle' });
      await page.waitForTimeout(1000); // Allow dynamic styles to load

      // Interact with common elements
      await page.hover('button').catch(() => {});
      await page.focus('input').catch(() => {});
    }

    // Stop coverage and analyze
    const coverage = await page.coverage.stopCSSCoverage();

    let totalBytes = 0;
    let usedBytes = 0;
    const unusedSelectors: string[] = [];

    for (const entry of coverage) {
      totalBytes += entry.text.length;

      // Calculate used bytes
      for (const range of entry.ranges) {
        usedBytes += range.end - range.start;
      }

      // Find unused CSS rules
      let currentPos = 0;
      for (const range of entry.ranges) {
        if (currentPos < range.start) {
          const unusedText = entry.text.substring(currentPos, range.start);
          const selectors = unusedText.match(/[^{]+(?=\s*{)/g);
          if (selectors) {
            unusedSelectors.push(...selectors.map((s) => s.trim()));
          }
        }
        currentPos = range.end;
      }
    }

    const usagePercent = (usedBytes / totalBytes) * 100;
    // TODO: Replace with proper logging
    // At least 60% of CSS should be used
    expect(usagePercent).toBeGreaterThan(60);

    // Log sample of unused selectors for optimization
    if (unusedSelectors.length > 0) {
    // TODO: Replace with proper logging
    }
  });

  test('Style recalculation performance', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Measure style recalculation during interactions
    const recalcMetrics = await page.evaluate(async () => {
      const metrics: number[] = [];

      // Function to trigger and measure style recalc
      const measureRecalc = async (action: () => void) => {
        const startTime = performance.now();
        action();
        // Force style recalculation
        void document.body.offsetHeight;
        const endTime = performance.now();
        return endTime - startTime;
      };

      // Test various style-changing operations
      // 1. Class toggle
      const button = document.querySelector('button');
      if (button) {
        const classToggleTime = await measureRecalc(() => {
          button.classList.add('test-class');
          button.classList.remove('test-class');
        });
        metrics.push(classToggleTime);
      }

      // 2. Style property change
      const element = document.createElement('div');
      document.body.appendChild(element);
      const styleChangeTime = await measureRecalc(() => {
        element.style.transform = 'translateX(100px)';
      });
      metrics.push(styleChangeTime);

      // 3. Dynamic style injection
      const styleInjectionTime = await measureRecalc(() => {
        const style = document.createElement('style');
        style.textContent = '.dynamic-test { color: red; }';
        document.head.appendChild(style);
      });
      metrics.push(styleInjectionTime);

      return metrics;
    });

    // Style recalculations should be fast
    for (const time of recalcMetrics) {
      expect(time).toBeLessThan(10); // Under 10ms
    }
  });

  test('CSS file optimization checks', async ({ page }) => {
    const cssFiles: string[] = [];

    page.on('response', async (response) => {
      if (response.url().includes('.css') && response.status() === 200) {
        cssFiles.push(response.url());
      }
    });

    await page.goto('/', { waitUntil: 'networkidle' });

    for (const cssUrl of cssFiles) {
      const response = await page.request.fetch(cssUrl);
      const cssContent = await response.text();

      // Check for minification
      const hasWhitespace = /\s{2,}/.test(cssContent);
      const hasComments = /\/\*[\s\S]*?\*\//.test(cssContent);
      expect(hasWhitespace).toBe(false); // Should be minified
      expect(hasComments).toBe(false); // Comments should be removed

      // Check for vendor prefixes optimization
      const vendorPrefixes = cssContent.match(/-webkit-|-moz-|-ms-|-o-/g) || [];
      expect(vendorPrefixes.length).toBeLessThan(50); // Minimal vendor prefixes

      // Check file size
      const size = cssContent.length;
      expect(size).toBeLessThan(100 * 1024); // Each CSS file under 100KB
    }
  });

  test('CSS specificity and complexity analysis', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const specificityAnalysis = await page.evaluate(() => {
      const results = {
        totalRules: 0,
        complexSelectors: [] as string[],
        deeplyNested: [] as string[],
        overlySpecific: [] as string[],
      };

      // Analyze all stylesheets
      for (const sheet of document.styleSheets) {
        try {
          const rules = sheet.cssRules || sheet.rules;
          results.totalRules += rules.length;

          for (const rule of rules) {
            if (rule instanceof CSSStyleRule) {
              const selector = rule.selectorText;

              // Check complexity
              const parts = selector.split(/[\s>+~]/);
              if (parts.length > 4) {
                results.deeplyNested.push(selector);
              }

              // Check specificity
              const idCount = (selector.match(/#/g) || []).length;
              const classCount = (selector.match(/\./g) || []).length;
              const elementCount = (selector.match(/^[a-z]+|[\s>+~][a-z]+/gi) || []).length;

              if (idCount > 1 || classCount > 3) {
                results.overlySpecific.push(selector);
              }

              // Check for complex pseudo-selectors
              if (selector.includes(':not(') || selector.includes(':has(')) {
                results.complexSelectors.push(selector);
              }
            }
          }
        } catch {
          // Skip cross-origin stylesheets
        }
      }

      return results;
    });

    // Assertions
    expect(specificityAnalysis.deeplyNested.length).toBeLessThan(10);
    expect(specificityAnalysis.overlySpecific.length).toBeLessThan(20);

    if (specificityAnalysis.deeplyNested.length > 0) {
    // TODO: Replace with proper logging
    }
  });

  test('CSS animation performance', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const animationMetrics = await page.evaluate(() => {
      const results = {
        animatedElements: 0,
        transforms: 0,
        willChange: 0,
        animations: [] as string[],
      };

      // Check all elements
      const allElements = document.querySelectorAll('*');

      allElements.forEach((element) => {
        const styles = window.getComputedStyle(element);

        // Check for animations
        if (styles.animation !== 'none' && styles.animation !== '') {
          results.animatedElements++;
          results.animations.push(styles.animation);
        }

        // Check for transforms
        if (styles.transform !== 'none') {
          results.transforms++;
        }

        // Check for will-change
        if (styles.willChange !== 'auto') {
          results.willChange++;
        }
      });

      return results;
    });

    // Verify performance best practices
    expect(animationMetrics.willChange).toBeLessThan(10); // Limited use of will-change

    // Log findings
    // TODO: Replace with proper logging
  });

  test('Critical rendering path optimization', async ({ page }) => {
    const renderBlockingResources: string[] = [];

    page.on('response', async (response) => {
      const url = response.url();
      if (url.includes('.css') || url.includes('.js')) {
        const headers = response.headers();

        // Check if resource is render-blocking
        if (
          !headers['cache-control']?.includes('immutable') &&
          !url.includes('async') &&
          !url.includes('defer')
        ) {
          renderBlockingResources.push(url);
        }
      }
    });

    await page.goto('/', { waitUntil: 'domcontentloaded' });

    // Check render-blocking resources
    expect(renderBlockingResources.length).toBeLessThan(5);

    // Measure time to first paint
    const paintTiming = await page.evaluate(() => {
      const paint = performance.getEntriesByType('paint');
      return {
        firstPaint: paint.find((p) => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint:
          paint.find((p) => p.name === 'first-contentful-paint')?.startTime || 0,
      };
    });

    expect(paintTiming.firstPaint).toBeLessThan(1000); // Under 1s
    expect(paintTiming.firstContentfulPaint).toBeLessThan(1500); // Under 1.5s
  });

  test('CSS Grid and Flexbox performance', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const layoutMetrics = await page.evaluate(() => {
      const results = {
        gridElements: 0,
        flexElements: 0,
        nestedGrids: 0,
        complexLayouts: [] as string[],
      };

      const checkElement = (element: Element, depth: number = 0) => {
        const styles = window.getComputedStyle(element);

        if (styles.display === 'grid') {
          results.gridElements++;
          if (depth > 0) results.nestedGrids++;
        }

        if (styles.display === 'flex') {
          results.flexElements++;
        }

        // Check for complex layouts
        if (
          (styles.display === 'grid' || styles.display === 'flex') &&
          element.children.length > 20
        ) {
          results.complexLayouts.push(`${element.tagName}.${element.className}`);
        }

        // Recurse through children
        Array.from(element.children).forEach((child) => checkElement(child, depth + 1));
      };

      checkElement(document.body);
      return results;
    });

    // Log layout usage
    // TODO: Replace with proper logging
    // Verify no overly complex layouts
    expect(layoutMetrics.complexLayouts.length).toBeLessThan(5);
    expect(layoutMetrics.nestedGrids).toBeLessThan(3);
  });
});
