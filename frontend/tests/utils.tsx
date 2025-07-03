import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, type RenderOptions } from '@testing-library/react'
import React, { type ReactElement } from 'react'

import { ThemeProvider } from '@/components/theme-provider'

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Mock data generators
export const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  role: 'admin' as const,
}

export const mockBusinessProfile = {
  id: '1',
  company_name: 'Test Company',
  industry: 'Technology',
  company_size: '50-100',
  primary_location: 'UK',
  handles_personal_data: true,
  data_types: ['Customer Data'],
  compliance_frameworks: ['GDPR'],
  current_compliance_level: 'Basic',
}

export const mockApiResponse = <T,>(data: T) => ({
  data,
  message: 'Success',
  status: 200,
})

export const mockPaginatedResponse = <T,>(items: T[]) => ({
  items,
  total: items.length,
  page: 1,
  page_size: 10,
  total_pages: Math.ceil(items.length / 10),
})

// Test helpers
export const waitForLoadingToFinish = () => 
  new Promise(resolve => setTimeout(resolve, 0))

export const createMockIntersectionObserver = () => {
  const mockIntersectionObserver = vi.fn()
  mockIntersectionObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  })
  window.IntersectionObserver = mockIntersectionObserver
  window.IntersectionObserverEntry = vi.fn() as any
}
