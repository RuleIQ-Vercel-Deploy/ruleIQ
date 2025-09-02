// Comprehensive API response mocks with proper data structure

export const mockApiResponses = {
  // Auth responses
  login: {
    data: {
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
  },

  // Business profile responses
  businessProfiles: {
    data: {
      items: [
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
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      size: 20,
    },
  },

  // Assessment responses
  assessments: {
    data: {
      items: [
        { id: 'assess-1', name: 'Test Assessment 1', status: 'draft' },
        { id: 'assess-2', name: 'Test Assessment 2', status: 'completed' },
      ],
      total: 2,
      page: 1,
      size: 20,
    },
  },

  // Specific assessment response
  assessment: (id: string) => ({
    data: {
      id: id,
      name: `Test Assessment ${id}`,
      status: 'completed',
      framework_id: 'gdpr',
      business_profile_id: 'profile-123',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  }),

  // Evidence responses
  evidence: {
    data: {
      items: [
        {
          id: 'evidence-1',
          title: 'Test Evidence',
          name: 'Test Evidence',
          status: 'approved',
          type: 'document',
          uploadDate: '2024-01-01',
          fileType: 'pdf',
        },
      ],
      total: 1,
      page: 1,
      size: 20,
    },
  },
};

// Error response helper
export const createErrorResponse = (status: number, message: string) => {
  const error = new Error(message);
  (error as any).status = status;
  return Promise.reject(error);
};
