import { vi } from 'vitest';
import { mockApiResponses, createErrorResponse } from './api-responses';

export const createUltimateApiClient = () => ({
  get: vi.fn().mockImplementation(async (url: string, options = {}) => {
    // TODO: Replace with proper logging
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

  post: vi.fn().mockImplementation(async (url: string, data: unknown, options = {}) => {
    // TODO: Replace with proper logging
    // Handle login
    if (url.includes('/auth/login')) {
      const loginData = data as { email: string; password: string };
      if (loginData.email === 'invalid@example.com') {
        return createErrorResponse(401, 'Invalid credentials');
      }
      return mockApiResponses.login;
    }

    // Handle register
    if (url.includes('/auth/register')) {
      const registerData = data as { email: string; password: string; name: string };
      if (registerData.password && registerData.password.length < 8) {
        return createErrorResponse(422, 'Password must be at least 8 characters');
      }
      return {
        data: {
          tokens: {
            access_token: 'new-access-token',
            refresh_token: 'new-refresh-token',
          },
          user: {
            id: 'user-456',
            email: registerData.email,
            name: registerData.name,
            is_active: true,
          },
        },
      };
    }

    // Handle assessments
    if (url.includes('/assessments')) {
      const assessmentData = data as { name?: string; framework_id?: string; business_profile_id?: string };
      return {
        data: {
          id: 'assess-new',
          name: assessmentData.name || 'New Assessment',
          status: 'draft',
          framework_id: assessmentData.framework_id || 'gdpr',
          business_profile_id: assessmentData.business_profile_id || 'profile-123',
        },
      };
    }

    // Handle evidence
    if (url.includes('/evidence')) {
      const evidenceData = data as { title?: string };
      return {
        data: {
          id: 'evidence-new',
          title: evidenceData.title || 'New Evidence',
          status: 'pending',
          type: 'document',
        },
      };
    }

    // Handle business profiles
    if (url.includes('/business-profiles')) {
      const profileData = data as { company_name?: string; industry?: string; employee_count?: string; handles_personal_data?: boolean };
      return {
        data: {
          id: 'profile-new',
          company_name: profileData.company_name || 'New Company',
          industry: profileData.industry || 'Technology',
          employee_count: profileData.employee_count || '1-10',
          handles_personal_data: profileData.handles_personal_data || true,
        },
      };
    }

    return { data: { success: true, id: 'new-item' } };
  }),

  put: vi.fn().mockImplementation(async (url: string, data: unknown, options = {}) => {
    // TODO: Replace with proper logging
    // Handle specific assessment updates
    if (url.includes('/assessments/assess-123')) {
      return mockApiResponses.assessment('assess-123');
    }

    return { data: { success: true, ...(data as object) } };
  }),

  patch: vi.fn().mockImplementation(async (url: string, data: unknown, options = {}) => {
    // TODO: Replace with proper logging
    // Handle evidence updates
    if (url.includes('/evidence/')) {
      const evidenceUpdateData = data as { status?: string; [key: string]: any };
      return {
        data: {
          id: url.split('/evidence/')[1],
          status: evidenceUpdateData.status || 'updated',
          ...evidenceUpdateData,
        },
      };
    }

    return { data: { success: true, ...(data as object) } };
  }),

  delete: vi.fn().mockImplementation(async (url: string, options = {}) => {
    // TODO: Replace with proper logging
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
  }),
});

export const ultimateApiClient = createUltimateApiClient();
