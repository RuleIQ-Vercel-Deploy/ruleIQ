import { vi } from 'vitest';
import { mockApiResponses, createErrorResponse } from './api-responses';

export const createUltimateApiClient = () => ({
  get: vi.fn().mockImplementation(async (url: string, options = {}) => {
    console.log('Ultimate API GET:', url, options);

    // Handle authentication endpoints
    if (url.includes('/auth/me')) {
      return mockApiResponses.login;
    }

    // Handle business profiles
    if (url.includes('/business-profiles')) {
      return mockApiResponses.businessProfiles;
    }

    // Handle assessments
    if (url.includes('/assessments/')) {
      const assessmentId = url.split('/assessments/')[1];
      if (assessmentId === 'assess-123') {
        return mockApiResponses.assessment('assess-123');
      }
      return mockApiResponses.assessment('assess-1');
    }

    if (url.includes('/assessments')) {
      return mockApiResponses.assessments;
    }

    // Handle evidence
    if (url.includes('/evidence')) {
      return mockApiResponses.evidence;
    }

    // Default response
    return { data: { success: true } };
  }),

  post: vi.fn().mockImplementation(async (url: string, data: any, options = {}) => {
    console.log('Ultimate API POST:', url, data, options);

    // Handle login
    if (url.includes('/auth/login')) {
      if (data.email === 'invalid@example.com') {
        return createErrorResponse(401, 'Invalid credentials');
      }
      return mockApiResponses.login;
    }

    // Handle register
    if (url.includes('/auth/register')) {
      if (data.password && data.password.length < 8) {
        return createErrorResponse(422, 'Password must be at least 8 characters');
      }
      return {
        data: {
          tokens: {
            access_token: 'new-access-token',
            refresh_token: 'new-refresh-token'
          },
          user: {
            id: 'user-456',
            email: data.email,
            name: data.name,
            is_active: true
          }
        }
      };
    }

    // Handle assessments
    if (url.includes('/assessments')) {
      return {
        data: {
          id: 'assess-new',
          name: data.name || 'New Assessment',
          status: 'draft',
          framework_id: data.framework_id || 'gdpr',
          business_profile_id: data.business_profile_id || 'profile-123'
        }
      };
    }

    // Handle evidence
    if (url.includes('/evidence')) {
      return {
        data: {
          id: 'evidence-new',
          title: data.title || 'New Evidence',
          status: 'pending',
          type: 'document'
        }
      };
    }

    // Handle business profiles
    if (url.includes('/business-profiles')) {
      return {
        data: {
          id: 'profile-new',
          company_name: data.company_name || 'New Company',
          industry: data.industry || 'Technology',
          employee_count: data.employee_count || '1-10',
          handles_personal_data: data.handles_personal_data || true
        }
      };
    }

    return { data: { success: true, id: 'new-item' } };
  }),

  put: vi.fn().mockImplementation(async (url: string, data: any, options = {}) => {
    console.log('Ultimate API PUT:', url, data, options);

    // Handle specific assessment updates
    if (url.includes('/assessments/assess-123')) {
      return mockApiResponses.assessment('assess-123');
    }

    return { data: { success: true, ...data } };
  }),

  patch: vi.fn().mockImplementation(async (url: string, data: any, options = {}) => {
    console.log('Ultimate API PATCH:', url, data, options);

    // Handle evidence updates
    if (url.includes('/evidence/')) {
      return {
        data: {
          id: url.split('/evidence/')[1],
          status: data.status || 'updated',
          ...data
        }
      };
    }

    return { data: { success: true, ...data } };
  }),

  delete: vi.fn().mockImplementation(async (url: string, options = {}) => {
    console.log('Ultimate API DELETE:', url, options);
    return { data: { success: true } };
  }),

  request: vi.fn().mockImplementation(async (method: string, url: string, options = {}) => {
    const client = createUltimateApiClient();
    const methodLower = method.toLowerCase();

    switch (methodLower) {
      case 'get':
        return client.get(url, options);
      case 'post':
        return client.post(url, (options as any).data, options);
      case 'put':
        return client.put(url, (options as any).data, options);
      case 'patch':
        return client.patch(url, (options as any).data, options);
      case 'delete':
        return client.delete(url, options);
      default:
        return { data: { success: true } };
    }
  })
});

export const ultimateApiClient = createUltimateApiClient();
