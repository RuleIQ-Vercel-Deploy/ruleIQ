import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the API client completely
const mockApiClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn(),
};

vi.mock('@/lib/api/client', () => ({
  apiClient: mockApiClient,
}));

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

describe('API Services - Simple Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const { authService } = await import('@/lib/api/auth.service');
      const result = await authService.login({
        email: 'test@example.com',
        password: 'password123',
        rememberMe: false,
      });

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/auth/login',
        expect.any(FormData),
        expect.objectContaining({
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }),
      );
    });

    it('should handle login failure', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('Invalid credentials'));

      const { authService } = await import('@/lib/api/auth.service');

      await expect(
        authService.login({
          email: 'test@example.com',
          password: 'wrong-password',
          rememberMe: false,
        }),
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('AssessmentService', () => {
    it('should get assessments', async () => {
      const mockAssessments = {
        items: [
          { id: 'assess-1', name: 'Test Assessment 1' },
          { id: 'assess-2', name: 'Test Assessment 2' },
        ],
        total: 2,
        page: 1,
        size: 20,
      };

      mockApiClient.get.mockResolvedValueOnce(mockAssessments);

      const { assessmentService } = await import('@/lib/api/assessments.service');
      const result = await assessmentService.getAssessments({
        page: 1,
        page_size: 20,
      });

      expect(result).toEqual(mockAssessments);
      expect(mockApiClient.get).toHaveBeenCalledWith('/assessments', {
        params: { page: 1, page_size: 20 },
      });
    });

    it('should create assessment', async () => {
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

      mockApiClient.post.mockResolvedValueOnce({ data: mockResponse });

      const { assessmentService } = await import('@/lib/api/assessments.service');
      const result = await assessmentService.createAssessment(assessmentData);

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith('/assessments', assessmentData);
    });
  });

  describe('EvidenceService', () => {
    it('should get evidence', async () => {
      const mockEvidence = {
        items: [
          { id: 'ev-1', name: 'Evidence 1' },
          { id: 'ev-2', name: 'Evidence 2' },
        ],
        total: 2,
      };

      mockApiClient.get.mockResolvedValueOnce(mockEvidence);

      const { evidenceService } = await import('@/lib/api/evidence.service');
      const result = await evidenceService.getEvidence({
        framework_id: 'gdpr',
        status: 'collected',
      });

      expect(result).toEqual(mockEvidence);
      expect(mockApiClient.get).toHaveBeenCalledWith('/evidence', {
        params: { framework_id: 'gdpr', status: 'collected' },
      });
    });

    it('should upload evidence', async () => {
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const metadata = {
        evidence_name: 'Test Evidence',
        framework_id: 'gdpr',
        control_reference: 'A.1.1',
      };

      mockApiClient.post.mockResolvedValueOnce({
        data: { id: 'ev-new', status: 'uploaded' },
      });

      const { evidenceService } = await import('@/lib/api/evidence.service');
      const result = await evidenceService.uploadEvidence(file, metadata);

      expect(result.status).toBe('uploaded');
      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/evidence/upload',
        expect.any(FormData),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'multipart/form-data',
          }),
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

      mockApiClient.get.mockResolvedValueOnce({ data: mockProfile });

      const { businessProfileService } = await import('@/lib/api/business-profiles.service');
      const result = await businessProfileService.getProfile();

      expect(result).toEqual(mockProfile);
      expect(mockApiClient.get).toHaveBeenCalledWith('/business-profiles/me');
    });

    it('should create business profile', async () => {
      const profileData = {
        company_name: 'New Company',
        industry: 'Healthcare',
        employee_count: 25,
      };

      mockApiClient.post.mockResolvedValueOnce({
        data: { id: 'profile-new', ...profileData },
      });

      const { businessProfileService } = await import('@/lib/api/business-profiles.service');
      const result = await businessProfileService.createProfile(profileData);

      expect(result.company_name).toBe('New Company');
      expect(mockApiClient.post).toHaveBeenCalledWith('/business-profiles', profileData);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Network error'));

      const { authService } = await import('@/lib/api/auth.service');
      await expect(authService.getCurrentUser()).rejects.toThrow('Network error');
    });

    it('should handle HTTP error responses', async () => {
      mockApiClient.get.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { detail: 'Resource not found' },
        },
      });

      const { assessmentService } = await import('@/lib/api/assessments.service');
      await expect(assessmentService.getAssessment('non-existent')).rejects.toMatchObject({
        response: expect.objectContaining({
          status: 404,
        }),
      });
    });
  });
});
