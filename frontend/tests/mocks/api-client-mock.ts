import { vi } from 'vitest';

// Mock responses for different endpoints
const mockResponses = {
  '/auth/login': {
    tokens: {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
    },
    user: {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true,
    },
  },
  '/auth/register': {
    tokens: {
      access_token: 'new-access-token',
      refresh_token: 'new-refresh-token',
    },
    user: {
      id: 'user-456',
      email: 'newuser@example.com',
      name: 'New User',
      is_active: true,
    },
  },
  '/auth/me': {
    id: 'user-123',
    email: 'test@example.com',
    name: 'Test User',
    is_active: true,
  },
  '/assessments': {
    items: [
      { id: 'assess-1', name: 'Test Assessment 1' },
      { id: 'assess-2', name: 'Test Assessment 2' },
    ],
    total: 2,
    page: 1,
    size: 20,
  },
  '/business-profiles': {
    items: [{ id: 'profile-1', company_name: 'Test Company' }],
    total: 1,
    page: 1,
    size: 20,
  },
  '/evidence': {
    items: [{ id: 'evidence-1', name: 'Test Evidence', status: 'approved' }],
    total: 1,
    page: 1,
    size: 20,
  },
};

// Create mock API client
export const createMockApiClient = () => ({
  get: vi.fn().mockImplementation((url, options = {}) => {
    // Handle different endpoints
    if (url.includes('/auth/me')) {
      return Promise.resolve(mockResponses['/auth/me']);
    }
    if (url.includes('/assessments')) {
      return Promise.resolve(mockResponses['/assessments']);
    }
    if (url.includes('/business-profiles')) {
      return Promise.resolve(mockResponses['/business-profiles']);
    }
    if (url.includes('/evidence')) {
      return Promise.resolve(mockResponses['/evidence']);
    }

    // Default response
    return Promise.resolve({ success: true });
  }),

  post: vi.fn().mockImplementation((url, data, options = {}) => {
    if (url.includes('/auth/login')) {
      // Check for invalid credentials
      if (data.email === 'invalid@example.com') {
        return Promise.reject(new Error('Invalid credentials'));
      }
      return Promise.resolve(mockResponses['/auth/login']);
    }
    if (url.includes('/auth/register')) {
      // Check for validation errors
      if (data.password && data.password.length < 8) {
        return Promise.reject(new Error('Password must be at least 8 characters'));
      }
      return Promise.resolve(mockResponses['/auth/register']);
    }
    if (url.includes('/assessments')) {
      return Promise.resolve({
        id: 'assess-new',
        name: 'New Assessment',
        status: 'draft',
        framework_id: 'gdpr',
        business_profile_id: 'profile-123',
      });
    }

    // Default response
    return Promise.resolve({ success: true, id: 'new-item' });
  }),

  put: vi.fn().mockImplementation((url, data, options = {}) => {
    return Promise.resolve({ success: true, ...data });
  }),

  delete: vi.fn().mockImplementation((url, options = {}) => {
    return Promise.resolve({ success: true });
  }),

  request: vi.fn().mockImplementation((method, url, options = {}) => {
    const mockClient = createMockApiClient();
    switch (method.toLowerCase()) {
      case 'get':
        return mockClient.get(url, options);
      case 'post':
        return mockClient.post(url, options.data, options);
      case 'put':
        return mockClient.put(url, options.data, options);
      case 'delete':
        return mockClient.delete(url, options);
      default:
        return Promise.resolve({ success: true });
    }
  }),
});

// Global API client mock
export const mockApiClient = createMockApiClient();
