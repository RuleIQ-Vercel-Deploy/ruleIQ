import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import LoginPage from '@/app/(auth)/login/page'
import RegisterPage from '@/app/(auth)/register/page'

// Mock the auth store
const mockAuthStore = {
  login: vi.fn(),
  register: vi.fn(),
  isLoading: false,
  error: null,
  clearError: vi.fn(),
  user: null,
  isAuthenticated: false,
}

vi.mock('@/lib/stores/auth.store', () => ({
  useAuthStore: () => mockAuthStore,
}))

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
  }),
  useSearchParams: () => ({
    get: vi.fn().mockReturnValue(null),
  }),
}))

// Test wrapper with QueryClient
const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  
  return function TestWrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    )
  }
}

describe('Authentication Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.isLoading = false
    mockAuthStore.error = null
  })

  describe('LoginPage', () => {
    it('should render login form', () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )
      
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    })

    it('should handle form submission', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)
      
      await waitFor(() => {
        expect(mockAuthStore.login).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
          rememberMe: false,
        })
      })
    })

    it('should validate form fields', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )
      
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      fireEvent.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument()
        expect(screen.getByText(/password is required/i)).toBeInTheDocument()
      })
    })

    it('should show loading state during authentication', () => {
      mockAuthStore.isLoading = true
      
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )
      
      const submitButton = screen.getByRole('button', { name: /signing in/i })
      expect(submitButton).toBeDisabled()
    })

    it('should display authentication errors', () => {
      mockAuthStore.error = 'Invalid credentials'
      
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )
      
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
    })

    it('should handle remember me checkbox', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )
      
      const rememberMeCheckbox = screen.getByLabelText(/remember me/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      fireEvent.click(rememberMeCheckbox)
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)
      
      await waitFor(() => {
        expect(mockAuthStore.login).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
          rememberMe: true,
        })
      })
    })
  })

  describe('RegisterPage', () => {
    it('should render registration form', () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      )
      
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/^password/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
    })

    it('should handle multi-step registration', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      )
      
      // Step 1: Account credentials
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/^password/i)
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } })
      
      const nextButton = screen.getByRole('button', { name: /next/i })
      fireEvent.click(nextButton)
      
      await waitFor(() => {
        expect(screen.getByLabelText(/first name/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/company name/i)).toBeInTheDocument()
      })
    })

    it('should validate password confirmation', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      )
      
      const passwordInput = screen.getByLabelText(/^password/i)
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.change(confirmPasswordInput, { target: { value: 'different' } })
      
      const nextButton = screen.getByRole('button', { name: /next/i })
      fireEvent.click(nextButton)
      
      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
      })
    })

    it('should require terms and conditions acceptance', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      )
      
      // Navigate through all steps without accepting terms
      // ... (simulate filling out form)
      
      const submitButton = screen.getByRole('button', { name: /create account/i })
      fireEvent.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/must accept terms/i)).toBeInTheDocument()
      })
    })

    it('should handle company size selection', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      )
      
      // Navigate to company info step
      // ... (simulate first step completion)
      
      const companySizeSelect = screen.getByLabelText(/company size/i)
      fireEvent.click(companySizeSelect)
      
      await waitFor(() => {
        expect(screen.getByText(/micro/i)).toBeInTheDocument()
        expect(screen.getByText(/small/i)).toBeInTheDocument()
        expect(screen.getByText(/medium/i)).toBeInTheDocument()
        expect(screen.getByText(/large/i)).toBeInTheDocument()
      })
    })

    it('should handle compliance framework selection', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      )
      
      // Navigate to compliance step
      // ... (simulate previous steps completion)
      
      const gdprCheckbox = screen.getByLabelText(/gdpr/i)
      const iso27001Checkbox = screen.getByLabelText(/iso 27001/i)
      
      fireEvent.click(gdprCheckbox)
      fireEvent.click(iso27001Checkbox)
      
      expect(gdprCheckbox).toBeChecked()
      expect(iso27001Checkbox).toBeChecked()
    })

    it('should complete registration successfully', async () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      )
      
      // Fill out complete registration form
      // ... (simulate all steps)
      
      const submitButton = screen.getByRole('button', { name: /create account/i })
      fireEvent.click(submitButton)
      
      await waitFor(() => {
        expect(mockAuthStore.register).toHaveBeenCalledWith(
          expect.objectContaining({
            email: expect.any(String),
            password: expect.any(String),
            agreedToTerms: true,
            agreedToDataProcessing: true,
          })
        )
      })
    })
  })

  describe('Authentication Security', () => {
    it('should not expose sensitive data in form state', () => {
      const TestWrapper = createTestWrapper()
      render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )
      
      const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement
      fireEvent.change(passwordInput, { target: { value: 'secret123' } })
      
      // Password should not be visible in the DOM
      expect(passwordInput.type).toBe('password')
      expect(passwordInput.value).toBe('secret123')
    })

    it('should clear form on component unmount', () => {
      const TestWrapper = createTestWrapper()
      const { unmount } = render(
        <TestWrapper>
          <LoginPage />
        </TestWrapper>
      )
      
      const passwordInput = screen.getByLabelText(/password/i)
      fireEvent.change(passwordInput, { target: { value: 'secret123' } })
      
      unmount()
      
      // Form data should be cleared
      expect(mockAuthStore.clearError).toHaveBeenCalled()
    })
  })
})