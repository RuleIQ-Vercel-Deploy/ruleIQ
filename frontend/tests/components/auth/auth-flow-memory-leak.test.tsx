import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import RegisterPage from '@/app/(auth)/register/page';
import { renderWithLeakDetection, testComponentMemoryLeaks, testRapidMountUnmount } from '@/tests/utils/component-test-helpers';

// Create mock references
let mockRouterPush: any;
let mockAuthServiceRegister: any;
let mockAuthServiceLogin: any;
let mockAuthStoreClearError: any;
let mockAppStoreAddNotification: any;

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
}));

// Create a function to get current auth store state
let authStoreState = {
  login: vi.fn(),
  register: vi.fn(),
  isLoading: false,
  error: null,
  clearError: vi.fn(),
  user: null,
  isAuthenticated: false,
};

// Mock the stores
vi.mock('@/lib/stores/auth.store', () => ({
  useAuthStore: () => authStoreState,
}));

vi.mock('@/lib/stores/app.store', () => ({
  useAppStore: () => ({
    addNotification: vi.fn(),
  }),
}));

// Mock authService
vi.mock('@/lib/api/auth.service', () => ({
  authService: {
    register: vi.fn(),
    login: vi.fn(),
  },
}));

const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('Authentication Flow - Memory Leak Detection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Reset auth store state
    authStoreState = {
      login: vi.fn(),
      register: vi.fn(),
      isLoading: false,
      error: null,
      clearError: vi.fn(),
      user: null,
      isAuthenticated: false,
    };
  });

  describe('RegisterPage Memory Leaks', () => {
    it('should cleanup all resources on unmount', async () => {
      await testComponentMemoryLeaks(
        RegisterPage,
        {},
        async (result) => {
          // Fill in form
          const emailInput = screen.getByLabelText(/email/i);
          const passwordInput = screen.getByLabelText(/^password/i);
          const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
          
          fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
          fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
          fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
          
          // Trigger some interactions
          const submitButton = screen.getByRole('button', { name: /create account/i });
          fireEvent.click(submitButton);
          
          // Wait for any async operations
          await waitFor(() => {
            expect(authStoreState.register).toHaveBeenCalled();
          });
        }
      );
    });

    it('should handle rapid mount/unmount cycles without leaks', async () => {
      const TestWrapper = createTestWrapper();
      
      await testRapidMountUnmount(
        () => (
          <TestWrapper>
            <RegisterPage />
          </TestWrapper>
        ),
        {},
        5 // Test with 5 rapid cycles
      );
    });

    it('should cleanup form state and event listeners on unmount', () => {
      const TestWrapper = createTestWrapper();
      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );
      
      // Add some form interactions
      const passwordInput = screen.getByLabelText(/^password/i) as HTMLInputElement;
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;
      
      fireEvent.change(passwordInput, { target: { value: 'secret123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'secret123' } });
      
      // Toggle password visibility
      const toggleButtons = screen.getAllByRole('button', { name: /toggle password visibility/i });
      toggleButtons.forEach(button => fireEvent.click(button));
      
      // Verify values are set
      expect(passwordInput.value).toBe('secret123');
      expect(confirmPasswordInput.value).toBe('secret123');
      
      // Unmount component
      unmount();
      
      // Assert no memory leaks
      assertNoLeaks();
      
      // Cleanup
      leakDetector.teardown();
    });

    it('should cleanup async operations on unmount', async () => {
      const TestWrapper = createTestWrapper();
      
      // Mock a slow registration process
      authStoreState.register.mockImplementation(() => {
        return new Promise(resolve => setTimeout(resolve, 1000));
      });
      
      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );
      
      // Start registration process
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'TestPassword123!' } });
      fireEvent.click(submitButton);
      
      // Unmount while async operation is in progress
      unmount();
      
      // Wait a bit to ensure no late updates
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Assert no memory leaks
      assertNoLeaks();
      
      // Cleanup
      leakDetector.teardown();
    });
  });

  describe('Form Input Memory Leaks', () => {
    it('should cleanup input event listeners', () => {
      const TestWrapper = createTestWrapper();
      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );
      
      // Get all form inputs
      const inputs = screen.getAllByRole('textbox');
      const passwordInputs = screen.getAllByLabelText(/password/i);
      
      // Add listeners by interacting with inputs
      [...inputs, ...passwordInputs].forEach(input => {
        fireEvent.focus(input);
        fireEvent.blur(input);
        fireEvent.change(input, { target: { value: 'test' } });
      });
      
      // Check for any select elements (framework dropdown)
      const selectElements = document.querySelectorAll('select');
      selectElements.forEach(select => {
        fireEvent.change(select, { target: { value: 'gdpr' } });
      });
      
      // Unmount
      unmount();
      
      // Assert no leaks
      assertNoLeaks();
      
      // Get detailed report
      const report = leakDetector.getReport();
      console.log('Memory leak report:', report);
      
      // Cleanup
      leakDetector.teardown();
    });
  });

  describe('Error State Memory Leaks', () => {
    it('should cleanup error states and handlers', async () => {
      const TestWrapper = createTestWrapper();
      
      // Set up error state
      authStoreState.error = 'Registration failed';
      authStoreState.clearError = vi.fn();
      
      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <TestWrapper>
          <RegisterPage />
        </TestWrapper>
      );
      
      // Wait for error to be displayed
      await waitFor(() => {
        expect(screen.getByText(/registration failed/i)).toBeInTheDocument();
      });
      
      // Clear error
      fireEvent.click(screen.getByRole('button', { name: /dismiss/i }));
      
      // Unmount
      unmount();
      
      // Assert no leaks
      assertNoLeaks();
      
      // Cleanup
      leakDetector.teardown();
    });
  });
});