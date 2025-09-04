# E2E Test Setup Guide for ruleIQ

## ✅ Setup Status

The E2E test infrastructure is now properly configured and ready to use.

### What's Been Fixed:

1. **Playwright Installation**: Browsers installed (`v1.53.1`)
2. **Test Configuration**: `playwright.config.ts` properly configured
3. **Directory Structure**: All required directories created
4. **Test Helpers**: Utility classes and selectors configured
5. **Global Setup/Teardown**: Application readiness checks implemented

## 📁 Directory Structure

```
tests/e2e/
├── fixtures/
│   ├── test-data.ts         # Test data constants
│   ├── test-selectors.ts    # Reusable selectors
│   └── test-document.pdf    # Sample test file
├── utils/
│   └── test-helpers.ts      # Helper classes for tests
├── global-setup.ts          # Pre-test setup
├── global-teardown.ts       # Post-test cleanup
├── verify-setup.ts          # Setup verification script
├── smoke-updated.test.ts    # Working smoke tests
└── *.test.ts               # Various test suites
```

## 🚀 Running E2E Tests

### Available Commands:

```bash
# Run all E2E tests
pnpm test:e2e

# Run tests with UI mode (recommended for debugging)
pnpm test:e2e:ui

# Run tests with browser visible
pnpm test:e2e:headed

# Run tests in debug mode
pnpm test:e2e:debug

# Run specific test file
pnpm exec playwright test tests/e2e/smoke-updated.test.ts

# Run tests for specific browser
pnpm exec playwright test --project=chromium
```

### Verify Setup:

```bash
# Run setup verification
npx tsx tests/e2e/verify-setup.ts
```

## 📝 Writing E2E Tests

### Best Practices:

1. **Use Flexible Selectors**: The app doesn't use data-testid attributes consistently, so use semantic selectors:
   ```typescript
   // Good
   await page.locator('input[type="email"]')
   await page.locator('button[type="submit"]')
   await page.locator('text=Login')
   
   // Avoid (unless data-testid exists)
   await page.locator('[data-testid="login-form"]')
   ```

2. **Use Test Helpers**: Import and use the helper classes:
   ```typescript
   import { TestHelpers } from './utils/test-helpers';
   import { TestSelectors } from './fixtures/test-selectors';
   ```

3. **Handle Loading States**: Always wait for content to be ready:
   ```typescript
   await helpers.navigateAndWait('/login');
   await helpers.waitForLoadingToComplete();
   ```

4. **Error Handling**: Filter out non-critical console errors:
   ```typescript
   const criticalErrors = errors.filter(error => 
     !error.includes('favicon.ico') && 
     !error.includes('Extension context invalidated') &&
     !error.includes('ResizeObserver')
   );
   ```

## 🔧 Common Issues & Solutions

### Issue: Tests timing out
**Solution**: Increase timeout in specific tests or globally in playwright.config.ts

### Issue: Selectors not found
**Solution**: Use the browser DevTools to inspect actual element attributes and update selectors accordingly

### Issue: Flaky tests
**Solution**: Add proper wait conditions and use `waitForLoadState('networkidle')`

### Issue: Authentication failures
**Solution**: Ensure test user exists or mock authentication for E2E tests

## 📊 Test Results

Test results are saved in:
- `test-results/` - Test artifacts
- `test-results/screenshots/` - Screenshots on failure
- HTML report opens automatically after test run

## 🎯 Next Steps

1. **Add data-testid attributes** to key components for more reliable testing
2. **Create test fixtures** for common test data
3. **Implement API mocking** for isolated testing
4. **Add visual regression tests** using Playwright's screenshot comparison
5. **Set up CI/CD integration** for automated test runs

## 📚 Example Test

Here's a working example test that follows best practices:

```typescript
import { test, expect } from '@playwright/test';
import { TestHelpers } from './utils/test-helpers';

test.describe('Login Flow', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test('should login successfully', async ({ page }) => {
    // Navigate to login page
    await helpers.navigateAndWait('/login');
    
    // Fill form
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('password123');
    
    // Submit form
    await page.locator('button[type="submit"]').click();
    
    // Wait for navigation
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Verify login success
    expect(page.url()).toContain('/dashboard');
  });
});
```

## 🔗 Resources

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Writing Tests](https://playwright.dev/docs/writing-tests)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [CI/CD Integration](https://playwright.dev/docs/ci)