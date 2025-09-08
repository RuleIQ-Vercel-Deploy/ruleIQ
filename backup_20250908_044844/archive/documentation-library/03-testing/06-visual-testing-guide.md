# Visual Regression Testing Guide

## Overview

This guide covers the visual regression testing infrastructure for the ruleIQ frontend application. We use multiple tools to ensure comprehensive visual testing coverage:

1. **Playwright** - For full page and component screenshots
2. **Chromatic** - For Storybook-based visual testing
3. **Storybook Test Runner** - For component interaction testing

## Architecture

```
tests/visual/
├── component-snapshots.test.tsx  # Component-level visual tests
├── page-layouts.test.tsx         # Full page layout tests
├── visual-regression.test.ts     # Legacy visual tests
├── visual-regression.config.ts   # Playwright configuration
└── VISUAL_TESTING_GUIDE.md      # This file

.storybook/
├── main.ts                      # Storybook configuration
├── preview.tsx                  # Global decorators and parameters
└── test-runner-jest.config.js   # Test runner configuration

components/
└── **/*.stories.tsx             # Component stories for visual testing
```

## Running Visual Tests

### Local Development

1. **Run all visual tests:**
   ```bash
   pnpm test:visual
   ```

2. **Update snapshots:**
   ```bash
   pnpm test:visual:update
   ```

3. **Run component visual tests:**
   ```bash
   pnpm test:visual:components
   ```

4. **Run page layout tests:**
   ```bash
   pnpm test:visual:pages
   ```

5. **Run Storybook:**
   ```bash
   pnpm storybook
   ```

6. **Run Storybook tests:**
   ```bash
   pnpm test:storybook
   ```

7. **Run Chromatic:**
   ```bash
   pnpm chromatic
   ```

### CI/CD Pipeline

Visual tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

The CI pipeline includes:
1. Multi-browser testing (Chrome, Firefox, Safari)
2. Responsive viewport testing
3. Dark mode testing
4. Chromatic deployment
5. Automated visual diff reporting

## Test Categories

### 1. Component Visual Tests (`component-snapshots.test.tsx`)

Tests individual UI components in isolation:
- All component variants and states
- Interactive states (hover, focus, active)
- Different sizes and configurations
- Theme variations (light/dark)
- Responsive behavior

Example:
```typescript
test('button - primary variant - default size', async ({ page }) => {
  await helpers.navigateAndWait('/components');
  const button = page.locator('[data-testid="button-primary-default"]');
  
  // Normal state
  await expect(button).toHaveScreenshot('button-primary-default-normal.png');
  
  // Hover state
  await button.hover();
  await expect(button).toHaveScreenshot('button-primary-default-hover.png');
});
```

### 2. Page Layout Tests (`page-layouts.test.tsx`)

Tests complete page layouts:
- Full page screenshots
- Page sections
- Loading states
- Error states
- Multi-step flows
- Cross-browser consistency

Example:
```typescript
test('dashboard - complete layout', async ({ page, browserName }) => {
  await helpers.navigateAndWait('/dashboard');
  await helpers.waitForLoadingToComplete();
  
  await expect(page).toHaveScreenshot(`dashboard-${browserName}.png`, {
    fullPage: true,
    animations: 'disabled',
    mask: [
      page.locator('[data-testid="dynamic-data"]'),
    ],
  });
});
```

### 3. Storybook Visual Tests

Component stories with visual testing:
- Isolated component rendering
- All props combinations
- Interaction states
- Accessibility testing
- Cross-browser rendering

## Best Practices

### 1. Writing Stable Visual Tests

- **Disable animations:** Use `animations: 'disabled'` in screenshot options
- **Mask dynamic content:** Hide timestamps, random data, etc.
- **Wait for content:** Ensure all content is loaded before screenshots
- **Use consistent viewports:** Define standard viewport sizes
- **Control external factors:** Set timezone, locale, and color scheme

### 2. Screenshot Options

```typescript
await expect(page).toHaveScreenshot('name.png', {
  fullPage: true,              // Capture entire page
  animations: 'disabled',       // Disable CSS animations
  maxDiffPixels: 100,          // Allowed pixel difference
  threshold: 0.2,              // Difference threshold (0-1)
  mask: [locator1, locator2],  // Elements to mask
  clip: { x, y, width, height }, // Specific area to capture
});
```

