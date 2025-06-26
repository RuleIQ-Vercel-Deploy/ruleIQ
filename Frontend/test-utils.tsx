import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from 'next-themes'

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0
      },
      mutations: {
        retry: false
      }
    }
  })

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Mock user data for testing
export const mockUser = {
  id: '1',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  role: 'user',
  permissions: ['read', 'write'],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Mock token response for testing
export const mockTokenResponse = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
  expires_in: 3600
}

// Mock business profile for testing
export const mockBusinessProfile = {
  id: '1',
  user_id: '1',
  company_name: 'Test Company',
  industry: 'Technology',
  company_size: '10-50',
  description: 'A test company',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Mock compliance framework for testing
export const mockComplianceFramework = {
  id: '1',
  name: 'GDPR',
  description: 'General Data Protection Regulation',
  category: 'Data Protection',
  requirements_count: 99,
  created_at: '2024-01-01T00:00:00Z'
}

// Mock evidence item for testing
export const mockEvidenceItem = {
  id: '1',
  user_id: '1',
  business_profile_id: '1',
  framework_id: '1',
  evidence_name: 'Test Evidence',
  evidence_type: 'document',
  control_reference: 'GDPR-001',
  description: 'Test evidence description',
  status: 'pending',
  file_path: '/uploads/test-evidence.pdf',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Helper function to create mock API responses
export const createMockApiResponse = <T,>(data: T, status = 200) => ({
  data,
  status,
  statusText: 'OK',
  headers: {},
  config: {}
})

// Helper function to create mock API error
export const createMockApiError = (message: string, status = 400) => ({
  response: {
    data: { detail: message },
    status,
    statusText: 'Bad Request',
    headers: {},
    config: {}
  },
  message,
  isAxiosError: true
})

// Helper to wait for async operations in tests
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0))

// Re-export everything from testing-library
export * from '@testing-library/react'
export { customRender as render }
