import { describe, it, expect, beforeEach, vi } from 'vitest'
import { businessProfileApi, type BusinessProfileCreateInput } from '../../app/api/business-profiles'
import apiClient from '../../app/lib/api-client'

// Mock the API client
vi.mock('../../app/lib/api-client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

const mockApiClient = vi.mocked(apiClient)

describe('Business Profile API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockBusinessProfile = {
    id: '1',
    company_name: 'Test Company',
    industry: 'Technology',
    employee_count: 50,
    country: 'United Kingdom',
    data_sensitivity: 'Low' as const,
    handles_personal_data: true,
    processes_payments: false,
    stores_health_data: false,
    provides_financial_services: false,
    operates_critical_infrastructure: false,
    has_international_operations: false,
    existing_frameworks: ['GDPR'],
    planned_frameworks: ['SOC 2'],
    cloud_providers: ['AWS'],
    saas_tools: ['Microsoft 365'],
    development_tools: ['GitHub'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }

  const mockCreateInput: BusinessProfileCreateInput = {
    company_name: 'Test Company',
    industry: 'Technology',
    employee_count: 50,
    country: 'United Kingdom',
    data_sensitivity: 'Low',
    handles_personal_data: true,
    existing_frameworks: ['GDPR'],
    planned_frameworks: ['SOC 2'],
    cloud_providers: ['AWS'],
    saas_tools: ['Microsoft 365'],
    development_tools: ['GitHub']
  }

  describe('createOrUpdate', () => {
    it('should create or update business profile successfully', async () => {
      mockApiClient.post.mockResolvedValueOnce({ data: mockBusinessProfile })

      const result = await businessProfileApi.createOrUpdate(mockCreateInput)

      expect(mockApiClient.post).toHaveBeenCalledWith('/business-profiles', mockCreateInput)
      expect(result).toEqual(mockBusinessProfile)
    })

    it('should handle create/update errors', async () => {
      const error = new Error('Failed to create profile')
      mockApiClient.post.mockRejectedValueOnce(error)

      await expect(businessProfileApi.createOrUpdate(mockCreateInput)).rejects.toThrow('Failed to create profile')
    })
  })

  describe('get', () => {
    it('should get business profile successfully', async () => {
      mockApiClient.get.mockResolvedValueOnce({ data: mockBusinessProfile })

      const result = await businessProfileApi.get()

      expect(mockApiClient.get).toHaveBeenCalledWith('/business-profiles')
      expect(result).toEqual(mockBusinessProfile)
    })

    it('should handle get errors', async () => {
      const error = new Error('Profile not found')
      mockApiClient.get.mockRejectedValueOnce(error)

      await expect(businessProfileApi.get()).rejects.toThrow('Profile not found')
    })
  })

  describe('getById', () => {
    it('should get business profile by ID successfully', async () => {
      const profileId = '123'
      mockApiClient.get.mockResolvedValueOnce({ data: mockBusinessProfile })

      const result = await businessProfileApi.getById(profileId)

      expect(mockApiClient.get).toHaveBeenCalledWith(`/business-profiles/${profileId}`)
      expect(result).toEqual(mockBusinessProfile)
    })
  })

  describe('update', () => {
    it('should update business profile successfully', async () => {
      const updateData = { company_name: 'Updated Company' }
      const updatedProfile = { ...mockBusinessProfile, company_name: 'Updated Company' }
      
      mockApiClient.put.mockResolvedValueOnce({ data: updatedProfile })

      const result = await businessProfileApi.update(updateData)

      expect(mockApiClient.put).toHaveBeenCalledWith('/business-profiles', updateData)
      expect(result).toEqual(updatedProfile)
    })
  })

  describe('updateById', () => {
    it('should update business profile by ID successfully', async () => {
      const profileId = '123'
      const updateData = { company_name: 'Updated Company' }
      const updatedProfile = { ...mockBusinessProfile, company_name: 'Updated Company' }
      
      mockApiClient.put.mockResolvedValueOnce({ data: updatedProfile })

      const result = await businessProfileApi.updateById(profileId, updateData)

      expect(mockApiClient.put).toHaveBeenCalledWith(`/business-profiles/${profileId}`, updateData)
      expect(result).toEqual(updatedProfile)
    })
  })

  describe('patch', () => {
    it('should partially update business profile successfully', async () => {
      const profileId = '123'
      const patchData = { company_name: 'Patched Company' }
      const patchedProfile = { ...mockBusinessProfile, company_name: 'Patched Company' }
      
      mockApiClient.patch.mockResolvedValueOnce({ data: patchedProfile })

      const result = await businessProfileApi.patch(profileId, patchData)

      expect(mockApiClient.patch).toHaveBeenCalledWith(`/business-profiles/${profileId}`, patchData)
      expect(result).toEqual(patchedProfile)
    })
  })

  describe('delete', () => {
    it('should delete business profile successfully', async () => {
      const profileId = '123'
      mockApiClient.delete.mockResolvedValueOnce({})

      await businessProfileApi.delete(profileId)

      expect(mockApiClient.delete).toHaveBeenCalledWith(`/business-profiles/${profileId}`)
    })

    it('should handle delete errors', async () => {
      const profileId = '123'
      const error = new Error('Failed to delete profile')
      mockApiClient.delete.mockRejectedValueOnce(error)

      await expect(businessProfileApi.delete(profileId)).rejects.toThrow('Failed to delete profile')
    })
  })

  describe('constants', () => {
    it('should export industry options', async () => {
      const { INDUSTRY_OPTIONS } = await import('../../app/api/business-profiles')
      
      expect(INDUSTRY_OPTIONS).toBeInstanceOf(Array)
      expect(INDUSTRY_OPTIONS).toContain('Technology')
      expect(INDUSTRY_OPTIONS).toContain('Healthcare')
    })

    it('should export employee count ranges', async () => {
      const { EMPLOYEE_COUNT_RANGES } = await import('../../app/api/business-profiles')
      
      expect(EMPLOYEE_COUNT_RANGES).toBeInstanceOf(Array)
      expect(EMPLOYEE_COUNT_RANGES[0]).toHaveProperty('label')
      expect(EMPLOYEE_COUNT_RANGES[0]).toHaveProperty('value')
    })

    it('should export compliance frameworks', async () => {
      const { COMPLIANCE_FRAMEWORKS } = await import('../../app/api/business-profiles')
      
      expect(COMPLIANCE_FRAMEWORKS).toBeInstanceOf(Array)
      expect(COMPLIANCE_FRAMEWORKS).toContain('GDPR')
      expect(COMPLIANCE_FRAMEWORKS).toContain('SOC 2')
    })

    it('should export cloud providers', async () => {
      const { CLOUD_PROVIDERS } = await import('../../app/api/business-profiles')
      
      expect(CLOUD_PROVIDERS).toBeInstanceOf(Array)
      expect(CLOUD_PROVIDERS).toContain('AWS')
      expect(CLOUD_PROVIDERS).toContain('Microsoft Azure')
    })
  })
})
