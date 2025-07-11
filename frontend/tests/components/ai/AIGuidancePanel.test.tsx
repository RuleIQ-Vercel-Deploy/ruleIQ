/**
 * Tests for AIGuidancePanel component
 * 
 * Tests panel functionality, collapsible behavior,
 * enhanced error handling, and user interactions.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { AIGuidancePanel } from '@/components/assessments/AIGuidancePanel';
import { assessmentAIService } from '@/lib/api/assessments-ai.service';
import { type Question } from '@/lib/assessment-engine/types';
import { type UserContext } from '@/types/ai';

// Mock the AI service
vi.mock('@/lib/api/assessments-ai.service', () => ({
  assessmentAIService: {
    getQuestionHelp: vi.fn(),
  }
}));

// Mock toast hook
const mockToast = vi.fn();
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: mockToast })
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

const mockQuestion: Question = {
  id: 'test-question-1',
  text: 'What are the key principles of GDPR?',
  type: 'textarea',
  validation: { required: true }
};

const mockUserContext: UserContext = {
  business_profile_id: 'test-profile-123',
  industry: 'technology',
  company_size: 'medium',
  location: 'UK'
};

const mockAIResponse = {
  guidance: 'The key principles of GDPR include lawfulness, fairness, transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity and confidentiality, and accountability.',
  confidence_score: 0.92,
  related_topics: ['Data Protection', 'Privacy Rights', 'Lawful Basis'],
  follow_up_suggestions: [
    'How do you ensure lawful basis for processing?',
    'What is data minimisation in practice?'
  ],
  source_references: ['GDPR Article 5', 'ICO Guidance'],
  request_id: 'test-request-456',
  generated_at: new Date().toISOString()
};

describe('AIGuidancePanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockToast.mockClear();
  });

  it('renders collapsed by default', () => {
    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        sectionId="principles"
        userContext={mockUserContext}
      />
    );

    expect(screen.getByText('AI Compliance Guidance')).toBeInTheDocument();
    expect(screen.queryByText('Get AI guidance for this question')).not.toBeInTheDocument();
  });

  it('renders expanded when defaultOpen is true', () => {
    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
        defaultOpen={true}
      />
    );

    expect(screen.getByText('AI Compliance Guidance')).toBeInTheDocument();
    
    // When defaultOpen is true, the panel is expanded but guidance is not loaded automatically
    // The CollapsibleContent should be visible
    const panel = screen.getByText('AI Compliance Guidance').closest('[data-state="open"]');
    expect(panel).toBeInTheDocument();
  });

  it('expands and loads guidance when clicked', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Click to expand
    const header = screen.getByText('AI Compliance Guidance');
    fireEvent.click(header);

    // Panel should be expanded
    const panel = screen.getByText('AI Compliance Guidance').closest('[data-state="open"]');
    expect(panel).toBeInTheDocument();

    // Wait for API to be called
    await waitFor(() => {
      expect(assessmentAIService.getQuestionHelp).toHaveBeenCalledWith({
        question_id: 'test-question-1',
        question_text: 'What are the key principles of GDPR?',
        framework_id: 'gdpr',
        user_context: mockUserContext
      });
    });

    // Wait for guidance to load - check for the actual guidance text
    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });
    
    // Check confidence score is displayed
    expect(screen.getByText(/92% confidence/)).toBeInTheDocument();
  });

  it('handles loading state correctly', async () => {
    // Mock delayed response
    vi.mocked(assessmentAIService.getQuestionHelp).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockAIResponse), 100))
    );

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Expand panel
    const header = screen.getByText('AI Compliance Guidance');
    fireEvent.click(header);

    // Should show loading state - look for the Bot icon with animate-pulse class
    const loadingBot = document.querySelector('.animate-pulse');
    expect(loadingBot).toBeInTheDocument();
    expect(screen.getByText(/Analyzing compliance requirements/i)).toBeInTheDocument();
    
    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    }, { timeout: 200 });
  });

  it('displays error state when AI service fails', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockRejectedValue(
      new Error('AI service timeout')
    );

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Expand panel
    const header = screen.getByText('AI Compliance Guidance');
    fireEvent.click(header);

    await waitFor(() => {
      expect(screen.getByText(/AI service timeout/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  it('allows retry after error', async () => {
    
    
    // First call fails, second succeeds
    vi.mocked(assessmentAIService.getQuestionHelp)
      .mockRejectedValueOnce(new Error('Service unavailable'))
      .mockResolvedValueOnce(mockAIResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Expand panel
    const header = screen.getByText('AI Compliance Guidance');
    fireEvent.click(header);

    // Wait for error
    await waitFor(() => {
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    // Click retry
    const retryButton = screen.getByText('Try Again');
    fireEvent.click(retryButton);

    // Should succeed on retry
    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });
  });

  it('copies guidance to clipboard', async () => {
    
    
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
        defaultOpen={true}
      />
    );

    // Wait for guidance to load
    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    // Click copy guidance button
    const copyButton = screen.getByText('Copy Guidance');
    fireEvent.click(copyButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockAIResponse.guidance);
    expect(mockToast).toHaveBeenCalledWith({
      title: "Guidance copied",
      description: "AI guidance has been copied to your clipboard.",
      duration: 2000
    });
  });

  it('copies all content to clipboard', async () => {
    
    
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
        defaultOpen={true}
      />
    );

    // Wait for guidance to load
    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    // Click copy all button
    const copyAllButton = screen.getByText('Copy All');
    fireEvent.click(copyAllButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      expect.stringContaining(mockAIResponse.guidance)
    );
    expect(mockToast).toHaveBeenCalledWith({
      title: "Full guidance copied",
      description: "Complete AI guidance has been copied to your clipboard.",
      duration: 2000
    });
  });

  it('refreshes guidance when refresh button is clicked', async () => {
    
    
    const updatedResponse = { ...mockAIResponse, guidance: 'Updated guidance content' };
    
    vi.mocked(assessmentAIService.getQuestionHelp)
      .mockResolvedValueOnce(mockAIResponse)
      .mockResolvedValueOnce(updatedResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
        defaultOpen={true}
      />
    );

    // Wait for initial guidance
    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    // Click refresh
    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);

    // Should show updated content
    await waitFor(() => {
      expect(screen.getByText('Updated guidance content')).toBeInTheDocument();
    });

    expect(assessmentAIService.getQuestionHelp).toHaveBeenCalledTimes(2);
  });

  it('displays related topics as badges', async () => {
    
    
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
        defaultOpen={true}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Data Protection')).toBeInTheDocument();
      expect(screen.getByText('Privacy Rights')).toBeInTheDocument();
      expect(screen.getByText('Lawful Basis')).toBeInTheDocument();
    });
  });

  it('displays follow-up suggestions', async () => {
    
    
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
        defaultOpen={true}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('How do you ensure lawful basis for processing?')).toBeInTheDocument();
      expect(screen.getByText('What is data minimisation in practice?')).toBeInTheDocument();
    });
  });

  it('displays source references', async () => {
    
    
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
        defaultOpen={true}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('GDPR Article 5')).toBeInTheDocument();
      expect(screen.getByText('ICO Guidance')).toBeInTheDocument();
    });
  });

  it('prevents race conditions with rapid expand/collapse', async () => {
    
    
    // Mock slow response
    vi.mocked(assessmentAIService.getQuestionHelp).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockAIResponse), 100))
    );

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    const header = screen.getByText('AI Compliance Guidance');
    
    // Rapid clicks
    fireEvent.click(header);
    fireEvent.click(header);
    fireEvent.click(header);

    // Should only make one API call
    await waitFor(() => {
      expect(assessmentAIService.getQuestionHelp).toHaveBeenCalledTimes(1);
    }, { timeout: 200 });
  });

  it('applies custom className', () => {
    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
        className="custom-class"
      />
    );

    const panel = screen.getByText('AI Compliance Guidance').closest('.custom-class');
    expect(panel).toBeInTheDocument();
  });

  it('calls API with correct parameters', async () => {
    
    
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIGuidancePanel
        question={mockQuestion}
        frameworkId="gdpr"
        sectionId="principles"
        userContext={mockUserContext}
        defaultOpen={true}
      />
    );

    await waitFor(() => {
      expect(assessmentAIService.getQuestionHelp).toHaveBeenCalledWith({
        question_id: 'test-question-1',
        question_text: 'What are the key principles of GDPR?',
        framework_id: 'gdpr',
        section_id: 'principles',
        user_context: mockUserContext
      });
    });
  });
});
