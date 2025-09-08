import { setupAuthMocks } from '../mocks/auth-setup';
import '../mocks/api-client-setup';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Create a mock axios instance
const mockAxiosInstance = {
  request: mockFetch,
  get: mockFetch,
  post: mockFetch,
  put: mockFetch,
  delete: mockFetch,
  patch: mockFetch,
  interceptors: {
    request: { use: vi.fn(), eject: vi.fn() },
    response: { use: vi.fn(), eject: vi.fn() },
  },
};

// Mock axios module
vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
      isAxiosError: vi.fn((error) => error.isAxiosError === true),
    },
  };
});

// Import services after mocking
import { assessmentService } from '@/lib/api/assessments.service';
import { authService } from '@/lib/api/auth.service';
import { evidenceService } from '@/lib/api/evidence.service';
import { businessProfileService } from '@/lib/api/business-profiles.service';
import { ApiError } from '@/lib/api/error-handler';

// Mock secure storage
vi.mock('@/lib/utils/secure-storage', () => ({
  default: {
    getAccessToken: vi.fn().mockResolvedValue('test-token'),
    setAccessToken: vi.fn(),
    getRefreshToken: vi.fn().mockReturnValue('refresh-token'),
    setRefreshToken: vi.fn(),
    clearAll: vi.fn(),
  },
}));

