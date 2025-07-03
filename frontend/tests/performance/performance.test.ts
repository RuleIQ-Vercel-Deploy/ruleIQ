import { test, expect } from '@playwright/test';

import { TestHelpers } from '../e2e/utils/test-helpers';

test.describe('Performance Tests', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test.describe('Core Web Vitals', () => {
    test('homepage should meet Core Web Vitals thresholds', async ({ page }) => {
      await page.goto('/');
      
      // Measure Core Web Vitals
      const vitals = await page.evaluate(() => {
        return new Promise((resolve) => {
          const vitals: Record<string, number> = {};
          
          // Largest Contentful Paint (LCP)
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            vitals.lcp = lastEntry.startTime;
          }).observe({ entryTypes: ['largest-contentful-paint'] });
          
          // First Input Delay (FID) - simulated
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            if (entries.length > 0) {
              vitals.fid = entries[0].processingStart - entries[0].startTime;
            }
          }).observe({ entryTypes: ['first-input'] });
          
          // Cumulative Layout Shift (CLS)
          let clsValue = 0;
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (!(entry as any).hadRecentInput) {
                clsValue += (entry as any).value;
              }
            }
            vitals.cls = clsValue;
          }).observe({ entryTypes: ['layout-shift'] });
          
          // Wait for measurements
          setTimeout(() => {
            resolve(vitals);
          }, 3000);
        });
      });
      
      // Core Web Vitals thresholds
      if (vitals.lcp) expect(vitals.lcp).toBeLessThan(2500); // LCP < 2.5s
      if (vitals.fid) expect(vitals.fid).toBeLessThan(100);  // FID < 100ms
      if (vitals.cls) expect(vitals.cls).toBeLessThan(0.1);  // CLS < 0.1
    });

    test('dashboard should load within performance budget', async ({ page }) => {
      // Login first
      await helpers.navigateAndWait('/login');
      await helpers.fillField('[data-testid="email-input"]', 'test@example.com');
      await helpers.fillField('[data-testid="password-input"]', 'password123');
      
      const startTime = Date.now();
      await helpers.clickAndWait('[data-testid="login-button"]', '[data-testid="dashboard"]');
      const loadTime = Date.now() - startTime;
      
      // Dashboard should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
      
      // Check for performance metrics
      const metrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.navigationStart,
          loadComplete: navigation.loadEventEnd - navigation.navigationStart,
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
        };
      });
      
      expect(metrics.domContentLoaded).toBeLessThan(2000); // DOM ready < 2s
      expect(metrics.firstContentfulPaint).toBeLessThan(1500); // FCP < 1.5s
    });
  });

  test.describe('Resource Loading', () => {
    test('should load critical resources efficiently', async ({ page }) => {
      await page.goto('/');
      
      // Wait for page to fully load
      await page.waitForLoadState('networkidle');
      
      const resourceMetrics = await page.evaluate(() => {
        const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
        
        const metrics = {
          totalResources: resources.length,
          totalSize: 0,
          slowResources: [] as string[],
          largeResources: [] as string[],
          cssFiles: 0,
          jsFiles: 0,
          imageFiles: 0,
        };
        
        resources.forEach((resource) => {
          const duration = resource.responseEnd - resource.requestStart;
          const size = resource.transferSize || 0;
          
          metrics.totalSize += size;
          
          // Flag slow resources (>1s)
          if (duration > 1000) {
            metrics.slowResources.push(resource.name);
          }
          
          // Flag large resources (>500KB)
          if (size > 500000) {
            metrics.largeResources.push(resource.name);
          }
          
          // Count by type
          if (resource.name.includes('.css')) metrics.cssFiles++;
          if (resource.name.includes('.js')) metrics.jsFiles++;
          if (resource.name.match(/\.(jpg|jpeg|png|gif|webp|svg)$/)) metrics.imageFiles++;
        });
        
        return metrics;
      });
      
      // Performance budgets
      expect(resourceMetrics.totalSize).toBeLessThan(2000000); // Total < 2MB
      expect(resourceMetrics.slowResources.length).toBe(0); // No slow resources
      expect(resourceMetrics.largeResources.length).toBeLessThan(3); // Max 2 large resources
      expect(resourceMetrics.cssFiles).toBeLessThan(5); // Max 4 CSS files
      expect(resourceMetrics.jsFiles).toBeLessThan(10); // Max 9 JS files
    });

    test('should optimize image loading', async ({ page }) => {
      await page.goto('/');
      
      const imageMetrics = await page.evaluate(() => {
        const images = Array.from(document.querySelectorAll('img'));
        
        return {
          totalImages: images.length,
          imagesWithAlt: images.filter(img => img.alt).length,
          imagesWithLazyLoading: images.filter(img => img.loading === 'lazy').length,
          imagesWithSrcset: images.filter(img => img.srcset).length,
          largeImages: images.filter(img => {
            const rect = img.getBoundingClientRect();
            return rect.width > 1000 || rect.height > 1000;
          }).length,
        };
      });
      
      // Image optimization checks
      expect(imageMetrics.imagesWithAlt).toBe(imageMetrics.totalImages); // All images have alt text
      expect(imageMetrics.imagesWithLazyLoading / imageMetrics.totalImages).toBeGreaterThan(0.5); // >50% lazy loaded
      expect(imageMetrics.largeImages).toBeLessThan(3); // Max 2 large images
    });
  });

  test.describe('JavaScript Performance', () => {
    test('should have minimal main thread blocking', async ({ page }) => {
      await page.goto('/');
      
      // Measure long tasks
      const longTasks = await page.evaluate(() => {
        return new Promise((resolve) => {
          const tasks: number[] = [];
          
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              tasks.push(entry.duration);
            }
          }).observe({ entryTypes: ['longtask'] });
          
          setTimeout(() => resolve(tasks), 5000);
        });
      });
      
      // Should have minimal long tasks (>50ms)
      expect(longTasks.length).toBeLessThan(5);
      
      // No single task should block for >200ms
      longTasks.forEach(duration => {
        expect(duration).toBeLessThan(200);
      });
    });

    test('should handle large datasets efficiently', async ({ page }) => {
      // Navigate to page with large dataset (e.g., evidence list)
      await helpers.navigateAndWait('/evidence');
      
      const startTime = Date.now();
      
      // Simulate loading large dataset
      await page.evaluate(() => {
        // Trigger loading of large dataset
        const event = new CustomEvent('loadLargeDataset');
        document.dispatchEvent(event);
      });
      
      // Wait for data to load
      await page.waitForSelector('[data-testid="evidence-list"]', { timeout: 10000 });
      
      const loadTime = Date.now() - startTime;
      
      // Should load large dataset within reasonable time
      expect(loadTime).toBeLessThan(5000);
      
      // Check for virtual scrolling or pagination
      const hasVirtualization = await page.evaluate(() => {
        const list = document.querySelector('[data-testid="evidence-list"]');
        return list?.getAttribute('data-virtualized') === 'true' ||
               document.querySelector('[data-testid="pagination"]') !== null;
      });
      
      expect(hasVirtualization).toBe(true);
    });
  });

  test.describe('Memory Usage', () => {
    test('should not have memory leaks in SPA navigation', async ({ page }) => {
      // Get initial memory usage
      const initialMemory = await page.evaluate(() => {
        return (performance as any).memory?.usedJSHeapSize || 0;
      });
      
      // Navigate through multiple pages
      const pages = ['/dashboard', '/assessments', '/evidence', '/policies', '/dashboard'];
      
      for (const pagePath of pages) {
        await helpers.navigateAndWait(pagePath);
        await page.waitForTimeout(1000); // Allow for cleanup
      }
      
      // Force garbage collection if available
      await page.evaluate(() => {
        if ((window as any).gc) {
          (window as any).gc();
        }
      });
      
      const finalMemory = await page.evaluate(() => {
        return (performance as any).memory?.usedJSHeapSize || 0;
      });
      
      // Memory should not increase significantly (allow 50% increase)
      if (initialMemory > 0 && finalMemory > 0) {
        const memoryIncrease = (finalMemory - initialMemory) / initialMemory;
        expect(memoryIncrease).toBeLessThan(0.5);
      }
    });
  });

  test.describe('Network Performance', () => {
    test('should minimize API calls', async ({ page }) => {
      const apiCalls: string[] = [];
      
      // Monitor network requests
      page.on('request', (request) => {
        if (request.url().includes('/api/')) {
          apiCalls.push(request.url());
        }
      });
      
      await helpers.navigateAndWait('/dashboard');
      
      // Wait for all API calls to complete
      await page.waitForLoadState('networkidle');
      
      // Should make reasonable number of API calls
      expect(apiCalls.length).toBeLessThan(10);
      
      // Check for duplicate API calls
      const uniqueCalls = new Set(apiCalls);
      expect(uniqueCalls.size).toBe(apiCalls.length);
    });

    test('should implement proper caching', async ({ page }) => {
      // First visit
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      const firstVisitRequests: string[] = [];
      
      page.on('request', (request) => {
        firstVisitRequests.push(request.url());
      });
      
      // Second visit (should use cache)
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      // Check cache headers
      const cachedResources = await page.evaluate(() => {
        const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
        return resources.filter(resource => 
          resource.transferSize === 0 && resource.decodedBodySize > 0
        ).length;
      });
      
      // Should have some cached resources
      expect(cachedResources).toBeGreaterThan(0);
    });
  });

  test.describe('Mobile Performance', () => {
    test('should perform well on mobile devices', async ({ page }) => {
      // Simulate mobile device
      await page.setViewportSize({ width: 375, height: 667 });
      
      // Throttle network and CPU
      const client = await page.context().newCDPSession(page);
      await client.send('Network.emulateNetworkConditions', {
        offline: false,
        downloadThroughput: 1.5 * 1024 * 1024 / 8, // 1.5 Mbps
        uploadThroughput: 750 * 1024 / 8, // 750 Kbps
        latency: 40, // 40ms
      });
      
      await client.send('Emulation.setCPUThrottlingRate', { rate: 4 });
      
      const startTime = Date.now();
      await helpers.navigateAndWait('/');
      const loadTime = Date.now() - startTime;
      
      // Should load within mobile performance budget
      expect(loadTime).toBeLessThan(5000);
      
      // Check for mobile-specific optimizations
      const mobileOptimizations = await page.evaluate(() => {
        return {
          hasViewportMeta: !!document.querySelector('meta[name="viewport"]'),
          hasTouchOptimization: document.body.style.touchAction !== '',
          hasPreloadLinks: document.querySelectorAll('link[rel="preload"]').length > 0,
        };
      });
      
      expect(mobileOptimizations.hasViewportMeta).toBe(true);
    });
  });
});
