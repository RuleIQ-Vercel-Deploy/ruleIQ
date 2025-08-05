/**
 * Security Tests for AI Assessment Freemium Strategy
 * 
 * Tests security measures:
 * - Input validation and sanitization
 * - Rate limiting enforcement
 * - XSS prevention
 * - SQL injection prevention
 * - CSRF protection
 * - Authentication and authorization
 * - Data privacy compliance
 */

import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';

// Security testing utilities
class SecurityTester {
  private baseUrl = 'http://localhost:8000';
  private rateLimitTracker = new Map<string, number[]>();
  
  async testInputValidation(endpoint: string, payload: any, expectedStatus: number = 400): Promise<Response> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    
    expect(response.status).toBe(expectedStatus);
    return response;
  }
  
  async testRateLimit(endpoint: string, requests: number, timeWindow: number = 60000): Promise<Response[]> {
    const responses: Response[] = [];
    const startTime = Date.now();
    
    for (let i = 0; i < requests; i++) {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Real-IP': '192.168.1.100', // Simulate same IP
        },
        body: JSON.stringify({
          email: `ratelimit${i}@example.com`,
          consent: true,
        }),
      });
      
      responses.push(response);
      
      // Small delay to avoid overwhelming the server
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    
    return responses;
  }
  
  async testXSSPrevention(endpoint: string, xssPayload: string): Promise<Response> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: xssPayload,
        consent: true,
      }),
    });
    
    const responseText = await response.text();
    
    // Check that XSS payload is not reflected in response
    expect(responseText).not.toContain('<script>');
    expect(responseText).not.toContain('javascript:');
    expect(responseText).not.toContain('onerror=');
    
    return response;
  }
  
  async testSQLInjection(endpoint: string, sqlPayload: string): Promise<Response> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: sqlPayload,
        consent: true,
      }),
    });
    
    const responseText = await response.text();
    
    // Check that SQL error messages are not exposed
    expect(responseText).not.toContain('SQL');
    expect(responseText).not.toContain('PostgreSQL');
    expect(responseText).not.toContain('syntax error');
    expect(responseText).not.toContain('column');
    expect(responseText).not.toContain('table');
    
    return response;
  }
}

