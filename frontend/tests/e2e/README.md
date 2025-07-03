# E2E Testing Guide for ruleIQ

This directory contains end-to-end tests for the ruleIQ frontend application using Playwright.

## 📁 Directory Structure

```
tests/e2e/
├── fixtures/           # Test data and files
│   ├── test-data.ts    # Test data constants
│   └── *.pdf           # Sample files for upload tests
├── utils/              # Test utilities and helpers
│   └── test-helpers.ts # Page object models and utilities
├── *.test.ts          # Test files
├── global-setup.ts    # Global test setup
├── global-teardown.ts # Global test cleanup
└── README.md          # This file
```

## 🧪 Test Files

### Core User Journeys
- **`smoke.test.ts`** - Basic smoke tests for critical functionality
- **`auth.test.ts`** - Authentication flow (login, register, logout)
- **`business-profile.test.ts`** - Business profile setup and management
- **`assessment-flow.test.ts`** - Assessment creation and completion
- **`evidence-management.test.ts`** - Evidence upload and management

### Test Coverage
- ✅ User authentication and session management
- ✅ Business profile wizard and management
- ✅ Assessment framework selection and execution
- ✅ Evidence upload, categorization, and approval
- ✅ Dashboard functionality and navigation
- ✅ Responsive design and mobile compatibility
- ✅ Error handling and validation

## 🚀 Running Tests

### Prerequisites
```bash
# Install dependencies
pnpm install

# Install Playwright browsers
pnpm exec playwright install
```

### Test Commands
```bash
# Run all E2E tests
pnpm test:e2e

# Run tests with UI mode (interactive)
pnpm test:e2e:ui

# Run tests in headed mode (see browser)
pnpm test:e2e:headed

# Run specific test file
pnpm test:e2e tests/e2e/auth.test.ts

# Run smoke tests only
pnpm test:e2e:smoke

# Debug tests
pnpm test:e2e:debug
```

### Browser Testing
Tests run on multiple browsers by default:
- Chromium (Chrome/Edge)
- Firefox
- WebKit (Safari)
- Mobile Chrome
- Mobile Safari

## 🛠️ Test Utilities

### TestHelpers Class
Base class providing common functionality:
- Navigation and waiting utilities
- Form filling and interaction helpers
- Screenshot and debugging tools
- API mocking capabilities

### Specialized Helpers
- **AuthHelpers** - Authentication-specific actions
- **BusinessProfileHelpers** - Profile setup and management
- **AssessmentHelpers** - Assessment flow actions
- **EvidenceHelpers** - Evidence management actions

### Example Usage
```typescript
import { test, expect } from '@playwright/test';
import { AuthHelpers } from './utils/test-helpers';

test('should login successfully', async ({ page }) => {
  const authHelpers = new AuthHelpers(page);
  
  await authHelpers.login('user@example.com', 'password');
  await expect(page).toHaveURL(/\/dashboard/);
});
```

## 📊 Test Data

### Fixtures
Test data is organized in `fixtures/test-data.ts`:
- **TEST_USERS** - User credentials for different scenarios
- **BUSINESS_PROFILES** - Sample business profile data
- **ASSESSMENT_DATA** - Assessment questions and answers
- **EVIDENCE_DATA** - Sample evidence metadata

### Dynamic Data Generation
```typescript
import { generateTestData } from './fixtures/test-data';

const user = generateTestData.user();
const profile = generateTestData.businessProfile();
```

## 🎯 Best Practices

### Test Organization
- Group related tests using `test.describe()`
- Use descriptive test names that explain the expected behavior
- Keep tests independent and isolated
- Use `test.beforeEach()` for common setup

### Data Management
- Use unique test data to avoid conflicts
- Clean up test data after tests complete
- Use fixtures for consistent test scenarios
- Mock external API calls when appropriate

### Assertions
- Use specific, meaningful assertions
- Test both positive and negative scenarios
- Verify UI state changes after actions
- Check for proper error handling

### Performance
- Use `page.waitForLoadState('networkidle')` for dynamic content
- Implement proper waiting strategies
- Take screenshots only when necessary
- Use parallel execution for faster test runs

## 🔧 Configuration

### Playwright Config
Key configuration options in `playwright.config.ts`:
- **baseURL** - Application URL for testing
- **timeout** - Global test timeout
- **retries** - Number of retries on failure
- **workers** - Parallel execution workers
- **reporter** - Test result reporting format

### Environment Variables
```bash
# Set base URL for testing
PLAYWRIGHT_BASE_URL=http://localhost:3000

# Enable debug mode
DEBUG=pw:api
```

## 📈 CI/CD Integration

### GitHub Actions
Tests are automatically run on:
- Pull requests to main/develop branches
- Pushes to main/develop branches
- Manual workflow dispatch

### Test Reports
- HTML reports generated for each test run
- Screenshots and videos captured on failures
- Test results uploaded as artifacts

## 🐛 Debugging

### Debug Mode
```bash
# Run tests in debug mode
pnpm test:e2e:debug

# Run specific test in debug mode
pnpm exec playwright test auth.test.ts --debug
```

### Screenshots and Videos
- Screenshots taken automatically on test failures
- Videos recorded for failed tests
- Manual screenshots: `await helpers.takeScreenshot('description')`

### Browser DevTools
```bash
# Open browser with DevTools
pnpm exec playwright test --headed --debug
```

## 📝 Writing New Tests

### Test Template
```typescript
import { test, expect } from '@playwright/test';
import { TestHelpers } from './utils/test-helpers';

test.describe('Feature Name', () => {
  let helpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    // Common setup
  });

  test('should perform expected behavior', async ({ page }) => {
    // Test implementation
    await helpers.navigateAndWait('/path');
    await expect(page.locator('[data-testid="element"]')).toBeVisible();
  });
});
```

### Data Test IDs
Use consistent `data-testid` attributes for reliable element selection:
```html
<button data-testid="submit-button">Submit</button>
<form data-testid="login-form">...</form>
<div data-testid="error-message">Error text</div>
```

## 🔍 Troubleshooting

### Common Issues
1. **Timeouts** - Increase timeout or improve waiting strategies
2. **Flaky tests** - Add proper waits and stabilize test data
3. **Element not found** - Verify selectors and page state
4. **Network issues** - Mock external dependencies

### Debug Commands
```bash
# Show test trace
pnpm exec playwright show-trace trace.zip

# Generate test code
pnpm exec playwright codegen localhost:3000

# Show test report
pnpm exec playwright show-report
```

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/)
- [Best Practices Guide](https://playwright.dev/docs/best-practices)
- [API Reference](https://playwright.dev/docs/api/class-playwright)
- [Test Generator](https://playwright.dev/docs/codegen)

## 🤝 Contributing

When adding new tests:
1. Follow the existing test structure and naming conventions
2. Add appropriate test data to fixtures
3. Update this README if adding new test categories
4. Ensure tests pass in all browsers
5. Add proper error handling and cleanup
