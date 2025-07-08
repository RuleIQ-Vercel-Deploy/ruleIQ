import { vi } from 'vitest'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ReactElement, ReactNode } from 'react'

// Mock data generators
export const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  created_at: new Date().toISOString(),
  is_active: true,
  permissions: ['read', 'write'],
  role: 'user' as const,
}

export const mockBusinessProfile = {
  id: 'profile-123',
  company_name: 'Test Company',
  industry: 'Technology',
  employee_count: 50,
  country: 'United Kingdom',
  data_sensitivity: 'Medium' as const,
  handles_personal_data: true,
  required_frameworks: ['gdpr'],
}

export const mockAssessment = {
  id: 'assess-123',
  name: 'GDPR Compliance Assessment',
  framework_id: 'gdpr',
  business_profile_id: 'profile-123',
  status: 'in_progress' as const,
  created_at: new Date().toISOString(),
  responses: {},
  score: null,
}

export const mockEvidence = {
  id: 'evidence-123',
  name: 'Data Protection Policy',
  filename: 'dp-policy.pdf',
  framework: 'GDPR',
  control_reference: 'A.1.1',
  status: 'approved' as const,
  uploaded_at: new Date().toISOString(),
  file_size: 2048000,
  file_type: 'application/pdf',
  description: 'Company data protection policy',
}

export const mockFramework = {
  id: 'gdpr',
  name: 'GDPR Compliance',
  description: 'General Data Protection Regulation assessment',
  version: '1.0',
  scoringMethod: 'percentage' as const,
  passingScore: 70,
  estimatedDuration: 30,
  tags: ['Privacy', 'Data Protection'],
  sections: [
    {
      id: 'data-processing',
      title: 'Data Processing',
      description: 'Data processing activities',
      order: 1,
      questions: [
        {
          id: 'q1',
          type: 'radio' as const,
          text: 'Do you maintain records of processing activities?',
          options: [
            { value: 'yes', label: 'Yes' },
            { value: 'no', label: 'No' },
          ],
          validation: { required: true },
          weight: 1,
        },
      ],
    },
  ],
}

// Store mocks
export const createMockAuthStore = (overrides = {}) => ({
  user: null,
  tokens: { access: null, refresh: null },
  isAuthenticated: false,
  isLoading: false,
  error: null,
  sessionExpiry: null,
  accessToken: null,
  refreshToken: null,
  permissions: [],
  role: null,
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  refreshTokens: vi.fn(),
  clearError: vi.fn(),
  hasPermission: vi.fn(),
  hasRole: vi.fn(),
  hasAnyPermission: vi.fn(),
  hasAllPermissions: vi.fn(),
  ...overrides,
})

export const createMockAssessmentStore = (overrides = {}) => ({
  currentAssessment: null,
  assessments: [],
  frameworks: [],
  isLoading: false,
  error: null,
  setAssessments: vi.fn(),
  addAssessment: vi.fn(),
  updateAssessment: vi.fn(),
  setCurrentAssessment: vi.fn(),
  setFrameworks: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn(),
  clearError: vi.fn(),
  ...overrides,
})

export const createMockEvidenceStore = (overrides = {}) => ({
  evidence: [],
  currentEvidence: null,
  isLoading: false,
  error: null,
  filters: {},
  setEvidence: vi.fn(),
  addEvidence: vi.fn(),
  updateEvidence: vi.fn(),
  removeEvidence: vi.fn(),
  setCurrentEvidence: vi.fn(),
  setFilters: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn(),
  clearError: vi.fn(),
  ...overrides,
})

export const createMockBusinessProfileStore = (overrides = {}) => ({
  profile: null,
  isLoading: false,
  error: null,
  setProfile: vi.fn(),
  createProfile: vi.fn(),
  updateProfile: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn(),
  clearError: vi.fn(),
  ...overrides,
})

export const createMockDashboardStore = (overrides = {}) => ({
  widgets: [],
  metrics: {},
  isLoading: false,
  error: null,
  layout: 'default' as const,
  setWidgets: vi.fn(),
  addWidget: vi.fn(),
  removeWidget: vi.fn(),
  updateWidget: vi.fn(),
  reorderWidgets: vi.fn(),
  setMetrics: vi.fn(),
  setLayout: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn(),
  ...overrides,
})

// API service mocks
export const createMockAuthService = () => ({
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  getCurrentUser: vi.fn(),
  refreshTokens: vi.fn(),
  post: vi.fn(),
  get: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
})

export const createMockAssessmentService = () => ({
  getAssessments: vi.fn(),
  getAssessment: vi.fn(),
  createAssessment: vi.fn(),
  updateAssessment: vi.fn(),
  completeAssessment: vi.fn(),
  deleteAssessment: vi.fn(),
  getFrameworks: vi.fn(),
  getFramework: vi.fn(),
})

export const createMockEvidenceService = () => ({
  getEvidence: vi.fn(),
  getEvidenceItem: vi.fn(),
  uploadEvidence: vi.fn(),
  updateEvidence: vi.fn(),
  deleteEvidence: vi.fn(),
  downloadEvidence: vi.fn(),
})

