import { defineConfig, devices } from '@playwright/test';
import path from 'path';

// Use process.env.PORT by default and fallback to 3000 if not specified.
const PORT = process.env['PORT'] || 3000;

// Set webServer.url and use.baseURL with the location of the WebServer respecting the PORT environment variable.
const baseURL = `http://localhost:${PORT}`;

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  // Timeout per test, as per the checklist.
  timeout: 30 * 1000,

  // Test directory for E2E tests.
  testDir: path.join(__dirname, 'tests/e2e'),

  // Run tests in files in parallel.
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code.
  forbidOnly: !!process.env['CI'],

  // Retry on CI only, as per the checklist (2 retries).
  retries: process.env['CI'] ? 2 : 0,

  // Set workers for parallel execution.
  // In CI, we explicitly set it to 2 as per the checklist.
  // Locally, we default to 1 to avoid resource contention.
  workers: process.env['CI'] ? 2 : 1,

  // Reporter to use. See https://playwright.dev/docs/test-reporters
  reporter: [
    ['html', { outputFolder: 'test-results/e2e-report' }],
    ['junit', { outputFile: 'test-results/e2e-results.xml' }],
  ],

  // Shared settings for all the projects below.
  use: {
    // Use baseURL so to make navigations relative.
    baseURL,

    // Collect trace when retrying the failed test.
    trace: 'on-first-retry',

    // Take screenshot on failure, as per the checklist.
    screenshot: 'only-on-failure',
  },

  // Configure projects for major browsers.
  projects: [
    {
      name: 'Desktop Chrome',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
    {
      name: 'Desktop Firefox',
      use: {
        ...devices['Desktop Firefox'],
      },
    },
    {
      name: 'Desktop Safari',
      use: {
        ...devices['Desktop Safari'],
      },
    },
    // Test against mobile viewports.
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Artifacts folder where screenshots, videos, and traces are stored.
  outputDir: 'test-results/e2e-artifacts/',

  // Run your local dev server before starting the tests.
  webServer: {
    command: 'pnpm dev',
    url: baseURL,
    timeout: 120 * 1000,
    reuseExistingServer: !process.env['CI'],
  },
});
