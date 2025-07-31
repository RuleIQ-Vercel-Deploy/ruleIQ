import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { LoginForm } from '@/components/auth/stack-login-form';
import { RegisterForm } from '@/components/auth/stack-register-form';
import { StackUserMenu } from '@/components/auth/stack-user-menu';

// Mock Stack Auth components
vi.mock('@stackframe/stack', () => ({
  SignIn: ({ redirectUrl, appearance }: any) => (
    <div data-testid="stack-signin" data-redirect={redirectUrl}>
      Stack Sign In Component
    </div>
  ),
  SignUp: ({ redirectUrl, appearance }: any) => (
    <div data-testid="stack-signup" data-redirect={redirectUrl}>
      Stack Sign Up Component
    </div>
  ),
  UserButton: ({ afterSignOutUrl }: any) => (
    <div data-testid="stack-user-button" data-signout-url={afterSignOutUrl}>
      Stack User Button
    </div>
  ),
}));

describe('Stack Auth Components', () => {
  describe('LoginForm', () => {
    it('renders Stack SignIn component', () => {
      render(<LoginForm />);
      
      const signIn = screen.getByTestId('stack-signin');
      expect(signIn).toBeInTheDocument();
      expect(signIn).toHaveAttribute('data-redirect', '/dashboard');
    });
  });

  describe('RegisterForm', () => {
    it('renders Stack SignUp component', () => {
      render(<RegisterForm />);
      
      const signUp = screen.getByTestId('stack-signup');
      expect(signUp).toBeInTheDocument();
      expect(signUp).toHaveAttribute('data-redirect', '/dashboard');
    });
  });

  describe('StackUserMenu', () => {
    it('renders Stack UserButton component', () => {
      render(<StackUserMenu />);
      
      const userButton = screen.getByTestId('stack-user-button');
      expect(userButton).toBeInTheDocument();
      expect(userButton).toHaveAttribute('data-signout-url', '/login');
    });
  });
});
