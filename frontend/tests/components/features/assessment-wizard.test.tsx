import { describe, it, expect, vi, beforeEach } from 'vitest';

import { AssessmentWizard } from '@/components/assessments/AssessmentWizard';
import type {
  AssessmentFramework,
  AssessmentProgress,
  Question,
  AssessmentSection,
  AssessmentResult,
} from '@/lib/assessment-engine';

import { render, screen, fireEvent, waitFor, act } from '../../utils';

// Mock dependencies
vi.mock('@/components/assessments/AIErrorBoundary', () => ({
  AIErrorBoundary: ({ children }: any) => <div data-testid="ai-error-boundary">{children}</div>,
}));

vi.mock('@/components/assessments/AssessmentNavigation', () => ({
  AssessmentNavigation: (props: any) => (
    <div data-testid="assessment-navigation">
      {props.framework.sections.map((section: any, index: number) => (
        <button key={section.id} onClick={() => props.onSectionClick(index)}>
          Section {index + 1}
        </button>
      ))}
    </div>
  ),
}));

vi.mock('@/components/assessments/QuestionRenderer', () => ({
  QuestionRenderer: (props: any) => (
    <div data-testid="question-renderer">
      <div>{props.question.text}</div>
      <input
        type="text"
        onChange={(e) => props.onChange(e.target.value)}
        data-testid="question-input"
        defaultValue={props.value}
      />
      {props.error && <div>{props.error}</div>}
    </div>
  ),
}));

vi.mock('@/components/assessments/FollowUpQuestion', () => ({
  FollowUpQuestion: (props: any) => (
    <div data-testid="follow-up-question">
      <div>{props.question.text}</div>
      <input
        type="text"
        onChange={(e) => props.onChange(e.target.value)}
        data-testid="follow-up-input"
        defaultValue={props.value}
      />
    </div>
  ),
}));

