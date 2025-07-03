import { describe, it, expect, vi, beforeEach } from 'vitest';

import { AssessmentWizard } from '@/components/assessments/AssessmentWizard';

import { render, screen, fireEvent, waitFor } from '../../utils';

// Mock the assessment store
const mockAssessmentStore = {
  currentQuestion: 0,
  questions: [
    {
      id: '1',
      text: 'Do you process personal data?',
      type: 'boolean',
      required: true,
      options: [
        { value: 'yes', label: 'Yes' },
        { value: 'no', label: 'No' }
      ]
    },
    {
      id: '2',
      text: 'What types of personal data do you process?',
      type: 'multiple',
      required: true,
      options: [
        { value: 'names', label: 'Names' },
        { value: 'emails', label: 'Email addresses' },
        { value: 'addresses', label: 'Physical addresses' }
      ]
    }
  ],
  answers: {},
  isLoading: false,
  error: null,
  nextQuestion: vi.fn(),
  previousQuestion: vi.fn(),
  setAnswer: vi.fn(),
  submitAssessment: vi.fn(),
  resetAssessment: vi.fn(),
};

vi.mock('@/lib/stores/assessment.store', () => ({
  useAssessmentStore: () => mockAssessmentStore,
}));

// Mock the router
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('AssessmentWizard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAssessmentStore.currentQuestion = 0;
    mockAssessmentStore.answers = {};
    mockAssessmentStore.isLoading = false;
    mockAssessmentStore.error = null;
  });

  describe('Rendering', () => {
    it('should render the first question', () => {
      render(<AssessmentWizard />);

      expect(screen.getByText('Do you process personal data?')).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: 'Yes' })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: 'No' })).toBeInTheDocument();
    });

    it('should show progress indicator', () => {
      render(<AssessmentWizard />);

      expect(screen.getByText('Question 1 of 2')).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('should show question number and total', () => {
      render(<AssessmentWizard />);

      const progressText = screen.getByText('Question 1 of 2');
      expect(progressText).toBeInTheDocument();
    });

    it('should render different question types correctly', () => {
      // Start with multiple choice question
      mockAssessmentStore.currentQuestion = 1;

      render(<AssessmentWizard />);

      expect(screen.getByText('What types of personal data do you process?')).toBeInTheDocument();
      expect(screen.getByRole('checkbox', { name: 'Names' })).toBeInTheDocument();
      expect(screen.getByRole('checkbox', { name: 'Email addresses' })).toBeInTheDocument();
      expect(screen.getByRole('checkbox', { name: 'Physical addresses' })).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should disable previous button on first question', () => {
      render(<AssessmentWizard />);

      const previousButton = screen.getByRole('button', { name: /previous/i });
      expect(previousButton).toBeDisabled();
    });

    it('should enable next button when question is answered', async () => {
      render(<AssessmentWizard />);

      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeDisabled();

      // Answer the question
      const yesOption = screen.getByRole('radio', { name: 'Yes' });
      fireEvent.click(yesOption);

      await waitFor(() => {
        expect(nextButton).toBeEnabled();
      });
    });

    it('should call nextQuestion when next button is clicked', async () => {
      render(<AssessmentWizard />);

      // Answer the question first
      const yesOption = screen.getByRole('radio', { name: 'Yes' });
      fireEvent.click(yesOption);

      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      expect(mockAssessmentStore.nextQuestion).toHaveBeenCalled();
    });

    it('should call previousQuestion when previous button is clicked', () => {
      mockAssessmentStore.currentQuestion = 1;

      render(<AssessmentWizard />);

      const previousButton = screen.getByRole('button', { name: /previous/i });
      fireEvent.click(previousButton);

      expect(mockAssessmentStore.previousQuestion).toHaveBeenCalled();
    });

    it('should show submit button on last question', () => {
      mockAssessmentStore.currentQuestion = 1; // Last question

      render(<AssessmentWizard />);

      expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /next/i })).not.toBeInTheDocument();
    });
  });

  describe('Answer Handling', () => {
    it('should call setAnswer when radio button is selected', () => {
      render(<AssessmentWizard />);

      const yesOption = screen.getByRole('radio', { name: 'Yes' });
      fireEvent.click(yesOption);

      expect(mockAssessmentStore.setAnswer).toHaveBeenCalledWith('1', 'yes');
    });

    it('should call setAnswer when checkbox is selected', () => {
      mockAssessmentStore.currentQuestion = 1;

      render(<AssessmentWizard />);

      const namesCheckbox = screen.getByRole('checkbox', { name: 'Names' });
      fireEvent.click(namesCheckbox);

      expect(mockAssessmentStore.setAnswer).toHaveBeenCalledWith('2', ['names']);
    });

    it('should handle multiple checkbox selections', () => {
      mockAssessmentStore.currentQuestion = 1;

      render(<AssessmentWizard />);

      const namesCheckbox = screen.getByRole('checkbox', { name: 'Names' });
      const emailsCheckbox = screen.getByRole('checkbox', { name: 'Email addresses' });

      fireEvent.click(namesCheckbox);
      fireEvent.click(emailsCheckbox);

      expect(mockAssessmentStore.setAnswer).toHaveBeenCalledWith('2', ['names']);
      expect(mockAssessmentStore.setAnswer).toHaveBeenCalledWith('2', ['names', 'emails']);
    });

    it('should preserve answers when navigating between questions', () => {
      mockAssessmentStore.answers = { '1': 'yes' };

      render(<AssessmentWizard />);

      const yesOption = screen.getByRole('radio', { name: 'Yes' });
      expect(yesOption).toBeChecked();
    });
  });

  describe('Validation', () => {
    it('should show validation error for required unanswered questions', async () => {
      render(<AssessmentWizard />);

      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Please select an answer')).toBeInTheDocument();
      });

      expect(mockAssessmentStore.nextQuestion).not.toHaveBeenCalled();
    });

    it('should clear validation error when question is answered', async () => {
      render(<AssessmentWizard />);

      // Try to proceed without answering
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Please select an answer')).toBeInTheDocument();
      });

      // Answer the question
      const yesOption = screen.getByRole('radio', { name: 'Yes' });
      fireEvent.click(yesOption);

      await waitFor(() => {
        expect(screen.queryByText('Please select an answer')).not.toBeInTheDocument();
      });
    });

    it('should validate multiple choice questions require at least one selection', async () => {
      mockAssessmentStore.currentQuestion = 1;

      render(<AssessmentWizard />);

      const submitButton = screen.getByRole('button', { name: /submit/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please select at least one option')).toBeInTheDocument();
      });
    });
  });

  describe('Submission', () => {
    it('should call submitAssessment when submit button is clicked', async () => {
      mockAssessmentStore.currentQuestion = 1;
      mockAssessmentStore.answers = { '2': ['names', 'emails'] };

      render(<AssessmentWizard />);

      const submitButton = screen.getByRole('button', { name: /submit/i });
      fireEvent.click(submitButton);

      expect(mockAssessmentStore.submitAssessment).toHaveBeenCalled();
    });

    it('should show loading state during submission', () => {
      mockAssessmentStore.currentQuestion = 1;
      mockAssessmentStore.isLoading = true;

      render(<AssessmentWizard />);

      const submitButton = screen.getByRole('button', { name: /submitting/i });
      expect(submitButton).toBeDisabled();
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('should redirect to results page after successful submission', async () => {
      mockAssessmentStore.currentQuestion = 1;
      mockAssessmentStore.answers = { '2': ['names'] };

      // Mock successful submission
      mockAssessmentStore.submitAssessment.mockResolvedValue({ id: 'assessment-123' });

      render(<AssessmentWizard />);

      const submitButton = screen.getByRole('button', { name: /submit/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/assessments/assessment-123/results');
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when there is an error', () => {
      mockAssessmentStore.error = 'Failed to load questions';

      render(<AssessmentWizard />);

      expect(screen.getByText('Failed to load questions')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    it('should call resetAssessment when retry button is clicked', () => {
      mockAssessmentStore.error = 'Failed to load questions';

      render(<AssessmentWizard />);

      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      expect(mockAssessmentStore.resetAssessment).toHaveBeenCalled();
    });

    it('should handle submission errors gracefully', async () => {
      mockAssessmentStore.currentQuestion = 1;
      mockAssessmentStore.answers = { '2': ['names'] };
      mockAssessmentStore.submitAssessment.mockRejectedValue(new Error('Submission failed'));

      render(<AssessmentWizard />);

      const submitButton = screen.getByRole('button', { name: /submit/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to submit assessment. Please try again.')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<AssessmentWizard />);

      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-label', 'Assessment progress');
      expect(screen.getByRole('group')).toHaveAttribute('aria-labelledby');
    });

    it('should support keyboard navigation', () => {
      render(<AssessmentWizard />);

      const yesOption = screen.getByRole('radio', { name: 'Yes' });
      const noOption = screen.getByRole('radio', { name: 'No' });

      // Tab navigation should work
      yesOption.focus();
      expect(document.activeElement).toBe(yesOption);

      // Arrow key navigation should work
      fireEvent.keyDown(yesOption, { key: 'ArrowDown' });
      expect(document.activeElement).toBe(noOption);
    });

    it('should announce question changes to screen readers', () => {
      render(<AssessmentWizard />);

      const questionElement = screen.getByRole('group');
      expect(questionElement).toHaveAttribute('aria-live', 'polite');
    });
  });
});
