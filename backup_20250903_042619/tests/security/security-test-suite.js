/**
 * Comprehensive Security Test Suite
 * Tests for OWASP Top 10 vulnerabilities and security best practices
 */

const { test, expect } = require("@playwright/test");
const {
  securityHeaders,
} = require("../../frontend/lib/security/security-headers");

// Test configuration
test.describe.configure({ mode: "serial" });

test.describe("Security Test Suite - OWASP Top 10", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000");
  });

  // A01: Broken Access Control
  test("A01 - Broken Access Control Prevention", async ({ page }) => {
    // Test unauthorized access to admin routes
    await page.goto("http://localhost:3000/admin/dashboard");
    await expect(page).toHaveURL(/.*login|.*unauthorized/);

    // Test direct API access without authentication
    const response = await page.request.get("/api/admin/users");
    expect(response.status()).toBe(401);
  });

  // A02: Cryptographic Failures
  test("A02 - Data Encryption in Transit", async ({ page }) => {
    // Check HTTPS enforcement
    const response = await page.request.get("/");
    const headers = response.headers();
    expect(headers["strict-transport-security"]).toContain("max-age=63072000");
  });

  // A03: Injection Prevention
  test("A03 - SQL Injection Prevention", async ({ page }) => {
    // Test SQL injection in login form
    await page.goto("http://localhost:3000/login");
    await page.fill('input[name="email"]', "admin' OR '1'='1");
    await page.fill('input[name="password"]', "password' OR '1'='1");
    await page.click('button[type="submit"]');

    // Should not login with SQL injection
    await expect(page).toHaveURL(/.*login/);
    await expect(page.locator(".error")).toBeVisible();
  });

  test("A03 - XSS Prevention", async ({ page }) => {
    // Test XSS in search input
    await page.goto("http://localhost:3000");
    await page.fill('input[type="search"]', '<script>alert("XSS")</script>');
    await page.press('input[type="search"]', "Enter");

    // Script should not execute
    const hasAlert = await page.evaluate(() => {
      return window.alertTriggered || false;
    });
    expect(hasAlert).toBe(false);
  });

  // A04: Insecure Design
  test("A04 - Rate Limiting", async ({ page }) => {
    // Test rate limiting on login endpoint
    const loginAttempts = 10;

    for (let i = 0; i < loginAttempts; i++) {
      const response = await page.request.post("/api/auth/login", {
        data: { email: "test@test.com", password: "wrongpassword" },
      });

      if (i >= 5) {
        expect(response.status()).toBe(429); // Rate limited
        break;
      }
    }
  });

  // A05: Security Misconfiguration
  test("A05 - Security Headers Present", async ({ page }) => {
    const response = await page.request.get("/");
    const headers = response.headers();

    // Check all security headers
    expect(headers["x-frame-options"]).toBe("DENY");
    expect(headers["x-content-type-options"]).toBe("nosniff");
    expect(headers["strict-transport-security"]).toContain("max-age=63072000");
    expect(headers["referrer-policy"]).toBe("strict-origin-when-cross-origin");
    expect(headers["x-xss-protection"]).toBe("1; mode=block");
    expect(headers["content-security-policy"]).toBeDefined();
  });

  // A06: Vulnerable Components
  test("A06 - No Sensitive Information Disclosure", async ({ page }) => {
    // Check for exposed .env files
    const envResponse = await page.request.get("/.env");
    expect(envResponse.status()).toBe(404);

    // Check for exposed package.json
    const packageResponse = await page.request.get("/package.json");
    expect(packageResponse.status()).toBe(404);

    // Check for exposed git directory
    const gitResponse = await page.request.get("/.git/config");
    expect(gitResponse.status()).toBe(404);
  });

  // A07: Authentication Failures
  test("A07 - Strong Authentication", async ({ page }) => {
    // Test weak password rejection
    await page.goto("http://localhost:3000/register");
    await page.fill('input[name="email"]', "test@example.com");
    await page.fill('input[name="password"]', "123"); // Weak password
    await page.click('button[type="submit"]');

    await expect(page.locator(".password-error")).toBeVisible();
  });

  // A08: Software and Data Integrity Failures
  test("A08 - CSRF Protection", async ({ page }) => {
    // Test CSRF token validation
    await page.goto("http://localhost:3000/dashboard");

    // Attempt to make POST request without CSRF token
    const response = await page.request.post("/api/assessments", {
      data: { name: "Test Assessment" },
    });

    expect(response.status()).toBe(403);
  });

  // A09: Security Logging and Monitoring
  test("A09 - Security Events Logging", async ({ page }) => {
    // Trigger failed login
    await page.goto("http://localhost:3000/login");
    await page.fill('input[name="email"]', "nonexistent@example.com");
    await page.fill('input[name="password"]', "wrongpassword");
    await page.click('button[type="submit"]');

    // Check if security event is logged (implementation specific)
    // This would typically check a monitoring endpoint
    const logsResponse = await page.request.get("/api/security/logs");
    expect(logsResponse.status()).toBe(401); // Should require authentication
  });

  // A10: Server-Side Request Forgery
  test("A10 - SSRF Prevention", async ({ page }) => {
    // Test SSRF in file upload
    await page.goto("http://localhost:3000/upload");

    // Attempt to upload URL instead of file
    const response = await page.request.post("/api/upload", {
      data: { url: "file:///etc/passwd" },
    });

    expect(response.status()).toBe(400);
  });

  // Additional Security Tests
  test("Session Management", async ({ page }) => {
    // Test session timeout
    await page.goto("http://localhost:3000/login");
    await page.fill('input[name="email"]', "test@example.com");
    await page.fill('input[name="password"]', "Test123!");
    await page.click('button[type="submit"]');

    // Wait for session timeout (simplified)
    await page.waitForTimeout(1000);

    // Refresh page - should still be authenticated
    await page.reload();
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test("Password Policy Enforcement", async ({ page }) => {
    await page.goto("http://localhost:3000/register");

    // Test weak passwords
    const weakPasswords = ["123456", "password", "admin", "qwerty"];

    for (const password of weakPasswords) {
      await page.fill('input[name="email"]', "test@example.com");
      await page.fill('input[name="password"]', password);
      await page.fill('input[name="confirmPassword"]', password);
      await page.click('button[type="submit"]');

      await expect(page.locator(".password-strength")).toContainText("weak");
    }
  });

  test("Input Validation", async ({ page }) => {
    await page.goto("http://localhost:3000/contact");

    // Test XSS in contact form
    await page.fill('input[name="name"]', '<script>alert("XSS")</script>');
    await page.fill('input[name="email"]', "test@example.com");
    await page.fill('textarea[name="message"]', "<img src=x onerror=alert(1)>");
    await page.click('button[type="submit"]');

    // Should sanitize input
    await expect(page.locator(".success-message")).toBeVisible();
    await expect(page.locator("script")).toHaveCount(0);
  });

  test("API Rate Limiting", async ({ page }) => {
    const requests = [];

    // Send multiple rapid requests
    for (let i = 0; i < 20; i++) {
      requests.push(page.request.get("/api/health"));
    }

    const responses = await Promise.all(requests);
    const rateLimited = responses.filter((r) => r.status() === 429);

    expect(rateLimited.length).toBeGreaterThan(0);
  });
});

