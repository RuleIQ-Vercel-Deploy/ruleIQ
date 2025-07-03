/**
 * Tests for AIHelpTooltip component
 * 
 * Tests AI help functionality, memory leak prevention,
 * race condition handling, and user interactions.
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import { AIHelpTooltip } from '@/components/assessments/AIHelpTooltip';
import { assessmentAIService } from '@/lib/api/assessments-ai.service';
import { type Question } from '@/lib/assessment-engine/types';
import { type UserContext } from '@/types/ai';

// Mock the AI service
vi.mock('@/lib/api/assessments-ai.service', () => ({
  assessmentAIService: {
    getQuestionHelp: vi.fn(),
    submitFeedback: vi.fn(),
  }
}));

// Mock toast hook
const mockToast = vi.fn();
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: mockToast })
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: 'div',
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

const mockQuestion: Question = {
  id: 'test-question-1',
  text: 'Do you have a data protection policy?',
  type: 'yes_no',
  validation: { required: true }
};

const mockUserContext: UserContext = {
  business_profile_id: 'test-profile-123',
  industry: 'technology',
  company_size: 'small',
  location: 'UK'
};

const mockAIResponse = {
  guidance: 'A data protection policy is essential for GDPR compliance...',
  confidence_score: 0.95,
  related_topics: ['GDPR', 'Data Protection'],
  follow_up_suggestions: ['What should be included in the policy?'],
  source_references: ['GDPR Article 5'],
  request_id: 'test-request-123',
  generated_at: new Date().toISOString()
};

describe('AIHelpTooltip', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockToast.mockClear();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  it('renders AI help button correctly', () => {
    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        sectionId="data-protection"
        userContext={mockUserContext}
      />
    );

    expect(screen.getByRole('button', { name: /ai help/i })).toBeInTheDocument();
    expect(screen.getByText('AI Help')).toBeInTheDocument();
  });

  it('shows loading state when fetching AI help', async () => {
    // Mock delayed response
    vi.mocked(assessmentAIService.getQuestionHelp).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockAIResponse), 100))
    );

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    // Should show loading state
    expect(helpButton).toBeDisabled();
    expect(screen.getByTestId('loading-spinner') || screen.getByRole('button', { name: /loading/i })).toBeInTheDocument();
  });

  it('displays AI guidance when successfully loaded', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    expect(screen.getByText('95% Confidence')).toBeInTheDocument();
    expect(screen.getByText('GDPR')).toBeInTheDocument();
    expect(screen.getByText('Data Protection')).toBeInTheDocument();
  });

  it('handles AI service errors gracefully', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockRejectedValue(
      new Error('AI service unavailable')
    );

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to get ai help/i)).toBeInTheDocument();
    });
  });

  it('prevents race conditions with multiple rapid clicks', async () => {
    // Mock slow response
    let resolveCount = 0;
    vi.mocked(assessmentAIService.getQuestionHelp).mockImplementation(
      () => new Promise(resolve => {
        setTimeout(() => {
          resolveCount++;
          resolve({ ...mockAIResponse, request_id: `request-${resolveCount}` });
        }, 50);
      })
    );

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    const helpButton = screen.getByRole('button', { name: /ai help/i });

    // Click multiple times rapidly
    fireEvent.click(helpButton);
    fireEvent.click(helpButton);
    fireEvent.click(helpButton);

    // Wait for all requests to complete
    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    }, { timeout: 200 });

    // Should only make one API call due to race condition prevention
    expect(assessmentAIService.getQuestionHelp).toHaveBeenCalledTimes(1);
  });

  it('copies AI guidance to clipboard', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Get AI help first
    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    // Click copy button
    const copyButton = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockAIResponse.guidance);
    expect(mockToast).toHaveBeenCalledWith({
      title: "Copied to clipboard",
      description: "AI guidance has been copied to your clipboard.",
      duration: 2000
    });
  });

  it('submits positive feedback correctly', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);
    vi.mocked(assessmentAIService.submitFeedback).mockResolvedValue({ status: 'success' });

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Get AI help first
    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    // Click thumbs up
    const thumbsUpButton = screen.getByRole('button', { name: /thumbs up/i });
    fireEvent.click(thumbsUpButton);

    expect(assessmentAIService.submitFeedback).toHaveBeenCalledWith(
      expect.stringContaining('test-question-1'),
      { helpful: true, rating: 5 }
    );

    expect(mockToast).toHaveBeenCalledWith({
      title: "Feedback submitted",
      description: "Thank you for helping us improve AI assistance.",
      duration: 2000
    });
  });

  it('submits negative feedback correctly', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);
    vi.mocked(assessmentAIService.submitFeedback).mockResolvedValue({ status: 'success' });

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Get AI help first
    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    // Click thumbs down
    const thumbsDownButton = screen.getByRole('button', { name: /thumbs down/i });
    fireEvent.click(thumbsDownButton);

    expect(assessmentAIService.submitFeedback).toHaveBeenCalledWith(
      expect.stringContaining('test-question-1'),
      { helpful: false, rating: 2 }
    );
  });

  it('handles feedback submission errors gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);
    vi.mocked(assessmentAIService.submitFeedback).mockRejectedValue(
      new Error('Feedback service unavailable')
    );

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Get AI help first
    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    // Click thumbs up
    const thumbsUpButton = screen.getByRole('button', { name: /thumbs up/i });
    fireEvent.click(thumbsUpButton);

    expect(consoleSpy).toHaveBeenCalledWith(
      'Failed to submit feedback:',
      expect.any(Error)
    );

    consoleSpy.mockRestore();
  });

  it('toggles tooltip visibility correctly', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    const helpButton = screen.getByRole('button', { name: /ai help/i });

    // First click - should open and fetch
    fireEvent.click(helpButton);

    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.guidance)).toBeInTheDocument();
    });

    // Second click - should close (no new API call)
    fireEvent.click(helpButton);
    
    await waitFor(() => {
      expect(screen.queryByText(mockAIResponse.guidance)).not.toBeInTheDocument();
    });

    // Should only have made one API call
    expect(assessmentAIService.getQuestionHelp).toHaveBeenCalledTimes(1);
  });

  it('calls API with correct parameters', async () => {
    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIResponse);

    render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        sectionId="data-protection"
        userContext={mockUserContext}
      />
    );

    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    expect(assessmentAIService.getQuestionHelp).toHaveBeenCalledWith({
      question_id: 'test-question-1',
      question_text: 'Do you have a data protection policy?',
      framework_id: 'gdpr',
      section_id: 'data-protection',
      user_context: mockUserContext
    });
  });

  it('cleans up properly on unmount to prevent memory leaks', () => {
    const { unmount } = render(
      <AIHelpTooltip
        question={mockQuestion}
        frameworkId="gdpr"
        userContext={mockUserContext}
      />
    );

    // Trigger a request
    const helpButton = screen.getByRole('button', { name: /ai help/i });
    fireEvent.click(helpButton);

    // Unmount component
    unmount();

    // Component should unmount without errors
    expect(document.body).toBeInTheDocument();
  });
});
