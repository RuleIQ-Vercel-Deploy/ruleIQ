import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FreemiumEmailCapture } from '../components/freemium/freemium-email-capture';
import { FreemiumAssessmentFlow } from '../components/freemium/freemium-assessment-flow';
import { FreemiumResults } from '../components/freemium/freemium-results';
import { useFreemiumStore } from '../lib/stores/freemium-store';
import * as freemiumApi from '../lib/api/freemium.service';

// Mock the API service
jest.mock('../lib/api/freemium.service');
const mockedFreemiumApi = jest.mocked(freemiumApi);

// Mock the store 
jest.mock('../lib/stores/freemium-store');
const mockedUseFreemiumStore = jest.mocked(useFreemiumStore);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('FreemiumEmailCapture', () => {
  beforeEach(() => {
    queryClient.clear();
    mockedUseFreemiumStore.mockReturnValue({
      email: '',
      token: null,
      utmSource: null,
      utmCampaign: null,
      setEmail: jest.fn(),
      setToken: jest.fn(),
      setUtmParams: jest.fn(),
      reset: jest.fn(),
    });
  });

  it('renders email capture form with required fields', () => {
    render(
      <TestWrapper>
        <FreemiumEmailCapture />
      </TestWrapper>
    );

    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/marketing consent/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start free assessment/i })).toBeInTheDocument();
  });

  it('validates email format before submission', async () => {
    render(
      <TestWrapper>
        <FreemiumEmailCapture />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/email address/i);
    const submitButton = screen.getByRole('button', { name: /start free assessment/i });

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
    });
  });

  it('captures UTM parameters from URL', () => {
    const mockSetUtmParams = jest.fn();
    mockedUseFreemiumStore.mockReturnValue({
      email: '',
      token: null,
      utmSource: null,
      utmCampaign: null,
      setEmail: jest.fn(),
      setToken: jest.fn(),
      setUtmParams: mockSetUtmParams,
      reset: jest.fn(),
    });

    // Mock URL with UTM parameters
    Object.defineProperty(window, 'location', {
      value: {
        search: '?utm_source=google&utm_campaign=compliance_assessment',
      },
    });

    render(
      <TestWrapper>
        <FreemiumEmailCapture />
      </TestWrapper>
    );

    expect(mockSetUtmParams).toHaveBeenCalledWith('google', 'compliance_assessment');
  });

  it('submits email with consent and starts assessment', async () => {
    const mockCaptureEmail = jest.fn().mockResolvedValue({ 
      success: true, 
      token: 'test-token-123'
    });
    mockedFreemiumApi.captureEmail = mockCaptureEmail;

    const mockSetToken = jest.fn();
    mockedUseFreemiumStore.mockReturnValue({
      email: '',
      token: null,
      utmSource: 'google',
      utmCampaign: 'compliance_assessment',
      setEmail: jest.fn(),
      setToken: mockSetToken,
      setUtmParams: jest.fn(),
      reset: jest.fn(),
    });

    render(
      <TestWrapper>
        <FreemiumEmailCapture />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/email address/i);
    const consentCheckbox = screen.getByLabelText(/marketing consent/i);
    const submitButton = screen.getByRole('button', { name: /start free assessment/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(consentCheckbox);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockCaptureEmail).toHaveBeenCalledWith({
        email: 'test@example.com',
        utm_source: 'google',
        utm_campaign: 'compliance_assessment',
        consent_marketing: true,
      });
      expect(mockSetToken).toHaveBeenCalledWith('test-token-123');
    });
  });
});

