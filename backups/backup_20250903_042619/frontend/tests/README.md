# Testing Guide for ruleIQ Frontend

This comprehensive testing guide covers all aspects of testing in the ruleIQ frontend application, from unit tests to end-to-end testing, performance monitoring, and accessibility validation.

## 📁 Testing Structure

```
tests/
├── accessibility/          # Accessibility testing
│   ├── accessibility.test.tsx
│   ├── utils.ts
│   └── MANUAL_TESTING_GUIDE.md
├── components/             # Component unit tests
│   ├── ui/                # UI component tests
│   └── features/          # Feature component tests
├── config/                # Test configuration
│   └── test-config.ts
├── e2e/                   # End-to-end tests
│   ├── fixtures/          # Test data and files
│   ├── utils/             # E2E test utilities
│   ├── auth.test.ts
│   ├── business-profile.test.ts
│   ├── assessment-flow.test.ts
│   ├── evidence-management.test.ts
│   ├── accessibility.test.ts
│   └── smoke.test.ts
├── integration/           # Integration tests
│   └── auth-flow.test.tsx
├── performance/           # Performance tests
│   └── performance.test.ts
├── services/              # Service layer tests
│   └── auth.service.test.ts
├── stores/                # State management tests
│   └── auth.store.test.ts
├── visual/                # Visual regression tests
│   └── visual-regression.test.ts
├── utils.tsx              # Test utilities
└── README.md              # This file
```

## 🧪 Test Types

### 1. Unit Tests

**Purpose**: Test individual components and functions in isolation
**Tools**: Vitest + React Testing Library
**Location**: `tests/components/`, `tests/services/`, `tests/stores/`

```bash
# Run unit tests
pnpm test

# Run with coverage
pnpm test:coverage

# Run in watch mode
pnpm test:watch

# Run specific test file
pnpm test auth.store.test.ts
```

### 2. Integration Tests

**Purpose**: Test component interactions and data flow
**Tools**: Vitest + React Testing Library + MSW
**Location**: `tests/integration/`

```bash
# Run integration tests
pnpm test tests/integration/
```

### 3. End-to-End Tests

**Purpose**: Test complete user workflows
**Tools**: Playwright
**Location**: `tests/e2e/`

```bash
# Run all E2E tests
pnpm test:e2e

# Run with UI mode
pnpm test:e2e:ui

# Run specific test
pnpm test:e2e auth.test.ts

# Run smoke tests only
pnpm test:e2e:smoke
```

### 4. Accessibility Tests

**Purpose**: Ensure WCAG 2.2 AA compliance
**Tools**: jest-axe + Playwright axe-core
**Location**: `tests/accessibility/`

```bash
# Run accessibility tests
pnpm test:accessibility

# Run E2E accessibility tests
pnpm test:e2e:accessibility
```

### 5. Performance Tests

**Purpose**: Monitor Core Web Vitals and performance budgets
**Tools**: Playwright + Custom monitoring
**Location**: `tests/performance/`

```bash
# Run performance tests
pnpm test:performance

# Analyze bundle size
pnpm analyze:bundle
```

### 6. Visual Regression Tests

**Purpose**: Detect unintended visual changes
**Tools**: Playwright visual comparisons
**Location**: `tests/visual/`

```bash
# Run visual tests
pnpm test:visual

# Update visual baselines
pnpm test:visual:update
```

## 🛠️ Test Configuration

### Environment Variables

```bash
# Test environment
PLAYWRIGHT_BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000
TEST_USER_EMAIL=test@ruleiq.com
TEST_USER_PASSWORD=TestPassword123!

# CI/CD settings
CI=true
HEADLESS=true
MOCK_API=true
```

### Test Configuration File

All test settings are centralized in `tests/config/test-config.ts`:

```typescript
import { TEST_CONFIG } from './tests/config/test-config';

// Access configuration
const timeout = TEST_CONFIG.TIMEOUTS.DEFAULT;
const user = TEST_CONFIG.TEST_DATA.USERS.REGULAR_USER;
```

## 📊 Test Coverage

### Coverage Thresholds

- **Statements**: 80%
- **Branches**: 75%
- **Functions**: 80%
- **Lines**: 80%

### Critical Components (90%+ coverage required)

- Authentication components
- Business profile wizard
- Assessment flow
- Evidence management
- API services
- Store logic

### Coverage Reports

```bash
# Generate coverage report
pnpm test:coverage

# View HTML report
open coverage/index.html
```

