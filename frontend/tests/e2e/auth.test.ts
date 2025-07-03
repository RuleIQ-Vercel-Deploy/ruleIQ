import { test, expect } from '@playwright/test';

import { TEST_USERS } from './fixtures/test-data';
import { AuthHelpers } from './utils/test-helpers';

test.describe('Authentication Flow', () => {
  let authHelpers: AuthHelpers;

  test.beforeEach(async ({ page }) => {
    authHelpers = new AuthHelpers(page);
  });

  test.describe('User Registration', () => {
    test('should register a new user successfully', async ({ page }) => {
      const newUser = {
        email: `test.${Date.now()}@example.com`,
        password: 'TestPassword123!',
        fullName: 'Test User',
        company: 'Test Company'
      };

      await authHelpers.register(newUser);
      
      // Should redirect to dashboard or email verification
      await expect(page).toHaveURL(/\/(dashboard|verify-email)/);
    });

    test('should show validation errors for invalid data', async ({ page }) => {
      await authHelpers.navigateAndWait('/register');
      
      // Try to submit with empty fields
      await authHelpers.clickAndWait('[data-testid="register-button"]');
      
      // Should show validation errors
      await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="full-name-error"]')).toBeVisible();
    });

    test('should show error for duplicate email', async ({ page }) => {
      await authHelpers.navigateAndWait('/register');
      
      // Try to register with existing email
      await authHelpers.fillField('[data-testid="full-name-input"]', 'Test User');
      await authHelpers.fillField('[data-testid="email-input"]', TEST_USERS.VALID_USER.email);
      await authHelpers.fillField('[data-testid="password-input"]', 'TestPassword123!');
      
      await authHelpers.clickAndWait('[data-testid="register-button"]');
      
      // Should show error message
      await expect(page.locator('text=Email already exists')).toBeVisible();
    });

    test('should enforce password requirements', async ({ page }) => {
      await authHelpers.navigateAndWait('/register');
      
      await authHelpers.fillField('[data-testid="full-name-input"]', 'Test User');
      await authHelpers.fillField('[data-testid="email-input"]', 'test@example.com');
      
      // Test weak password
      await authHelpers.fillField('[data-testid="password-input"]', 'weak');
      await authHelpers.clickAndWait('[data-testid="register-button"]');
      
      // Should show password strength error
      await expect(page.locator('[data-testid="password-error"]')).toContainText('Password must be at least 8 characters');
    });
  });

  test.describe('User Login', () => {
    test('should login with valid credentials', async ({ page }) => {
      await authHelpers.login(TEST_USERS.VALID_USER.email, TEST_USERS.VALID_USER.password);
      
      // Should be redirected to dashboard
      await expect(page).toHaveURL(/\/dashboard/);
      
      // Should show user menu
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
      
      // Should show user name
      await expect(page.locator('[data-testid="user-name"]')).toContainText(TEST_USERS.VALID_USER.fullName);
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await authHelpers.navigateAndWait('/login');
      
      await authHelpers.fillField('[data-testid="email-input"]', 'invalid@example.com');
      await authHelpers.fillField('[data-testid="password-input"]', 'wrongpassword');
      
      await authHelpers.clickAndWait('[data-testid="login-button"]');
      
      // Should show error message
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
      
      // Should remain on login page
      await expect(page).toHaveURL(/\/login/);
    });

    test('should show validation errors for empty fields', async ({ page }) => {
      await authHelpers.navigateAndWait('/login');
      
      await authHelpers.clickAndWait('[data-testid="login-button"]');
      
      // Should show validation errors
      await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
    });

    test('should remember login state after page refresh', async ({ page }) => {
      await authHelpers.login();
      
      // Refresh the page
      await page.reload();
      
      // Should still be logged in
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
      await expect(page).toHaveURL(/\/dashboard/);
    });

    test('should handle "Remember Me" functionality', async ({ page }) => {
      await authHelpers.navigateAndWait('/login');
      
      await authHelpers.fillField('[data-testid="email-input"]', TEST_USERS.VALID_USER.email);
      await authHelpers.fillField('[data-testid="password-input"]', TEST_USERS.VALID_USER.password);
      
      // Check remember me
      await page.check('[data-testid="remember-me-checkbox"]');
      
      await authHelpers.clickAndWait('[data-testid="login-button"]', '[data-testid="dashboard"]');
      
      // Should be logged in
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });
  });

  test.describe('User Logout', () => {
    test('should logout successfully', async ({ page }) => {
      // Login first
      await authHelpers.login();
      
      // Logout
      await authHelpers.logout();
      
      // Should be redirected to login page
      await expect(page).toHaveURL(/\/login/);
      
      // Should not show user menu
      await expect(page.locator('[data-testid="user-menu"]')).not.toBeVisible();
    });

    test('should clear session data on logout', async ({ page }) => {
      await authHelpers.login();
      
      // Check that user data is present
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
      
      await authHelpers.logout();
      
      // Try to access protected page
      await page.goto('/dashboard');
      
      // Should be redirected to login
      await expect(page).toHaveURL(/\/login/);
    });
  });

  test.describe('Password Reset', () => {
    test('should request password reset', async ({ page }) => {
      await authHelpers.navigateAndWait('/login');
      
      // Click forgot password link
      await page.click('[data-testid="forgot-password-link"]');
      
      // Should navigate to password reset page
      await expect(page).toHaveURL(/\/forgot-password/);
      
      // Enter email
      await authHelpers.fillField('[data-testid="email-input"]', TEST_USERS.VALID_USER.email);
      
      await authHelpers.clickAndWait('[data-testid="reset-password-button"]');
      
      // Should show success message
      await authHelpers.waitForToast('Password reset email sent');
    });

    test('should show error for non-existent email', async ({ page }) => {
      await authHelpers.navigateAndWait('/forgot-password');
      
      await authHelpers.fillField('[data-testid="email-input"]', 'nonexistent@example.com');
      
      await authHelpers.clickAndWait('[data-testid="reset-password-button"]');
      
      // Should show error message
      await expect(page.locator('text=Email not found')).toBeVisible();
    });
  });

  test.describe('Session Management', () => {
    test('should handle expired session', async ({ page }) => {
      await authHelpers.login();
      
      // Mock expired token response
      await authHelpers.mockApiResponse('**/api/auth/refresh', {
        error: 'Token expired'
      });
      
      // Try to access protected resource
      await page.goto('/dashboard');
      
      // Should be redirected to login
      await expect(page).toHaveURL(/\/login/);
      
      // Should show session expired message
      await expect(page.locator('text=Session expired')).toBeVisible();
    });

    test('should auto-refresh tokens', async ({ page }) => {
      await authHelpers.login();
      
      // Mock successful token refresh
      await authHelpers.mockApiResponse('**/api/auth/refresh', {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      });
      
      // Wait for auto-refresh (this would happen in background)
      await page.waitForTimeout(2000);
      
      // Should still be logged in
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });
  });

  test.describe('Social Authentication', () => {
    test.skip('should login with Google', async ({ page }) => {
      // This would require mocking OAuth flow
      await authHelpers.navigateAndWait('/login');
      
      await page.click('[data-testid="google-login-button"]');
      
      // Mock OAuth success
      // Implementation depends on OAuth provider setup
    });

    test.skip('should login with Microsoft', async ({ page }) => {
      // This would require mocking OAuth flow
      await authHelpers.navigateAndWait('/login');
      
      await page.click('[data-testid="microsoft-login-button"]');
      
      // Mock OAuth success
      // Implementation depends on OAuth provider setup
    });
  });
});
