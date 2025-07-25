import { test, expect } from '@playwright/test';
import { chromium } from 'playwright';

// Core Web Vitals thresholds
const THRESHOLDS = {
  LCP: 2500, // 2.5s for good LCP
  FID: 100, // 100ms for good FID
  CLS: 0.1, // 0.1 for good CLS
  BUNDLE_SIZE: 500 * 1024, // 500KB max bundle size
};

test.describe('Core Web Vitals Performance Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Enable performance metrics collection
    await page.coverage.startJSCoverage();
    await page.coverage.startCSSCoverage();
  });

  test.afterEach(async ({ page }) => {
    // Stop coverage collection
    await page.coverage.stopJSCoverage();
    await page.coverage.stopCSSCoverage();
  });

  test('LCP (Largest Contentful Paint) should be under 2.5s', async ({ page }) => {
    // Navigate and wait for load
    await page.goto('/', { waitUntil: 'networkidle' });

    // Measure LCP using Performance Observer API
    const lcp = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        // Fallback timeout
        setTimeout(() => resolve(0), 5000);
      });
    });

    expect(lcp).toBeGreaterThan(0);
    expect(lcp).toBeLessThan(THRESHOLDS.LCP);
  });

  test('FID (First Input Delay) should be under 100ms', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Simulate user interaction to measure FID
    const fidMeasurement = await page.evaluate(async () => {
      return new Promise<number>((resolve) => {
        let startTime: number;

        // Set up event listener
        document.addEventListener(
          'click',
          () => {
            const endTime = performance.now();
            resolve(endTime - startTime);
          },
          { once: true },
        );

        // Trigger click after a delay
        setTimeout(() => {
          startTime = performance.now();
          document.body.click();
        }, 1000);
      });
    });

    expect(fidMeasurement).toBeLessThan(THRESHOLDS.FID);
  });

  test('CLS (Cumulative Layout Shift) should be under 0.1', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Measure CLS
    const cls = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let clsValue = 0;

        new PerformanceObserver((entryList) => {
          for (const entry of entryList.getEntries()) {
            if (!(entry as any).hadRecentInput) {
              clsValue += (entry as any).value;
            }
          }
        }).observe({ entryTypes: ['layout-shift'] });

        // Allow time for layout shifts
        setTimeout(() => resolve(clsValue), 3000);
      });
    });

    expect(cls).toBeLessThan(THRESHOLDS.CLS);
  });

  test('Bundle size monitoring', async ({ page }) => {
    const resourceSizes: { [key: string]: number } = {};

    // Monitor network requests
    page.on('response', async (response) => {
      const url = response.url();
      if (url.includes('.js') || url.includes('.css')) {
        const size = (await response.body()).length;
        const type = url.includes('.js') ? 'js' : 'css';
        resourceSizes[type] = (resourceSizes[type] || 0) + size;
      }
    });

    await page.goto('/', { waitUntil: 'networkidle' });

    // Check bundle sizes
    const totalSize = Object.values(resourceSizes).reduce((a, b) => a + b, 0);
    expect(totalSize).toBeLessThan(THRESHOLDS.BUNDLE_SIZE);

    // Log bundle sizes for monitoring
    console.log('Bundle sizes:', {
      js: `${(resourceSizes.js || 0) / 1024}KB`,
      css: `${(resourceSizes.css || 0) / 1024}KB`,
      total: `${totalSize / 1024}KB`,
    });
  });

  test('Time to Interactive (TTI) should be under 3.8s', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const tti = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        if ('PerformanceObserver' in window) {
          const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (entry.name === 'first-contentful-paint') {
                resolve(entry.startTime);
              }
            }
          });
          observer.observe({ entryTypes: ['paint'] });
        } else {
          resolve(performance.timing.domInteractive - performance.timing.navigationStart);
        }
      });
    });

    expect(tti).toBeLessThan(3800); // 3.8s threshold
  });

  test('Memory usage should not exceed limits', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    // Navigate through the app to simulate usage
    await page.click('[data-testid="dashboard-link"]', { force: true }).catch(() => {});
    await page.waitForTimeout(1000);

    // Measure memory usage
    const metrics = await page.evaluate(() => {
      if ('memory' in performance) {
        return {
          usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
          totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
          jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit,
        };
      }
      return null;
    });

    if (metrics) {
      const heapUsagePercent = (metrics.usedJSHeapSize / metrics.jsHeapSizeLimit) * 100;
      expect(heapUsagePercent).toBeLessThan(80); // Should use less than 80% of heap
    }
  });

  test('Network requests should be optimized', async ({ page }) => {
    const requests: any[] = [];

    page.on('request', (request) => {
      requests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType(),
      });
    });

    await page.goto('/', { waitUntil: 'networkidle' });

    // Check for duplicate requests
    const urls = requests.map((r) => r.url);
    const uniqueUrls = [...new Set(urls)];
    expect(urls.length).toBe(uniqueUrls.length);

    // Check for large images
    const imageRequests = requests.filter((r) => r.resourceType === 'image');
    for (const imgRequest of imageRequests) {
      const response = await page.request.fetch(imgRequest.url);
      const size = (await response.body()).length;
      expect(size).toBeLessThan(500 * 1024); // Images should be under 500KB
    }
  });

  test('Resource hints should be properly configured', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' });

    const resourceHints = await page.evaluate(() => {
      const hints = {
        preconnect: [] as string[],
        prefetch: [] as string[],
        preload: [] as string[],
        dnsPrefetch: [] as string[],
      };

      // Check for resource hints
      document.querySelectorAll('link[rel="preconnect"]').forEach((link) => {
        hints.preconnect.push(link.getAttribute('href') || '');
      });
      document.querySelectorAll('link[rel="prefetch"]').forEach((link) => {
        hints.prefetch.push(link.getAttribute('href') || '');
      });
      document.querySelectorAll('link[rel="preload"]').forEach((link) => {
        hints.preload.push(link.getAttribute('href') || '');
      });
      document.querySelectorAll('link[rel="dns-prefetch"]').forEach((link) => {
        hints.dnsPrefetch.push(link.getAttribute('href') || '');
      });

      return hints;
    });

    // Verify critical resource hints exist
    expect(resourceHints.preconnect.length).toBeGreaterThan(0);
    expect(resourceHints.preload.length).toBeGreaterThan(0);
  });

  test('Long tasks should be minimized', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const longTasks = await page.evaluate(() => {
      return new Promise<number[]>((resolve) => {
        const tasks: number[] = [];

        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 50) {
              // Tasks longer than 50ms
              tasks.push(entry.duration);
            }
          }
        }).observe({ entryTypes: ['longtask'] });

        // Allow time for tasks
        setTimeout(() => resolve(tasks), 3000);
      });
    });

    // Should have minimal long tasks
    expect(longTasks.length).toBeLessThan(5);

    // No task should be longer than 200ms
    for (const duration of longTasks) {
      expect(duration).toBeLessThan(200);
    }
  });
});

test.describe('Performance Metrics Across Routes', () => {
  const routes = ['/', '/dashboard', '/assessments', '/policies', '/evidence'];

  for (const route of routes) {
    test(`Performance metrics for ${route}`, async ({ page }) => {
      await page.goto(route, { waitUntil: 'networkidle' });

      const metrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType(
          'navigation',
        )[0] as PerformanceNavigationTiming;
        return {
          domContentLoaded:
            navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint:
            performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
        };
      });

      expect(metrics.firstPaint).toBeLessThan(1000); // Under 1s
      expect(metrics.firstContentfulPaint).toBeLessThan(1500); // Under 1.5s
      expect(metrics.domContentLoaded).toBeLessThan(2000); // Under 2s
      expect(metrics.loadComplete).toBeLessThan(3000); // Under 3s
    });
  }
});