## 🎯 Testing Best Practices

### 1. Test Organization

```typescript
describe('Component/Feature Name', () => {
  describe('Rendering', () => {
    it('should render correctly with default props', () => {
      // Test implementation
    });
  });

  describe('User Interactions', () => {
    it('should handle click events', () => {
      // Test implementation
    });
  });

  describe('Error States', () => {
    it('should display error message on failure', () => {
      // Test implementation
    });
  });
});
```

### 2. Test Data Management

```typescript
// Use test fixtures
import { TEST_USERS, BUSINESS_PROFILES } from './fixtures/test-data';

// Generate dynamic data
import { generateTestData } from './fixtures/test-data';
const user = generateTestData.user();
```

### 3. Mocking Guidelines

```typescript
// Mock external dependencies
vi.mock('@/lib/api/client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
  }),
}));
```

### 4. Async Testing

```typescript
// Wait for async operations
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
});

// Test loading states
expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
```

### 5. Accessibility Testing

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('should be accessible', async () => {
  const { container } = render(<Component />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## 🚀 Running Tests

### Local Development

```bash
# Run all tests
pnpm test:all

# Run tests in watch mode
pnpm test:watch

# Run specific test type
pnpm test:e2e
pnpm test:accessibility
pnpm test:performance
```

### CI/CD Pipeline

```bash
# Install dependencies
pnpm install

# Build application
pnpm build

# Run all test suites
pnpm test --run
pnpm test:e2e
pnpm test:accessibility
pnpm analyze:bundle
```

## 📈 Performance Monitoring

### Core Web Vitals Thresholds

- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

### Bundle Size Limits

- **Total JavaScript**: < 800KB
- **First Load JS**: < 300KB
- **Individual Chunks**: < 250KB

### Performance Testing

```typescript
// Monitor performance in tests
import { performanceMonitor } from '@/lib/performance/monitoring';

await performanceMonitor.measureCustomMetric('component-render', () => {
  render(<Component />);
});
```

## 🔍 Debugging Tests

### Debug Commands

```bash
# Debug E2E tests
pnpm test:e2e:debug

# Run tests with browser visible
pnpm test:e2e:headed

# Generate test code
pnpm exec playwright codegen localhost:3000
```

### Common Issues

1. **Flaky Tests**: Add proper waits and stabilize test data
2. **Timeout Issues**: Increase timeouts or improve performance
3. **Element Not Found**: Verify selectors and page state
4. **Network Issues**: Mock external dependencies

### Debug Utilities

```typescript
// Take screenshot for debugging
await helpers.takeScreenshot('debug-state');

// Log element state
console.log(await element.textContent());

// Wait for network idle
await page.waitForLoadState('networkidle');
```

## 📋 Test Checklists

### Before Committing

- [ ] All unit tests pass
- [ ] No TypeScript errors
- [ ] Code coverage meets thresholds
- [ ] Accessibility tests pass
- [ ] No console errors in tests

### Before Releasing

- [ ] All test suites pass
- [ ] E2E tests pass on all browsers
- [ ] Performance budgets met
- [ ] Visual regression tests pass
- [ ] Accessibility compliance verified

### New Feature Checklist

- [ ] Unit tests for new components
- [ ] Integration tests for user flows
- [ ] E2E tests for critical paths
- [ ] Accessibility tests added
- [ ] Performance impact assessed

## 🤝 Contributing

### Adding New Tests

1. Follow existing test structure and naming conventions
2. Add appropriate test data to fixtures
3. Update this README if adding new test categories
4. Ensure tests pass in all environments

### Test Review Guidelines

- Tests should be readable and maintainable
- Mock external dependencies appropriately
- Include both positive and negative test cases
- Test error states and edge cases
- Verify accessibility compliance

## 📚 Resources

### Documentation

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/)
- [jest-axe Documentation](https://github.com/nickcolley/jest-axe)

### Best Practices

- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Accessibility Testing](https://web.dev/accessibility-testing/)
- [Performance Testing](https://web.dev/performance-testing/)

### Tools

- [Testing Playground](https://testing-playground.com/)
- [Playwright Test Generator](https://playwright.dev/docs/codegen)
- [axe DevTools](https://www.deque.com/axe/devtools/)

## 🆘 Support

For testing-related questions or issues:

1. Check this documentation first
2. Review existing test examples
3. Consult team testing guidelines
4. Ask for help in team channels

Remember: Good tests are an investment in code quality and team productivity. Write tests that provide confidence and catch real issues!
