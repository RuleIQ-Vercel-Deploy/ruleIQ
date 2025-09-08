import { vi } from 'vitest';

// Emergency comprehensive API mock
export const createEmergencyApiClient = () => ({
  get: vi.fn().mockImplementation(async (url: string, options = {}) => {
    // TODO: Replace with proper logging
    // Handle all possible endpoints with proper responses
    if (url.includes('/auth/me')) {
      return {
        data: { id: 'user-123', email: 'test@example.com', name: 'Test User', is_active: true },
      };
    }
    if (url.includes('/business-profiles')) {
      return { data: { items: [{ id: 'profile-1', company_name: 'Test Company' }], total: 1 } };
    }
    if (url.includes('/assessments')) {
      if (url.includes('assess-123')) {
        return { data: { id: 'assess-123', name: 'Test Assessment', status: 'completed' } };
      }
      return { data: { items: [{ id: 'assess-1', name: 'Test Assessment 1' }], total: 1 } };
    }
    if (url.includes('/evidence')) {
      return {
        data: {
          items: [{ id: 'evidence-1', name: 'Test Evidence', status: 'approved' }],
          total: 1,
        },
      };
    }

    // Default response
    return { data: { success: true } };
  }),

  post: vi.fn().mockImplementation(async (url: string, data: unknown, options = {}) => {
    // TODO: Replace with proper logging
    if (url.includes('/auth/login')) {
      if (data.email === 'invalid@example.com') {
        throw new Error('Invalid credentials');
      }
      return {
        data: {
          tokens: { access_token: 'mock-token', refresh_token: 'mock-refresh' },
          user: { id: 'user-123', email: data.email, name: 'Test User', is_active: true },
        },
      };
    }

    if (url.includes('/auth/register')) {
      if (data.password && data.password.length < 8) {
        throw new Error('Password must be at least 8 characters');
      }
      return {
        data: {
          tokens: { access_token: 'new-token', refresh_token: 'new-refresh' },
          user: { id: 'user-456', email: data.email, name: data.name, is_active: true },
        },
      };
    }

    return { data: { success: true, id: 'new-item' } };
  }),

  put: vi.fn().mockResolvedValue({ data: { success: true } }),
  patch: vi.fn().mockResolvedValue({ data: { success: true } }),
  delete: vi.fn().mockResolvedValue({ data: { success: true } }),
  request: vi.fn().mockResolvedValue({ data: { success: true } }),
});

export const emergencyApiClient = createEmergencyApiClient();
