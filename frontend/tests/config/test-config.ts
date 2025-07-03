/**
 * Comprehensive Testing Configuration for ruleIQ
 * 
 * This file contains all testing configurations, thresholds, and utilities
 * used across different types of tests (unit, integration, E2E, performance, visual).
 */

export const TEST_CONFIG = {
  // Test environment settings
  ENVIRONMENT: {
    BASE_URL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
    TEST_USER_EMAIL: process.env.TEST_USER_EMAIL || 'test@ruleiq.com',
    TEST_USER_PASSWORD: process.env.TEST_USER_PASSWORD || 'TestPassword123!',
    HEADLESS: process.env.CI === 'true',
    SLOW_MO: process.env.CI === 'true' ? 0 : 100,
  },

  // Performance thresholds
  PERFORMANCE: {
    // Core Web Vitals (milliseconds)
    LCP_THRESHOLD: 2500,        // Largest Contentful Paint
    FID_THRESHOLD: 100,         // First Input Delay
    CLS_THRESHOLD: 0.1,         // Cumulative Layout Shift
    FCP_THRESHOLD: 1800,        // First Contentful Paint
    TTI_THRESHOLD: 3800,        // Time to Interactive
    
    // Page load times (milliseconds)
    PAGE_LOAD_TIMEOUT: 30000,
    API_RESPONSE_TIMEOUT: 5000,
    COMPONENT_RENDER_TIMEOUT: 1000,
    
    // Bundle size limits (KB)
    MAX_BUNDLE_SIZE: 800,
    MAX_CHUNK_SIZE: 250,
    MAX_CSS_SIZE: 100,
    MAX_FIRST_LOAD_JS: 300,
    
    // Resource limits
    MAX_RESOURCES: 50,
    MAX_SLOW_RESOURCES: 0,
    MAX_LARGE_RESOURCES: 2,
  },

  // Accessibility standards
  ACCESSIBILITY: {
    WCAG_LEVEL: 'AA',
    WCAG_VERSION: '2.2',
    COLOR_CONTRAST_RATIO: 4.5,
    LARGE_TEXT_CONTRAST_RATIO: 3.0,
    UI_COMPONENT_CONTRAST_RATIO: 3.0,
    TOUCH_TARGET_SIZE: 44, // pixels
    
    // Allowed violations (for gradual improvement)
    ALLOWED_VIOLATIONS: {
      'color-contrast': 0,
      'keyboard-navigation': 0,
      'aria-labels': 0,
      'heading-order': 0,
    },
  },

  // Visual regression settings
  VISUAL: {
    THRESHOLD: 0.2,             // Pixel difference threshold (0-1)
    ANIMATION_HANDLING: 'disabled',
    FULL_PAGE: true,
    CLIP_SELECTOR: null,
    
    // Viewport sizes for responsive testing
    VIEWPORTS: {
      MOBILE: { width: 375, height: 667 },
      TABLET: { width: 768, height: 1024 },
      DESKTOP: { width: 1920, height: 1080 },
      LARGE_DESKTOP: { width: 2560, height: 1440 },
    },
    
    // Elements to mask in screenshots
    DYNAMIC_CONTENT_SELECTORS: [
      '[data-testid="current-time"]',
      '[data-testid="user-avatar"]',
      '[data-testid="dynamic-score"]',
      '[data-testid="timestamp"]',
    ],
  },

  // Test data and fixtures
  TEST_DATA: {
    // User accounts for testing
    USERS: {
      ADMIN: {
        email: 'admin@ruleiq.com',
        password: 'AdminPassword123!',
        role: 'admin',
      },
      REGULAR_USER: {
        email: 'user@ruleiq.com',
        password: 'UserPassword123!',
        role: 'user',
      },
      COMPLIANCE_OFFICER: {
        email: 'compliance@ruleiq.com',
        password: 'CompliancePassword123!',
        role: 'compliance_officer',
      },
    },

    // Business profiles for testing
    BUSINESS_PROFILES: {
      TECH_STARTUP: {
        company_name: 'TechStart Solutions',
        industry: 'Technology',
        employee_count: '10-50',
        data_types: ['personal_data', 'financial_data'],
      },
      HEALTHCARE: {
        company_name: 'HealthCare Plus',
        industry: 'Healthcare',
        employee_count: '50-100',
        data_types: ['personal_data', 'health_data', 'sensitive_data'],
      },
      FINANCIAL: {
        company_name: 'FinServ Corp',
        industry: 'Financial Services',
        employee_count: '100-500',
        data_types: ['personal_data', 'financial_data', 'payment_data'],
      },
    },

    // Assessment frameworks
    FRAMEWORKS: {
      GDPR: {
        name: 'GDPR',
        category: 'privacy',
        estimated_time: 30,
        question_count: 25,
      },
      ISO27001: {
        name: 'ISO 27001',
        category: 'security',
        estimated_time: 45,
        question_count: 35,
      },
      SOC2: {
        name: 'SOC 2',
        category: 'security',
        estimated_time: 60,
        question_count: 40,
      },
    },
  },

  // Test timeouts and retries
  TIMEOUTS: {
    DEFAULT: 30000,
    NAVIGATION: 30000,
    API_CALL: 10000,
    ELEMENT_VISIBLE: 5000,
    ELEMENT_HIDDEN: 5000,
    FORM_SUBMISSION: 15000,
    FILE_UPLOAD: 30000,
    ASSESSMENT_COMPLETION: 60000,
  },

  RETRIES: {
    DEFAULT: 2,
    FLAKY_TESTS: 3,
    NETWORK_DEPENDENT: 3,
    VISUAL_TESTS: 1,
  },

  // Browser configurations
  BROWSERS: {
    CHROMIUM: {
      name: 'chromium',
      use: {
        viewport: { width: 1280, height: 720 },
        ignoreHTTPSErrors: true,
        video: 'retain-on-failure',
        screenshot: 'only-on-failure',
      },
    },
    FIREFOX: {
      name: 'firefox',
      use: {
        viewport: { width: 1280, height: 720 },
        ignoreHTTPSErrors: true,
        video: 'retain-on-failure',
        screenshot: 'only-on-failure',
      },
    },
    WEBKIT: {
      name: 'webkit',
      use: {
        viewport: { width: 1280, height: 720 },
        ignoreHTTPSErrors: true,
        video: 'retain-on-failure',
        screenshot: 'only-on-failure',
      },
    },
  },

  // API mocking configurations
  API_MOCKING: {
    ENABLED: process.env.MOCK_API === 'true',
    DELAY_RANGE: [100, 500], // Random delay range for realistic testing
    ERROR_RATE: 0.05,        // 5% error rate for resilience testing
    
    // Mock responses
    MOCK_RESPONSES: {
      LOGIN_SUCCESS: {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
        },
      },
      DASHBOARD_DATA: {
        compliance_score: 85,
        total_assessments: 5,
        completed_assessments: 3,
        pending_tasks: 12,
      },
    },
  },

  // Test reporting
  REPORTING: {
    HTML_REPORT: true,
    JSON_REPORT: true,
    JUNIT_REPORT: process.env.CI === 'true',
    COVERAGE_REPORT: true,
    PERFORMANCE_BUDGET_REPORT: true,
    ACCESSIBILITY_REPORT: true,
    
    // Report paths
    REPORTS_DIR: 'test-results',
    COVERAGE_DIR: 'coverage',
    SCREENSHOTS_DIR: 'test-results/screenshots',
    VIDEOS_DIR: 'test-results/videos',
  },

  // CI/CD specific settings
  CI: {
    PARALLEL_WORKERS: process.env.CI === 'true' ? 2 : undefined,
    FAIL_FAST: process.env.CI === 'true',
    FORBID_ONLY: process.env.CI === 'true',
    MAX_FAILURES: process.env.CI === 'true' ? 5 : undefined,
    
    // Artifact retention
    ARTIFACT_RETENTION_DAYS: 30,
    VIDEO_RETENTION_DAYS: 7,
    SCREENSHOT_RETENTION_DAYS: 14,
  },

  // Feature flags for testing
  FEATURE_FLAGS: {
    ENABLE_PERFORMANCE_TESTS: true,
    ENABLE_VISUAL_TESTS: true,
    ENABLE_ACCESSIBILITY_TESTS: true,
    ENABLE_CROSS_BROWSER_TESTS: true,
    ENABLE_MOBILE_TESTS: true,
    ENABLE_API_TESTS: true,
  },

  // Test categories and tags
  TAGS: {
    SMOKE: 'smoke',
    REGRESSION: 'regression',
    CRITICAL: 'critical',
    PERFORMANCE: 'performance',
    ACCESSIBILITY: 'accessibility',
    VISUAL: 'visual',
    MOBILE: 'mobile',
    INTEGRATION: 'integration',
    E2E: 'e2e',
  },

  // Security testing
  SECURITY: {
    CSP_ENABLED: true,
    HTTPS_ONLY: process.env.NODE_ENV === 'production',
    SECURE_HEADERS: [
      'X-Frame-Options',
      'X-Content-Type-Options',
      'X-XSS-Protection',
      'Strict-Transport-Security',
    ],
  },
} as const;

