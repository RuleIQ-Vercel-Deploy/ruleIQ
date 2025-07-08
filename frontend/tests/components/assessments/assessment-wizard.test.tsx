import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AssessmentWizard } from '@/components/assessments/AssessmentWizard'
import type { AssessmentFramework } from '@/lib/assessment-engine'

// Mock dependencies
vi.mock('@/components/assessments/AIErrorBoundary', () => ({
  AIErrorBoundary: ({ children }: any) => <div data-testid="ai-error-boundary">{children}</div>,
}))

vi.mock('@/components/assessments/AssessmentNavigation', () => ({
  AssessmentNavigation: (props: any) => (
    <div data-testid="assessment-navigation">
      <button onClick={() => props.onPrevious()}>Previous</button>
      <button onClick={() => props.onNext()}>Next</button>
    </div>
  ),
}))

vi.mock('@/components/assessments/QuestionRenderer', () => ({
  QuestionRenderer: (props: any) => (
    <div data-testid="question-renderer">
      <input
        type="text"
        onChange={(e) => props.onAnswer(e.target.value)}
        data-testid="question-input"
      />
    </div>
  ),
}))

vi.mock('@/components/assessments/ProgressTracker', () => ({
  ProgressTracker: (props: any) => (
    <div data-testid="progress-tracker">Progress: {props.currentStep}/{props.totalSteps}</div>
  ),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}))

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
          text: 'Do you maintain records of processing activities?',
          options: [
            { value: 'yes', label: 'Yes' },
            { value: 'no', label: 'No' },
          ],
          validation: { required: true },
          weight: 1,
        },
        {
          id: 'q2',
          type: 'textarea',
          text: 'Describe your data retention policies',
          validation: { required: true, minLength: 10 },
          weight: 1,
        },
      ],
    },
  ],
}

describe('AssessmentWizard', () => {
  const mockProps = {
    framework: mockFramework,
    assessmentId: 'test-assessment-id',
    businessProfileId: 'test-profile-id',
    onComplete: vi.fn(),
    onSave: vi.fn(),
    onExit: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render assessment wizard with framework details', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    expect(screen.getByText('GDPR Compliance Assessment')).toBeInTheDocument()
    expect(screen.getByText('Test assessment framework')).toBeInTheDocument()
  })

  it('should display progress tracker', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    expect(screen.getByTestId('progress-tracker')).toBeInTheDocument()
  })

  it('should show current question', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    expect(screen.getByText('Do you maintain records of processing activities?')).toBeInTheDocument()
    expect(screen.getByTestId('question-renderer')).toBeInTheDocument()
  })

  it('should handle navigation between questions', async () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Answer current question
    const input = screen.getByTestId('question-input')
    fireEvent.change(input, { target: { value: 'yes' } })
    
    // Navigate to next question
    const nextButton = screen.getByText('Next')
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      expect(screen.getByText('Describe your data retention policies')).toBeInTheDocument()
    })
  })

  it('should save progress when onSave is provided', async () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Answer a question
    const input = screen.getByTestId('question-input')
    fireEvent.change(input, { target: { value: 'yes' } })
    
    await waitFor(() => {
      expect(mockProps.onSave).toHaveBeenCalled()
    })
  })

  it('should validate required questions', async () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Try to navigate without answering required question
    const nextButton = screen.getByText('Next')
    fireEvent.click(nextButton)
    
    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/required/i)).toBeInTheDocument()
    })
  })

  it('should complete assessment when all questions answered', async () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Answer first question
    let input = screen.getByTestId('question-input')
    fireEvent.change(input, { target: { value: 'yes' } })
    
    // Navigate to next question
    let nextButton = screen.getByText('Next')
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      input = screen.getByTestId('question-input')
    })
    
    // Answer second question
    fireEvent.change(input, { target: { value: 'We have comprehensive data retention policies.' } })
    
    // Complete assessment
    nextButton = screen.getByText('Next')
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      expect(mockProps.onComplete).toHaveBeenCalled()
    })
  })

  it('should handle exit functionality', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Find and click exit button (would be in actual component)
    const exitButton = screen.getByRole('button', { name: /exit|close/i })
    fireEvent.click(exitButton)
    
    expect(mockProps.onExit).toHaveBeenCalled()
  })

  it('should display estimated duration', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    expect(screen.getByText(/30/)).toBeInTheDocument() // Estimated duration
  })

  it('should wrap content in AI error boundary', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    expect(screen.getByTestId('ai-error-boundary')).toBeInTheDocument()
  })

  it('should handle framework with no sections gracefully', () => {
    const emptyFramework = { ...mockFramework, sections: [] }
    
    render(<AssessmentWizard {...mockProps} framework={emptyFramework} />)
    
    expect(screen.getByText('GDPR Compliance Assessment')).toBeInTheDocument()
    // Should show completion or error state
  })

  it('should calculate progress correctly', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Should show progress as 1 out of total questions
    expect(screen.getByText(/Progress: 1\//)).toBeInTheDocument()
  })

  it('should be accessible', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Check for proper headings
    expect(screen.getByRole('heading')).toBeInTheDocument()
    
    // Check for proper form controls
    expect(screen.getByTestId('question-input')).toBeInTheDocument()
    
    // Check for navigation buttons
    expect(screen.getByRole('button', { name: /previous/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument()
  })
})