describe('API Services', () => {
  beforeEach(() => {
    setupAuthMocks();
    vi.clearAllMocks();
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('AuthService', () => {
    it('should handle successful login', async () => {
      const mockResponse = {
        tokens: {
          access_token: 'new-access-token',
          refresh_token: 'new-refresh-token',
        },
        user: {
          id: 'user-123',
          email: 'test@example.com',
          is_active: true,
        },
      };

      mockFetch.mockResolvedValueOnce({
        data: mockResponse,
        status: 200,
        statusText: 'OK',
      });

      const result = await authService.login({
        email: 'test@example.com',
        password: 'password123',
        rememberMe: false,
      });

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password123',
          }),
        }),
      );
    });

    it('should handle login failure', async () => {
      mockFetch.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { detail: 'Invalid credentials' },
        },
      });

      await expect(
        authService.login({
          email: 'test@example.com',
          password: 'wrong-password',
          rememberMe: false,
        }),
      ).rejects.toThrow('Invalid credentials');
    });

    it('should handle registration', async () => {
      const registrationData = {
        email: 'test@example.com',
        password: 'password123',
        name: 'Test User',
        company_name: 'Test Company',
        company_size: 'small' as const,
        industry: 'Technology',
        compliance_frameworks: ['gdpr'],
        has_dpo: false,
        agreed_to_terms: true,
        agreed_to_data_processing: true,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({ data: { user: { id: 'user-123' } } }),
      });

      await authService.register(registrationData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/register'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(registrationData),
        }),
      );
    });

    it('should handle logout', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ message: 'Logged out successfully' }),
      });

      await authService.logout();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/logout'),
        expect.objectContaining({
          method: 'POST',
        }),
      );
    });

    it('should get current user', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        is_active: true,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockUser }),
      });

      const result = await authService.getCurrentUser();

      expect(result).toEqual(mockUser);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        }),
      );
    });
  });

  describe('AssessmentService', () => {
    it('should get assessments with pagination', async () => {
      const mockAssessments = {
        items: [
          { id: 'assess-1', name: 'Test Assessment 1' },
          { id: 'assess-2', name: 'Test Assessment 2' },
        ],
        total: 2,
        page: 1,
        size: 20,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockAssessments,
      });

      const result = await assessmentService.getAssessments({
        page: 1,
        page_size: 20,
      });

      expect(result).toEqual(mockAssessments);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/assessments?page=1&page_size=20'),
        expect.any(Object),
      );
    });

    it('should create new assessment', async () => {
      const assessmentData = {
        name: 'New Assessment',
        framework_id: 'gdpr',
        business_profile_id: 'profile-123',
      };

      const mockResponse = {
        id: 'assess-new',
        ...assessmentData,
        status: 'draft',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({ data: mockResponse }),
      });

      const result = await assessmentService.createAssessment(assessmentData);

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/assessments'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(assessmentData),
        }),
      );
    });

    it('should get single assessment', async () => {
      const mockAssessment = {
        id: 'assess-123',
        name: 'Test Assessment',
        status: 'completed',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockAssessment }),
      });

      const result = await assessmentService.getAssessment('assess-123');

      expect(result).toEqual(mockAssessment);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/assessments/assess-123'),
        expect.any(Object),
      );
    });

    it('should update assessment', async () => {
      const updateData = {
        status: 'completed',
        responses: { q1: 'yes', q2: 'no' },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: { id: 'assess-123', ...updateData } }),
      });

      const result = await assessmentService.updateAssessment('assess-123', updateData);

      expect(result.status).toBe('completed');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/assessments/assess-123'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(updateData),
        }),
      );
    });

    it('should complete assessment', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: { status: 'completed' } }),
      });

      await assessmentService.completeAssessment('assess-123');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/assessments/assess-123/complete'),
        expect.objectContaining({
          method: 'POST',
        }),
      );
    });
  });

  describe('EvidenceService', () => {
    it('should get evidence with filters', async () => {
      const filters = {
        framework_id: 'gdpr',
        status: 'collected',
        page: 1,
        page_size: 10,
      };

      const mockEvidence = {
        items: [
          { id: 'ev-1', name: 'Evidence 1' },
          { id: 'ev-2', name: 'Evidence 2' },
        ],
        total: 2,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockEvidence,
      });

      const result = await evidenceService.getEvidence(filters);

      expect(result).toEqual(mockEvidence);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/evidence'),
        expect.any(Object),
      );
    });

    it('should upload evidence file', async () => {
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const metadata = {
        evidence_name: 'Test Evidence',
        framework_id: 'gdpr',
        control_reference: 'A.1.1',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({ data: { id: 'ev-new', status: 'uploaded' } }),
      });

      const result = await evidenceService.uploadEvidence(file, metadata);

      expect(result.status).toBe('uploaded');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/evidence/upload'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        }),
      );
    });

    it('should update evidence status', async () => {
      const updateData = {
        status: 'approved',
        notes: 'Evidence approved by reviewer',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: { id: 'ev-123', ...updateData } }),
      });

      const result = await evidenceService.updateEvidence('ev-123', updateData);

      expect(result.status).toBe('approved');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/evidence/ev-123'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(updateData),
        }),
      );
    });

    it('should delete evidence', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: async () => ({}),
      });

      await evidenceService.deleteEvidence('ev-123');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/evidence/ev-123'),
        expect.objectContaining({
          method: 'DELETE',
        }),
      );
    });
  });

  describe('BusinessProfileService', () => {
    it('should get business profile', async () => {
      const mockProfile = {
        id: 'profile-123',
        company_name: 'Test Company',
        industry: 'Technology',
        employee_count: 50,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: mockProfile }),
      });

      const result = await businessProfileService.getProfile();

      expect(result).toEqual(mockProfile);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/business-profiles/me'),
        expect.any(Object),
      );
    });

    it('should create business profile', async () => {
      const profileData = {
        company_name: 'New Company',
        industry: 'Healthcare',
        employee_count: 25,
        country: 'United Kingdom',
        data_sensitivity: 'High',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({ data: { id: 'profile-new', ...profileData } }),
      });

      const result = await businessProfileService.createProfile(profileData);

      expect(result.company_name).toBe('New Company');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/business-profiles'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(profileData),
        }),
      );
    });

    it('should update business profile', async () => {
      const updateData = {
        employee_count: 75,
        data_sensitivity: 'Critical',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: { id: 'profile-123', ...updateData } }),
      });

      const result = await businessProfileService.updateProfile(updateData);

      expect(result.employee_count).toBe(75);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/business-profiles'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(updateData),
        }),
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(authService.getCurrentUser()).rejects.toThrow('Network error');
    });

    it('should handle HTTP error responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Resource not found' }),
      });

      await expect(assessmentService.getAssessment('non-existent')).rejects.toThrow(
        'Resource not found',
      );
    });

    it('should handle authentication errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Token expired' }),
      });

      await expect(authService.getCurrentUser()).rejects.toThrow('Token expired');
    });

    it('should handle validation errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({
          detail: [
            { field: 'email', message: 'Invalid email format' },
            { field: 'password', message: 'Password too short' },
          ],
        }),
      });

      await expect(
        authService.register({
          email: 'invalid-email',
          password: '123',
        } as any),
      ).rejects.toThrow();
    });

    it('should handle rate limiting', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: async () => ({ detail: 'Rate limit exceeded' }),
      });

      await expect(assessmentService.getAssessments()).rejects.toThrow('Rate limit exceeded');
    });
  });

  describe('Request Interceptors', () => {
    it('should include authorization headers', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: {} }),
      });

      await authService.getCurrentUser();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        }),
      );
    });

    it('should handle requests without auth', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: {} }),
      });

      await authService.login({
        email: 'test@example.com',
        password: 'password',
        rememberMe: false,
      });

      const callArgs = mockFetch.mock.calls[0][1] as RequestInit;
      expect(callArgs.headers).not.toHaveProperty('Authorization');
    });
  });
});
