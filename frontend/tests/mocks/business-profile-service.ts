import { vi } from 'vitest';

export const mockBusinessProfileService = {
  getBusinessProfiles: vi.fn().mockResolvedValue([
    {
      id: 'profile-1',
      company_name: 'Test Company',
      industry: 'Technology',
      employee_count: '50-100',
      annual_revenue: '1M-5M',
      data_processing_activities: ['Customer data', 'Employee data'],
      handles_personal_data: true,
      gdpr_applicable: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    }
  ]),

  getProfile: vi.fn().mockResolvedValue({
    id: 'profile-1',
    company_name: 'Test Company',
    industry: 'Technology',
    employee_count: '50-100',
    annual_revenue: '1M-5M',
    data_processing_activities: ['Customer data', 'Employee data'],
    handles_personal_data: true,
    gdpr_applicable: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  }),

  createBusinessProfile: vi.fn().mockImplementation(async (data) => ({
    id: 'profile-new',
    company_name: data.company_name || 'New Company',
    industry: data.industry || 'Technology',
    employee_count: data.employee_count || '1-10',
    handles_personal_data: data.handles_personal_data || true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...data
  })),

  updateBusinessProfile: vi.fn().mockImplementation(async (id, data) => ({
    id: id,
    company_name: data.company_name || 'Updated Company',
    industry: data.industry || 'Technology',
    employee_count: data.employee_count || '1-10',
    handles_personal_data: data.handles_personal_data || true,
    updated_at: new Date().toISOString(),
    ...data
  }))
};

// Mock the business profile service module
vi.mock('@/lib/api/business-profiles.service', () => ({
  BusinessProfileService: vi.fn().mockImplementation(() => mockBusinessProfileService),
  businessProfileService: mockBusinessProfileService
}));