// Type definitions for better TypeScript support
export type TestConfig = typeof TEST_CONFIG;
export type TestEnvironment = TestConfig['ENVIRONMENT'];
export type PerformanceConfig = TestConfig['PERFORMANCE'];
export type AccessibilityConfig = TestConfig['ACCESSIBILITY'];
export type VisualConfig = TestConfig['VISUAL'];

// Utility functions for test configuration
export function getTestUser(role: keyof TestConfig['TEST_DATA']['USERS'] = 'REGULAR_USER') {
  return TEST_CONFIG.TEST_DATA.USERS[role];
}

export function getBusinessProfile(type: keyof TestConfig['TEST_DATA']['BUSINESS_PROFILES'] = 'TECH_STARTUP') {
  return TEST_CONFIG.TEST_DATA.BUSINESS_PROFILES[type];
}

export function getFramework(name: keyof TestConfig['TEST_DATA']['FRAMEWORKS'] = 'GDPR') {
  return TEST_CONFIG.TEST_DATA.FRAMEWORKS[name];
}

export function isFeatureEnabled(feature: keyof TestConfig['FEATURE_FLAGS']): boolean {
  return TEST_CONFIG.FEATURE_FLAGS[feature];
}

export function getTimeout(type: keyof TestConfig['TIMEOUTS'] = 'DEFAULT'): number {
  return TEST_CONFIG.TIMEOUTS[type];
}

export function getRetryCount(type: keyof TestConfig['RETRIES'] = 'DEFAULT'): number {
  return TEST_CONFIG.RETRIES[type];
}

// Environment-specific configurations
export function getEnvironmentConfig() {
  const env = process.env.NODE_ENV || 'development';
  
  return {
    ...TEST_CONFIG.ENVIRONMENT,
    IS_DEVELOPMENT: env === 'development',
    IS_PRODUCTION: env === 'production',
    IS_CI: process.env.CI === 'true',
    IS_LOCAL: !process.env.CI,
  };
}
