/**
 * Integration Tests for Complete AI Assessment Flows
 * 
 * Tests end-to-end AI assessment functionality including:
 * - Conversational assessment mode
 * - Smart question adaptation
 * - Real-time scoring with AI insights
 * - Complete data flow validation
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import { AIErrorBoundary } from '@/components/assessments/AIErrorBoundary';
import { AIGuidancePanel } from '@/components/assessments/AIGuidancePanel';
import { AIHelpTooltip } from '@/components/assessments/AIHelpTooltip';
import { assessmentAIService } from '@/lib/api/assessments-ai.service';
import { QuestionnaireEngine } from '@/lib/assessment-engine/QuestionnaireEngine';
import { type AssessmentFramework, type AssessmentContext, type Question } from '@/lib/assessment-engine/types';

// Mock AI service
vi.mock('@/lib/api/assessments-ai.service', () => ({
  assessmentAIService: {
    getQuestionHelp: vi.fn(),
    getFollowUpQuestions: vi.fn(),
    getPersonalizedRecommendations: vi.fn(),
    getAssessmentAnalysis: vi.fn(),
    submitFeedback: vi.fn(),
  }
}));

// Mock toast
const mockToast = vi.fn();
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: mockToast })
}));

// Test Assessment Framework
const mockFramework: AssessmentFramework = {
  id: 'gdpr-test',
  name: 'GDPR Compliance Assessment',
  description: 'Test GDPR framework',
  version: '1.0',
  scoringMethod: 'percentage',
  sections: [
    {
      id: 'data-protection',
      title: 'Data Protection',
      description: 'Data protection principles',
      weight: 1,
      questions: [
        {
          id: 'q1',
          text: 'Do you process personal data?',
          type: 'yes_no',
          validation: { required: true },
          weight: 1,
          metadata: { priority: 'high', triggers_ai: true }
        },
        {
          id: 'q2',
          text: 'Do you have a data protection policy?',
          type: 'yes_no',
          validation: { required: true },
          weight: 1
        }
      ]
    }
  ]
};

const mockContext: AssessmentContext = {
  frameworkId: 'gdpr-test',
  assessmentId: 'test-assessment-123',
  businessProfileId: 'test-profile-456',
  answers: new Map(),
  metadata: {
    industry: 'technology',
    company_size: 'small',
    location: 'UK'
  }
};

// Mock AI Responses
const mockAIHelp = {
  guidance: 'Personal data includes any information relating to an identified or identifiable natural person...',
  confidence_score: 0.95,
  related_topics: ['GDPR', 'Personal Data', 'Data Processing'],
  follow_up_suggestions: ['What types of personal data do you process?'],
  source_references: ['GDPR Article 4']
};

const mockFollowUpQuestions = {
  follow_up_questions: [
    {
      id: 'ai-q1',
      text: 'What types of personal data do you process?',
      type: 'multiple_choice',
      options: ['Names', 'Email addresses', 'Financial data', 'Health data'],
      validation: { required: true },
      metadata: { source: 'ai', reasoning: 'Need to understand data types for compliance assessment' }
    },
    {
      id: 'ai-q2',
      text: 'What is the legal basis for processing this data?',
      type: 'multiple_choice',
      options: ['Consent', 'Contract', 'Legal obligation', 'Legitimate interest'],
      validation: { required: true },
      metadata: { source: 'ai', reasoning: 'Legal basis is required for GDPR compliance' }
    }
  ],
  reasoning: 'Based on your answer, we need more details about your data processing activities'
};

const mockRecommendations = {
  recommendations: [
    {
      id: 'rec-1',
      title: 'Implement Data Protection Policy',
      description: 'Create a comprehensive data protection policy covering all GDPR requirements',
      priority: 'high',
      category: 'Policy',
      estimatedEffort: 'Medium',
      timeline: '2-4 weeks'
    }
  ],
  implementation_plan: {
    phases: [
      {
        name: 'Policy Development',
        duration_weeks: 2,
        tasks: ['Draft policy', 'Review with legal', 'Approve policy']
      }
    ],
    total_timeline_weeks: 4,
    resource_requirements: ['Legal review', 'Management approval']
  },
  success_metrics: [
    { metric: 'Policy completion', target: '100%' },
    { metric: 'Staff training', target: '90%' }
  ]
};

// Test Component that integrates AI features
function TestAssessmentWithAI({ 
  framework, 
  context, 
  enableAI = true 
}: { 
  framework: AssessmentFramework; 
  context: AssessmentContext; 
  enableAI?: boolean;
}) {
  const [engine, setEngine] = React.useState<QuestionnaireEngine | null>(null);
  const [currentQuestion, setCurrentQuestion] = React.useState<Question | null>(null);
  const [isAIMode, setIsAIMode] = React.useState(false);

  React.useEffect(() => {
    const newEngine = new QuestionnaireEngine(framework, context, {
      enableAI,
      useMockAIOnError: true
    });
    setEngine(newEngine);
    setCurrentQuestion(newEngine.getCurrentQuestion());
    setIsAIMode(newEngine.isInAIMode());

    return () => {
      newEngine.destroy();
    };
  }, [framework, context, enableAI]);

  const handleAnswer = async (value: any) => {
    if (!engine || !currentQuestion) return;

    engine.answerQuestion(currentQuestion.id, value);
    const hasMore = await engine.nextQuestion();
    
    if (hasMore) {
      setCurrentQuestion(engine.getCurrentQuestion() || engine.getCurrentAIQuestion());
      setIsAIMode(engine.isInAIMode());
    } else {
      setCurrentQuestion(null);
    }
  };

  const handleGetResults = async () => {
    if (!engine) return null;
    return await engine.calculateResults();
  };

  if (!currentQuestion) {
    return (
      <div>
        <div>Assessment Complete</div>
        <button onClick={handleGetResults}>Get Results</button>
      </div>
    );
  }

  return (
    <AIErrorBoundary>
      <div data-testid="assessment-container">
        <div data-testid="question-text">{currentQuestion.text}</div>
        <div data-testid="ai-mode-indicator">{isAIMode ? 'AI Mode' : 'Framework Mode'}</div>
        
        {/* AI Help Tooltip */}
        <AIHelpTooltip
          question={currentQuestion}
          frameworkId={framework.id}
          sectionId="data-protection"
          userContext={{
            business_profile_id: context.businessProfileId,
            industry: context.metadata.industry,
            company_size: context.metadata.company_size,
            location: context.metadata.location
          }}
        />

        {/* AI Guidance Panel */}
        <AIGuidancePanel
          question={currentQuestion}
          frameworkId={framework.id}
          sectionId="data-protection"
          userContext={{
            business_profile_id: context.businessProfileId,
            industry: context.metadata.industry,
            company_size: context.metadata.company_size,
            location: context.metadata.location
          }}
        />

        {/* Answer Buttons */}
        {currentQuestion.type === 'yes_no' && (
          <div>
            <button onClick={() => handleAnswer('yes')} data-testid="answer-yes">
              Yes
            </button>
            <button onClick={() => handleAnswer('no')} data-testid="answer-no">
              No
            </button>
          </div>
        )}

        {currentQuestion.type === 'multiple_choice' && currentQuestion.options && (
          <div>
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                data-testid={`answer-option-${index}`}
              >
                {option}
              </button>
            ))}
          </div>
        )}
      </div>
    </AIErrorBoundary>
  );
}

