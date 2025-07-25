import { test, expect } from '@playwright/test';
import { TEST_USERS, generateTestData } from './fixtures/test-data';
import { TestSelectors } from './fixtures/test-selectors';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test.describe('User Registration', () => {
    test('should register a new user successfully', async ({ page }) => {
      const newUser = generateTestData.user();

      // Navigate to registration
      await page.getByRole('link', { name: /sign up|register/i }).click();
      await expect(page).toHaveURL(/.*register/);

      // Fill registration form
      await page.fill(TestSelectors.auth.emailInput, newUser.email);
      await page.fill(TestSelectors.auth.passwordInput, newUser.password);
      await page.fill(TestSelectors.auth.fullNameInput, newUser.fullName);

      // Submit form
      await page.click(TestSelectors.auth.submitButton);

      // Verify successful registration
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('text=Welcome')).toBeVisible();
    });

    test('should validate email format', async ({ page }) => {
      await page.getByRole('link', { name: /sign up|register/i }).click();

      await page.fill(TestSelectors.auth.emailInput, 'invalid-email');
      await page.fill(TestSelectors.auth.passwordInput, 'ValidPass123!');
      await page.fill(TestSelectors.auth.fullNameInput, 'Test User');

      await page.click(TestSelectors.auth.submitButton);

      // Should show validation error
      await expect(page.locator('text=valid email')).toBeVisible();
    });

    test('should validate password requirements', async ({ page }) => {
      await page.getByRole('link', { name: /sign up|register/i }).click();

      await page.fill(TestSelectors.auth.emailInput, 'test@example.com');
      await page.fill(TestSelectors.auth.passwordInput, 'weak'); // Too weak
      await page.fill(TestSelectors.auth.fullNameInput, 'Test User');

      await page.click(TestSelectors.auth.submitButton);

      // Should show password requirements
      await expect(page.locator('text=password must')).toBeVisible();
    });
  });

  test.describe('User Login', () => {
    test('should login with valid credentials', async ({ page }) => {
      // Navigate to login
      await page.getByRole('link', { name: /sign in|login/i }).click();
      await expect(page).toHaveURL(/.*login/);

      // Fill login form
      await page.fill(TestSelectors.auth.emailInput, TEST_USERS.VALID_USER.email);
      await page.fill(TestSelectors.auth.passwordInput, TEST_USERS.VALID_USER.password);

      // Submit form
      await page.click(TestSelectors.auth.submitButton);

      // Verify successful login
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator(`text=${TEST_USERS.VALID_USER.fullName}`)).toBeVisible();
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await page.getByRole('link', { name: /sign in|login/i }).click();

      await page.fill(TestSelectors.auth.emailInput, 'wrong@example.com');
      await page.fill(TestSelectors.auth.passwordInput, 'wrongpassword');

      await page.click(TestSelectors.auth.submitButton);

      // Should show error message
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
    });

    test('should remember user with "remember me" checked', async ({ page }) => {
      await page.getByRole('link', { name: /sign in|login/i }).click();

      await page.fill(TestSelectors.auth.emailInput, TEST_USERS.VALID_USER.email);
      await page.fill(TestSelectors.auth.passwordInput, TEST_USERS.VALID_USER.password);
      await page.check(TestSelectors.auth.rememberMeCheckbox);

      await page.click(TestSelectors.auth.submitButton);

      // Verify login success
      await expect(page).toHaveURL(/.*dashboard/);

      // Simulate browser restart by clearing session storage
      await page.evaluate(() => window.sessionStorage.clear());
      await page.reload();

      // Should still be logged in (cookie-based auth)
      await expect(page).toHaveURL(/.*dashboard/);
    });
  });

  test.describe('Password Reset', () => {
    test('should request password reset', async ({ page }) => {
      await page.getByRole('link', { name: /sign in|login/i }).click();
      await page.getByRole('link', { name: /forgot password/i }).click();

      await expect(page).toHaveURL(/.*forgot-password/);

      await page.fill(TestSelectors.auth.emailInput, TEST_USERS.VALID_USER.email);
      await page.click(TestSelectors.auth.submitButton);

      // Should show success message
      await expect(page.locator('text=reset email sent')).toBeVisible();
    });
  });

  test.describe('Session Management', () => {
    test('should logout successfully', async ({ page }) => {
      // Login first
      await page.getByRole('link', { name: /sign in|login/i }).click();
      await page.fill(TestSelectors.auth.emailInput, TEST_USERS.VALID_USER.email);
      await page.fill(TestSelectors.auth.passwordInput, TEST_USERS.VALID_USER.password);
      await page.click(TestSelectors.auth.submitButton);

      // Wait for dashboard
      await expect(page).toHaveURL(/.*dashboard/);

      // Logout
      await page.click(TestSelectors.navigation.userMenu);
      await page.click(TestSelectors.navigation.logoutButton);

      // Verify logout
      await expect(page).toHaveURL(/.*login|.*\//);
    });

    test('should redirect to login when accessing protected routes unauthenticated', async ({
      page,
    }) => {
      await page.goto('/dashboard');

      // Should redirect to login
      await expect(page).toHaveURL(/.*login/);
      await expect(page.locator('text=Please sign in')).toBeVisible();
    });
  });
});
