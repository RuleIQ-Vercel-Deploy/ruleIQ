import { chromium, type FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  // TODO: Replace with proper logging
  // Ensure test results directories exist
  const dirs = ['test-results', 'test-results/screenshots', 'playwright-report'];
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  // Create a browser instance for setup with robust options
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process',
    ],
  });

  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1280, height: 720 },
  });

  const page = await context.newPage();

  // Set up console logging for debugging
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      // TODO: Replace with proper logging
    }
  });

  page.on('pageerror', (err) => {
    // TODO: Replace with proper logging
  });

  try {
    // Wait for the application to be ready
    // TODO: Replace with proper logging
    const baseURL = config.projects[0].use?.baseURL || 'http://localhost:3000';

    // Try multiple times to ensure the server is ready
    let retries = 5;
    let isReady = false;

    while (retries > 0 && !isReady) {
      try {
        const response = await page.goto(baseURL, {
          waitUntil: 'domcontentloaded',
          timeout: 20000,
        });

        if (response && response.ok()) {
          isReady = true;
        }
      } catch (error) {
        // TODO: Replace with proper logging
        retries--;
        if (retries > 0) {
          await new Promise((resolve) => setTimeout(resolve, 3000));
        }
      }
    }

    if (!isReady) {
      throw new Error('Server did not become ready in time');
    }

    // Wait for the main content to load
    await page.waitForSelector('body', { timeout: 30000 });

    // Additional wait for any React/Next.js hydration
    await page.waitForTimeout(2000);

    // Check if the app is running properly
    const title = await page.title();
    // TODO: Replace with proper logging
    // Check for critical errors
    const hasErrors = await page.evaluate(() => {
      return (
        window.document.body.innerHTML.includes('Error') ||
        window.document.body.innerHTML.includes('error')
      );
    });

    if (hasErrors) {
      console.warn('⚠️  Warning: Page may contain errors, but continuing with tests');
    }

    // Create test user if needed (optional)
    // await createTestUser(page);
  } catch (error) {
    // Development logging - consider proper logger

    console.error('❌ Global setup failed:', error);
    // Take a screenshot for debugging
    await page.screenshot({
      path: 'test-results/screenshots/setup-error.png',
      fullPage: true,
    });
    throw error;
  } finally {
    await context.close();
    await browser.close();
  }
  // TODO: Replace with proper logging
}

// Helper function to create test user (uncomment if needed)
// async function createTestUser(page: Page) {
//   // Implementation for creating test user
// }

export default globalSetup;
