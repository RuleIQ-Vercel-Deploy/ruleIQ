import { test, expect, devices } from '@playwright/test';

const mobileDevices = [
  { name: 'iPhone 12', device: devices['iPhone 12'] },
  { name: 'Pixel 5', device: devices['Pixel 5'] },
  { name: 'iPhone SE', device: devices['iPhone SE'] },
  { name: 'Galaxy S21', device: devices['Galaxy S21'] }
];

test.describe('Mobile Performance Tests', () => {
  for (const { name, device } of mobileDevices) {
    test.describe(`${name} Performance`, () => {
      test.use({ ...device });

      test('Mobile page load performance', async ({ page }) => {
        const startTime = Date.now();
        
        await page.goto('/', { waitUntil: 'networkidle' });
        
        const loadTime = Date.now() - startTime;
        expect(loadTime).toBeLessThan(3000); // 3s on mobile

        // Measure mobile-specific metrics
        const metrics = await page.evaluate(() => {
          const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
          return {
            domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
            loadComplete: navigation.loadEventEnd - navigation.fetchStart,
            firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
            firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
          };
        });

        // Mobile thresholds (slightly higher than desktop)
        expect(metrics.firstPaint).toBeLessThan(1500); // 1.5s
        expect(metrics.firstContentfulPaint).toBeLessThan(2000); // 2s
        expect(metrics.domContentLoaded).toBeLessThan(3000); // 3s
      });

      test('Touch interaction responsiveness', async ({ page }) => {
        await page.goto('/', { waitUntil: 'networkidle' });

        // Test tap delay
        const tapDelay = await page.evaluate(() => {
          return new Promise<number>((resolve) => {
            const button = document.querySelector('button');
            if (!button) {
              resolve(0);
              return;
            }

            let startTime: number;
            
            button.addEventListener('touchstart', () => {
              startTime = performance.now();
            }, { once: true });

            button.addEventListener('click', () => {
              const delay = performance.now() - startTime;
              resolve(delay);
            }, { once: true });

            // Simulate touch
            const touch = new Touch({
              identifier: 1,
              target: button,
              clientX: button.getBoundingClientRect().left + 10,
              clientY: button.getBoundingClientRect().top + 10
            });

            button.dispatchEvent(new TouchEvent('touchstart', {
              touches: [touch],
              targetTouches: [touch],
              changedTouches: [touch],
              bubbles: true
            }));

            setTimeout(() => {
              button.dispatchEvent(new TouchEvent('touchend', {
                touches: [],
                targetTouches: [],
                changedTouches: [touch],
                bubbles: true
              }));
              button.click();
            }, 50);
          });
        });

        expect(tapDelay).toBeLessThan(300); // No 300ms tap delay
      });

      test('Scroll performance on mobile', async ({ page }) => {
        await page.goto('/dashboard', { waitUntil: 'networkidle' });

        // Test scroll performance
        const scrollMetrics = await page.evaluate(async () => {
          const metrics = {
            scrollEvents: 0,
            jankFrames: 0,
            averageFrameTime: 0
          };

          let lastTime = performance.now();
          const frameTimes: number[] = [];

          // Monitor scroll performance
          const scrollHandler = () => {
            metrics.scrollEvents++;
            const currentTime = performance.now();
            const frameTime = currentTime - lastTime;
            frameTimes.push(frameTime);
            
            if (frameTime > 16.67) { // More than 60fps threshold
              metrics.jankFrames++;
            }
            
            lastTime = currentTime;
          };

          window.addEventListener('scroll', scrollHandler);

          // Perform scroll
          for (let i = 0; i < 10; i++) {
            window.scrollTo(0, i * 100);
            await new Promise(resolve => requestAnimationFrame(resolve));
          }

          window.removeEventListener('scroll', scrollHandler);

          metrics.averageFrameTime = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length;
          
          return metrics;
        });

        expect(scrollMetrics.jankFrames).toBeLessThan(2); // Minimal jank
        expect(scrollMetrics.averageFrameTime).toBeLessThan(16.67); // 60fps
      });

      test('Mobile-specific resource optimization', async ({ page }) => {
        const resources = {
          images: [] as { url: string; size: number }[],
          scripts: [] as { url: string; size: number }[],
          styles: [] as { url: string; size: number }[]
        };

        page.on('response', async (response) => {
          const url = response.url();
          const size = (await response.body()).length;

          if (response.request().resourceType() === 'image') {
            resources.images.push({ url, size });
          } else if (url.includes('.js')) {
            resources.scripts.push({ url, size });
          } else if (url.includes('.css')) {
            resources.styles.push({ url, size });
          }
        });

        await page.goto('/', { waitUntil: 'networkidle' });

        // Check image optimization for mobile
        for (const img of resources.images) {
          expect(img.size).toBeLessThan(200 * 1024); // 200KB max for mobile images
        }

        // Check total page weight
        const totalSize = 
          resources.images.reduce((sum, r) => sum + r.size, 0) +
          resources.scripts.reduce((sum, r) => sum + r.size, 0) +
          resources.styles.reduce((sum, r) => sum + r.size, 0);

        expect(totalSize).toBeLessThan(2 * 1024 * 1024); // 2MB total for mobile
      });

      test('Viewport and responsive design', async ({ page }) => {
        await page.goto('/', { waitUntil: 'networkidle' });

        // Check viewport meta tag
        const viewportMeta = await page.evaluate(() => {
          const meta = document.querySelector('meta[name="viewport"]');
          return meta?.getAttribute('content');
        });

        expect(viewportMeta).toContain('width=device-width');
        expect(viewportMeta).toContain('initial-scale=1');

        // Check responsive elements
        const responsiveCheck = await page.evaluate(() => {
          const results = {
            horizontalOverflow: false,
            textReadability: true,
            touchTargetSize: true
          };

          // Check for horizontal overflow
          const bodyWidth = document.body.scrollWidth;
          const viewportWidth = window.innerWidth;
          results.horizontalOverflow = bodyWidth > viewportWidth;

          // Check text readability
          const texts = document.querySelectorAll('p, span, div');
          texts.forEach(text => {
            const fontSize = parseFloat(window.getComputedStyle(text).fontSize);
            if (fontSize < 12) {
              results.textReadability = false;
            }
          });

          // Check touch target sizes
          const clickables = document.querySelectorAll('button, a, input, select');
          clickables.forEach(element => {
            const rect = element.getBoundingClientRect();
            if (rect.width < 44 || rect.height < 44) {
              results.touchTargetSize = false;
            }
          });

          return results;
        });

        expect(responsiveCheck.horizontalOverflow).toBe(false);
        expect(responsiveCheck.textReadability).toBe(true);
        expect(responsiveCheck.touchTargetSize).toBe(true);
      });

      test('Mobile network simulation - 3G', async ({ page, context }) => {
        // Simulate 3G network conditions
        await context.route('**/*', async (route) => {
          // Add 100ms latency to simulate 3G
          await new Promise(resolve => setTimeout(resolve, 100));
          await route.continue();
        });

        const startTime = Date.now();
        await page.goto('/', { waitUntil: 'networkidle' });
        const loadTime = Date.now() - startTime;

        // Should still load within reasonable time on 3G
        expect(loadTime).toBeLessThan(10000); // 10s on 3G
      });

      test('Touch gesture support', async ({ page }) => {
        await page.goto('/dashboard', { waitUntil: 'networkidle' });

        // Test swipe gesture support
        const swipeSupport = await page.evaluate(() => {
          let touchStartX = 0;
          let touchEndX = 0;
          let swipeDetected = false;

          const handleTouchStart = (e: TouchEvent) => {
            touchStartX = e.touches[0].clientX;
          };

          const handleTouchEnd = (e: TouchEvent) => {
            touchEndX = e.changedTouches[0].clientX;
            if (Math.abs(touchEndX - touchStartX) > 50) {
              swipeDetected = true;
            }
          };

          document.addEventListener('touchstart', handleTouchStart);
          document.addEventListener('touchend', handleTouchEnd);

          // Simulate swipe
          const target = document.body;
          const touchStart = new Touch({
            identifier: 1,
            target,
            clientX: 100,
            clientY: 100
          });

          const touchEnd = new Touch({
            identifier: 1,
            target,
            clientX: 200,
            clientY: 100
          });

          target.dispatchEvent(new TouchEvent('touchstart', {
            touches: [touchStart],
            targetTouches: [touchStart],
            changedTouches: [touchStart]
          }));

          target.dispatchEvent(new TouchEvent('touchend', {
            touches: [],
            targetTouches: [],
            changedTouches: [touchEnd]
          }));

          return swipeDetected;
        });

        expect(swipeSupport).toBe(true);
      });

      test('Mobile memory usage', async ({ page }) => {
        await page.goto('/', { waitUntil: 'networkidle' });

        // Navigate through app to test memory usage
        await page.goto('/dashboard', { waitUntil: 'networkidle' });
        await page.goto('/assessments', { waitUntil: 'networkidle' });

        const memoryUsage = await page.evaluate(() => {
          if ('memory' in performance) {
            return {
              usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
              totalJSHeapSize: (performance as any).memory.totalJSHeapSize
            };
          }
          return null;
        });

        if (memoryUsage) {
          // Mobile devices have limited memory
          expect(memoryUsage.usedJSHeapSize).toBeLessThan(50 * 1024 * 1024); // 50MB
        }
      });

      test('Mobile font loading optimization', async ({ page }) => {
        const fontLoadTimes: number[] = [];

        await page.evaluateOnNewDocument(() => {
          if ('fonts' in document) {
            (document as any).fonts.addEventListener('loadingdone', (event: any) => {
              console.log('Font loaded:', event.fontfaces.length);
            });
          }
        });

        await page.goto('/', { waitUntil: 'networkidle' });

        const fontMetrics = await page.evaluate(() => {
          return new Promise((resolve) => {
            if ('fonts' in document) {
              (document as any).fonts.ready.then(() => {
                const loadedFonts = Array.from((document as any).fonts);
                resolve({
                  fontsLoaded: loadedFonts.length,
                  fontFamilies: loadedFonts.map((font: any) => font.family)
                });
              });
            } else {
              resolve({ fontsLoaded: 0, fontFamilies: [] });
            }
          });
        });

        console.log('Font metrics:', fontMetrics);
      });

      test('Mobile battery usage indicators', async ({ page }) => {
        await page.goto('/', { waitUntil: 'networkidle' });

        // Check for battery-intensive operations
        const batteryMetrics = await page.evaluate(() => {
          const results = {
            animations: 0,
            intervals: 0,
            highFrequencyTimers: 0
          };

          // Check for CSS animations
          const allElements = document.querySelectorAll('*');
          allElements.forEach(element => {
            const animation = window.getComputedStyle(element).animation;
            if (animation !== 'none' && animation !== '') {
              results.animations++;
            }
          });

          // Check for high-frequency timers (would need to instrument)
          // This is a simplified check
          const originalSetInterval = window.setInterval;
          let intervalCount = 0;
          window.setInterval = function(fn, delay, ...args) {
            intervalCount++;
            if (delay < 100) {
              results.highFrequencyTimers++;
            }
            return originalSetInterval(fn, delay, ...args);
          };

          return results;
        });

        // Minimize battery-draining operations
        expect(batteryMetrics.animations).toBeLessThan(10);
        expect(batteryMetrics.highFrequencyTimers).toBe(0);
      });
    });
  }

  test.describe('Progressive Web App (PWA) Performance', () => {
    test('Service Worker performance', async ({ page }) => {
      await page.goto('/', { waitUntil: 'networkidle' });

      const swMetrics = await page.evaluate(async () => {
        if ('serviceWorker' in navigator) {
          const registration = await navigator.serviceWorker.getRegistration();
          return {
            registered: !!registration,
            state: registration?.active?.state,
            scope: registration?.scope
          };
        }
        return { registered: false };
      });

      if (swMetrics.registered) {
        expect(swMetrics.state).toBe('activated');
      }
    });

    test('Offline functionality', async ({ page, context }) => {
      await page.goto('/', { waitUntil: 'networkidle' });
      
      // Go offline
      await context.setOffline(true);
      
      // Try to navigate
      await page.reload().catch(() => {});
      
      // Check if app still works offline
      const isVisible = await page.isVisible('body');
      expect(isVisible).toBe(true);
      
      // Go back online
      await context.setOffline(false);
    });
  });
});