# E2E Test Configuration Guide

## Overview

This guide documents the E2E test setup for ruleIQ frontend using Playwright.

## Configuration

### Browser Automation Setup

The E2E tests are configured with the following browser automation settings:

1. **Browsers Tested**:
   - Chromium (Desktop)
   - Firefox (Desktop)
   - WebKit/Safari (Desktop)
   - Mobile Chrome (Pixel 5)
   - Mobile Safari (iPhone 12)

2. **Key Configuration Options**:

   ```typescript
   // playwright.config.ts
   {
     // Parallel execution
     fullyParallel: true,
     workers: process.env.CI ? 1 : undefined,

     // Timeouts
     timeout: 30000,           // Test timeout
     actionTimeout: 10000,     // Action timeout
     navigationTimeout: 30000, // Navigation timeout

     // Debugging
     trace: 'on-first-retry',
     screenshot: 'only-on-failure',
     video: 'retain-on-failure',

     // Browser launch options
     launchOptions: {
       args: [
         '--no-sandbox',
         '--disable-setuid-sandbox',
         '--disable-dev-shm-usage',
         '--disable-gpu',
       ],
     },
   }
   ```

3. **Global Setup**:
   - Creates test result directories
   - Verifies application is running
   - Handles retry logic for server readiness
   - Takes error screenshots if setup fails

## Running Tests

### Basic Commands

```bash
# Run all E2E tests
pnpm test:e2e

# Run tests with UI mode (interactive)
pnpm test:e2e:ui

# Run tests with browser visible
pnpm test:e2e:headed

# Run tests in debug mode
pnpm test:e2e:debug

# Run specific test file
pnpm test:e2e tests/e2e/basic-flow.test.ts

# Run tests for specific browser
pnpm test:e2e --project=chromium
pnpm test:e2e --project=firefox
pnpm test:e2e --project=webkit
```

### Verify Setup

```bash
# Check E2E test setup
npx tsx tests/e2e/verify-setup.ts
```

## Test Structure

### Test Helpers

Located in `tests/e2e/utils/test-helpers.ts`:

- `TestHelpers`: Base class with common utilities
- `AuthHelpers`: Authentication-specific helpers
- `BusinessProfileHelpers`: Business profile setup helpers
- `AssessmentHelpers`: Assessment flow helpers
- `EvidenceHelpers`: Evidence management helpers

### Test Selectors

Located in `tests/e2e/fixtures/test-selectors.ts`:

- Organized by feature area
- Uses flexible selectors that work across different implementations
- Supports both data-testid and semantic selectors

## Common Issues and Solutions

### Issue: Navigation Element Not Visible on Mobile

**Problem**: Tests fail because navigation is hidden on mobile viewports.

**Solution**: Use responsive-aware selectors:

```typescript
const desktopNav = page.locator('nav.md\\:flex').first();
const mobileMenuButton = page.locator('button[aria-label*="menu" i]').first();

const isDesktop = await desktopNav.isVisible().catch(() => false);
const isMobile = await mobileMenuButton.isVisible().catch(() => false);

expect(isDesktop || isMobile).toBeTruthy();
```

### Issue: Slow Test Execution

**Problem**: Tests take too long to run.

**Solution**:

- Use parallel execution (enabled by default)
- Run specific test files instead of all tests
- Use `--project` flag to test specific browsers

### Issue: Flaky Tests

**Problem**: Tests pass/fail inconsistently.

**Solution**:

- Add explicit waits: `await page.waitForSelector(selector)`
- Use `waitForLoadState('networkidle')` after navigation
- Increase timeouts for slow operations
- Add retry logic in global setup

### Issue: Browser Launch Failures

**Problem**: Browsers fail to launch in certain environments.

**Solution**: The configuration includes browser launch arguments:

```typescript
args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'];
```

## Best Practices

1. **Use Page Object Pattern**: Organize selectors and actions in helper classes
2. **Handle Responsive Design**: Always consider mobile/desktop differences
3. **Take Screenshots**: Use `helpers.takeScreenshot()` for debugging
4. **Filter Console Errors**: Ignore non-critical errors in production
5. **Use Flexible Selectors**: Prefer semantic selectors over brittle CSS classes

## Environment Variables

- `PLAYWRIGHT_BASE_URL`: Override base URL (default: http://localhost:3000)
- `CI`: Set to true in CI environments for different behavior
- `SLOW_MO`: Add delay between actions for debugging (milliseconds)

## Debugging

### Visual Debugging

```bash
# Run with UI mode
pnpm test:e2e:ui

# Run with browser visible
pnpm test:e2e:headed

# Debug specific test
pnpm test:e2e:debug tests/e2e/basic-flow.test.ts
```

### Trace Viewer

After test failures, traces are saved. View them with:

```bash
npx playwright show-trace test-results/[trace-file].zip
```

### Screenshots and Videos

- Screenshots: `test-results/screenshots/`
- Videos: `test-results/[test-name]/video.webm`
- HTML Report: `playwright-report/index.html`

## CI/CD Integration

The tests are configured for CI environments:

1. Single worker to avoid resource contention
2. Retry failed tests twice
3. Generate multiple report formats (HTML, JSON, JUnit)
4. Fail on `test.only` in source code

## Performance Considerations

1. **Parallel Execution**: Tests run in parallel by default
2. **Shared Setup**: Global setup runs once before all tests
3. **Smart Waits**: Use Playwright's built-in waiting strategies
4. **Resource Cleanup**: Global teardown ensures proper cleanup

## Maintenance

1. **Update Selectors**: Keep `test-selectors.ts` up to date
2. **Review Timeouts**: Adjust timeouts based on application performance
3. **Monitor Flakiness**: Track and fix flaky tests promptly
4. **Browser Updates**: Run `npx playwright install` regularly
