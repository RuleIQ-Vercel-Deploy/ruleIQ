import { vi } from 'vitest';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ReactElement, ReactNode } from 'react';

// Mock data generators
export const mockUser = {
  id: 'user-123',
  email: 'test@example.com',
  created_at: new Date().toISOString(),
  is_active: true,
  permissions: ['read', 'write'],
  role: 'user' as const,
};

export const mockBusinessProfile = {
  id: 'profile-123',
  company_name: 'Test Company',
  industry: 'Technology',
  size: '50-200',
  country: 'UK',
  data_types: ['personal', 'financial'],
  handles_personal_data: true,
  processes_payments: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export const mockAssessment = {
  id: 'assessment-123',
  name: 'GDPR Assessment',
  framework_id: 'gdpr',
  business_profile_id: 'profile-123',
  status: 'in_progress' as const,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export const mockEvidence = {
  id: 'evidence-123',
  title: 'Data Protection Policy',
  description: 'Company data protection policy document',
  status: 'collected' as const,
  evidence_type: 'policy',
  framework_id: 'gdpr',
  business_profile_id: 'profile-123',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// Query client factory
export function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: 0,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
  initialRoute?: string;
}

export function renderWithProviders(
  ui: ReactElement,
  {
    queryClient = createQueryClient(),
    initialRoute = '/',
    ...renderOptions
  }: CustomRenderOptions = {},
) {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </BrowserRouter>
    );
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  };
}

// Mock chart components to avoid canvas issues in tests
export const mockChartComponents = () => {
  vi.mock('recharts', () => ({
    ResponsiveContainer: ({ children }: { children: ReactNode }) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    LineChart: ({ children }: { children: ReactNode }) => (
      <div data-testid="line-chart">{children}</div>
    ),
    Line: () => <div data-testid="line" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />,
    BarChart: ({ children }: { children: ReactNode }) => (
      <div data-testid="bar-chart">{children}</div>
    ),
    Bar: () => <div data-testid="bar" />,
    PieChart: ({ children }: { children: ReactNode }) => (
      <div data-testid="pie-chart">{children}</div>
    ),
    Pie: () => <div data-testid="pie" />,
    Cell: () => <div data-testid="cell" />,
  }));
};

// Mock react-chartjs-2 components
export const mockChartJs2 = () => {
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
  }));
};

// Local storage mock
export const mockLocalStorage = () => {
  const storage: Record<string, string> = {};

  return {
    getItem: vi.fn((key: string) => storage[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      storage[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete storage[key];
    }),
    clear: vi.fn(() => {
      Object.keys(storage).forEach((key) => delete storage[key]);
    }),
    length: Object.keys(storage).length,
    key: vi.fn((index: number) => Object.keys(storage)[index] || null),
  };
};

// Session storage mock
export const mockSessionStorage = () => {
  const storage: Record<string, string> = {};

  return {
    getItem: vi.fn((key: string) => storage[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      storage[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete storage[key];
    }),
    clear: vi.fn(() => {
      Object.keys(storage).forEach((key) => delete storage[key]);
    }),
    length: Object.keys(storage).length,
    key: vi.fn((index: number) => Object.keys(storage)[index] || null),
  };
};

// Web API mocks
export const mockWebAPIs = () => {
  Object.defineProperty(window, 'localStorage', {
    value: mockLocalStorage(),
    writable: true,
  });

  Object.defineProperty(window, 'sessionStorage', {
    value: mockSessionStorage(),
    writable: true,
  });

  Object.defineProperty(window, 'matchMedia', {
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
    writable: true,
  });

  // Mock IntersectionObserver
  const mockIntersectionObserver = vi.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  });
  window.IntersectionObserver = mockIntersectionObserver;

  // Mock ResizeObserver
  const mockResizeObserver = vi.fn();
  mockResizeObserver.mockReturnValue({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  });
  window.ResizeObserver = mockResizeObserver;
};

// Async test utilities
export const waitFor = async (condition: () => boolean, timeout = 5000) => {
  const startTime = Date.now();
  while (!condition() && Date.now() - startTime < timeout) {
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  if (!condition()) {
    throw new Error(`Condition not met within ${timeout}ms`);
  }
};

export const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

// Test data factories
export const createMockUser = (overrides: Partial<typeof mockUser> = {}) => ({
  ...mockUser,
  ...overrides,
});

export const createMockBusinessProfile = (overrides: Partial<typeof mockBusinessProfile> = {}) => ({
  ...mockBusinessProfile,
  ...overrides,
});

export const createMockAssessment = (overrides: Partial<typeof mockAssessment> = {}) => ({
  ...mockAssessment,
  ...overrides,
});

export const createMockEvidence = (overrides: Partial<typeof mockEvidence> = {}) => ({
  ...mockEvidence,
  ...overrides,
});

// API mock responses
export const mockAPIResponses = {
  success: (data: unknown) => ({ data, message: 'Success', status: 200 }),
  error: (message: string, status = 400) => ({ detail: message, status }),
  paginated: (items: unknown[], total = items.length) => ({
    items,
    total,
    page: 1,
    size: 20,
  }),
};

// Default export for convenience
export default {
  renderWithProviders,
  mockUser,
  mockBusinessProfile,
  mockAssessment,
  mockEvidence,
  mockChartComponents,
  mockChartJs2,
  mockWebAPIs,
  mockAPIResponses,
  createMockUser,
  createMockBusinessProfile,
  createMockAssessment,
  createMockEvidence,
  waitFor,
  flushPromises,
};
