import { PlaywrightTestConfig } from '@playwright/test';

/**
 * Configuration specifically for visual regression tests
 * Optimized for consistency across different environments
 */

const config: PlaywrightTestConfig = {
  // Test directory
  testDir: '.',
  
  // Test match pattern
  testMatch: ['**/*.test.{ts,tsx}'],
  
  // Timeout for each test
  timeout: 60 * 1000,
  
  // Number of retries for flaky tests
  retries: process.env['CI'] ? 2 : 0,
  
  // Number of workers
  workers: process.env['CI'] ? 2 : 4,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report/visual' }],
    ['json', { outputFile: 'test-results/visual-results.json' }],
    ['junit', { outputFile: 'test-results/visual-junit.xml' }],
  ],
  
  // Global test configuration
  use: {
    // Base URL
    baseURL: process.env['PLAYWRIGHT_BASE_URL'] || 'http://localhost:3000',
    
    // Screenshot options
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true,
    },
    
    // Video recording
    video: process.env['CI'] ? 'retain-on-failure' : 'off',
    
    // Trace recording
    trace: process.env['CI'] ? 'on-first-retry' : 'off',
    
    // Viewport
    viewport: { width: 1440, height: 900 },
    
    // Device scale factor for high DPI screenshots
    deviceScaleFactor: 2,
    
    // Disable animations for consistent screenshots
    launchOptions: {
      args: ['--disable-web-animations'],
    },
    
    // Color scheme
    colorScheme: 'light',
    
    // Locale
    locale: 'en-US',
    
    // Timezone
    timezoneId: 'America/New_York',
  },
  
  // Project configuration for different browsers and viewports
  projects: [
    // Desktop browsers
    {
      name: 'chromium-desktop',
      use: {
        ...require('@playwright/test').devices['Desktop Chrome'],
        viewport: { width: 1440, height: 900 },
      },
    },
    {
      name: 'firefox-desktop',
      use: {
        ...require('@playwright/test').devices['Desktop Firefox'],
        viewport: { width: 1440, height: 900 },
      },
    },
    {
      name: 'webkit-desktop',
      use: {
        ...require('@playwright/test').devices['Desktop Safari'],
        viewport: { width: 1440, height: 900 },
      },
    },
    
    // Mobile devices
    {
      name: 'mobile-chrome',
      use: {
        ...require('@playwright/test').devices['Pixel 5'],
      },
    },
    {
      name: 'mobile-safari',
      use: {
        ...require('@playwright/test').devices['iPhone 13'],
      },
    },
    
    // Tablet devices
    {
      name: 'tablet-chrome',
      use: {
        ...require('@playwright/test').devices['iPad Pro'],
      },
    },
    
    // Dark mode variants
    {
      name: 'chromium-dark',
      use: {
        ...require('@playwright/test').devices['Desktop Chrome'],
        viewport: { width: 1440, height: 900 },
        colorScheme: 'dark',
      },
    },
  ],
  
  // Visual regression specific settings
  expect: {
    // Threshold for pixel differences
    toHaveScreenshot: {
      // Maximum difference in pixels
      maxDiffPixels: 100,
      
      // Threshold between 0-1 for pixel difference ratio
      threshold: 0.2,
      
      // Animation handling
      animations: 'disabled',
      
      // CSS animations
      caret: 'hide',
      
      // Screenshot scale
      scale: 'device',
    },
  },
  
  // Output directory for test results
  outputDir: 'test-results/visual',
  
  // Preserve output between test runs
  preserveOutput: 'failures-only',
  
  // Quiet mode
  quiet: false,
  
  // Update snapshots
  updateSnapshots: process.env['UPDATE_SNAPSHOTS'] === 'true' ? 'all' : 'missing',
  
  // Web server configuration for local testing
  webServer: process.env['CI'] ? undefined : {
    command: 'pnpm dev',
    port: 3000,
    timeout: 120 * 1000,
    reuseExistingServer: true,
  },
};

export default config;