#!/usr/bin/env node

/**
 * Verify E2E test setup
 * Run with: npx tsx tests/e2e/verify-setup.ts
 */

import { chromium } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function verifySetup() {
  const results = {
    playwright: false,
    browsers: false,
    testDir: false,
    resultsDir: false,
    config: false,
    helpers: false,
  };

  // 1. Check if Playwright is installed
  try {
    const playwrightVersion = require('@playwright/test/package.json').version;
    results.playwright = true;
  } catch (error) {
  }

  // 2. Check if browsers are installed
  try {
    const browser = await chromium.launch();
    await browser.close();
    results.browsers = true;
  } catch (error) {
  }

  // 3. Check test directory structure
  const testDirs = ['tests/e2e', 'tests/e2e/fixtures', 'tests/e2e/utils'];

  const missingDirs = testDirs.filter((dir) => !fs.existsSync(dir));
  if (missingDirs.length === 0) {
    results.testDir = true;
  } else {
  }

  // 4. Check test results directory
  if (fs.existsSync('test-results')) {
    results.resultsDir = true;
  } else {
    fs.mkdirSync('test-results', { recursive: true });
    fs.mkdirSync('test-results/screenshots', { recursive: true });
    results.resultsDir = true;
  }

  // 5. Check Playwright config
  if (fs.existsSync('playwright.config.ts')) {
    results.config = true;
  } else {
  }

  // 6. Check test helpers and fixtures
  const requiredFiles = [
    'tests/e2e/utils/test-helpers.ts',
    'tests/e2e/fixtures/test-selectors.ts',
    'tests/e2e/global-setup.ts',
    'tests/e2e/global-teardown.ts',
  ];

  const missingFiles = requiredFiles.filter((file) => !fs.existsSync(file));
  if (missingFiles.length === 0) {
    results.helpers = true;
  } else {
  }

  // Summary
  const allPassed = Object.values(results).every((v) => v);

  if (allPassed) {
  } else {
  }

  process.exit(allPassed ? 0 : 1);
}

// Run verification
verifySetup().catch(console.error);
