import { describe, it, expect, vi, beforeEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import { authService } from '@/lib/api/auth.service'
import { assessmentService } from '@/lib/api/assessments.service'
import { evidenceService } from '@/lib/api/evidence.service'
import { businessProfileService } from '@/lib/api/business-profiles.service'

// Mock secure storage
vi.mock('@/lib/utils/secure-storage', () => ({
  default: {
    getAccessToken: vi.fn().mockResolvedValue('test-token'),
    setAccessToken: vi.fn(),
    getRefreshToken: vi.fn().mockReturnValue('refresh-token'),
    setRefreshToken: vi.fn(),
    clearAll: vi.fn(),
    migrateLegacyTokens: vi.fn(),
  },
}))

describe('API Services with MSW', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('AuthService', () => {
    it('should handle successful login', async () => {
      const result = await authService.login({
        email: 'test@example.com',
        password: 'password123',
        rememberMe: false,
      })

      expect(result.user.id).toBe('user-123')
      expect(result.user.email).toBe('test@example.com')
      expect(result.tokens.access_token).toBe('mock-access-token')
    })

    it('should handle login failure', async () => {
      // Override the default handler for this test
      server.use(
        http.post('http://localhost:8000/api/auth/login', () => {
          return HttpResponse.json(
            { detail: 'Invalid credentials' },
            { status: 401 }
          )
        })
      )

      await expect(
        authService.login({
          email: 'test@example.com',
          password: 'wrong-password',
          rememberMe: false,
        })
      ).rejects.toThrow()
    })

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
      }

      const result = await authService.register(registrationData)
      expect(result.user.email).toBe('newuser@example.com')
    })

    it('should get current user', async () => {
      const result = await authService.getCurrentUser()
      
      expect(result.id).toBe('user-123')
      expect(result.email).toBe('test@example.com')
      expect(result.is_active).toBe(true)
    })
  })

  describe('AssessmentService', () => {
    it('should get assessments with pagination', async () => {
      const result = await assessmentService.getAssessments({
        page: 1,
        page_size: 20,
      })

      expect(result.items).toHaveLength(2)
      expect(result.total).toBe(2)
      expect(result.page).toBe(1)
      expect(result.size).toBe(20)
    })

    it('should create new assessment', async () => {
      const assessmentData = {
        name: 'New Assessment',
        framework_id: 'gdpr',
        business_profile_id: 'profile-123',
      }

      const result = await assessmentService.createAssessment(assessmentData)

      expect(result.name).toBe('New Assessment')
      expect(result.framework_id).toBe('gdpr')
      expect(result.status).toBe('draft')
    })

    it('should get single assessment', async () => {
      const result = await assessmentService.getAssessment('assess-123')

      expect(result.id).toBe('assess-123')
      expect(result.name).toBe('Test Assessment')
      expect(result.status).toBe('completed')
    })

    it('should update assessment', async () => {
      const updateData = {
        status: 'completed',
        responses: { q1: 'yes', q2: 'no' },
      }

      const result = await assessmentService.updateAssessment('assess-123', updateData)

      expect(result.id).toBe('assess-123')
      expect(result.status).toBe('completed')
    })

    it('should complete assessment', async () => {
      const result = await assessmentService.completeAssessment('assess-123')

      expect(result.id).toBe('assess-123')
      expect(result.status).toBe('completed')
    })
  })

  describe('EvidenceService', () => {
    it('should get evidence with filters', async () => {
      const filters = {
        framework_id: 'gdpr',
        status: 'collected',
        page: 1,
        page_size: 10,
      }

      const result = await evidenceService.getEvidence(filters)

      expect(result.items).toHaveLength(2)
      expect(result.total).toBe(2)
    })

    it('should upload evidence file', async () => {
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
      const metadata = {
        evidence_name: 'Test Evidence',
        framework_id: 'gdpr',
        control_reference: 'A.1.1',
      }

      const result = await evidenceService.uploadEvidence(file, metadata)

      expect(result.name).toBe('Uploaded Evidence')
      expect(result.status).toBe('uploaded')
    })

    it('should update evidence status', async () => {
      const updateData = {
        status: 'approved',
        notes: 'Evidence approved by reviewer',
      }

      const result = await evidenceService.updateEvidence('ev-123', updateData)

      expect(result.id).toBe('ev-123')
      expect(result.status).toBe('approved')
    })

    it('should delete evidence', async () => {
      // This should not throw
      await evidenceService.deleteEvidence('ev-123')
      // Test passes if no error is thrown
      expect(true).toBe(true)
    })
  })

  describe('BusinessProfileService', () => {
    it('should get business profile', async () => {
      const result = await businessProfileService.getProfile()

      expect(result.id).toBe('profile-123')
      expect(result.company_name).toBe('Test Company')
      expect(result.industry).toBe('Technology')
    })

    it('should create business profile', async () => {
      const profileData = {
        company_name: 'New Company',
        industry: 'Healthcare',
        employee_count: 25,
        country: 'United Kingdom',
        data_sensitivity: 'High',
      }

      const result = await businessProfileService.createProfile(profileData)

      expect(result.company_name).toBe('New Company')
      expect(result.industry).toBe('Healthcare')
    })

    it('should update business profile', async () => {
      const updateData = {
        employee_count: 75,
        data_sensitivity: 'Critical',
      }

      const result = await businessProfileService.updateProfile(updateData)

      expect(result.id).toBe('profile-123')
      expect(result.employee_count).toBe(75)
    })
  })

  describe('Error Handling', () => {
    it('should handle HTTP 401 errors', async () => {
      server.use(
        http.get('http://localhost:8000/api/error/401', () => {
          return HttpResponse.json(
            { detail: 'Unauthorized' },
            { status: 401 }
          )
        })
      )

      // Mock a request that will hit the error endpoint
      server.use(
        http.get('http://localhost:8000/api/auth/me', () => {
          return HttpResponse.json(
            { detail: 'Unauthorized' },
            { status: 401 }
          )
        })
      )

      await expect(authService.getCurrentUser()).rejects.toThrow()
    })

    it('should handle HTTP 404 errors', async () => {
      server.use(
        http.get('http://localhost:8000/api/assessments/non-existent', () => {
          return HttpResponse.json(
            { detail: 'Resource not found' },
            { status: 404 }
          )
        })
      )

      await expect(assessmentService.getAssessment('non-existent')).rejects.toThrow()
    })

    it('should handle validation errors (422)', async () => {
      server.use(
        http.post('http://localhost:8000/api/auth/register', () => {
          return HttpResponse.json({
            detail: [
              { field: 'email', message: 'Invalid email format' },
              { field: 'password', message: 'Password too short' },
            ],
          }, { status: 422 })
        })
      )

      await expect(
        authService.register({
          email: 'invalid-email',
          password: '123',
        } as any)
      ).rejects.toThrow()
    })

    it('should handle rate limiting (429)', async () => {
      server.use(
        http.get('http://localhost:8000/api/assessments', () => {
          return HttpResponse.json(
            { detail: 'Rate limit exceeded' },
            { status: 429 }
          )
        })
      )

      await expect(assessmentService.getAssessments()).rejects.toThrow()
    })

    it('should handle network errors', async () => {
      server.use(
        http.get('http://localhost:8000/api/auth/me', () => {
          return HttpResponse.error()
        })
      )

      await expect(authService.getCurrentUser()).rejects.toThrow()
    })
  })
})