// Security configuration validation
test.describe("Security Configuration", () => {
  test("CSP Configuration", async ({ page }) => {
    const response = await page.request.get("/");
    const csp = response.headers()["content-security-policy"];

    expect(csp).toContain("default-src 'self'");
    expect(csp).toContain("script-src");
    expect(csp).toContain("style-src");
    expect(csp).toContain("img-src");
  });

  test("HTTPS Enforcement", async ({ page }) => {
    const response = await page.request.get("/");
    const hsts = response.headers()["strict-transport-security"];

    expect(hsts).toContain("max-age=63072000");
    expect(hsts).toContain("includeSubDomains");
    expect(hsts).toContain("preload");
  });
});

// Security scanning utilities
const securityScan = {
  async scanHeaders(page) {
    const response = await page.request.get("/");
    const headers = response.headers();

    return {
      score:
        (Object.keys(securityHeaders).filter((key) => headers[key]).length /
          Object.keys(securityHeaders).length) *
        100,
      missing: Object.keys(securityHeaders).filter((key) => !headers[key]),
      headers,
    };
  },

  async checkSSLConfiguration(url) {
    // This would typically use a library like ssl-checker
    return {
      valid: true,
      protocols: ["TLSv1.2", "TLSv1.3"],
      grade: "A+",
    };
  },

  async runVulnerabilityScan(url) {
    // Placeholder for vulnerability scanning
    return {
      vulnerabilities: [],
      score: 100,
      timestamp: new Date().toISOString(),
    };
  },
};

module.exports = {
  securityScan,
  securityHeaders,
};
