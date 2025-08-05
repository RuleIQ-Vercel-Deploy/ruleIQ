/**
 * Integration tests for complete freemium user journey
 * 
 * Tests the entire flow from email capture to conversion:
 * 1. Landing page with UTM parameters
 * 2. Email capture and validation
 * 3. Assessment flow with dynamic questions
 * 4. Results display and analysis
 * 5. Conversion CTA interaction
 * 6. Error recovery and edge cases
 * 
 * This test suite ensures all components work together seamlessly
 * and covers the critical user paths for the freemium strategy.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

import { FreemiumEmailCapture } from '../../components/freemium/freemium-email-capture';
import { FreemiumAssessmentFlow } from '../../components/freemium/freemium-assessment-flow';
import { FreemiumResults } from '../../components/freemium/freemium-results';
import { useFreemiumStore } from '../../lib/stores/freemium-store';
import * as freemiumApi from '../../lib/api/freemium.service';

// Mock the API service with realistic scenarios
vi.mock('../../lib/api/freemium.service');
const mockedFreemiumApi = vi.mocked(freemiumApi);

// Mock router
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({
      search: '?utm_source=google&utm_campaign=compliance_assessment&utm_medium=cpc',
      pathname: '/freemium'
    })
  };
});

// Mock window.location for UTM parameter extraction
Object.defineProperty(window, 'location', {
  value: {
    search: '?utm_source=google&utm_campaign=compliance_assessment&utm_medium=cpc&utm_term=gdpr_compliance&utm_content=hero_cta',
    href: 'https://ruleiq.com/freemium?utm_source=google&utm_campaign=compliance_assessment',
    origin: 'https://ruleiq.com'
  },
  writable: true
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const TestApp = ({ initialRoute = '/freemium' }: { initialRoute?: string }) => (
  <QueryClientProvider client={queryClient}>
    <MemoryRouter initialEntries={[initialRoute]}>
      <Routes>
        <Route path="/freemium" element={<FreemiumEmailCapture />} />
        <Route path="/freemium/assessment" element={<FreemiumAssessmentFlow />} />
        <Route path="/freemium/results" element={<FreemiumResults />} />
      </Routes>
    </MemoryRouter>
  </QueryClientProvider>
);

// Mock assessment flow data
const mockAssessmentFlow = {
  questions: [
    {
      question_id: 'q1_business_type',
      question_text: 'What type of business do you operate?',
      question_type: 'multiple_choice',
      options: ['E-commerce', 'SaaS', 'Healthcare', 'Financial Services', 'Other'],
      help_text: 'Select the category that best describes your primary business model.',
      validation_rules: { required: true },
      progress: 0
    },
    {
      question_id: 'q2_employee_count',
      question_text: 'How many employees do you have?',
      question_type: 'multiple_choice',
      options: ['1-10', '11-50', '51-200', '200+'],
      help_text: 'Include full-time, part-time, and contractors.',
      validation_rules: { required: true },
      progress: 25
    },
    {
      question_id: 'q3_data_handling',
      question_text: 'What type of data does your business process?',
      question_type: 'multi_select',
      options: ['Customer personal data', 'Payment information', 'Health records', 'Employee data', 'Marketing data'],
      help_text: 'Select all that apply to your business operations.',
      validation_rules: { required: true, min_selections: 1 },
      progress: 50
    },
    {
      question_id: 'q4_current_compliance',
      question_text: 'What is your current compliance status?',
      question_type: 'multiple_choice',
      options: ['Fully compliant', 'Partially compliant', 'Starting compliance journey', 'Not sure'],
      help_text: 'Be honest - this helps us provide better recommendations.',
      validation_rules: { required: true },
      progress: 75
    },
    {
      question_id: 'q5_compliance_goals',
      question_text: 'Which compliance frameworks are you targeting?',
      question_type: 'multi_select',
      options: ['GDPR', 'ISO 27001', 'SOC 2', 'HIPAA', 'PCI DSS', 'Other'],
      help_text: 'Select your priority frameworks for the next 12 months.',
      validation_rules: { required: true, min_selections: 1 },
      progress: 100
    }
  ],
  expectedAnswers: {
    'q1_business_type': 'SaaS',
    'q2_employee_count': '11-50',
    'q3_data_handling': ['Customer personal data', 'Payment information'],
    'q4_current_compliance': 'Partially compliant',
    'q5_compliance_goals': ['GDPR', 'ISO 27001']
  },
  finalResults: {
    compliance_gaps: [
      {
        framework: 'GDPR',
        severity: 'high',
        gap_description: 'Missing data processing records under Article 30',
        impact_score: 8.5,
        remediation_effort: 'medium',
        potential_fine: '€20,000,000 or 4% of annual turnover'
      },
      {
        framework: 'ISO 27001',
        severity: 'medium',
        gap_description: 'Incomplete risk assessment documentation',
        impact_score: 6.2,
        remediation_effort: 'low',
        potential_fine: 'Certification failure'
      }
    ],
    risk_score: 7.3,
    risk_level: 'high',
    business_impact: 'Potential regulatory fines up to €20M under GDPR, plus reputational damage',
    recommendations: [
      'Implement comprehensive data mapping under Article 30',
      'Establish formal risk management processes',
      'Create incident response procedures',
      'Conduct regular privacy impact assessments'
    ],
    priority_actions: [
      'Complete GDPR Article 30 documentation within 30 days',
      'Conduct privacy impact assessments for high-risk processing'
    ],
    trial_offer: {
      discount_percentage: 30,
      trial_days: 14,
      cta_text: 'Get Compliant Now - 30% Off',
      payment_link: 'https://billing.ruleiq.com/subscribe?plan=pro&discount=30&token=test-token'
    }
  }
};

describe('Freemium User Journey Integration', () => {
  beforeEach(() => {
    queryClient.clear();
    vi.clearAllMocks();
    mockNavigate.mockClear();
    
    // Reset store state
    useFreemiumStore.getState().reset();
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe('Complete Happy Path Journey', () => {
    it('completes full freemium flow from email capture to conversion', async () => {
      const user = userEvent.setup();
      
      // Mock API responses for complete journey
      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'journey-token-123',
        message: 'Email captured successfully'
      });

      mockedFreemiumApi.startAssessment.mockResolvedValue(mockAssessmentFlow.questions[0]);

      // Mock progressive question responses
      mockAssessmentFlow.questions.slice(0, -1).forEach((question, index) => {
        const nextQuestion = mockAssessmentFlow.questions[index + 1];
        mockedFreemiumApi.answerQuestion.mockResolvedValueOnce({
          answer_recorded: true,
          ...nextQuestion,
          assessment_complete: false
        });
      });

      // Mock final question completion
      mockedFreemiumApi.answerQuestion.mockResolvedValueOnce({
        answer_recorded: true,
        assessment_complete: true,
        redirect_to_results: true,
        progress: 100
      });

      mockedFreemiumApi.getResults.mockResolvedValue(mockAssessmentFlow.finalResults);
      mockedFreemiumApi.trackConversion.mockResolvedValue({
        tracked: true,
        event_id: 'conversion-123',
        message: 'Conversion tracked'
      });

      // 1. Start at landing page with UTM parameters
      render(<TestApp initialRoute="/freemium" />);

      // Verify UTM parameters are captured
      await waitFor(() => {
        const store = useFreemiumStore.getState();
        expect(store.utmSource).toBe('google');
        expect(store.utmCampaign).toBe('compliance_assessment');
        expect(store.utmMedium).toBe('cpc');
      });

      // 2. Email capture flow
      expect(screen.getByText(/start your free compliance assessment/i)).toBeInTheDocument();
      
      const emailInput = screen.getByLabelText(/email address/i);
      const marketingConsent = screen.getByLabelText(/marketing communications/i);
      const termsConsent = screen.getByLabelText(/terms of service/i);
      const startButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'journey.test@example.com');
      await user.click(marketingConsent);
      await user.click(termsConsent);
      await user.click(startButton);

      // Verify API call
      await waitFor(() => {
        expect(mockedFreemiumApi.captureEmail).toHaveBeenCalledWith({
          email: 'journey.test@example.com',
          utm_source: 'google',
          utm_campaign: 'compliance_assessment',
          utm_medium: 'cpc',
          utm_term: 'gdpr_compliance',
          utm_content: 'hero_cta',
          consent_marketing: true,
          consent_terms: true
        });
      });

      // 3. Assessment flow - navigate to assessment page
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/freemium/assessment');
      });

      // Render assessment page manually since navigation is mocked
      render(<TestApp initialRoute="/freemium/assessment" />);

      // Wait for first question to load
      await waitFor(() => {
        expect(screen.getByText(/what type of business do you operate/i)).toBeInTheDocument();
      });

      // Answer all questions in sequence
      for (let i = 0; i < mockAssessmentFlow.questions.length; i++) {
        const question = mockAssessmentFlow.questions[i];
        const answer = mockAssessmentFlow.expectedAnswers[question.question_id];

        // Wait for question to be displayed
        await waitFor(() => {
          expect(screen.getByText(new RegExp(question.question_text, 'i'))).toBeInTheDocument();
        });

        // Verify progress indicator 
        expect(screen.getByText(new RegExp(`${question.progress}%`, 'i'))).toBeInTheDocument();

        // Answer based on question type
        if (question.question_type === 'multiple_choice') {
          const option = screen.getByRole('radio', { name: new RegExp(answer as string, 'i') });
          await user.click(option);
        } else if (question.question_type === 'multi_select') {
          const answers = answer as string[];
          for (const ans of answers) {
            const checkbox = screen.getByRole('checkbox', { name: new RegExp(ans, 'i') });
            await user.click(checkbox);
          }
        }

        // Submit answer
        const nextButton = screen.getByRole('button', { name: /next|finish/i });
        await user.click(nextButton);

        // Wait for API call
        await waitFor(() => {
          expect(mockedFreemiumApi.answerQuestion).toHaveBeenCalledWith(
            'journey-token-123',
            expect.objectContaining({
              question_id: question.question_id,
              answer: answer
            })
          );
        });
      }

      // 4. Results page - navigate after assessment completion
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/freemium/results?token=journey-token-123');
      });

      // Render results page
      render(<TestApp initialRoute="/freemium/results" />);

      // Wait for results to load
      await waitFor(() => {
        expect(screen.getByText(/your compliance assessment results/i)).toBeInTheDocument();
      });

      // Verify results display
      expect(screen.getByText(/risk score: 7\.3/i)).toBeInTheDocument();
      expect(screen.getByText(/high risk/i)).toBeInTheDocument();
      expect(screen.getByText(/missing data processing records/i)).toBeInTheDocument();
      expect(screen.getByText(/incomplete risk assessment documentation/i)).toBeInTheDocument();

      // Verify recommendations
      expect(screen.getByText(/implement comprehensive data mapping/i)).toBeInTheDocument();
      expect(screen.getByText(/establish formal risk management processes/i)).toBeInTheDocument();

      // 5. Conversion interaction
      const ctaButton = screen.getByRole('link', { name: /get compliant now - 30% off/i });
      expect(ctaButton).toHaveAttribute('href', expect.stringContaining('billing.ruleiq.com'));

      await user.click(ctaButton);

      // Verify conversion tracking
      await waitFor(() => {
        expect(mockedFreemiumApi.trackConversion).toHaveBeenCalledWith(
          'journey-token-123',
          expect.objectContaining({
            event_type: 'cta_click',
            cta_text: 'Get Compliant Now - 30% Off',
            conversion_value: 30
          })
        );
      });

      // Verify final store state
      const finalState = useFreemiumStore.getState();
      expect(finalState.email).toBe('journey.test@example.com');
      expect(finalState.token).toBe('journey-token-123');
      expect(finalState.assessmentCompleted).toBe(true);
      expect(finalState.progress).toBe(100);
      expect(Object.keys(finalState.responses)).toHaveLength(5);
    });
  });

  describe('Error Recovery Scenarios', () => {
    it('recovers from API errors during assessment', async () => {
      const user = userEvent.setup();

      // Mock email capture success
      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'error-recovery-token',
        message: 'Email captured successfully'
      });

      // Mock assessment start failure then success
      mockedFreemiumApi.startAssessment
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockAssessmentFlow.questions[0]);

      render(<TestApp initialRoute="/freemium" />);

      // Complete email capture
      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/terms of service/i);
      const startButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'recovery@example.com');
      await user.click(termsConsent);
      await user.click(startButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/freemium/assessment');
      });

      // Navigate to assessment page
      render(<TestApp initialRoute="/freemium/assessment" />);

      // Should show error initially
      await waitFor(() => {
        expect(screen.getByText(/failed to load assessment/i)).toBeInTheDocument();
      });

      // Retry should work
      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText(/what type of business do you operate/i)).toBeInTheDocument();
      });

      expect(mockedFreemiumApi.startAssessment).toHaveBeenCalledTimes(2);
    });

    it('handles session expiration gracefully', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'expiring-token',
        message: 'Email captured successfully'
      });

      mockedFreemiumApi.startAssessment.mockResolvedValue(mockAssessmentFlow.questions[0]);

      // Mock token expiration during answer submission
      mockedFreemiumApi.answerQuestion.mockRejectedValue(
        new Error('Token expired')
      );

      render(<TestApp initialRoute="/freemium" />);

      // Complete email capture
      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/terms of service/i);
      const startButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'expiring@example.com');
      await user.click(termsConsent);
      await user.click(startButton);

      // Navigate to assessment
      render(<TestApp initialRoute="/freemium/assessment" />);

      await waitFor(() => {
        expect(screen.getByText(/what type of business do you operate/i)).toBeInTheDocument();
      });

      // Try to answer question
      const saasOption = screen.getByRole('radio', { name: /saas/i });
      await user.click(saasOption);

      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.click(nextButton);

      // Should show session expired error
      await waitFor(() => {
        expect(screen.getByText(/session expired/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /start over/i })).toBeInTheDocument();
      });
    });

    it('handles AI service fallback mode', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'fallback-token',
        message: 'Email captured successfully'
      });

      // Mock AI service unavailable, use fallback
      mockedFreemiumApi.startAssessment.mockResolvedValue({
        ...mockAssessmentFlow.questions[0],
        fallback_mode: true,
        ai_service_available: false
      });

      mockedFreemiumApi.answerQuestion.mockResolvedValue({
        answer_recorded: true,
        ...mockAssessmentFlow.questions[1],
        fallback_mode: true,
        assessment_complete: false
      });

      render(<TestApp initialRoute="/freemium" />);

      // Complete email capture
      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/terms of service/i);
      const startButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'fallback@example.com');
      await user.click(termsConsent);
      await user.click(startButton);

      // Navigate to assessment
      render(<TestApp initialRoute="/freemium/assessment" />);

      await waitFor(() => {
        expect(screen.getByText(/what type of business do you operate/i)).toBeInTheDocument();
        expect(screen.getByText(/using simplified assessment mode/i)).toBeInTheDocument();
      });

      // Should still be able to answer questions
      const saasOption = screen.getByRole('radio', { name: /saas/i });
      await user.click(saasOption);

      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText(/how many employees do you have/i)).toBeInTheDocument();
      });
    });
  });

  describe('Session Persistence and Resume', () => {
    it('resumes interrupted assessment session', async () => {
      const user = userEvent.setup();

      // Mock resumed session
      mockedFreemiumApi.startAssessment.mockResolvedValue({
        session_started: false,
        session_resumed: true,
        question_id: 'q3_data_handling',
        question_text: 'What type of data does your business process?',
        question_type: 'multi_select',
        options: ['Customer personal data', 'Payment information', 'Health records'],
        progress: 50,
        previous_responses: {
          'q1_business_type': 'SaaS',
          'q2_employee_count': '11-50'
        }
      });

      // Set existing session state
      act(() => {
        useFreemiumStore.setState({
          email: 'resume@example.com',
          token: 'resume-token-123',
          assessmentStarted: true,
          responses: {
            'q1_business_type': 'SaaS',
            'q2_employee_count': '11-50'
          },
          progress: 50
        });
      });

      render(<TestApp initialRoute="/freemium/assessment" />);

      await waitFor(() => {
        expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
        expect(screen.getByText(/what type of data does your business process/i)).toBeInTheDocument();
        expect(screen.getByText(/50%/i)).toBeInTheDocument();
      });

      // Verify previous responses are maintained
      const store = useFreemiumStore.getState();
      expect(store.responses).toEqual({
        'q1_business_type': 'SaaS',
        'q2_employee_count': '11-50'
      });
    });

    it('persists state across page refreshes', async () => {
      // Mock localStorage with saved session
      const mockLocalStorage = {
        'freemium-email': 'persistent@example.com',
        'freemium-utm': JSON.stringify({
          utm_source: 'linkedin',
          utm_campaign: 'retargeting'
        }),
        'freemium-consent': JSON.stringify({
          marketing: true,
          terms: true
        })
      };

      const mockSessionStorage = {
        'freemium-token': 'persistent-token-456',
        'freemium-responses': JSON.stringify({
          'q1_business_type': 'Healthcare',
          'q2_employee_count': '51-200'
        })
      };

      // Mock storage methods
      Storage.prototype.getItem = vi.fn((key) => {
        return mockLocalStorage[key] || mockSessionStorage[key] || null;
      });

      // Initialize new store to trigger hydration
      const { result } = renderHook(() => useFreemiumStore());

      expect(result.current.email).toBe('persistent@example.com');
      expect(result.current.token).toBe('persistent-token-456');
      expect(result.current.utmSource).toBe('linkedin');
      expect(result.current.consentMarketing).toBe(true);
      expect(result.current.responses).toEqual({
        'q1_business_type': 'Healthcare',
        'q2_employee_count': '51-200'
      });
    });
  });

  describe('Conversion Optimization', () => {
    it('tracks detailed user behavior for optimization', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'optimization-token',
        message: 'Email captured successfully'
      });

      mockedFreemiumApi.getResults.mockResolvedValue(mockAssessmentFlow.finalResults);
      mockedFreemiumApi.trackConversion.mockResolvedValue({
        tracked: true,
        event_id: 'behavior-tracking-123',
        message: 'Event tracked'
      });

      render(<TestApp initialRoute="/freemium/results" />);

      await waitFor(() => {
        expect(screen.getByText(/your compliance assessment results/i)).toBeInTheDocument();
      });

      // Track multiple user interactions
      const shareButton = screen.getByRole('button', { name: /share results/i });
      const downloadButton = screen.getByRole('button', { name: /download pdf/i });
      const ctaButton = screen.getByRole('link', { name: /get compliant now/i });

      // Simulate user exploring results
      await user.hover(shareButton);
      await user.hover(downloadButton);
      
      // Scroll through recommendations (simulated)
      fireEvent.scroll(window, { target: { scrollY: 500 } });

      // Finally click CTA
      await user.click(ctaButton);

      // Verify detailed tracking
      await waitFor(() => {
        expect(mockedFreemiumApi.trackConversion).toHaveBeenCalledWith(
          'optimization-token', 
          expect.objectContaining({
            event_type: 'cta_click',
            metadata: expect.objectContaining({
              time_on_page: expect.any(Number),
              scroll_depth: expect.any(Number),
              results_viewed: true
            })
          })
        );
      });
    });

    it('handles different conversion paths', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.getResults.mockResolvedValue({
        ...mockAssessmentFlow.finalResults,
        risk_level: 'low',
        trial_offer: {
          discount_percentage: 20,
          trial_days: 7,
          cta_text: 'Maintain Compliance - 20% Off',
          payment_link: 'https://billing.ruleiq.com/subscribe?plan=basic&discount=20'
        }
      });

      mockedFreemiumApi.trackConversion.mockResolvedValue({
        tracked: true,
        event_id: 'low-risk-conversion',
        message: 'Conversion tracked'
      });

      act(() => {
        useFreemiumStore.setState({
          token: 'low-risk-token',
          assessmentCompleted: true
        });
      });

      render(<TestApp initialRoute="/freemium/results" />);

      await waitFor(() => {
        expect(screen.getByText(/low risk/i)).toBeInTheDocument();
        expect(screen.getByText(/maintain compliance - 20% off/i)).toBeInTheDocument();
      });

      // Different CTA for low-risk users
      const maintainButton = screen.getByRole('link', { name: /maintain compliance/i });
      await user.click(maintainButton);

      expect(mockedFreemiumApi.trackConversion).toHaveBeenCalledWith(
        'low-risk-token',
        expect.objectContaining({
          event_type: 'cta_click',
          conversion_value: 20
        })
      );
    });
  });

  describe('Mobile and Responsive Behavior', () => {
    it('adapts journey for mobile devices', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      const user = userEvent.setup();

      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'mobile-token',
        message: 'Email captured successfully'
      });

      render(<TestApp initialRoute="/freemium" />);

      // Mobile-specific elements should be present
      expect(screen.getByTestId('mobile-email-capture')).toBeInTheDocument();

      // Email capture should work on mobile
      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/terms of service/i);
      const startButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'mobile@example.com');
      await user.click(termsConsent);
      await user.click(startButton);

      await waitFor(() => {
        expect(mockedFreemiumApi.captureEmail).toHaveBeenCalledWith(
          expect.objectContaining({
            email: 'mobile@example.com'
          })
        );
      });
    });
  });

  describe('Analytics and Attribution', () => {
    it('maintains UTM attribution throughout journey', async () => {
      const user = userEvent.setup();

      // Set initial UTM parameters
      Object.defineProperty(window, 'location', {
        value: {
          search: '?utm_source=facebook&utm_campaign=retargeting&utm_medium=social&utm_term=compliance_software&utm_content=video_ad',
          href: 'https://ruleiq.com/freemium?utm_source=facebook',
          origin: 'https://ruleiq.com'
        },
        writable: true
      });

      mockedFreemiumApi.captureEmail.mockResolvedValue({
        success: true,
        token: 'attribution-token',
        message: 'Email captured successfully'
      });

      mockedFreemiumApi.trackConversion.mockResolvedValue({
        tracked: true,
        event_id: 'attribution-123',
        message: 'Conversion tracked'
      });

      render(<TestApp initialRoute="/freemium" />);

      // Complete email capture
      const emailInput = screen.getByLabelText(/email address/i);
      const termsConsent = screen.getByLabelText(/terms of service/i);
      const startButton = screen.getByRole('button', { name: /start free assessment/i });

      await user.type(emailInput, 'attribution@example.com');
      await user.click(termsConsent);
      await user.click(startButton);

      // Verify UTM parameters are passed through
      await waitFor(() => {
        expect(mockedFreemiumApi.captureEmail).toHaveBeenCalledWith(
          expect.objectContaining({
            utm_source: 'facebook',
            utm_campaign: 'retargeting',
            utm_medium: 'social',
            utm_term: 'compliance_software',
            utm_content: 'video_ad'
          })
        );
      });

      // Verify UTM parameters persist in store
      const store = useFreemiumStore.getState();
      expect(store.utmSource).toBe('facebook');
      expect(store.utmCampaign).toBe('retargeting');
      expect(store.utmMedium).toBe('social');
      expect(store.utmTerm).toBe('compliance_software');
      expect(store.utmContent).toBe('video_ad');
    });
  });
});