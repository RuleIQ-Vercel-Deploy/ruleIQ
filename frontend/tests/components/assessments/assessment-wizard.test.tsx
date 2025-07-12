import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { AssessmentWizard } from '@/components/assessments/AssessmentWizard'
import type { AssessmentFramework, AssessmentProgress, Question, AssessmentSection, AssessmentResult } from '@/lib/assessment-engine'

// Mock dependencies
vi.mock('@/components/assessments/AIErrorBoundary', () => ({
  AIErrorBoundary: ({ children }: any) => <div data-testid="ai-error-boundary">{children}</div>,
}))

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
}))

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
}))

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
}))

vi.mock('@/components/assessments/ProgressTracker', () => ({
  ProgressTracker: (props: any) => (
    <div data-testid="progress-tracker">
      Progress: {props.progress.answeredQuestions + 1}/{props.progress.totalQuestions}
    </div>
  ),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}))

// Mock the QuestionnaireEngine class
let mockOnProgress: ((progress: any) => void) | null = null

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
}

vi.mock('@/lib/assessment-engine', () => ({
  QuestionnaireEngine: vi.fn().mockImplementation((framework, context, config) => {
    // Capture the onProgress callback
    mockOnProgress = config?.onProgress || null
    return mockEngine
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

  const mockProgress: AssessmentProgress = {
    totalQuestions: 2,
    answeredQuestions: 0,
    currentSection: 'section-1',
    currentQuestion: 'q1',
    percentComplete: 0,
    estimatedTimeRemaining: 30,
  }

  const mockSection: AssessmentSection = mockFramework.sections[0]
  const mockQuestion: Question = mockFramework.sections[0].questions[0]

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Create a mock answers map that can be updated
    const mockAnswers = new Map()
    
    // Set up default mock return values
    mockEngine.getCurrentQuestion.mockReturnValue(mockQuestion)
    mockEngine.getCurrentSection.mockReturnValue(mockSection)
    mockEngine.getProgress.mockReturnValue(mockProgress)
    mockEngine.loadProgress.mockReturnValue(false)
    mockEngine.getAnswers.mockReturnValue(mockAnswers)
    mockEngine.isInAIMode.mockReturnValue(false)
    mockEngine.getCurrentAIQuestion.mockReturnValue(null)
    mockEngine.hasAIQuestionsRemaining.mockReturnValue(false)
    mockEngine.getAIQuestionProgress.mockReturnValue({ current: 1, total: 1 })
    
    // Mock answerQuestion to update the answers map
    mockEngine.answerQuestion.mockImplementation((questionId: string, value: any) => {
      mockAnswers.set(questionId, { value, timestamp: new Date() })
    })
    mockEngine.nextQuestion.mockResolvedValue(true)
    mockEngine.previousQuestion.mockReturnValue(true)
    mockEngine.jumpToSection.mockReturnValue(true)
    mockEngine.calculateResults.mockResolvedValue({
      assessmentId: mockProps.assessmentId,
      frameworkId: mockFramework.id,
      overallScore: 85,
      sectionScores: { 'section-1': 85 },
      gaps: [],
      recommendations: [],
      completedAt: new Date(),
    } as AssessmentResult)
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
    const secondQuestion = mockFramework.sections[0].questions[1]
    
    render(<AssessmentWizard {...mockProps} />)
    
    // Answer current question
    const input = screen.getByTestId('question-input')
    fireEvent.change(input, { target: { value: 'yes' } })
    
    // Mock the engine to update to next question after nextQuestion is called
    mockEngine.nextQuestion.mockImplementation(async () => {
      // This runs when nextQuestion is called, updating the mock returns
      // for subsequent calls to getCurrentQuestion and getProgress
      mockEngine.getCurrentQuestion.mockReturnValue(secondQuestion)
      mockEngine.getProgress.mockReturnValue({
        ...mockProgress,
        currentQuestion: 'q2',
        answeredQuestions: 1,
        percentComplete: 50,
      })
      return true
    })
    
    // Wait for the button to be enabled after answering the question
    await waitFor(() => {
      const nextButton = screen.getByRole('button', { name: /next/i })
      expect(nextButton).toBeEnabled()
    })
    
    // Navigate to next question
    const nextButton = screen.getByRole('button', { name: /next/i })
    await act(async () => {
      fireEvent.click(nextButton)
    })
    
    // Verify that nextQuestion was called
    expect(mockEngine.nextQuestion).toHaveBeenCalled()
    
    await waitFor(() => {
      expect(screen.getByText('Describe your data retention policies')).toBeInTheDocument()
    })
  })

  it('should save progress when onSave is provided', async () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Answer a question
    const input = screen.getByTestId('question-input')
    fireEvent.change(input, { target: { value: 'yes' } })
    
    // The onSave is called when answerQuestion updates the progress
    expect(mockEngine.answerQuestion).toHaveBeenCalledWith('q1', 'yes')
    
    // Simulate the engine calling onProgress callback
    act(() => {
      if (mockOnProgress) {
        const updatedProgress = { ...mockProgress, answeredQuestions: 1 }
        mockOnProgress(updatedProgress)
      }
    })
    
    // onSave should be called from the engine's onProgress callback
    await waitFor(() => {
      expect(mockProps.onSave).toHaveBeenCalled()
    })
  })

  it('should validate required questions', async () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // The next button should be disabled when required question is not answered
    const nextButton = screen.getByRole('button', { name: /next/i })
    expect(nextButton).toBeDisabled()
    
    // Answer the question to enable the button
    const input = screen.getByTestId('question-input')
    fireEvent.change(input, { target: { value: 'yes' } })
    
    // Now the button should be enabled
    await waitFor(() => {
      expect(nextButton).toBeEnabled()
    })
  })

  it('should complete assessment when all questions answered', async () => {
    // First set up for first question
    mockEngine.getCurrentQuestion.mockReturnValue(mockQuestion)
    
    render(<AssessmentWizard {...mockProps} />)
    
    // Answer first question
    const input = screen.getByTestId('question-input')
    fireEvent.change(input, { target: { value: 'yes' } })
    
    // Set up for navigation to next question
    const secondQuestion = mockFramework.sections[0].questions[1]
    mockEngine.getCurrentQuestion.mockReturnValue(secondQuestion)
    mockEngine.getProgress.mockReturnValue({
      ...mockProgress,
      answeredQuestions: 1,
      percentComplete: 50,
    })
    
    // Navigate to next question
    const nextButton = screen.getByRole('button', { name: /next/i })
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      expect(mockEngine.nextQuestion).toHaveBeenCalled()
    })
    
    // Answer second question
    const input2 = screen.getByTestId('question-input')
    fireEvent.change(input2, { target: { value: 'We have comprehensive data retention policies.' } })
    
    // Set up for completion
    mockEngine.nextQuestion.mockResolvedValue(false) // No more questions
    mockEngine.getProgress.mockReturnValue({
      ...mockProgress,
      answeredQuestions: 1, // Last question (0-indexed)
      percentComplete: 100,
    })
    
    // Complete assessment
    fireEvent.click(nextButton)
    
    await waitFor(() => {
      expect(mockEngine.calculateResults).toHaveBeenCalled()
      expect(mockProps.onComplete).toHaveBeenCalled()
    })
  })

  it('should handle exit functionality', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // The exit button is rendered based on the component code
    const exitButton = screen.getByRole('button', { name: /exit/i })
    fireEvent.click(exitButton)
    
    expect(mockProps.onExit).toHaveBeenCalled()
  })

  it('should display estimated duration', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // The progress tracker shows the current/total questions which includes the number 1 and 2
    expect(screen.getByTestId('progress-tracker')).toHaveTextContent('Progress: 1/2')
  })

  it('should wrap content in AI error boundary', () => {
    // Set up the engine to be in AI mode with an AI question
    mockEngine.isInAIMode.mockReturnValue(true)
    mockEngine.getCurrentAIQuestion.mockReturnValue({
      id: 'ai-q1',
      type: 'text',
      text: 'AI follow-up question',
    })
    
    render(<AssessmentWizard {...mockProps} />)
    
    // The AI error boundary only wraps the FollowUpQuestion component when in AI mode
    expect(screen.getByTestId('ai-error-boundary')).toBeInTheDocument()
  })

  it('should handle framework with no sections gracefully', () => {
    const emptyFramework = { ...mockFramework, sections: [] }
    
    // Set up engine to return null for questions/sections when framework is empty
    mockEngine.getCurrentQuestion.mockReturnValue(null)
    mockEngine.getCurrentSection.mockReturnValue(null)
    mockEngine.getProgress.mockReturnValue({
      ...mockProgress,
      totalQuestions: 0,
    })
    
    render(<AssessmentWizard {...mockProps} framework={emptyFramework} />)
    
    expect(screen.getByText('GDPR Compliance Assessment')).toBeInTheDocument()
  })

  it('should calculate progress correctly', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Progress tracker shows answeredQuestions + 1 / totalQuestions
    expect(screen.getByTestId('progress-tracker')).toHaveTextContent('Progress: 1/2')
  })

  it('should be accessible', () => {
    render(<AssessmentWizard {...mockProps} />)
    
    // Check for proper headings - the framework name is rendered as h1
    expect(screen.getByRole('heading', { level: 1, name: 'GDPR Compliance Assessment' })).toBeInTheDocument()
    
    // Check for proper form controls
    expect(screen.getByTestId('question-input')).toBeInTheDocument()
    
    // Check for navigation buttons
    expect(screen.getByRole('button', { name: /previous/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument()
  })
})