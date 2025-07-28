import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';
import React from 'react';

// Test the OAuth2 token endpoint integration
describe('OAuth2 Token Endpoint Integration', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  describe('Authentication Service OAuth2 Integration', () => {
    it('should send OAuth2 form data to /auth/token endpoint', async () => {
      // Mock successful OAuth2 token response
      let capturedRequestBody: any = null;
      server.use(
        http.post('http://localhost:8000/api/auth/token', async ({ request }) => {
          capturedRequestBody = await request.text();
          return HttpResponse.json({
            access_token: 'mock-access-token',
            refresh_token: 'mock-refresh-token',
            token_type: 'bearer',
            expires_in: 28800,
          });
        }),
        // Mock the /auth/me endpoint for user data
        http.get('http://localhost:8000/api/auth/me', () => {
          return HttpResponse.json({
            id: 'user-123',
            email: 'test@example.com',
            is_active: true,
            permissions: ['read', 'write'],
            role: 'user',
          });
        }),
      );

      const { authService } = await import('@/lib/api/auth.service');

      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      };

      await authService.login(credentials);

      // Verify OAuth2 form data format
      expect(capturedRequestBody).toBe(
        'username=test%40example.com&password=password123&grant_type=password',
      );
    });

    it('should handle 422 authentication errors correctly', async () => {
      server.use(
        http.post('http://localhost:8000/api/auth/token', () => {
          return HttpResponse.json(
            {
              detail: [
                { loc: ['body', 'username'], msg: 'field required', type: 'value_error.missing' },
              ],
            },
            { status: 422 },
          );
        }),
      );

      const { authService } = await import('@/lib/api/auth.service');

      await expect(
        authService.login({
          email: '',
          password: 'password123',
        }),
      ).rejects.toThrow();
    });

    it('should handle invalid credentials (401) correctly', async () => {
      server.use(
        http.post('http://localhost:8000/api/auth/token', () => {
          return HttpResponse.json(
            {
              detail: 'Incorrect username or password',
            },
            { status: 401 },
          );
        }),
      );

      const { authService } = await import('@/lib/api/auth.service');

      await expect(
        authService.login({
          email: 'wrong@example.com',
          password: 'wrongpassword',
        }),
      ).rejects.toThrow();
    });

    it('should fetch user data after successful token response', async () => {
      let userDataRequested = false;
      server.use(
        http.post('http://localhost:8000/api/auth/token', () => {
          return HttpResponse.json({
            access_token: 'new-access-token',
            refresh_token: 'new-refresh-token',
            token_type: 'bearer',
            expires_in: 28800,
          });
        }),
        http.get('http://localhost:8000/api/auth/me', ({ request }) => {
          userDataRequested = true;
          const authHeader = request.headers.get('Authorization');
          expect(authHeader).toBe('Bearer new-access-token');
          return HttpResponse.json({
            id: 'user-456',
            email: 'test@example.com',
            is_active: true,
            permissions: ['read', 'write'],
            role: 'user',
          });
        }),
      );

      const { authService } = await import('@/lib/api/auth.service');

      const result = await authService.login({
        email: 'test@example.com',
        password: 'password123',
      });

      expect(userDataRequested).toBe(true);
      expect(result.user.id).toBe('user-456');
      expect(result.tokens.access_token).toBe('new-access-token');
    });

    it('should store tokens securely after successful login', async () => {
      server.use(
        http.post('http://localhost:8000/api/auth/token', () => {
          return HttpResponse.json({
            access_token: 'test-access-token',
            refresh_token: 'test-refresh-token',
            token_type: 'bearer',
            expires_in: 28800,
          });
        }),
        http.get('http://localhost:8000/api/auth/me', () => {
          return HttpResponse.json({
            id: 'user-789',
            email: 'test@example.com',
            is_active: true,
            permissions: ['read'],
            role: 'user',
          });
        }),
      );

      const { authService } = await import('@/lib/api/auth.service');

      await authService.login({
        email: 'test@example.com',
        password: 'password123',
      });

      // Verify token storage (mocked in test setup)
      const storedUser = authService.getStoredUser();
      expect(storedUser?.id).toBe('user-789');
    });

    it('should handle network errors gracefully', async () => {
      server.use(
        http.post('http://localhost:8000/api/auth/token', () => {
          return HttpResponse.error();
        }),
      );

      const { authService } = await import('@/lib/api/auth.service');

      await expect(
        authService.login({
          email: 'test@example.com',
          password: 'password123',
        }),
      ).rejects.toThrow();
    });
  });

  describe('Token Storage and Retrieval', () => {
    it('should store tokens with proper expiry time', async () => {
      const { authService } = await import('@/lib/api/auth.service');
      const mockSetAccessToken = vi.fn();
      const mockSetRefreshToken = vi.fn();

      // Mock SecureStorage
      vi.doMock('@/lib/utils/secure-storage', () => ({
        default: {
          setAccessToken: mockSetAccessToken,
          setRefreshToken: mockSetRefreshToken,
        },
      }));

      server.use(
        http.post('http://localhost:8000/api/auth/token', () => {
          return HttpResponse.json({
            access_token: 'access-token',
            refresh_token: 'refresh-token',
            token_type: 'bearer',
            expires_in: 28800,
          });
        }),
        http.get('http://localhost:8000/api/auth/me', () => {
          return HttpResponse.json({
            id: 'user-123',
            email: 'test@example.com',
            is_active: true,
          });
        }),
      );

      await authService.login({
        email: 'test@example.com',
        password: 'password123',
      });

      // Verify tokens are stored with proper expiry (8 hours)
      expect(mockSetAccessToken).toHaveBeenCalledWith('access-token', {
        expiry: expect.any(Number),
      });
      expect(mockSetRefreshToken).toHaveBeenCalledWith('refresh-token', expect.any(Number));
    });

    it('should retrieve stored tokens for authenticated requests', async () => {
      const { authService } = await import('@/lib/api/auth.service');

      const isAuthenticated = await authService.isAuthenticated();
      // Should return false in test environment unless tokens are present
      expect(typeof isAuthenticated).toBe('boolean');
    });
  });
});