describe('FreemiumAssessmentFlow', () => {
  const mockAssessmentState = {
    email: 'test@example.com',
    token: 'test-token-123',
    utmSource: 'google',
    utmCampaign: 'compliance',
    setEmail: jest.fn(),
    setToken: jest.fn(),
    setUtmParams: jest.fn(),
    reset: jest.fn(),
  };

  beforeEach(() => {
    queryClient.clear();
    mockedUseFreemiumStore.mockReturnValue(mockAssessmentState);
  });

  it('renders initial loading state', () => {
    render(
      <TestWrapper>
        <FreemiumAssessmentFlow />
      </TestWrapper>
    );

    expect(screen.getByText(/loading your assessment/i)).toBeInTheDocument();
  });

  it('displays first question when assessment starts', async () => {
    const mockStartAssessment = jest.fn().mockResolvedValue({
      question_id: 'q1',
      question_text: 'What type of business do you operate?',
      question_type: 'multiple_choice',
      options: ['E-commerce', 'SaaS', 'Healthcare', 'Financial Services'],
      progress: 0,
    });
    mockedFreemiumApi.startAssessment = mockStartAssessment;

    render(
      <TestWrapper>
        <FreemiumAssessmentFlow />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/what type of business do you operate/i)).toBeInTheDocument();
      expect(screen.getByText(/e-commerce/i)).toBeInTheDocument();
      expect(screen.getByText(/saas/i)).toBeInTheDocument();
    });
  });

  it('submits answer and displays next question', async () => {
    const mockStartAssessment = jest.fn().mockResolvedValue({
      question_id: 'q1',
      question_text: 'What type of business do you operate?',
      question_type: 'multiple_choice',
      options: ['E-commerce', 'SaaS', 'Healthcare', 'Financial Services'],
      progress: 0,
    });

    const mockAnswerQuestion = jest.fn().mockResolvedValue({
      question_id: 'q2',
      question_text: 'How many employees do you have?',
      question_type: 'multiple_choice',
      options: ['1-10', '11-50', '51-200', '200+'],
      progress: 20,
    });

    mockedFreemiumApi.startAssessment = mockStartAssessment;
    mockedFreemiumApi.answerQuestion = mockAnswerQuestion;

    render(
      <TestWrapper>
        <FreemiumAssessmentFlow />
      </TestWrapper>
    );

    // Wait for first question
    await waitFor(() => {
      expect(screen.getByText(/what type of business do you operate/i)).toBeInTheDocument();
    });

    // Select an answer
    const saasOption = screen.getByText(/saas/i);
    fireEvent.click(saasOption);

    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);

    // Wait for second question
    await waitFor(() => {
      expect(mockAnswerQuestion).toHaveBeenCalledWith('test-token-123', {
        question_id: 'q1',
        answer: 'SaaS',
      });
      expect(screen.getByText(/how many employees do you have/i)).toBeInTheDocument();
    });
  });

  it('displays progress indicator', async () => {
    const mockStartAssessment = jest.fn().mockResolvedValue({
      question_id: 'q1',
      question_text: 'What type of business do you operate?',
      question_type: 'multiple_choice',
      options: ['E-commerce', 'SaaS', 'Healthcare', 'Financial Services'],
      progress: 20,
    });
    mockedFreemiumApi.startAssessment = mockStartAssessment;

    render(
      <TestWrapper>
        <FreemiumAssessmentFlow />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/20%/i)).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });

  it('redirects to results when assessment is complete', async () => {
    const mockAnswerQuestion = jest.fn().mockResolvedValue({
      assessment_complete: true,
      redirect_to_results: true,
    });
    mockedFreemiumApi.answerQuestion = mockAnswerQuestion;

    // Mock router
    const mockPush = jest.fn();
    jest.mock('next/navigation', () => ({
      useRouter: () => ({ push: mockPush }),
      useSearchParams: () => new URLSearchParams(),
    }));

    render(
      <TestWrapper>
        <FreemiumAssessmentFlow />
      </TestWrapper>
    );

    // This would need to be triggered after initial render
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/freemium/results?token=test-token-123');
    });
  });
});