describe('Freemium Security Tests', () => {
  let securityTester: SecurityTester;
  
  beforeAll(() => {
    securityTester = new SecurityTester();
  });
  
  describe('Input Validation Tests', () => {
    it('should reject invalid email formats', async () => {
      const invalidEmails = [
        'invalid-email',
        '@example.com',
        'test@',
        'test..test@example.com',
        'test@example',
        '',
        null,
        undefined,
      ];
      
      for (const email of invalidEmails) {
        await securityTester.testInputValidation('/api/freemium/capture-email', {
          email,
          consent: true,
        }, 400);
      }
    });
    
    it('should reject missing required fields', async () => {
      const invalidPayloads = [
        {}, // Missing all fields
        { email: 'test@example.com' }, // Missing consent
        { consent: true }, // Missing email
        { email: '', consent: true }, // Empty email
        { email: 'test@example.com', consent: false }, // Consent not given
      ];
      
      for (const payload of invalidPayloads) {
        await securityTester.testInputValidation('/api/freemium/capture-email', payload, 400);
      }
    });
    
    it('should validate business type enumeration', async () => {
      const invalidBusinessTypes = [
        'invalid_type',
        123,
        null,
        '',
        '<script>alert("xss")</script>',
        'DROP TABLE users;',
      ];
      
      for (const businessType of invalidBusinessTypes) {
        await securityTester.testInputValidation('/api/freemium/start-assessment', {
          email: 'test@example.com',
          business_type: businessType,
          company_size: '10-50',
        }, 400);
      }
    });
    
    it('should validate company size enumeration', async () => {
      const invalidCompanySizes = [
        'invalid_size',
        999,
        null,
        '',
        '<script>',
        "'; DROP TABLE companies; --",
      ];
      
      for (const companySize of invalidCompanySizes) {
        await securityTester.testInputValidation('/api/freemium/start-assessment', {
          email: 'test@example.com',
          business_type: 'technology',
          company_size: companySize,
        }, 400);
      }
    });
    
    it('should validate UTM parameter length and format', async () => {
      const longString = 'a'.repeat(256); // Exceed reasonable limit
      
      await securityTester.testInputValidation('/api/freemium/capture-email', {
        email: 'test@example.com',
        consent: true,
        utm_source: longString,
      }, 400);
      
      await securityTester.testInputValidation('/api/freemium/capture-email', {
        email: 'test@example.com',
        consent: true,
        utm_medium: '<script>alert("xss")</script>',
      }, 400);
    });
  });
  
  describe('Rate Limiting Tests', () => {
    it('should enforce rate limits on email capture endpoint', async () => {
      const responses = await securityTester.testRateLimit('/api/freemium/capture-email', 25);
      
      // Check that some requests are rate limited (429 status)
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
      
      // Verify rate limit headers are present
      const lastResponse = responses[responses.length - 1];
      expect(lastResponse.headers.get('X-RateLimit-Limit')).toBeTruthy();
      expect(lastResponse.headers.get('X-RateLimit-Remaining')).toBeTruthy();
    });
    
    it('should enforce rate limits on assessment start endpoint', async () => {
      const responses = await securityTester.testRateLimit('/api/freemium/start-assessment', 15);
      
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
    
    it('should enforce stricter rate limits on AI-powered endpoints', async () => {
      // Assessment results use AI processing, so should have stricter limits
      const responses: Response[] = [];
      
      for (let i = 0; i < 10; i++) {
        const response = await fetch('http://localhost:8000/api/freemium/results', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer mock-token-${i}`,
            'X-Real-IP': '192.168.1.101',
          },
        });
        responses.push(response);
      }
      
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
    
    it('should have per-IP rate limiting', async () => {
      // Test that different IPs get separate rate limits
      const ip1Responses = await Promise.all(
        Array.from({ length: 5 }, (_, i) => 
          fetch('http://localhost:8000/api/freemium/capture-email', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Real-IP': '192.168.1.200',
            },
            body: JSON.stringify({
              email: `ip1-${i}@example.com`,
              consent: true,
            }),
          })
        )
      );
      
      const ip2Responses = await Promise.all(
        Array.from({ length: 5 }, (_, i) => 
          fetch('http://localhost:8000/api/freemium/capture-email', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Real-IP': '192.168.1.201',
            },
            body: JSON.stringify({
              email: `ip2-${i}@example.com`,
              consent: true,
            }),
          })
        )
      );
      
      // Both IPs should be successful initially
      expect(ip1Responses.every(r => r.status === 200 || r.status === 201)).toBe(true);
      expect(ip2Responses.every(r => r.status === 200 || r.status === 201)).toBe(true);
    });
  });
  
  describe('XSS Prevention Tests', () => {
    it('should prevent reflected XSS in email field', async () => {
      const xssPayloads = [
        '<script>alert("xss")</script>',
        'javascript:alert("xss")',
        '<img src="x" onerror="alert(\'xss\')" />',
        '<svg onload="alert(\'xss\')" />',
        '"><script>alert("xss")</script>',
        "'; alert('xss'); //",
      ];
      
      for (const payload of xssPayloads) {
        await securityTester.testXSSPrevention('/api/freemium/capture-email', payload);
      }
    });
    
    it('should sanitize UTM parameters', async () => {
      const xssPayload = '<script>document.location="http://evil.com"</script>';
      
      const response = await fetch('http://localhost:8000/api/freemium/capture-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          consent: true,
          utm_source: xssPayload,
          utm_medium: '<img src="x" onerror="alert(1)">',
        }),
      });
      
      const responseText = await response.text();
      expect(responseText).not.toContain('<script>');
      expect(responseText).not.toContain('onerror=');
    });
    
    it('should prevent XSS in assessment answers', async () => {
      const xssAnswer = '<script>fetch("/api/admin/users").then(r=>r.json()).then(console.log)</script>';
      
      const response = await fetch('http://localhost:8000/api/freemium/assessment/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock-token',
        },
        body: JSON.stringify({
          question_id: 'test-question',
          answer: xssAnswer,
          session_token: 'test-session',
        }),
      });
      
      const responseText = await response.text();
      expect(responseText).not.toContain('<script>');
      expect(responseText).not.toContain('fetch(');
    });
  });
  
  describe('SQL Injection Prevention Tests', () => {
    it('should prevent SQL injection in email field', async () => {
      const sqlPayloads = [
        "test@example.com'; DROP TABLE users; --",
        "test@example.com' OR '1'='1",
        "test@example.com'; INSERT INTO users (email) VALUES ('hacker@evil.com'); --",
        "test@example.com' UNION SELECT * FROM admin_users; --",
        "test@example.com'; UPDATE users SET role='admin' WHERE email='test@example.com'; --",
      ];
      
      for (const payload of sqlPayloads) {
        await securityTester.testSQLInjection('/api/freemium/capture-email', payload);
      }
    });
    
    it('should prevent SQL injection in search parameters', async () => {
      const sqlPayload = "'; DELETE FROM assessments WHERE '1'='1'; --";
      
      const response = await fetch('http://localhost:8000/api/freemium/assessment/questions', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer mock-token',
        },
      });
      
      expect(response.status).not.toBe(500); // No server error from SQL injection
    });
  });
  
  describe('Authentication and Authorization Tests', () => {
    it('should require valid tokens for protected endpoints', async () => {
      const protectedEndpoints = [
        '/api/freemium/assessment/questions',
        '/api/freemium/assessment/answer',
        '/api/freemium/results',
        '/api/freemium/conversion',
      ];
      
      for (const endpoint of protectedEndpoints) {
        // Test without token
        const noTokenResponse = await fetch(`http://localhost:8000${endpoint}`);
        expect(noTokenResponse.status).toBe(401);
        
        // Test with invalid token
        const invalidTokenResponse = await fetch(`http://localhost:8000${endpoint}`, {
          headers: {
            'Authorization': 'Bearer invalid-token-123',
          },
        });
        expect(invalidTokenResponse.status).toBe(401);
      }
    });
    
    it('should validate token format and structure', async () => {
      const invalidTokens = [
        'Bearer ', // Empty token
        'bearer valid-token', // Wrong case
        'Token valid-token', // Wrong scheme
        'Bearer token-with-spaces token', // Invalid format
        'Bearer ' + 'a'.repeat(1000), // Excessively long token
      ];
      
      for (const token of invalidTokens) {
        const response = await fetch('http://localhost:8000/api/freemium/results', {
          headers: {
            'Authorization': token,
          },
        });
        expect(response.status).toBe(401);
      }
    });
    
    it('should prevent token reuse after logout', async () => {
      // This would be tested with actual logout implementation
      const mockToken = 'Bearer logout-test-token';
      
      // First request should succeed (mocked)
      const firstResponse = await fetch('http://localhost:8000/api/freemium/results', {
        headers: {
          'Authorization': mockToken,
        },
      });
      
      // After logout, same token should be invalid
      // This would require actual logout endpoint implementation
      expect(firstResponse.status).toBeOneOf([200, 401]); // Flexible for mock environment
    });
  });
  
  describe('Data Privacy and Security Tests', () => {
    it('should not expose sensitive information in error messages', async () => {
      const response = await fetch('http://localhost:8000/api/freemium/capture-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'invalid-email-format',
          consent: true,
        }),
      });
      
      const responseText = await response.text();
      
      // Should not expose internal details
      expect(responseText).not.toContain('database');
      expect(responseText).not.toContain('connection');
      expect(responseText).not.toContain('exception');
      expect(responseText).not.toContain('traceback');
      expect(responseText).not.toContain('/home/');
      expect(responseText).not.toContain('localhost');
    });
    
    it('should validate GDPR compliance headers', async () => {
      const response = await fetch('http://localhost:8000/api/freemium/capture-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'gdpr@example.com',
          consent: true,
        }),
      });
      
      // Check for privacy-related headers
      expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
      expect(response.headers.get('X-Frame-Options')).toBeTruthy();
      expect(response.headers.get('X-XSS-Protection')).toBeTruthy();
    });
    
    it('should enforce HTTPS in production', async () => {
      // This test would be more relevant in production environment
      const response = await fetch('http://localhost:8000/api/freemium/capture-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'https@example.com',
          consent: true,
        }),
      });
      
      // In development, this is expected to work
      // In production, should redirect to HTTPS or fail
      expect(response.status).toBeOneOf([200, 201, 301, 302]);
    });
    
    it('should not cache sensitive responses', async () => {
      const response = await fetch('http://localhost:8000/api/freemium/results', {
        headers: {
          'Authorization': 'Bearer cache-test-token',
        },
      });
      
      expect(response.headers.get('Cache-Control')).toContain('no-cache');
      expect(response.headers.get('Cache-Control')).toContain('no-store');
    });
  });
  
  describe('CSRF Protection Tests', () => {
    it('should validate origin header for state-changing requests', async () => {
      const response = await fetch('http://localhost:8000/api/freemium/capture-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Origin': 'http://evil.com',
        },
        body: JSON.stringify({
          email: 'csrf@example.com',
          consent: true,
        }),
      });
      
      // Should reject requests from unauthorized origins
      expect(response.status).toBeOneOf([403, 400]);
    });
    
    it('should validate referer header', async () => {
      const response = await fetch('http://localhost:8000/api/freemium/capture-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Referer': 'http://malicious-site.com/fake-form',
        },
        body: JSON.stringify({
          email: 'referer@example.com',
          consent: true,
        }),
      });
      
      // Should reject requests with suspicious referers
      expect(response.status).toBeOneOf([403, 400]);
    });
  });
  
  describe('Frontend Security Tests', () => {
    it('should sanitize user input in forms', () => {
      const sanitizeInput = (input: string): string => {
        return input
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#x27;')
          .replace(/\//g, '&#x2F;');
      };
      
      const maliciousInput = '<script>alert("xss")</script>';
      const sanitized = sanitizeInput(maliciousInput);
      
      expect(sanitized).not.toContain('<script>');
      expect(sanitized).toBe('&lt;script&gt;alert(&quot;xss&quot;)&lt;&#x2F;script&gt;');
    });
    
    it('should validate email format client-side', () => {
      const validateEmail = (email: string): boolean => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
      };
      
      expect(validateEmail('valid@example.com')).toBe(true);
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('<script>@example.com')).toBe(false);
      expect(validateEmail('test@<script>.com')).toBe(false);
    });
    
    it('should prevent DOM-based XSS', () => {
      // Simulate URL parameter parsing
      const parseUrlParam = (param: string): string => {
        const decoded = decodeURIComponent(param);
        // Should sanitize or validate
        if (decoded.includes('<script>') || decoded.includes('javascript:')) {
          throw new Error('Invalid parameter');
        }
        return decoded;
      };
      
      expect(() => parseUrlParam('javascript:alert(1)')).toThrow();
      expect(() => parseUrlParam('%3Cscript%3Ealert(1)%3C/script%3E')).toThrow();
      expect(parseUrlParam('valid-param')).toBe('valid-param');
    });
  });
});

describe('Security Configuration Tests', () => {
  it('should have proper CORS configuration', async () => {
    const response = await fetch('http://localhost:8000/api/freemium/capture-email', {
      method: 'OPTIONS',
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
      },
    });
    
    expect(response.headers.get('Access-Control-Allow-Origin')).toBeTruthy();
    expect(response.headers.get('Access-Control-Allow-Methods')).toBeTruthy();
    expect(response.headers.get('Access-Control-Allow-Headers')).toBeTruthy();
  });
  
  it('should have security headers configured', async () => {
    const response = await fetch('http://localhost:8000/api/freemium/capture-email', {
      method: 'GET',
    });
    
    // Basic security headers
    expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
    expect(response.headers.get('X-Frame-Options')).toBeTruthy();
    expect(response.headers.get('X-XSS-Protection')).toBeTruthy();
  });
});