import { vi } from 'vitest';
import { mockApiClient } from './api-client-mock';

// Mock the API client module
vi.mock('@/lib/api/client', () => ({
  APIClient: vi.fn().mockImplementation(() => mockApiClient),
  apiClient: mockApiClient
}));

// Mock individual service modules
vi.mock('@/lib/api/auth.service', () => ({
  AuthService: vi.fn().mockImplementation(() => ({
    login: vi.fn().mockImplementation(async (credentials) => {
      if (credentials.email === 'invalid@example.com') {
        throw new Error('Invalid credentials');
      }
      return {
        tokens: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token'
        },
        user: {
          id: 'user-123',
          email: 'test@example.com',
          name: 'Test User',
          is_active: true
        }
      };
    }),
    register: vi.fn().mockResolvedValue({
      tokens: {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      },
      user: {
        id: 'user-456',
        email: 'newuser@example.com',
        name: 'New User',
        is_active: true
      }
    }),
    getCurrentUser: vi.fn().mockResolvedValue({
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true
    }),
    logout: vi.fn().mockResolvedValue(undefined)
  })),
  authService: {
    login: vi.fn().mockImplementation(async (credentials) => {
      if (credentials.email === 'invalid@example.com') {
        throw new Error('Invalid credentials');
      }
      return {
        tokens: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token'
        },
        user: {
          id: 'user-123',
          email: 'test@example.com',
          name: 'Test User',
          is_active: true
        }
      };
    }),
    register: vi.fn().mockResolvedValue({
      tokens: {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      },
      user: {
        id: 'user-456',
        email: 'newuser@example.com',
        name: 'New User',
        is_active: true
      }
    }),
    getCurrentUser: vi.fn().mockResolvedValue({
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true
    }),
    logout: vi.fn().mockResolvedValue(undefined)
  }
}));

vi.mock('@/lib/api/assessments.service', () => ({
  AssessmentService: vi.fn().mockImplementation(() => ({
    getAssessments: vi.fn().mockResolvedValue({
      items: [
        { id: 'assess-1', name: 'Test Assessment 1' },
        { id: 'assess-2', name: 'Test Assessment 2' }
      ],
      total: 2,
      page: 1,
      size: 20
    }),
    getAssessment: vi.fn().mockResolvedValue({
      id: 'assess-1',
      name: 'Test Assessment 1',
      status: 'draft'
    }),
    createAssessment: vi.fn().mockResolvedValue({
      id: 'assess-new',
      name: 'New Assessment',
      status: 'draft',
      framework_id: 'gdpr',
      business_profile_id: 'profile-123'
    }),
    updateAssessment: vi.fn().mockResolvedValue({
      id: 'assess-1',
      name: 'Updated Assessment',
      status: 'in_progress'
    }),
    completeAssessment: vi.fn().mockResolvedValue({
      id: 'assess-1',
      status: 'completed'
    })
  })),
  assessmentService: {
    getAssessments: vi.fn().mockResolvedValue({
      items: [
        { id: 'assess-1', name: 'Test Assessment 1' },
        { id: 'assess-2', name: 'Test Assessment 2' }
      ],
      total: 2,
      page: 1,
      size: 20
    }),
    getAssessment: vi.fn().mockResolvedValue({
      id: 'assess-1',
      name: 'Test Assessment 1',
      status: 'draft'
    }),
    createAssessment: vi.fn().mockResolvedValue({
      id: 'assess-new',
      name: 'New Assessment',
      status: 'draft',
      framework_id: 'gdpr',
      business_profile_id: 'profile-123'
    }),
    updateAssessment: vi.fn().mockResolvedValue({
      id: 'assess-1',
      name: 'Updated Assessment',
      status: 'in_progress'
    }),
    completeAssessment: vi.fn().mockResolvedValue({
      id: 'assess-1',
      status: 'completed'
    })
  }
}));
