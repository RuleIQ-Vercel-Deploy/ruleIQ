/**
 * Login Page Object Model
 * 
 * Provides interface for authentication during E2E testing
 */

import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  
  // Login elements
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;
  
  constructor(page: Page) {
    this.page = page;
    
    this.emailInput = page.locator('[data-testid="email-input"]');
    this.passwordInput = page.locator('[data-testid="password-input"]');
    this.loginButton = page.locator('[data-testid="login-button"]');
    this.errorMessage = page.locator('[data-testid="error-message"]');
  }
  
  /**
   * Navigate to login page
   */
  async goto() {
    await this.page.goto('/login');
  }
  
  /**
   * Perform login
   */
  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
    
    // Wait for navigation to complete
    await this.page.waitForURL(/\/dashboard|\/chat/);
  }
}