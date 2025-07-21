#!/usr/bin/env node

/**
 * Verify E2E test setup
 * Run with: npx tsx tests/e2e/verify-setup.ts
 */

import { chromium } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function verifySetup() {
  console.log('🔍 Verifying E2E test setup...\n');

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
    console.log(`✅ Playwright installed: v${playwrightVersion}`);
    results.playwright = true;
  } catch (error) {
    console.log('❌ Playwright not installed');
  }

  // 2. Check if browsers are installed
  try {
    const browser = await chromium.launch();
    await browser.close();
    console.log('✅ Browsers installed and working');
    results.browsers = true;
  } catch (error) {
    console.log('❌ Browsers not installed. Run: pnpm exec playwright install');
  }

  // 3. Check test directory structure
  const testDirs = ['tests/e2e', 'tests/e2e/fixtures', 'tests/e2e/utils'];

  const missingDirs = testDirs.filter((dir) => !fs.existsSync(dir));
  if (missingDirs.length === 0) {
    console.log('✅ Test directory structure exists');
    results.testDir = true;
  } else {
    console.log(`❌ Missing directories: ${missingDirs.join(', ')}`);
  }

  // 4. Check test results directory
  if (fs.existsSync('test-results')) {
    console.log('✅ Test results directory exists');
    results.resultsDir = true;
  } else {
    console.log('❌ Test results directory missing. Creating...');
    fs.mkdirSync('test-results', { recursive: true });
    fs.mkdirSync('test-results/screenshots', { recursive: true });
    results.resultsDir = true;
  }

  // 5. Check Playwright config
  if (fs.existsSync('playwright.config.ts')) {
    console.log('✅ Playwright config exists');
    results.config = true;
  } else {
    console.log('❌ Playwright config missing');
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
    console.log('✅ All test helper files exist');
    results.helpers = true;
  } else {
    console.log(`❌ Missing files: ${missingFiles.join(', ')}`);
  }

  // Summary
  console.log('\n📊 Setup Summary:');
  const allPassed = Object.values(results).every((v) => v);

  if (allPassed) {
    console.log('✅ E2E test setup is complete and ready!');
    console.log('\nYou can run tests with:');
    console.log('  pnpm test:e2e           - Run all E2E tests');
    console.log('  pnpm test:e2e:ui        - Run tests with UI mode');
    console.log('  pnpm test:e2e:headed    - Run tests with browser visible');
    console.log('  pnpm test:e2e:debug     - Run tests in debug mode');
  } else {
    console.log('❌ E2E test setup needs attention. Fix the issues above.');
  }

  process.exit(allPassed ? 0 : 1);
}

// Run verification
verifySetup().catch(console.error);
