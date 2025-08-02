import { vi } from 'vitest';

// Mock auth tokens for tests
export const mockTokens = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
  expires_in: 3600
};

export const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  is_active: true
};

// Setup auth mocks for tests
export const setupAuthMocks = () => {
  // Mock SecureStorage
  vi.mock('@/lib/utils/secure-storage', () => ({
    SecureStorage: {
      getAccessToken: vi.fn().mockResolvedValue('mock-access-token'),
      setAccessToken: vi.fn().mockResolvedValue(undefined),
      getRefreshToken: vi.fn().mockResolvedValue('mock-refresh-token'),
      setRefreshToken: vi.fn().mockResolvedValue(undefined),
      clearAll: vi.fn().mockResolvedValue(undefined),
      isSessionExpired: vi.fn().mockReturnValue(false)
    }
  }));

  // Mock auth store
  vi.mock('@/lib/stores/auth.store', () => ({
    useAuthStore: {
      getState: vi.fn(() => ({
        user: mockUser,
        tokens: mockTokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        login: vi.fn().mockResolvedValue(mockUser),
        register: vi.fn().mockResolvedValue(mockUser),
        logout: vi.fn().mockResolvedValue(undefined),
        getCurrentUser: vi.fn().mockResolvedValue(mockUser)
      })),
      setState: vi.fn(),
      subscribe: vi.fn()
    }
  }));

  // Mock API client with auth
  global.fetch = vi.fn().mockImplementation((url, options = {}) => {
    const headers = options.headers || {};
    
    // Mock successful responses based on URL
    if (url.includes('/auth/login')) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ ...mockTokens, user: mockUser })
      });
    }
    
    if (url.includes('/auth/register')) {
      return Promise.resolve({
        ok: true,
        status: 201,
        json: () => Promise.resolve({ ...mockTokens, user: mockUser })
      });
    }
    
    if (url.includes('/auth/me')) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockUser)
      });
    }
    
    // Default successful response
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ success: true })
    });
  });
};
