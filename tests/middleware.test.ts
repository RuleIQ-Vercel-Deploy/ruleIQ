/**
 * Comprehensive test suite for Next.js Authentication Middleware
 * 
 * Tests all authentication flows to ensure no bypass vulnerabilities exist.
 */

import { NextRequest, NextResponse } from 'next/server';
import { middleware } from '../middleware';
import jwt from 'jsonwebtoken';

// Mock Next.js server components
jest.mock('next/server', () => ({
  NextResponse: {
    next: jest.fn(() => ({ 
      headers: new Map(),
      cookies: {
        delete: jest.fn()
      }
    })),
    redirect: jest.fn((url) => ({ 
      type: 'redirect', 
      url: url.toString(),
      headers: new Map(),
      cookies: {
        delete: jest.fn()
      }
    })),
    json: jest.fn((body, options) => ({ 
      type: 'json', 
      body, 
      status: options?.status || 200,
      headers: new Map(Object.entries(options?.headers || {}))
    }))
  },
  NextRequest: jest.fn()
}));

// Mock jwt-decode
jest.mock('jwt-decode', () => ({
  jwtDecode: jest.fn()
}));

import { jwtDecode } from 'jwt-decode';

describe('Authentication Middleware', () => {
  const SECRET_KEY = 'test-secret-key';
  
  // Helper to create mock request
  const createMockRequest = (path: string, headers: Record<string, string> = {}, cookies: Record<string, string> = {}) => {
    const url = new URL(path, 'http://localhost:3000');
    const request = {
      nextUrl: url,
      url: url.toString(),
      headers: new Map(Object.entries(headers)),
      cookies: {
        get: (name: string) => cookies[name] ? { value: cookies[name] } : undefined
      }
    } as unknown as NextRequest;
    
    // Add get method to headers Map
    request.headers.get = function(name: string) {
      return this.get(name.toLowerCase()) || null;
    };
    
    return request;
  };
  
  // Helper to create valid JWT token
  const createValidToken = (overrides: any = {}) => {
    const payload = {
      sub: 'test-user-id',
      exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
      type: 'access',
      iat: Math.floor(Date.now() / 1000),
      ...overrides
    };
    return jwt.sign(payload, SECRET_KEY);
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('Public Paths', () => {
    test('should allow access to public paths without authentication', () => {
      const publicPaths = [
        '/',
        '/login',
        '/register',
        '/forgot-password',
        '/reset-password',
        '/health',
        '/api/health'
      ];
      
      publicPaths.forEach(path => {
        const request = createMockRequest(path);
        const response = middleware(request);
        
        expect(NextResponse.next).toHaveBeenCalled();
        expect(NextResponse.redirect).not.toHaveBeenCalled();
        expect(NextResponse.json).not.toHaveBeenCalled();
      });
    });
    
    test('should allow access to static assets without authentication', () => {
      const staticPaths = [
        '/_next/static/chunks/main.js',
        '/_next/image',
        '/static/logo.png',
        '/favicon.ico',
        '/robots.txt',
        '/sitemap.xml'
      ];
      
      staticPaths.forEach(path => {
        const request = createMockRequest(path);
        const response = middleware(request);
        
        expect(NextResponse.next).toHaveBeenCalled();
        expect(NextResponse.redirect).not.toHaveBeenCalled();
      });
    });
  });
  
  describe('Protected Paths', () => {
    test('should redirect to login when accessing protected paths without token', () => {
      const protectedPaths = [
        '/dashboard',
        '/profile',
        '/settings',
        '/admin',
        '/assessments',
        '/policies'
      ];
      
      protectedPaths.forEach(path => {
        jest.clearAllMocks();
        const request = createMockRequest(path);
        const response = middleware(request);
        
        expect(NextResponse.redirect).toHaveBeenCalled();
        const redirectCall = (NextResponse.redirect as jest.Mock).mock.calls[0][0];
        expect(redirectCall.toString()).toContain('/login');
        expect(redirectCall.toString()).toContain(`from=${encodeURIComponent(path)}`);
      });
    });
    
    test('should allow access to protected paths with valid token in cookie', () => {
      const token = createValidToken();
      const decodedToken = jwt.decode(token);
      
      (jwtDecode as jest.Mock).mockReturnValue(decodedToken);
      
      const request = createMockRequest('/dashboard', {}, { access_token: token });
      const response = middleware(request);
      
      expect(NextResponse.next).toHaveBeenCalled();
      expect(NextResponse.redirect).not.toHaveBeenCalled();
    });
    
    test('should allow access to protected paths with valid token in Authorization header', () => {
      const token = createValidToken();
      const decodedToken = jwt.decode(token);
      
      (jwtDecode as jest.Mock).mockReturnValue(decodedToken);
      
      const request = createMockRequest('/dashboard', { 
        authorization: `Bearer ${token}` 
      });
      const response = middleware(request);
      
      expect(NextResponse.next).toHaveBeenCalled();
      expect(NextResponse.redirect).not.toHaveBeenCalled();
    });
  });
  
  describe('API Paths', () => {
    test('should return 401 for API paths without authentication', () => {
      const apiPaths = [
        '/api/users',
        '/api/v1/assessments',
        '/api/v1/policies',
        '/api/admin/settings'
      ];
      
      apiPaths.forEach(path => {
        jest.clearAllMocks();
        const request = createMockRequest(path);
        const response = middleware(request);
        
        expect(NextResponse.json).toHaveBeenCalledWith(
          { error: 'Authentication required' },
          expect.objectContaining({
            status: 401,
            headers: { 'WWW-Authenticate': 'Bearer' }
          })
        );
      });
    });
    
    test('should forward API requests with valid authentication', () => {
      const token = createValidToken();
      const request = createMockRequest('/api/users', {
        authorization: `Bearer ${token}`
      });
      
      const response = middleware(request);
      
      expect(NextResponse.next).toHaveBeenCalled();
      expect(NextResponse.json).not.toHaveBeenCalled();
    });
  });
  
  describe('Token Validation', () => {
    test('should reject expired tokens', () => {
      const expiredToken = createValidToken({
        exp: Math.floor(Date.now() / 1000) - 3600 // Expired 1 hour ago
      });
      
      (jwtDecode as jest.Mock).mockReturnValue(jwt.decode(expiredToken));
      
      const request = createMockRequest('/dashboard', {}, { access_token: expiredToken });
      const response = middleware(request);
      
      expect(NextResponse.redirect).toHaveBeenCalled();
      const redirectCall = (NextResponse.redirect as jest.Mock).mock.calls[0][0];
      expect(redirectCall.toString()).toContain('/login');
      expect(redirectCall.toString()).toContain('expired=true');
    });
    
    test('should reject refresh tokens for access', () => {
      const refreshToken = createValidToken({ type: 'refresh' });
      
      (jwtDecode as jest.Mock).mockReturnValue(jwt.decode(refreshToken));
      
      const request = createMockRequest('/dashboard', {}, { access_token: refreshToken });
      const response = middleware(request);
      
      expect(NextResponse.redirect).toHaveBeenCalled();
      const redirectCall = (NextResponse.redirect as jest.Mock).mock.calls[0][0];
      expect(redirectCall.toString()).toContain('/login');
      expect(redirectCall.toString()).toContain('invalid=true');
    });
    
    test('should reject malformed tokens', () => {
      const malformedToken = 'not.a.valid.token';
      
      (jwtDecode as jest.Mock).mockImplementation(() => {
        throw new Error('Invalid token');
      });
      
      const request = createMockRequest('/dashboard', {}, { access_token: malformedToken });
      const response = middleware(request);
      
      expect(NextResponse.redirect).toHaveBeenCalled();
      const redirectCall = (NextResponse.redirect as jest.Mock).mock.calls[0][0];
      expect(redirectCall.toString()).toContain('/login');
      expect(redirectCall.toString()).toContain('invalid=true');
    });
    
    test('should add warning headers for tokens expiring soon', () => {
      const expiringToken = createValidToken({
        exp: Math.floor(Date.now() / 1000) + 240 // Expires in 4 minutes
      });
      
      (jwtDecode as jest.Mock).mockReturnValue(jwt.decode(expiringToken));
      
      const request = createMockRequest('/dashboard', {}, { access_token: expiringToken });
      const response = middleware(request);
      
      expect(NextResponse.next).toHaveBeenCalledWith(
        expect.objectContaining({
          request: expect.objectContaining({
            headers: expect.any(Headers)
          })
        })
      );
    });
  });
  
  describe('Security Tests', () => {
    test('should not allow bypass with URL manipulation', () => {
      const bypassAttempts = [
        '/api/v1/users/../../../login',
        '/api/v1//users/profile',
        '/api/v1/users/profile?auth=bypass',
        '/api/v1/users/profile#auth',
        '//api/v1/users/profile'
      ];
      
      bypassAttempts.forEach(path => {
        jest.clearAllMocks();
        const request = createMockRequest(path);
        const response = middleware(request);
        
        // Should either redirect to login or return 401
        const redirectCalled = (NextResponse.redirect as jest.Mock).mock.calls.length > 0;
        const jsonCalled = (NextResponse.json as jest.Mock).mock.calls.length > 0;
        
        expect(redirectCalled || jsonCalled).toBe(true);
        
        if (jsonCalled) {
          const jsonResponse = (NextResponse.json as jest.Mock).mock.calls[0];
          expect(jsonResponse[1].status).toBe(401);
        }
      });
    });
    
    test('should not allow bypass with header manipulation', () => {
      const request = createMockRequest('/dashboard', {
        'X-Forwarded-Host': 'evil.com',
        'X-Original-URL': '/login',
        'X-Rewrite-URL': '/api/health'
      });
      
      const response = middleware(request);
      
      expect(NextResponse.redirect).toHaveBeenCalled();
      const redirectCall = (NextResponse.redirect as jest.Mock).mock.calls[0][0];
      expect(redirectCall.toString()).toContain('/login');
    });
    
    test('should not allow bypass with empty or invalid Bearer token', () => {
      const invalidTokens = [
        'Bearer',
        'Bearer ',
        'Bearer  ',
        'Basic dGVzdDp0ZXN0',
        'Token abc123',
        ''
      ];
      
      invalidTokens.forEach(authHeader => {
        jest.clearAllMocks();
        const request = createMockRequest('/api/users', {
          authorization: authHeader
        });
        
        const response = middleware(request);
        
        expect(NextResponse.json).toHaveBeenCalledWith(
          { error: 'Authentication required' },
          expect.objectContaining({
            status: 401
          })
        );
      });
    });
    
    test('should clear expired token cookie on redirect', () => {
      const expiredToken = createValidToken({
        exp: Math.floor(Date.now() / 1000) - 3600
      });
      
      (jwtDecode as jest.Mock).mockReturnValue(jwt.decode(expiredToken));
      
      const request = createMockRequest('/dashboard', {}, { access_token: expiredToken });
      const response = middleware(request);
      
      expect(NextResponse.redirect).toHaveBeenCalled();
      expect(response.cookies.delete).toHaveBeenCalledWith('access_token');
    });
  });
  
  describe('Comprehensive No-Bypass Test', () => {
    test('should block all authentication bypass attempts', () => {
      // This is the most critical test - ensures NO bypass vulnerability exists
      const protectedPath = '/api/v1/users/profile';
      
      const bypassScenarios = [
        // No auth
        { headers: {}, cookies: {} },
        
        // Invalid auth headers
        { headers: { authorization: 'Bearer' }, cookies: {} },
        { headers: { authorization: 'Bearer ' }, cookies: {} },
        { headers: { authorization: '' }, cookies: {} },
        { headers: { Authorization: 'bearer token' }, cookies: {} }, // Wrong format
        { headers: { auth: 'Bearer token' }, cookies: {} }, // Wrong header
        
        // Invalid cookies
        { headers: {}, cookies: { access_token: '' } },
        { headers: {}, cookies: { access_token: 'invalid' } },
        { headers: {}, cookies: { token: 'valid_token' } }, // Wrong cookie name
        
        // Method override attempts
        { headers: { 'X-HTTP-Method-Override': 'OPTIONS' }, cookies: {} },
        { headers: { 'X-Original-Method': 'GET' }, cookies: {} },
        
        // Content-type manipulation
        { headers: { 'Content-Type': 'application/jwt' }, cookies: {} },
        
        // Referrer spoofing
        { headers: { 'Referer': 'http://localhost:3000/login' }, cookies: {} },
      ];
      
      bypassScenarios.forEach((scenario, index) => {
        jest.clearAllMocks();
        (jwtDecode as jest.Mock).mockImplementation(() => {
          throw new Error('Invalid token');
        });
        
        const request = createMockRequest(protectedPath, scenario.headers, scenario.cookies);
        const response = middleware(request);
        
        // Must return 401 for API paths
        expect(NextResponse.json).toHaveBeenCalledWith(
          { error: 'Authentication required' },
          expect.objectContaining({
            status: 401
          })
        );
        
        // Should never call next() for protected paths without valid auth
        expect(NextResponse.next).not.toHaveBeenCalled();
      });
    });
  });
});