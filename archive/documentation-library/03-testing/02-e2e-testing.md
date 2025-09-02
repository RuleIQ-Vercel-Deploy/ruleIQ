# 🧪 E2E Test Suite Documentation

## Overview

Comprehensive end-to-end test suite for ruleIQ frontend using Playwright.

## Test Structure

```
tests/e2e/
├── auth.test.ts                    # Authentication flows
├── assessment-flow.test.ts         # Assessment wizard completion
├── evidence-upload.test.ts         # Evidence management
├── dashboard-navigation.test.ts    # Dashboard and navigation
├── homepage.spec.ts               # Homepage smoke tests
├── fixtures/
│   ├── test-data.ts               # Test data constants
│   ├── test-selectors.ts          # Reusable selectors
│   └── test-document.pdf          # Test file for uploads
└── README.md                      # This documentation
```

## Test Coverage

### ✅ Authentication Flow

- User registration with validation
- User login with credentials
- Password reset functionality
- Session management
- Protected route access

### ✅ Assessment Wizard

- New assessment creation
- Question navigation
- Progress saving
- Assessment completion
- Results display

### ✅ Evidence Management

- File upload (PDF, Excel)
- File type validation
- File size limits
- Evidence metadata editing
- Search and filtering
- Download functionality

### ✅ Dashboard & Navigation

- Desktop navigation
- Mobile responsive behavior
- Widget interactions
- Loading states
- Error handling

## Running Tests

### Local Development

```bash
# Run all tests
pnpm test:e2e

# Run specific test file
pnpm exec playwright test tests/e2e/auth.test.ts

# Run with UI
pnpm exec playwright test --ui

# Run headed browser
pnpm exec playwright test --headed
```

### CI/CD Pipeline

Tests run automatically on:

- Pull request creation
- Merge to main branch
- Nightly builds

## Test Configuration

### Browsers Tested

- Desktop Chrome
- Desktop Firefox
- Desktop Safari
- Mobile Chrome (Pixel 5)
- Mobile Safari (iPhone 12)

### Test Settings

- **Timeout**: 30 seconds per test
- **Retries**: 2 retries on CI
- **Parallel Workers**: 2 on CI, 1 locally
- **Screenshots**: On failure
- **Video**: On first retry
- **Trace**: On first retry

## Test Data

### Test Users

- `VALID_USER`: Pre-registered test user
- `ADMIN_USER`: Admin-level user
- `NEW_USER`: Generated for registration tests

### Test Files

- `test-document.pdf`: Valid PDF for upload tests
- Excel files: Generated programmatically

## Best Practices

### Selectors

- Use data-testid attributes when available
- Prefer semantic selectors over CSS classes
- Use the TestSelectors utility for consistency

### Test Data

- Use fixtures for reusable test data
- Generate unique data for registration tests
- Clean up test data after tests

### Assertions

- Use specific assertions over generic ones
- Wait for elements before interacting
- Check both positive and negative cases

## Troubleshooting

### Common Issues

1. **Tests failing locally**: Ensure dev server is running
2. **Mobile tests failing**: Check viewport settings
3. **File upload tests**: Verify test files exist
4. **Authentication tests**: Ensure test users exist

### Debug Commands

```bash
# Run with debug output
DEBUG=pw:api pnpm exec playwright test

# Run specific test with tracing
pnpm exec playwright test tests/e2e/auth.test.ts --trace on

# View test report
pnpm exec playwright show-report
```

## Adding New Tests

1. Create test file in `tests/e2e/`
2. Use existing fixtures and selectors
3. Follow naming convention: `feature-name.test.ts`
4. Add test to appropriate test suite
5. Update this documentation

## Performance Considerations

- Tests run in parallel where possible
- Use `test.describe.parallel` for independent tests
- Avoid unnecessary waits
- Use `page.waitForLoadState()` appropriately