### 3. Handling Dynamic Content

```typescript
// Mask dynamic elements
await expect(page).toHaveScreenshot('dashboard.png', {
  mask: [
    page.locator('[data-testid="current-time"]'),
    page.locator('[data-testid="user-avatar"]'),
    page.locator('.dynamic-chart'),
  ],
});

// Mock data for consistency
await page.route('**/api/dashboard/**', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify(mockDashboardData),
  });
});
```

### 4. Responsive Testing

```typescript
const viewports = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
];

for (const viewport of viewports) {
  test(`component - ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    // ... rest of test
  });
}
```

### 5. Cross-Browser Testing

```typescript
test.describe('Cross-browser consistency', () => {
  ['chromium', 'firefox', 'webkit'].forEach(browserName => {
    test(`renders consistently in ${browserName}`, async ({ page }) => {
      // Test implementation
    });
  });
});
```

## Debugging Visual Test Failures

### 1. Local Debugging

1. **View test report:**
   ```bash
   npx playwright show-report
   ```

2. **Update specific snapshots:**
   ```bash
   pnpm playwright test path/to/test.ts --update-snapshots
   ```

3. **Debug mode:**
   ```bash
   pnpm playwright test --debug
   ```

### 2. CI Debugging

1. **Download artifacts:** Visual diffs are uploaded as artifacts
2. **Check Chromatic:** View visual changes in Chromatic UI
3. **Review PR comments:** Automated reports on pull requests

### 3. Common Issues

1. **Font loading:** Ensure fonts are loaded before screenshots
2. **Animation timing:** Disable or wait for animations
3. **Network requests:** Mock or wait for API calls
4. **Random data:** Use consistent test data
5. **Time-based content:** Mock date/time functions

## Chromatic Integration

### Setup

1. **Get project token:**
   - Sign up at [chromatic.com](https://www.chromatic.com/)
   - Create a project
   - Copy the project token

2. **Set environment variable:**
   ```bash
   export CHROMATIC_PROJECT_TOKEN=your-token-here
   ```

3. **Run Chromatic:**
   ```bash
   pnpm chromatic
   ```

### Features

- Automatic visual testing for all stories
- Cross-browser testing
- Responsive viewport testing
- Visual review workflow
- Git integration
- Baseline management

## Maintenance

### 1. Updating Baselines

When intentional visual changes are made:

1. **Review changes locally:**
   ```bash
   pnpm test:visual
   ```

2. **Update snapshots:**
   ```bash
   pnpm test:visual:update
   ```

3. **Commit new baselines:**
   ```bash
   git add tests/visual/**/*.png
   git commit -m "chore: update visual baselines"
   ```

### 2. Adding New Tests

1. **Component test:**
   - Add test to `component-snapshots.test.tsx`
   - Add data-testid to component
   - Run test to generate baseline

2. **Page test:**
   - Add test to `page-layouts.test.tsx`
   - Ensure page is accessible
   - Handle dynamic content

3. **Storybook story:**
   - Create `Component.stories.tsx`
   - Add chromatic parameters
   - Test in Storybook UI

### 3. Performance Optimization

- **Parallel execution:** Tests run in parallel by default
- **Selective testing:** Use `--grep` to run specific tests
- **Shared setup:** Use `beforeEach` for common setup
- **Resource caching:** Reuse browser contexts when possible

## Troubleshooting

### Issue: Flaky tests
**Solution:** Increase wait times, disable animations, mask dynamic content

### Issue: Different results locally vs CI
**Solution:** Ensure same viewport, fonts, and browser versions

### Issue: Large snapshot files
**Solution:** Use targeted screenshots instead of full page, optimize images

### Issue: Slow test execution
**Solution:** Run tests in parallel, use selective testing, optimize waits

## Resources

- [Playwright Documentation](https://playwright.dev/docs/test-snapshots)
- [Chromatic Documentation](https://www.chromatic.com/docs/)
- [Storybook Testing](https://storybook.js.org/docs/react/writing-tests/introduction)
- [Visual Testing Best Practices](https://www.chromatic.com/docs/best-practices)