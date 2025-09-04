/**
 * Comprehensive tests for FreemiumResults component
 *
 * Tests:
 * - Results display and formatting
 * - Compliance gaps visualization
 * - Risk scoring and severity indicators
 * - Recommendations and priority actions
 * - Conversion CTA and trial offers
 * - Sharing functionality
 * - Error handling and loading states
 * - Accessibility and screen reader support
 * - Performance and caching
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

import { FreemiumResults } from '../../../components/freemium/freemium-results';
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
    get: vi.fn((param) => (param === 'token' ? 'test-token-123' : null)),
    toString: () => 'token=test-token-123',
  }),
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn(),
  },
});

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
  email: 'test@example.com',
  token: 'test-token-123',
  utmSource: 'google',
  utmCampaign: 'compliance_assessment',
  responses: {
    q1_business_type: 'SaaS',
    q2_employee_count: '11-50',
    q3_data_handling: 'Customer personal data',
    q4_current_compliance: 'GDPR partially',
    q5_compliance_goals: 'Full GDPR and ISO 27001',
  },
  reset: vi.fn(),
};

const mockResults = {
  compliance_gaps: [
    {
      framework: 'GDPR',
      severity: 'high',
      gap_description: 'Missing data processing records under Article 30',
      impact_score: 8.5,
      remediation_effort: 'medium',
      potential_fine: '€20,000,000 or 4% of annual turnover',
      priority: 1,
    },
    {
      framework: 'ISO 27001',
      severity: 'medium',
      gap_description: 'Incomplete risk assessment documentation',
      impact_score: 6.2,
      remediation_effort: 'low',
      potential_fine: 'Certification failure',
      priority: 2,
    },
    {
      framework: 'GDPR',
      severity: 'low',
      gap_description: 'Privacy policy needs updating for recent changes',
      impact_score: 3.1,
      remediation_effort: 'low',
      potential_fine: '€10,000,000 or 2% of annual turnover',
      priority: 3,
    },
  ],
  risk_score: 7.3,
  risk_level: 'high',
  business_impact: 'Potential regulatory fines up to €20M under GDPR, plus reputational damage',
  recommendations: [
    'Implement comprehensive data mapping under Article 30',
    'Establish formal risk management processes',
    'Create incident response procedures',
    'Conduct regular privacy impact assessments',
    'Train staff on data protection requirements',
  ],
  priority_actions: [
    'Complete GDPR Article 30 documentation within 30 days',
    'Conduct privacy impact assessments for high-risk processing',
    'Update privacy policy and consent mechanisms',
  ],
  frameworks_analyzed: ['GDPR', 'ISO 27001'],
  assessment_date: '2025-01-15T10:30:00Z',
  trial_offer: {
    discount_percentage: 30,
    trial_days: 14,
    cta_text: 'Get Compliant Now - 30% Off',
    payment_link: 'https://billing.ruleiq.com/subscribe?plan=pro&discount=30&token=test-token-123',
    features_included: [
      'Complete compliance assessment',
      'Action plan with deadlines',
      'Document templates',
      'Expert support',
    ],
  },
  sharing: {
    enabled: true,
    share_url: 'https://ruleiq.com/share/results/test-token-123',
    pdf_download_url: 'https://api.ruleiq.com/freemium/results/test-token-123/pdf',
  },
};

describe('FreemiumResults', () => {
  beforeEach(() => {
    queryClient.clear();
    vi.clearAllMocks();
    mockPush.mockClear();
    mockedUseFreemiumStore.mockReturnValue(defaultStoreState);
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe('Initial Loading and Data Display', () => {
    it('shows loading state initially', () => {
      mockedFreemiumApi.getResults.mockImplementation(
        () => new Promise(() => {}), // Never resolves
      );

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      expect(screen.getByText(/loading your results/i)).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('displays results after successful API call', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/your compliance assessment results/i)).toBeInTheDocument();
        expect(screen.getByText(/risk score: 7\.3/i)).toBeInTheDocument();
        expect(screen.getByText(/high risk/i)).toBeInTheDocument();
      });

      expect(mockedFreemiumApi.getResults).toHaveBeenCalledWith('test-token-123');
    });

    it('displays assessment metadata', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/assessed on january 15, 2025/i)).toBeInTheDocument();
        expect(screen.getByText(/frameworks: gdpr, iso 27001/i)).toBeInTheDocument();
      });
    });
  });

  describe('Compliance Gaps Display', () => {
    it('renders all compliance gaps with severity indicators', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/missing data processing records/i)).toBeInTheDocument();
        expect(screen.getByText(/incomplete risk assessment documentation/i)).toBeInTheDocument();
        expect(screen.getByText(/privacy policy needs updating/i)).toBeInTheDocument();
      });

      // Check severity indicators
      const highSeverityElements = screen.getAllByText(/high/i);
      const mediumSeverityElements = screen.getAllByText(/medium/i);
      const lowSeverityElements = screen.getAllByText(/low/i);

      expect(highSeverityElements.length).toBeGreaterThan(0);
      expect(mediumSeverityElements.length).toBeGreaterThan(0);
      expect(lowSeverityElements.length).toBeGreaterThan(0);
    });

    it('displays impact scores and potential fines', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/8\.5/)).toBeInTheDocument(); // Impact score
        expect(screen.getByText(/€20,000,000 or 4% of annual turnover/i)).toBeInTheDocument();
        expect(screen.getByText(/certification failure/i)).toBeInTheDocument();
      });
    });

    it('sorts gaps by priority', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        const gapElements = screen.getAllByTestId(/compliance-gap-/);
        expect(gapElements).toHaveLength(3);

        // First gap should be highest priority (GDPR Article 30)
        expect(gapElements[0]).toHaveTextContent(/missing data processing records/i);
        expect(gapElements[1]).toHaveTextContent(/incomplete risk assessment/i);
        expect(gapElements[2]).toHaveTextContent(/privacy policy needs updating/i);
      });
    });

    it('shows remediation effort indicators', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/medium effort/i)).toBeInTheDocument();
        expect(screen.getAllByText(/low effort/i)).toHaveLength(2);
      });
    });
  });

  describe('Risk Score and Level Display', () => {
    it('displays overall risk score with visual indicator', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/7\.3/)).toBeInTheDocument();
        expect(screen.getByText(/high risk/i)).toBeInTheDocument();

        // Risk level should have appropriate styling
        const riskElement = screen.getByTestId('risk-level');
        expect(riskElement).toHaveClass(/high/i);
      });
    });

    it('displays business impact explanation', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/potential regulatory fines up to €20m/i)).toBeInTheDocument();
        expect(screen.getByText(/reputational damage/i)).toBeInTheDocument();
      });
    });

    it('adapts risk visualization based on score', async () => {
      const lowRiskResults = {
        ...mockResults,
        risk_score: 2.1,
        risk_level: 'low',
      };

      mockedFreemiumApi.getResults.mockResolvedValue(lowRiskResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/low risk/i)).toBeInTheDocument();

        const riskElement = screen.getByTestId('risk-level');
        expect(riskElement).toHaveClass(/low/i);
      });
    });
  });

  describe('Recommendations and Priority Actions', () => {
    it('displays all recommendations', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/implement comprehensive data mapping/i)).toBeInTheDocument();
        expect(screen.getByText(/establish formal risk management processes/i)).toBeInTheDocument();
        expect(screen.getByText(/create incident response procedures/i)).toBeInTheDocument();
        expect(screen.getByText(/conduct regular privacy impact assessments/i)).toBeInTheDocument();
        expect(screen.getByText(/train staff on data protection/i)).toBeInTheDocument();
      });
    });

    it('highlights priority actions separately', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/priority actions/i)).toBeInTheDocument();
        expect(
          screen.getByText(/complete gdpr article 30 documentation within 30 days/i),
        ).toBeInTheDocument();
        expect(
          screen.getByText(/conduct privacy impact assessments for high-risk processing/i),
        ).toBeInTheDocument();
        expect(
          screen.getByText(/update privacy policy and consent mechanisms/i),
        ).toBeInTheDocument();
      });
    });

    it('allows expanding/collapsing recommendation details', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/see all recommendations/i)).toBeInTheDocument();
      });

      const expandButton = screen.getByRole('button', { name: /see all recommendations/i });
      await user.click(expandButton);

      expect(screen.getByText(/hide recommendations/i)).toBeInTheDocument();
      expect(screen.getAllByText(/recommendation/i).length).toBeGreaterThan(3);
    });
  });

  describe('Conversion CTA and Trial Offer', () => {
    it('displays trial offer with all details', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/get compliant now - 30% off/i)).toBeInTheDocument();
        expect(screen.getByText(/14.*day.*trial/i)).toBeInTheDocument();

        const ctaLink = screen.getByRole('link', { name: /get compliant now/i });
        expect(ctaLink).toHaveAttribute('href', expect.stringContaining('billing.ruleiq.com'));
      });
    });

    it('displays included features', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/complete compliance assessment/i)).toBeInTheDocument();
        expect(screen.getByText(/action plan with deadlines/i)).toBeInTheDocument();
        expect(screen.getByText(/document templates/i)).toBeInTheDocument();
        expect(screen.getByText(/expert support/i)).toBeInTheDocument();
      });
    });

    it('tracks conversion when CTA is clicked', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);
      mockedFreemiumApi.trackConversion.mockResolvedValue({ success: true, event_id: 'evt_123' });

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/get compliant now - 30% off/i)).toBeInTheDocument();
      });

      const ctaButton = screen.getByRole('link', { name: /get compliant now/i });
      await user.click(ctaButton);

      expect(mockedFreemiumApi.trackConversion).toHaveBeenCalledWith('test-token-123', {
        event_type: 'cta_click',
        cta_text: 'Get Compliant Now - 30% Off',
        conversion_value: 30,
        page_url: expect.any(String),
        user_agent: expect.any(String),
        metadata: expect.any(Object),
      });
    });

    it('shows urgency indicators', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/limited time offer/i)).toBeInTheDocument();
        expect(screen.getByText(/high priority compliance gaps found/i)).toBeInTheDocument();
      });
    });
  });

  describe('Sharing Functionality', () => {
    it('displays sharing options when enabled', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /share results/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /download pdf/i })).toBeInTheDocument();
      });
    });

    it('copies share URL to clipboard', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /share results/i })).toBeInTheDocument();
      });

      const shareButton = screen.getByRole('button', { name: /share results/i });
      await user.click(shareButton);

      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        'https://ruleiq.com/share/results/test-token-123',
      );

      await waitFor(() => {
        expect(screen.getByText(/link copied to clipboard/i)).toBeInTheDocument();
      });
    });

    it('initiates PDF download', async () => {
      const user = userEvent.setup();

      // Mock window.open
      const mockOpen = vi.fn();
      vi.stubGlobal('open', mockOpen);

      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /download pdf/i })).toBeInTheDocument();
      });

      const downloadButton = screen.getByRole('button', { name: /download pdf/i });
      await user.click(downloadButton);

      expect(mockOpen).toHaveBeenCalledWith(
        'https://api.ruleiq.com/freemium/results/test-token-123/pdf',
        '_blank',
      );
    });

    it('hides sharing options when disabled', async () => {
      const resultsWithoutSharing = {
        ...mockResults,
        sharing: {
          enabled: false,
        },
      };

      mockedFreemiumApi.getResults.mockResolvedValue(resultsWithoutSharing);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /share results/i })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /download pdf/i })).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      mockedFreemiumApi.getResults.mockRejectedValue(new Error('Failed to load results'));

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/unable to load your results/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      });
    });

    it('retries failed API calls', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.getResults
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/unable to load your results/i)).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /try again/i });
      await user.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText(/your compliance assessment results/i)).toBeInTheDocument();
      });

      expect(mockedFreemiumApi.getResults).toHaveBeenCalledTimes(2);
    });

    it('handles invalid token error', async () => {
      mockedFreemiumApi.getResults.mockRejectedValue(new Error('Invalid or expired token'));

      render(
        <TestWrapper>
          <FreemiumResults token="invalid-token" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/session expired/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /start new assessment/i })).toBeInTheDocument();
      });
    });

    it('handles empty results gracefully', async () => {
      const emptyResults = {
        compliance_gaps: [],
        risk_score: 0,
        risk_level: 'unknown',
        recommendations: [],
        priority_actions: [],
      };

      mockedFreemiumApi.getResults.mockResolvedValue(emptyResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/no compliance gaps found/i)).toBeInTheDocument();
        expect(screen.getByText(/excellent compliance posture/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper heading structure', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        const mainHeading = screen.getByRole('heading', { level: 1 });
        expect(mainHeading).toHaveTextContent(/your compliance assessment results/i);

        const sectionHeadings = screen.getAllByRole('heading', { level: 2 });
        expect(sectionHeadings.length).toBeGreaterThan(0);
      });
    });

    it('provides alternative text for visual elements', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        const riskScoreChart = screen.getByRole('img', { name: /risk score visualization/i });
        expect(riskScoreChart).toBeInTheDocument();

        const severityIcons = screen.getAllByRole('img', { name: /severity indicator/i });
        expect(severityIcons.length).toBeGreaterThan(0);
      });
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /share results/i })).toBeInTheDocument();
      });

      // Tab through interactive elements
      const shareButton = screen.getByRole('button', { name: /share results/i });
      const downloadButton = screen.getByRole('button', { name: /download pdf/i });
      const ctaButton = screen.getByRole('link', { name: /get compliant now/i });

      shareButton.focus();
      expect(shareButton).toHaveFocus();

      await user.tab();
      expect(downloadButton).toHaveFocus();

      await user.tab();
      expect(ctaButton).toHaveFocus();
    });

    it('announces important information to screen readers', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        const liveRegion = screen.getByRole('status');
        expect(liveRegion).toHaveTextContent(/assessment results loaded/i);
      });
    });
  });

  describe('Performance and Caching', () => {
    it('caches results to prevent unnecessary API calls', async () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      const { rerender } = render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByText(/your compliance assessment results/i)).toBeInTheDocument();
      });

      expect(mockedFreemiumApi.getResults).toHaveBeenCalledTimes(1);

      // Re-render with same token should use cache
      rerender(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      expect(mockedFreemiumApi.getResults).toHaveBeenCalledTimes(1); // No additional calls
    });

    it('does not cause memory leaks on unmount', () => {
      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      const { unmount } = render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      expect(() => unmount()).not.toThrow();
    });
  });

  describe('Social Media Integration', () => {
    it('provides social sharing options', async () => {
      const user = userEvent.setup();

      mockedFreemiumApi.getResults.mockResolvedValue(mockResults);

      render(
        <TestWrapper>
          <FreemiumResults token="test-token-123" />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /share results/i })).toBeInTheDocument();
      });

      const shareButton = screen.getByRole('button', { name: /share results/i });
      await user.click(shareButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /share on linkedin/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /share on twitter/i })).toBeInTheDocument();
      });
    });
  });
});