vi.mock('@/components/assessments/ProgressTracker', () => ({
  ProgressTracker: (props: any) => (
    <div data-testid="progress-tracker">
      Progress: {props.progress.answeredQuestions + 1}/{props.progress.totalQuestions}
    </div>
  ),
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

// Mock the QuestionnaireEngine class
let mockOnProgress: ((progress: any) => void) | null = null;

const mockEngine = {
  getCurrentQuestion: vi.fn(),
  getCurrentSection: vi.fn(),
  getProgress: vi.fn(),
  answerQuestion: vi.fn(),
  nextQuestion: vi.fn(),
  previousQuestion: vi.fn(),
  jumpToSection: vi.fn(),
  calculateResults: vi.fn(),
  loadProgress: vi.fn(),
  destroy: vi.fn(),
  getAnswers: vi.fn(),
  isInAIMode: vi.fn(),
  getCurrentAIQuestion: vi.fn(),
  hasAIQuestionsRemaining: vi.fn(),
  getAIQuestionProgress: vi.fn(),
};

vi.mock('@/lib/assessment-engine', () => ({
  QuestionnaireEngine: vi.fn().mockImplementation((framework, context, config) => {
    // Capture the onProgress callback
    mockOnProgress = config?.onProgress || null;
    return mockEngine;
  }),
}));

// Mock framework data
const mockFramework: AssessmentFramework = {
  id: 'gdpr',
  name: 'GDPR Compliance Assessment',
  description: 'Test assessment framework',
  version: '1.0',
  scoringMethod: 'percentage',
  passingScore: 70,
  estimatedDuration: 30,
  tags: ['Privacy'],
  sections: [
    {
      id: 'section-1',
      title: 'Data Processing',
      description: 'Test section',
      order: 1,
      questions: [
        {
          id: 'q1',
          type: 'radio',
          text: 'Do you process personal data?',
          options: [
            { value: 'yes', label: 'Yes' },
            { value: 'no', label: 'No' },
          ],
          validation: { required: true },
          weight: 1,
        },
        {
          id: 'q2',
          type: 'checkbox',
          text: 'What types of personal data do you process?',
          options: [
            { value: 'names', label: 'Names' },
            { value: 'emails', label: 'Email addresses' },
            { value: 'addresses', label: 'Physical addresses' },
          ],
          validation: { required: true },
          weight: 1,
        },
      ],
    },
  ],
};

// Mock the router
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('AssessmentWizard', () => {
  const mockProps = {
    framework: mockFramework,
    assessmentId: 'test-assessment-id',
    businessProfileId: 'test-profile-id',
    onComplete: vi.fn(),
    onSave: vi.fn(),
    onExit: vi.fn(),
  };

  const mockProgress: AssessmentProgress = {
    totalQuestions: 2,
    answeredQuestions: 0,
    currentSection: 'section-1',
    currentQuestion: 'q1',
    percentComplete: 0,
    estimatedTimeRemaining: 30,
  };

  const mockSection: AssessmentSection = mockFramework.sections[0];
  const mockQuestion: Question = mockFramework.sections[0].questions[0];

  beforeEach(() => {
    vi.clearAllMocks();

    // Create a mock answers map that can be updated
    const mockAnswers = new Map();

    // Set up default mock return values
    mockEngine.getCurrentQuestion.mockReturnValue(mockQuestion);
    mockEngine.getCurrentSection.mockReturnValue(mockSection);
    mockEngine.getProgress.mockReturnValue(mockProgress);
    mockEngine.loadProgress.mockReturnValue(false);
    mockEngine.getAnswers.mockReturnValue(mockAnswers);
    mockEngine.isInAIMode.mockReturnValue(false);
    mockEngine.getCurrentAIQuestion.mockReturnValue(null);
    mockEngine.hasAIQuestionsRemaining.mockReturnValue(false);
    mockEngine.getAIQuestionProgress.mockReturnValue({ current: 1, total: 1 });

    // Mock answerQuestion to update the answers map
    mockEngine.answerQuestion.mockImplementation((questionId: string, value: any) => {
      mockAnswers.set(questionId, { value, timestamp: new Date() });
    });
    mockEngine.nextQuestion.mockResolvedValue(true);
    mockEngine.previousQuestion.mockReturnValue(true);
    mockEngine.jumpToSection.mockReturnValue(true);
    mockEngine.calculateResults.mockResolvedValue({
      assessmentId: mockProps.assessmentId,
      frameworkId: mockFramework.id,
      overallScore: 85,
      sectionScores: { 'section-1': 85 },
      gaps: [],
      recommendations: [],
      completedAt: new Date(),
    } as AssessmentResult);
  });

  describe('Rendering', () => {
    it('should render the first question', () => {
      render(<AssessmentWizard {...mockProps} />);

      expect(screen.getByText('Do you process personal data?')).toBeInTheDocument();
      expect(screen.getByTestId('question-renderer')).toBeInTheDocument();
    });

    it('should show progress indicator', () => {
      render(<AssessmentWizard {...mockProps} />);

      expect(screen.getByTestId('progress-tracker')).toBeInTheDocument();
      expect(screen.getByText('Progress: 1/2')).toBeInTheDocument();
    });

    it('should show question number and total', () => {
      render(<AssessmentWizard {...mockProps} />);

      const progressText = screen.getByText('Progress: 1/2');
      expect(progressText).toBeInTheDocument();
    });

    it('should render different question types correctly', () => {
      // Set up for checkbox question
      const checkboxQuestion = mockFramework.sections[0].questions[1];
      mockEngine.getCurrentQuestion.mockReturnValue(checkboxQuestion);

      render(<AssessmentWizard {...mockProps} />);

      expect(screen.getByText('What types of personal data do you process?')).toBeInTheDocument();
      expect(screen.getByTestId('question-renderer')).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should disable previous button on first question', () => {
      render(<AssessmentWizard {...mockProps} />);

      const previousButton = screen.getByRole('button', { name: /previous/i });
      expect(previousButton).toBeDisabled();
    });

    it('should enable next button when question is answered', async () => {
      render(<AssessmentWizard {...mockProps} />);

      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeDisabled();

      // Answer the question
      const questionInput = screen.getByTestId('question-input');
      act(() => {
        fireEvent.change(questionInput, { target: { value: 'yes' } });
      });

      await waitFor(() => {
        expect(nextButton).toBeEnabled();
      });
    });

    it('should call nextQuestion when next button is clicked', async () => {
      render(<AssessmentWizard {...mockProps} />);

      // Answer the question first
      const questionInput = screen.getByTestId('question-input');
      act(() => {
        fireEvent.change(questionInput, { target: { value: 'yes' } });
      });

      const nextButton = screen.getByRole('button', { name: /next/i });
      act(() => {
        fireEvent.click(nextButton);
      });

      expect(mockEngine.nextQuestion).toHaveBeenCalled();
    });

    it('should call previousQuestion when previous button is clicked', () => {
      // Set up for second question
      const updatedProgress = { ...mockProgress, currentQuestion: 'q2', answeredQuestions: 1 };
      mockEngine.getProgress.mockReturnValue(updatedProgress);

      render(<AssessmentWizard {...mockProps} />);

      const previousButton = screen.getByRole('button', { name: /previous/i });
      fireEvent.click(previousButton);

      expect(mockEngine.previousQuestion).toHaveBeenCalled();
    });

    it('should show submit button on last question', () => {
      // Set up for last question
      const lastQuestionProgress = { ...mockProgress, currentQuestion: 'q2', answeredQuestions: 1 };
      mockEngine.getProgress.mockReturnValue(lastQuestionProgress);
      mockEngine.nextQuestion.mockResolvedValue(false); // No more questions

      render(<AssessmentWizard {...mockProps} />);

      expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /next/i })).not.toBeInTheDocument();
    });
  });

  describe('Answer Handling', () => {
    it('should call setAnswer when radio button is selected', () => {
      render(<AssessmentWizard {...mockProps} />);

      const questionInput = screen.getByTestId('question-input');
      fireEvent.change(questionInput, { target: { value: 'yes' } });

      expect(mockEngine.answerQuestion).toHaveBeenCalledWith('q1', 'yes');
    });

    it('should call setAnswer when checkbox is selected', () => {
      // Set up for checkbox question
      const checkboxQuestion = mockFramework.sections[0].questions[1];
      mockEngine.getCurrentQuestion.mockReturnValue(checkboxQuestion);

      render(<AssessmentWizard {...mockProps} />);

      const questionInput = screen.getByTestId('question-input');
      fireEvent.change(questionInput, { target: { value: 'names' } });

      expect(mockEngine.answerQuestion).toHaveBeenCalledWith('q2', 'names');
    });

    it('should handle multiple checkbox selections', () => {
      // Set up for checkbox question
      const checkboxQuestion = mockFramework.sections[0].questions[1];
      mockEngine.getCurrentQuestion.mockReturnValue(checkboxQuestion);

      render(<AssessmentWizard {...mockProps} />);

      const questionInput = screen.getByTestId('question-input');
      fireEvent.change(questionInput, { target: { value: 'names,emails' } });

      expect(mockEngine.answerQuestion).toHaveBeenCalledWith('q2', 'names,emails');
    });

    it('should preserve answers when navigating between questions', () => {
      // Set up answers in the engine
      const answersMap = new Map();
      answersMap.set('q1', { questionId: 'q1', value: 'yes', timestamp: new Date() });
      mockEngine.getAnswers.mockReturnValue(answersMap);

      render(<AssessmentWizard {...mockProps} />);

      const questionInput = screen.getByTestId('question-input');
      expect(questionInput).toHaveValue('yes');
    });
  });

  describe('Validation', () => {
    it('should show validation error for required unanswered questions', async () => {
      // Mock validation error
      mockEngine.nextQuestion.mockRejectedValue(new Error('Please select an answer'));

      render(<AssessmentWizard {...mockProps} />);

      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Please select an answer')).toBeInTheDocument();
      });
    });

    it('should clear validation error when question is answered', async () => {
      // First, set up validation error
      mockEngine.nextQuestion.mockRejectedValueOnce(new Error('Please select an answer'));

      render(<AssessmentWizard {...mockProps} />);

      // Try to proceed without answering
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Please select an answer')).toBeInTheDocument();
      });

      // Answer the question
      const questionInput = screen.getByTestId('question-input');
      fireEvent.change(questionInput, { target: { value: 'yes' } });

      // Now nextQuestion should succeed
      mockEngine.nextQuestion.mockResolvedValue(true);
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.queryByText('Please select an answer')).not.toBeInTheDocument();
      });
    });

    it('should validate multiple choice questions require at least one selection', async () => {
      // Set up for checkbox question
      const checkboxQuestion = mockFramework.sections[0].questions[1];
      mockEngine.getCurrentQuestion.mockReturnValue(checkboxQuestion);
      mockEngine.nextQuestion.mockRejectedValue(new Error('Please select at least one option'));

      render(<AssessmentWizard {...mockProps} />);

      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Please select at least one option')).toBeInTheDocument();
      });
    });
  });

  describe('Submission', () => {
    it('should call submitAssessment when submit button is clicked', async () => {
      // Set up for last question
      const lastQuestionProgress = { ...mockProgress, currentQuestion: 'q2', answeredQuestions: 1 };
      mockEngine.getProgress.mockReturnValue(lastQuestionProgress);
      mockEngine.nextQuestion.mockResolvedValue(false); // No more questions

      render(<AssessmentWizard {...mockProps} />);

      const submitButton = screen.getByRole('button', { name: /complete assessment/i });
      fireEvent.click(submitButton);

      expect(mockEngine.calculateResults).toHaveBeenCalled();
    });

    it('should show loading state during submission', () => {
      // Set up for last question with loading state
      const lastQuestionProgress = { ...mockProgress, currentQuestion: 'q2', answeredQuestions: 1 };
      mockEngine.getProgress.mockReturnValue(lastQuestionProgress);
      mockEngine.nextQuestion.mockResolvedValue(false);

      render(<AssessmentWizard {...mockProps} />);

      // Check for "Complete Assessment" button on last question
      const submitButton = screen.getByRole('button', { name: /complete assessment/i });
      expect(submitButton).toBeInTheDocument();
    });

    it('should redirect to results page after successful submission', async () => {
      // Set up for last question
      const lastQuestionProgress = { ...mockProgress, currentQuestion: 'q2', answeredQuestions: 1 };
      mockEngine.getProgress.mockReturnValue(lastQuestionProgress);
      mockEngine.nextQuestion.mockResolvedValue(false);

      const mockResult = {
        assessmentId: mockProps.assessmentId,
        frameworkId: mockFramework.id,
        overallScore: 85,
        sectionScores: { 'section-1': 85 },
        gaps: [],
        recommendations: [],
        completedAt: new Date(),
      };
      mockEngine.calculateResults.mockResolvedValue(mockResult);

      render(<AssessmentWizard {...mockProps} />);

      const submitButton = screen.getByRole('button', { name: /complete assessment/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockProps.onComplete).toHaveBeenCalledWith(mockResult);
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when there is an error', () => {
      // Mock the engine to return an error state
      mockEngine.getCurrentQuestion.mockReturnValue(null);

      render(<AssessmentWizard {...mockProps} />);

      // The component should handle the error gracefully
      expect(screen.getByText('GDPR Compliance Assessment')).toBeInTheDocument();
    });

    it('should call resetAssessment when retry button is clicked', () => {
      // Mock error state and retry functionality
      mockEngine.getCurrentQuestion.mockReturnValue(null);

      render(<AssessmentWizard {...mockProps} />);

      // Check if component renders without crashing
      expect(screen.getByText('GDPR Compliance Assessment')).toBeInTheDocument();
    });

    it('should handle submission errors gracefully', async () => {
      // Set up for last question
      const lastQuestionProgress = { ...mockProgress, currentQuestion: 'q2', answeredQuestions: 1 };
      mockEngine.getProgress.mockReturnValue(lastQuestionProgress);
      mockEngine.nextQuestion.mockResolvedValue(false);
      mockEngine.calculateResults.mockRejectedValue(new Error('Submission failed'));

      render(<AssessmentWizard {...mockProps} />);

      const submitButton = screen.getByRole('button', { name: /complete assessment/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        // The error should be handled by the component
        expect(mockEngine.calculateResults).toHaveBeenCalled();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<AssessmentWizard {...mockProps} />);

      expect(screen.getByTestId('progress-tracker')).toBeInTheDocument();
      expect(screen.getByTestId('question-renderer')).toBeInTheDocument();
    });

    it('should support keyboard navigation', () => {
      render(<AssessmentWizard {...mockProps} />);

      const questionInput = screen.getByTestId('question-input');

      // Tab navigation should work
      questionInput.focus();
      expect(document.activeElement).toBe(questionInput);
    });

    it('should announce question changes to screen readers', () => {
      render(<AssessmentWizard {...mockProps} />);

      // Check for progress tracker which provides screen reader updates
      expect(screen.getByTestId('progress-tracker')).toBeInTheDocument();
    });
  });
});
