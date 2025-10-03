import { type FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  try {
    // Clean up test data if needed
    // await cleanupTestData();
    // Clean up test files
    // await cleanupTestFiles();
  } catch (error) {
    // Development logging - consider proper logger

    console.error('❌ Global teardown failed:', error);
    // Don't throw here to avoid masking test failures
  }
}

export default globalTeardown;
