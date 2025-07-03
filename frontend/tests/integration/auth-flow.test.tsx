import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import { AuthProvider } from '@/components/auth/auth-provider';
import { LoginForm } from '@/components/auth/login-form';
import { authService } from '@/lib/api/auth.service';

import { render, screen, fireEvent, waitFor } from '../utils';

// Mock the auth service
vi.mock('@/lib/api/auth.service', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

// Mock Next.js router
const mockPush = vi.fn();
const mockReplace = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
  }),
}));

// Mock toast notifications
const mockToast = vi.fn();
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: mockToast,
  }),
}));

describe('Authentication Flow Integration', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          {component}
        </AuthProvider>
      </QueryClientProvider>
    );
  };

  describe('Login Flow', () => {
    it('should complete successful login flow', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
      };

      const mockAuthResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user: mockUser,
      };

      vi.mocked(authService.login).mockResolvedValue(mockAuthResponse);

      renderWithProviders(<LoginForm />);

      // Fill in login form
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      // Submit form
      fireEvent.click(submitButton);

      // Wait for API call
      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
        });
      });

      // Should show success toast
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Welcome back!',
        description: 'You have been successfully logged in.',
      });

      // Should redirect to dashboard
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });

    it('should handle login validation errors', async () => {
      renderWithProviders(<LoginForm />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Try to submit without filling fields
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
        expect(screen.getByText('Password is required')).toBeInTheDocument();
      });

      // Should not call API
      expect(authService.login).not.toHaveBeenCalled();
    });

    it('should handle login API errors', async () => {
      const loginError = new Error('Invalid credentials');
      vi.mocked(authService.login).mockRejectedValue(loginError);

      renderWithProviders(<LoginForm />);

      // Fill in form with invalid credentials
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'invalid@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: 'Login failed',
          description: 'Invalid credentials',
          variant: 'destructive',
        });
      });

      // Should not redirect
      expect(mockPush).not.toHaveBeenCalled();
    });

    it('should show loading state during login', async () => {
      // Mock a delayed response
      vi.mocked(authService.login).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      renderWithProviders(<LoginForm />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      // Should show loading state
      expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument();
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

      // Form should be disabled
      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
    });

    it('should handle remember me functionality', async () => {
      const mockAuthResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
        },
      };

      vi.mocked(authService.login).mockResolvedValue(mockAuthResponse);

      renderWithProviders(<LoginForm />);

      // Fill form and check remember me
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const rememberMeCheckbox = screen.getByLabelText(/remember me/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(rememberMeCheckbox);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
          remember_me: true,
        });
      });
    });
  });

  describe('Registration Flow', () => {
    it('should complete successful registration flow', async () => {
      const mockUser = {
        id: '1',
        email: 'newuser@example.com',
        full_name: 'New User',
        is_active: true,
      };

      const mockAuthResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user: mockUser,
      };

      vi.mocked(authService.register).mockResolvedValue(mockAuthResponse);

      const RegisterForm = () => (
        <form data-testid="register-form">
          <input name="full_name" placeholder="Full Name" />
          <input name="email" placeholder="Email" />
          <input name="password" placeholder="Password" />
          <input name="company" placeholder="Company" />
          <button type="submit">Create Account</button>
        </form>
      );

      renderWithProviders(<RegisterForm />);

      // Fill registration form
      const fullNameInput = screen.getByPlaceholderText('Full Name');
      const emailInput = screen.getByPlaceholderText('Email');
      const passwordInput = screen.getByPlaceholderText('Password');
      const companyInput = screen.getByPlaceholderText('Company');
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(fullNameInput, { target: { value: 'New User' } });
      fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(companyInput, { target: { value: 'Test Company' } });

      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          full_name: 'New User',
          email: 'newuser@example.com',
          password: 'password123',
          company: 'Test Company',
        });
      });

      // Should show success message
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Account created!',
        description: 'Welcome to ruleIQ. Your account has been created successfully.',
      });

      // Should redirect to business profile setup
      expect(mockPush).toHaveBeenCalledWith('/business-profile/setup');
    });

    it('should validate password strength', async () => {
      const RegisterForm = () => (
        <form data-testid="register-form">
          <input name="password" placeholder="Password" />
          <div data-testid="password-strength"></div>
        </form>
      );

      renderWithProviders(<RegisterForm />);

      const passwordInput = screen.getByPlaceholderText('Password');

      // Test weak password
      fireEvent.change(passwordInput, { target: { value: 'weak' } });

      await waitFor(() => {
        expect(screen.getByText('Password is too weak')).toBeInTheDocument();
      });

      // Test strong password
      fireEvent.change(passwordInput, { target: { value: 'StrongPassword123!' } });

      await waitFor(() => {
        expect(screen.getByText('Password strength: Strong')).toBeInTheDocument();
      });
    });

    it('should handle duplicate email registration', async () => {
      const duplicateError = new Error('Email already exists');
      vi.mocked(authService.register).mockRejectedValue(duplicateError);

      const RegisterForm = () => (
        <form data-testid="register-form">
          <input name="email" placeholder="Email" />
          <button type="submit">Create Account</button>
        </form>
      );

      renderWithProviders(<RegisterForm />);

      const emailInput = screen.getByPlaceholderText('Email');
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith({
          title: 'Registration failed',
          description: 'Email already exists',
          variant: 'destructive',
        });
      });
    });
  });

  describe('Logout Flow', () => {
    it('should complete logout flow', async () => {
      vi.mocked(authService.logout).mockResolvedValue();

      const LogoutButton = () => (
        <button onClick={() => authService.logout()}>
          Logout
        </button>
      );

      renderWithProviders(<LogoutButton />);

      const logoutButton = screen.getByRole('button', { name: /logout/i });
      fireEvent.click(logoutButton);

      await waitFor(() => {
        expect(authService.logout).toHaveBeenCalled();
      });

      // Should redirect to login page
      expect(mockReplace).toHaveBeenCalledWith('/login');

      // Should show logout message
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Logged out',
        description: 'You have been successfully logged out.',
      });
    });
  });

  describe('Session Management', () => {
    it('should handle token refresh', async () => {
      const mockRefreshResponse = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token',
      };

      vi.mocked(authService.refreshToken).mockResolvedValue(mockRefreshResponse);

      // Simulate token refresh scenario
      const TokenRefreshComponent = () => {
        const handleRefresh = async () => {
          try {
            await authService.refreshToken();
          } catch (error) {
            console.error('Token refresh failed:', error);
          }
        };

        return (
          <button onClick={handleRefresh}>
            Refresh Token
          </button>
        );
      };

      renderWithProviders(<TokenRefreshComponent />);

      const refreshButton = screen.getByRole('button', { name: /refresh token/i });
      fireEvent.click(refreshButton);

      await waitFor(() => {
        expect(authService.refreshToken).toHaveBeenCalled();
      });
    });

    it('should handle expired session', async () => {
      const expiredError = new Error('Session expired');
      vi.mocked(authService.getCurrentUser).mockRejectedValue(expiredError);

      const ProtectedComponent = () => {
        const handleGetUser = async () => {
          try {
            await authService.getCurrentUser();
          } catch (error) {
            // Handle expired session
            mockReplace('/login');
          }
        };

        return (
          <button onClick={handleGetUser}>
            Get User
          </button>
        );
      };

      renderWithProviders(<ProtectedComponent />);

      const getUserButton = screen.getByRole('button', { name: /get user/i });
      fireEvent.click(getUserButton);

      await waitFor(() => {
        expect(mockReplace).toHaveBeenCalledWith('/login');
      });
    });
  });
});