describe('AI Assessment Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockToast.mockClear();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  it('completes full assessment flow with AI follow-up questions', async () => {
    const user = userEvent.setup();

    // Mock AI responses
    vi.mocked(assessmentAIService.getFollowUpQuestions).mockResolvedValue(mockFollowUpQuestions);
    vi.mocked(assessmentAIService.getPersonalizedRecommendations).mockResolvedValue(mockRecommendations);

    render(
      <TestAssessmentWithAI 
        framework={mockFramework} 
        context={mockContext} 
        enableAI={true}
      />
    );

    // Start with first framework question
    expect(screen.getByTestId('question-text')).toHaveTextContent('Do you process personal data?');
    expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('Framework Mode');

    // Answer 'yes' to trigger AI follow-up
    await user.click(screen.getByTestId('answer-yes'));

    // Should enter AI mode with follow-up questions
    await waitFor(() => {
      expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('AI Mode');
    });

    expect(screen.getByTestId('question-text')).toHaveTextContent('What types of personal data do you process?');

    // Answer first AI question
    await user.click(screen.getByTestId('answer-option-0')); // Names

    // Should move to second AI question
    await waitFor(() => {
      expect(screen.getByTestId('question-text')).toHaveTextContent('What is the legal basis for processing this data?');
    });

    // Answer second AI question
    await user.click(screen.getByTestId('answer-option-0')); // Consent

    // Should return to framework questions
    await waitFor(() => {
      expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('Framework Mode');
    });

    expect(screen.getByTestId('question-text')).toHaveTextContent('Do you have a data protection policy?');

    // Complete assessment
    await user.click(screen.getByTestId('answer-no'));

    // Should complete assessment
    await waitFor(() => {
      expect(screen.getByText('Assessment Complete')).toBeInTheDocument();
    });

    // Verify AI services were called
    expect(assessmentAIService.getFollowUpQuestions).toHaveBeenCalledWith({
      question_id: 'q1',
      question_text: 'Do you process personal data?',
      user_answer: 'yes',
      assessment_context: expect.objectContaining({
        framework_id: 'gdpr-test',
        business_profile_id: 'test-profile-456'
      })
    });
  });

  it('handles AI service failures gracefully with fallback', async () => {
    const user = userEvent.setup();

    // Mock AI service failure
    vi.mocked(assessmentAIService.getFollowUpQuestions).mockRejectedValue(
      new Error('AI service unavailable')
    );

    render(
      <TestAssessmentWithAI 
        framework={mockFramework} 
        context={mockContext} 
        enableAI={true}
      />
    );

    // Answer question that would trigger AI
    await user.click(screen.getByTestId('answer-yes'));

    // Should still enter AI mode with fallback questions
    await waitFor(() => {
      expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('AI Mode');
    });

    // Should show some AI question (fallback)
    expect(screen.getByTestId('question-text')).toBeInTheDocument();
  });

  it('integrates AI help tooltip with assessment flow', async () => {
    const user = userEvent.setup();

    vi.mocked(assessmentAIService.getQuestionHelp).mockResolvedValue(mockAIHelp);

    render(
      <TestAssessmentWithAI 
        framework={mockFramework} 
        context={mockContext} 
        enableAI={true}
      />
    );

    // Click AI help button
    const helpButton = screen.getByRole('button', { name: /ai help/i });
    await user.click(helpButton);

    // Should show AI guidance
    await waitFor(() => {
      expect(screen.getByText(mockAIHelp.guidance)).toBeInTheDocument();
    });

    expect(screen.getByText('95% Confidence')).toBeInTheDocument();

    // Should still be able to answer question
    await user.click(screen.getByTestId('answer-yes'));

    // Assessment should continue normally
    await waitFor(() => {
      expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('AI Mode');
    });
  });

  it('handles concurrent AI requests without race conditions', async () => {
    const user = userEvent.setup();

    // Mock slow AI responses
    vi.mocked(assessmentAIService.getQuestionHelp).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockAIHelp), 100))
    );
    vi.mocked(assessmentAIService.getFollowUpQuestions).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockFollowUpQuestions), 50))
    );

    render(
      <TestAssessmentWithAI 
        framework={mockFramework} 
        context={mockContext} 
        enableAI={true}
      />
    );

    // Trigger multiple AI requests simultaneously
    const helpButton = screen.getByRole('button', { name: /ai help/i });
    await user.click(helpButton); // AI help request

    // Immediately answer question to trigger follow-up
    await user.click(screen.getByTestId('answer-yes')); // Follow-up request

    // Both should complete without conflicts
    await waitFor(() => {
      expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('AI Mode');
    }, { timeout: 200 });

    // Should have made both API calls
    expect(assessmentAIService.getQuestionHelp).toHaveBeenCalled();
    expect(assessmentAIService.getFollowUpQuestions).toHaveBeenCalled();
  });

  it('maintains assessment state during AI interactions', async () => {
    const user = userEvent.setup();

    vi.mocked(assessmentAIService.getFollowUpQuestions).mockResolvedValue(mockFollowUpQuestions);

    render(
      <TestAssessmentWithAI 
        framework={mockFramework} 
        context={mockContext} 
        enableAI={true}
      />
    );

    // Answer first question
    await user.click(screen.getByTestId('answer-yes'));

    // Enter AI mode
    await waitFor(() => {
      expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('AI Mode');
    });

    // Answer AI questions
    await user.click(screen.getByTestId('answer-option-1')); // Email addresses
    
    await waitFor(() => {
      expect(screen.getByTestId('question-text')).toHaveTextContent('What is the legal basis');
    });

    await user.click(screen.getByTestId('answer-option-1')); // Contract

    // Return to framework mode
    await waitFor(() => {
      expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('Framework Mode');
    });

    // Should be on second framework question
    expect(screen.getByTestId('question-text')).toHaveTextContent('Do you have a data protection policy?');

    // Complete assessment
    await user.click(screen.getByTestId('answer-no'));

    await waitFor(() => {
      expect(screen.getByText('Assessment Complete')).toBeInTheDocument();
    });
  });

  it('generates AI recommendations at assessment completion', async () => {
    const user = userEvent.setup();

    vi.mocked(assessmentAIService.getPersonalizedRecommendations).mockResolvedValue(mockRecommendations);

    render(
      <TestAssessmentWithAI 
        framework={mockFramework} 
        context={mockContext} 
        enableAI={true}
      />
    );

    // Complete assessment quickly (no AI follow-up)
    await user.click(screen.getByTestId('answer-no')); // First question
    
    await waitFor(() => {
      expect(screen.getByTestId('question-text')).toHaveTextContent('Do you have a data protection policy?');
    });

    await user.click(screen.getByTestId('answer-no')); // Second question

    // Assessment should complete
    await waitFor(() => {
      expect(screen.getByText('Assessment Complete')).toBeInTheDocument();
    });

    // Click get results
    const resultsButton = screen.getByText('Get Results');
    await user.click(resultsButton);

    // Should call AI recommendations
    await waitFor(() => {
      expect(assessmentAIService.getPersonalizedRecommendations).toHaveBeenCalled();
    });
  });

  it('works without AI when disabled', async () => {
    const user = userEvent.setup();

    render(
      <TestAssessmentWithAI 
        framework={mockFramework} 
        context={mockContext} 
        enableAI={false}
      />
    );

    // Answer questions normally
    await user.click(screen.getByTestId('answer-yes'));

    // Should NOT enter AI mode
    await waitFor(() => {
      expect(screen.getByTestId('question-text')).toHaveTextContent('Do you have a data protection policy?');
    });

    expect(screen.getByTestId('ai-mode-indicator')).toHaveTextContent('Framework Mode');

    // Complete assessment
    await user.click(screen.getByTestId('answer-no'));

    await waitFor(() => {
      expect(screen.getByText('Assessment Complete')).toBeInTheDocument();
    });

    // Should not have called AI services
    expect(assessmentAIService.getFollowUpQuestions).not.toHaveBeenCalled();
  });
});
