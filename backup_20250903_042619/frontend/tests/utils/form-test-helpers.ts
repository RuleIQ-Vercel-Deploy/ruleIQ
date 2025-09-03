import { fireEvent, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

export const fillAndSubmitLoginForm = async (email: string, password: string) => {
  const emailInput = screen.getByLabelText(/email/i);
  const passwordInput = screen.getByLabelText(/password/i);
  const submitButton = screen.getByRole('button', { name: /login/i });

  fireEvent.change(emailInput, { target: { value: email } });
  fireEvent.change(passwordInput, { target: { value: password } });
  fireEvent.click(submitButton);

  return { emailInput, passwordInput, submitButton };
};

export const fillAndSubmitRegisterForm = async (formData: {
  company: string;
  email: string;
  password: string;
  confirmPassword: string;
}) => {
  const companyInput = screen.getByLabelText(/company name/i);
  const emailInput = screen.getByLabelText(/email/i);
  const passwordInput = screen.getByLabelText(/^password$/i);
  const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
  const submitButton = screen.getByRole('button', { name: /create account/i });

  fireEvent.change(companyInput, { target: { value: formData.company } });
  fireEvent.change(emailInput, { target: { value: formData.email } });
  fireEvent.change(passwordInput, { target: { value: formData.password } });
  fireEvent.change(confirmPasswordInput, { target: { value: formData.confirmPassword } });
  fireEvent.click(submitButton);

  return { companyInput, emailInput, passwordInput, confirmPasswordInput, submitButton };
};

export const mockAuthService = {
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  getCurrentUser: vi.fn(),
};
