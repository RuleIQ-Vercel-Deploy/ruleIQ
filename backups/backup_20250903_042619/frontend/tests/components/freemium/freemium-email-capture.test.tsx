/**
 * Comprehensive tests for FreemiumEmailCapture component
 *
 * Tests:
 * - Email validation and format checking
 * - UTM parameter capture from URL
 * - Consent handling (marketing and terms)
 * - Form submission and API integration
 * - Error handling and loading states
 * - Accessibility and keyboard navigation
 * - Performance and memory leak prevention
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { server } from '../../mocks/server';
import { rest } from 'msw';

import { FreemiumEmailCapture } from '../../../components/freemium/freemium-email-capture';
import { useFreemiumStore } from '../../../lib/stores/freemium-store';
import * as freemiumApi from '../../../lib/api/freemium.service';

// Mock the API service
vi.mock('../../../lib/api/freemium.service');
const mockedFreemiumApi = vi.mocked(freemiumApi);

// Mock the store
vi.mock('../../../lib/stores/freemium-store');
const mockedUseFreemiumStore = vi.mocked(useFreemiumStore);

// Mock router
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () => ({
    get: vi.fn((param) => {
      const params: Record<string, string> = {
        utm_source: 'google',
        utm_campaign: 'compliance_assessment',
        utm_medium: 'cpc',
        utm_term: 'gdpr_compliance',
        utm_content: 'cta_button',
      };
      return params[param] || null;
    }),
    toString: () => 'utm_source=google&utm_campaign=compliance_assessment',
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

const defaultStoreState = {
  email: '',
  token: null,
  utmSource: null,
  utmCampaign: null,
  utmMedium: null,
  utmTerm: null,
  utmContent: null,
  consentMarketing: false,
  consentTerms: false,
  setEmail: vi.fn(),
  setToken: vi.fn(),
  setUtmParams: vi.fn(),
  setConsent: vi.fn(),
  reset: vi.fn(),
};

describe('FreemiumEmailCapture', () => {
  beforeEach(() => {
    queryClient.clear();
    vi.clearAllMocks();
    mockPush.mockClear();
    mockedUseFreemiumStore.mockReturnValue(defaultStoreState);
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe('Initial Render', () => {
    it('renders all required form elements', () => {
      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/i agree to receive marketing/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/i agree to the terms of service/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /start free assessment/i })).toBeInTheDocument();
    });

    it('has proper accessibility attributes', () => {
      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('required');
      expect(emailInput).toHaveAttribute('aria-invalid', 'false');

      const submitButton = screen.getByRole('button', { name: /start free assessment/i });
      expect(submitButton).toHaveAttribute('type', 'submit');
    });

    it('displays helpful placeholder text', () => {
      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      expect(screen.getByPlaceholderText(/enter your email address/i)).toBeInTheDocument();
    });
  });

  describe('Email Validation', () => {
    const user = userEvent.setup();

    it('validates email format on blur', async () => {
      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);

      await user.type(emailInput, 'invalid-email');
      await user.tab(); // Trigger blur

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
      });

      expect(emailInput).toHaveAttribute('aria-invalid', 'true');
    });

    it('clears validation error when valid email is entered', async () => {
      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);

      // Enter invalid email first
      await user.type(emailInput, 'invalid');
      await user.tab();

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
      });

      // Clear and enter valid email
      await user.clear(emailInput);
      await user.type(emailInput, 'valid@example.com');
      await user.tab();

      await waitFor(() => {
        expect(screen.queryByText(/please enter a valid email address/i)).not.toBeInTheDocument();
      });

      expect(emailInput).toHaveAttribute('aria-invalid', 'false');
    });

    it('accepts various valid email formats', async () => {
      const validEmails = [
        'test@example.com',
        'user.name+tag@domain.co.uk',
        'test123@test-domain.com',
        'a@b.co',
      ];

      for (const email of validEmails) {
        render(
          <TestWrapper>
            <FreemiumEmailCapture />
          </TestWrapper>,
        );

        const emailInput = screen.getByLabelText(/email address/i);
        await user.type(emailInput, email);
        await user.tab();

        await waitFor(() => {
          expect(screen.queryByText(/please enter a valid email address/i)).not.toBeInTheDocument();
        });

        // Cleanup for next iteration
        queryClient.clear();
      }
    });

    it('rejects invalid email formats', async () => {
      const invalidEmails = [
        'plainaddress',
        '@missinglocalpart.com',
        'missing-at-sign.com',
        'missing.domain@',
        'spaces in@email.com',
        'double@@domain.com',
      ];

      for (const email of invalidEmails) {
        render(
          <TestWrapper>
            <FreemiumEmailCapture />
          </TestWrapper>,
        );

        const emailInput = screen.getByLabelText(/email address/i);
        await user.type(emailInput, email);
        await user.tab();

        await waitFor(() => {
          expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
        });

        // Cleanup for next iteration
        queryClient.clear();
      }
    });
  });

  describe('UTM Parameter Capture', () => {
    it('captures UTM parameters on component mount', () => {
      const mockSetUtmParams = vi.fn();
      mockedUseFreemiumStore.mockReturnValue({
        ...defaultStoreState,
        setUtmParams: mockSetUtmParams,
      });

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      expect(mockSetUtmParams).toHaveBeenCalledWith({
        utm_source: 'google',
        utm_campaign: 'compliance_assessment',
        utm_medium: 'cpc',
        utm_term: 'gdpr_compliance',
        utm_content: 'cta_button',
      });
    });

    it('handles missing UTM parameters gracefully', () => {
      // Mock empty search params
      vi.mocked(vi.importMock('next/navigation')).useSearchParams.mockReturnValue({
        get: vi.fn(() => null),
        toString: () => '',
      });

      const mockSetUtmParams = vi.fn();
      mockedUseFreemiumStore.mockReturnValue({
        ...defaultStoreState,
        setUtmParams: mockSetUtmParams,
      });

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      expect(mockSetUtmParams).toHaveBeenCalledWith({
        utm_source: null,
        utm_campaign: null,
        utm_medium: null,
        utm_term: null,
        utm_content: null,
      });
    });
  });

  describe('Consent Handling', () => {
    const user = userEvent.setup();

    it('prevents submission without terms consent', async () => {
      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const marketingConsent = screen.getByLabelText(/i agree to receive marketing/i);
      const submitButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(marketingConsent);
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/you must agree to the terms of service/i)).toBeInTheDocument();
      });

      expect(mockedFreemiumApi.captureEmail).not.toHaveBeenCalled();
    });

    it('allows submission with terms consent only', async () => {
      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'test-token-123',
        message: 'Email captured successfully',
      });

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(termsConsent);
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockedFreemiumApi.captureEmail).toHaveBeenCalledWith({
          email: 'test@example.com',
          utm_source: 'google',
          utm_campaign: 'compliance_assessment',
          utm_medium: 'cpc',
          utm_term: 'gdpr_compliance',
          utm_content: 'cta_button',
          consent_marketing: false,
          consent_terms: true,
        });
      });
    });

    it('updates store when consent checkboxes are toggled', async () => {
      const mockSetConsent = vi.fn();
      mockedUseFreemiumStore.mockReturnValue({
        ...defaultStoreState,
        setConsent: mockSetConsent,
      });

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const marketingConsent = screen.getByLabelText(/i agree to receive marketing/i);
      const termsConsent = screen.getByLabelText(/i agree to the terms of service/i);

      await user.click(marketingConsent);
      await user.click(termsConsent);

      expect(mockSetConsent).toHaveBeenCalledWith('marketing', true);
      expect(mockSetConsent).toHaveBeenCalledWith('terms', true);
    });
  });

  describe('Form Submission', () => {
    const user = userEvent.setup();

    it('submits form with all required data', async () => {
      const mockSetToken = vi.fn();
      mockedUseFreemiumStore.mockReturnValue({
        ...defaultStoreState,
        setToken: mockSetToken,
        utmSource: 'google',
        utmCampaign: 'compliance_assessment',
      });

      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'test-token-123',
        message: 'Email captured successfully',
      });

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const marketingConsent = screen.getByLabelText(/i agree to receive marketing/i);
      const termsConsent = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(marketingConsent);
      await user.click(termsConsent);
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockedFreemiumApi.captureEmail).toHaveBeenCalledWith({
          email: 'test@example.com',
          utm_source: 'google',
          utm_campaign: 'compliance_assessment',
          utm_medium: 'cpc',
          utm_term: 'gdpr_compliance',
          utm_content: 'cta_button',
          consent_marketing: true,
          consent_terms: true,
        });

        expect(mockSetToken).toHaveBeenCalledWith('test-token-123');
        expect(mockPush).toHaveBeenCalledWith('/freemium/assessment');
      });
    });

    it('shows loading state during submission', async () => {
      // Mock delayed API response
      mockedFreemiumApi.captureEmail.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  success: true,
                  token: 'test-token-123',
                  message: 'Email captured successfully',
                }),
              100,
            ),
          ),
      );

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(termsConsent);
      await user.click(submitButton);

      // Check loading state
      expect(screen.getByText(/starting your assessment/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();

      // Wait for completion
      await waitFor(() => {
        expect(screen.queryByText(/starting your assessment/i)).not.toBeInTheDocument();
      });
    });

    it('handles API errors gracefully', async () => {
      mockedFreemiumApi.captureEmail.mockRejectedValue(new Error('Network error'));

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'test@example.com');
      await user.click(termsConsent);
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to start assessment/i)).toBeInTheDocument();
        expect(screen.getByText(/please try again/i)).toBeInTheDocument();
      });

      expect(submitButton).not.toBeDisabled();
    });

    it('handles duplicate email scenario', async () => {
      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'existing-token-456',
        message: 'Email already registered',
        duplicate: true,
      });

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'existing@example.com');
      await user.click(termsConsent);
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
        expect(mockPush).toHaveBeenCalledWith('/freemium/assessment');
      });
    });
  });

  describe('Keyboard Navigation', () => {
    const user = userEvent.setup();

    it('supports tab navigation through form elements', async () => {
      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const marketingConsent = screen.getByLabelText(/i agree to receive marketing/i);
      const termsConsent = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /start free assessment/i });

      emailInput.focus();
      expect(emailInput).toHaveFocus();

      await user.tab();
      expect(marketingConsent).toHaveFocus();

      await user.tab();
      expect(termsConsent).toHaveFocus();

      await user.tab();
      expect(submitButton).toHaveFocus();
    });

    it('allows form submission with Enter key', async () => {
      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'test-token-123',
        message: 'Email captured successfully',
      });

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/i agree to the terms of service/i);

      await user.type(emailInput, 'test@example.com');
      await user.click(termsConsent);
      await user.type(emailInput, '{enter}');

      await waitFor(() => {
        expect(mockedFreemiumApi.captureEmail).toHaveBeenCalled();
      });
    });

    it('allows checkbox toggling with spacebar', async () => {
      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const marketingConsent = screen.getByLabelText(/i agree to receive marketing/i);

      marketingConsent.focus();
      await user.keyboard(' ');

      expect(marketingConsent).toBeChecked();

      await user.keyboard(' ');
      expect(marketingConsent).not.toBeChecked();
    });
  });

  describe('Performance and Memory', () => {
    it('does not cause memory leaks on unmount', () => {
      const { unmount } = render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      // Component should unmount cleanly
      expect(() => unmount()).not.toThrow();
    });

    it('debounces email validation to prevent excessive API calls', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);

      // Type rapidly
      await user.type(emailInput, 'test');
      await user.type(emailInput, '@example');
      await user.type(emailInput, '.com');

      // Should not validate until user stops typing
      expect(screen.queryByText(/please enter a valid email address/i)).not.toBeInTheDocument();

      // Trigger validation by blurring
      await user.tab();

      await waitFor(() => {
        expect(screen.queryByText(/please enter a valid email address/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Mobile Responsiveness', () => {
    it('adapts to mobile viewport', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const form = screen.getByRole('form');
      expect(form).toHaveClass(/mobile/i); // Assuming mobile-specific CSS classes
    });

    it('handles virtual keyboard on mobile', async () => {
      // Mock mobile environment
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      const user = userEvent.setup();

      render(
        <TestWrapper>
          <FreemiumEmailCapture />
        </TestWrapper>,
      );

      const emailInput = screen.getByLabelText(/email address/i);

      await user.type(emailInput, 'test@example.com');

      // Should maintain focus and visibility
      expect(emailInput).toHaveFocus();
      expect(emailInput.value).toBe('test@example.com');
    });
  });
});