describe('FreemiumResults', () => {
  const mockResults = {
    compliance_gaps: [
      {
        framework: 'GDPR',
        severity: 'high',
        gap_description: 'Missing data processing records',
        impact_score: 8.5,
      },
      {
        framework: 'ISO 27001',
        severity: 'medium',
        gap_description: 'Incomplete risk assessment documentation',
        impact_score: 6.2,
      },
    ],
    risk_score: 7.3,
    recommendations: [
      'Implement comprehensive data mapping',
      'Establish formal risk management processes',
      'Create incident response procedures',
    ],
    trial_offer: {
      discount_percentage: 30,
      trial_days: 14,
      cta_text: 'Get Compliant Now - 30% Off',
      payment_link: 'https://billing.ruleiq.com/subscribe?plan=pro&discount=30',
    },
  };

  beforeEach(() => {
    queryClient.clear();
  });

  it('renders compliance gaps with severity indicators', async () => {
    const mockGetResults = jest.fn().mockResolvedValue(mockResults);
    mockedFreemiumApi.getResults = mockGetResults;

    render(
      <TestWrapper>
        <FreemiumResults token="test-token-123" />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/missing data processing records/i)).toBeInTheDocument();
      expect(screen.getByText(/incomplete risk assessment documentation/i)).toBeInTheDocument();
      expect(screen.getByText(/high/i)).toBeInTheDocument();
      expect(screen.getByText(/medium/i)).toBeInTheDocument();
    });
  });

  it('displays overall risk score', async () => {
    const mockGetResults = jest.fn().mockResolvedValue(mockResults);
    mockedFreemiumApi.getResults = mockGetResults;

    render(
      <TestWrapper>
        <FreemiumResults token="test-token-123" />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/7\.3/)).toBeInTheDocument();
      expect(screen.getByText(/risk score/i)).toBeInTheDocument();
    });
  });

  it('shows key recommendations', async () => {
    const mockGetResults = jest.fn().mockResolvedValue(mockResults);
    mockedFreemiumApi.getResults = mockGetResults;

    render(
      <TestWrapper>
        <FreemiumResults token="test-token-123" />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/implement comprehensive data mapping/i)).toBeInTheDocument();
      expect(screen.getByText(/establish formal risk management processes/i)).toBeInTheDocument();
      expect(screen.getByText(/create incident response procedures/i)).toBeInTheDocument();
    });
  });

  it('displays conversion CTA with trial offer', async () => {
    const mockGetResults = jest.fn().mockResolvedValue(mockResults);
    mockedFreemiumApi.getResults = mockGetResults;

    render(
      <TestWrapper>
        <FreemiumResults token="test-token-123" />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/get compliant now - 30% off/i)).toBeInTheDocument();
      expect(screen.getByText(/14.*day.*trial/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /get compliant now/i })).toHaveAttribute(
        'href',
        'https://billing.ruleiq.com/subscribe?plan=pro&discount=30'
      );
    });
  });

  it('tracks conversion when CTA is clicked', async () => {
    const mockGetResults = jest.fn().mockResolvedValue(mockResults);
    const mockTrackConversion = jest.fn().mockResolvedValue({ success: true });
    mockedFreemiumApi.getResults = mockGetResults;
    mockedFreemiumApi.trackConversion = mockTrackConversion;

    render(
      <TestWrapper>
        <FreemiumResults token="test-token-123" />
      </TestWrapper>
    );

    await waitFor(() => {
      const ctaButton = screen.getByRole('link', { name: /get compliant now/i });
      fireEvent.click(ctaButton);
    });

    expect(mockTrackConversion).toHaveBeenCalledWith('test-token-123', {
      event_type: 'cta_click',
      cta_text: 'Get Compliant Now - 30% Off',
      conversion_value: 30,
    });
  });

  it('handles loading and error states', async () => {
    const mockGetResults = jest.fn().mockRejectedValue(new Error('API Error'));
    mockedFreemiumApi.getResults = mockGetResults;

    render(
      <TestWrapper>
        <FreemiumResults token="test-token-123" />
      </TestWrapper>
    );

    // Initial loading state
    expect(screen.getByText(/loading your results/i)).toBeInTheDocument();

    // Error state
    await waitFor(() => {
      expect(screen.getByText(/unable to load results/i)).toBeInTheDocument();
    });
  });
});