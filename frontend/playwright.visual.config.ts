import { defineConfig, devices } from '@playwright/test';
import baseConfig from './playwright.config';

/**
 * Configuration specifically for visual regression tests
 * Extends the base configuration with visual testing specific settings
 */
export default defineConfig({
  ...baseConfig,
  
  // Override test directory for visual tests
  testDir: './tests/visual',
  
  // Visual test specific reporters
  reporter: [
    ['html', { outputFolder: 'playwright-report/visual' }],
    ['json', { outputFile: 'test-results/visual-results.json' }],
    ['junit', { outputFile: 'test-results/visual-junit.xml' }],
  ],
  
  // Shared settings for visual tests
  use: {
    ...baseConfig.use,
    
    // Higher quality screenshots for visual testing
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true,
    },
    
    // Disable animations for consistent screenshots
    launchOptions: {
      args: ['--disable-web-animations'],
    },
    
    // High DPI screenshots
    deviceScaleFactor: 2,
    
    // Consistent viewport
    viewport: { width: 1440, height: 900 },
    
    // Video recording for debugging
    video: process.env['CI'] ? 'retain-on-failure' : 'off',
  },
  
  // Visual test specific projects
  projects: [
    // Desktop browsers
    {
      name: 'chromium-desktop',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1440, height: 900 },
        deviceScaleFactor: 2,
        launchOptions: {
          args: ['--disable-web-animations'],
        },
      },
    },
    {
      name: 'firefox-desktop',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1440, height: 900 },
        deviceScaleFactor: 2,
        launchOptions: {
          args: ['--disable-web-animations'],
        },
      },
    },
    {
      name: 'webkit-desktop',
      use: {
        ...devices['Desktop Safari'],
        viewport: { width: 1440, height: 900 },
        deviceScaleFactor: 2,
        launchOptions: {
          args: ['--disable-web-animations'],
        },
      },
    },
    
    // Mobile devices
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
        deviceScaleFactor: 2,
        launchOptions: {
          args: ['--disable-web-animations'],
        },
      },
    },
    {
      name: 'mobile-safari',
      use: {
        ...devices['iPhone 13'],
        deviceScaleFactor: 2,
        launchOptions: {
          args: ['--disable-web-animations'],
        },
      },
    },
    
    // Tablet devices
    {
      name: 'tablet-chrome',
      use: {
        ...devices['iPad Pro'],
        deviceScaleFactor: 2,
        launchOptions: {
          args: ['--disable-web-animations'],
        },
      },
    },
    
    // Dark mode variants
    {
      name: 'chromium-dark',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1440, height: 900 },
        deviceScaleFactor: 2,
        colorScheme: 'dark',
        launchOptions: {
          args: ['--disable-web-animations'],
        },
      },
    },
    {
      name: 'mobile-dark',
      use: {
        ...devices['iPhone 13'],
        deviceScaleFactor: 2,
        colorScheme: 'dark',
        launchOptions: {
          args: ['--disable-web-animations'],
        },
      },
    },
  ],
  
  // Visual regression specific expectations
  expect: {
    ...baseConfig.expect,
    toHaveScreenshot: {
      // Maximum difference in pixels
      maxDiffPixels: 100,
      
      // Threshold between 0-1 for pixel difference ratio
      threshold: 0.2,
      
      // Disable animations
      animations: 'disabled',
      
      // Hide caret
      caret: 'hide',
      
      // Wait for fonts
      fonts: 'wait',
      
      // Screenshot scale
      scale: 'device',
    },
  },
  
  // Output directory for visual test results
  outputDir: 'test-results/visual',
  
  // Screenshot directory
  snapshotDir: './tests/visual/screenshots',
  snapshotPathTemplate: '{snapshotDir}/{testFileDir}/{testFileName}-{arg}-{projectName}-{platform}{ext}',
  
  // Update snapshots mode
  updateSnapshots: process.env['UPDATE_SNAPSHOTS'] === 'true' ? 'all' : 'missing',
});