export const createMockBusinessProfileService = () => ({
  getProfile: vi.fn(),
  createProfile: vi.fn(),
  updateProfile: vi.fn(),
  deleteProfile: vi.fn(),
})

// Secure storage mock
export const createMockSecureStorage = () => ({
  setAccessToken: vi.fn(),
  setRefreshToken: vi.fn(),
  getAccessToken: vi.fn().mockResolvedValue('test-token'),
  getRefreshToken: vi.fn().mockReturnValue('refresh-token'),
  getSessionExpiry: vi.fn(),
  isSessionExpired: vi.fn().mockReturnValue(false),
  clearAll: vi.fn(),
  migrateLegacyTokens: vi.fn(),
})

// Test utilities
export const createQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

// Test wrapper with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient
  initialRoute?: string
}

export function renderWithProviders(
  ui: ReactElement,
  {
    queryClient = createQueryClient(),
    initialRoute = '/',
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </BrowserRouter>
    )
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  }
}

// File upload utilities
export const createMockFile = (
  name: string,
  content: string = 'test content',
  type: string = 'text/plain'
): File => {
  const file = new File([content], name, { type })
  return file
}

export const createMockFileList = (files: File[]): FileList => {
  const fileList = {
    length: files.length,
    item: (index: number) => files[index] || null,
    [Symbol.iterator]: function* () {
      for (const file of files) {
        yield file
      }
    },
  }
  
  files.forEach((file, index) => {
    Object.defineProperty(fileList, index, {
      value: file,
      enumerable: true,
    })
  })
  
  return fileList as FileList
}

// Date utilities for testing
export const mockDate = (dateString: string) => {
  const date = new Date(dateString)
  vi.spyOn(global, 'Date').mockImplementation(() => date)
  return date
}

export const restoreDate = () => {
  vi.restoreAllMocks()
}

// Form validation utilities
export const expectFormValidation = async (
  submitButton: HTMLElement,
  expectedErrors: string[]
) => {
  const { fireEvent, waitFor, screen } = await import('@testing-library/react')
  
  fireEvent.click(submitButton)
  
  await waitFor(() => {
    expectedErrors.forEach(error => {
      expect(screen.getByText(new RegExp(error, 'i'))).toBeInTheDocument()
    })
  })
}

// Async utilities
export const waitForLoadingToFinish = async () => {
  const { waitFor, screen } = await import('@testing-library/react')
  
  await waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
  })
}

export const waitForErrorToAppear = async (errorText: string) => {
  const { waitFor, screen } = await import('@testing-library/react')
  
  await waitFor(() => {
    expect(screen.getByText(new RegExp(errorText, 'i'))).toBeInTheDocument()
  })
}

// Mock intersection observer for components that use it
export const mockIntersectionObserver = () => {
  const mockIntersectionObserver = vi.fn()
  mockIntersectionObserver.mockReturnValue({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  })
  
  Object.defineProperty(window, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: mockIntersectionObserver,
  })
  
  return mockIntersectionObserver
}

// Mock resize observer
export const mockResizeObserver = () => {
  const mockResizeObserver = vi.fn()
  mockResizeObserver.mockReturnValue({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  })
  
  Object.defineProperty(window, 'ResizeObserver', {
    writable: true,
    configurable: true,
    value: mockResizeObserver,
  })
  
  return mockResizeObserver
}

// Chart.js mock for dashboard tests
export const mockChartJs = () => {
  vi.mock('chart.js', () => ({
    Chart: vi.fn(),
    registerables: [],
  }))
  
  vi.mock('react-chartjs-2', () => ({
    Line: ({ data, options }: any) => (
      <div data-testid="line-chart" data-chart-data={JSON.stringify(data)} />
    ),
    Bar: ({ data, options }: any) => (
      <div data-testid="bar-chart" data-chart-data={JSON.stringify(data)} />
    ),
    Doughnut: ({ data, options }: any) => (
      <div data-testid="doughnut-chart" data-chart-data={JSON.stringify(data)} />
    ),
  }))
}

// Local storage mock
export const mockLocalStorage = () => {
  const storage: Record<string, string> = {}
  
  vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key: string) => {
    return storage[key] || null
  })
  
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation((key: string, value: string) => {
    storage[key] = value
  })
  
  vi.spyOn(Storage.prototype, 'removeItem').mockImplementation((key: string) => {
    delete storage[key]
  })
  
  vi.spyOn(Storage.prototype, 'clear').mockImplementation(() => {
    Object.keys(storage).forEach(key => delete storage[key])
  })
  
  return storage
}

// Console error suppression for expected errors
export const suppressConsoleErrors = (patterns: (string | RegExp)[]) => {
  const originalError = console.error
  console.error = (...args: any[]) => {
    const message = args[0]
    const shouldSuppress = patterns.some(pattern => {
      if (typeof pattern === 'string') {
        return message.includes(pattern)
      }
      return pattern.test(message)
    })
    
    if (!shouldSuppress) {
      originalError(...args)
    }
  }
  
  return () => {
    console.error = originalError
  }
}

export * from '@testing-library/react'
export { userEvent } from '@testing-library/user-event'