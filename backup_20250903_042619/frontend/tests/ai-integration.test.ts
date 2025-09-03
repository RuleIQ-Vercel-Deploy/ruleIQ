/**
 * AI Integration Test - Testing the AI follow-up question implementation
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { assessmentAIService } from '@/lib/api/assessments-ai.service';
import { QuestionnaireEngine } from '@/lib/assessment-engine/QuestionnaireEngine';
import {
  type AssessmentFramework,
  type AssessmentContext,
  type Question,
} from '@/lib/assessment-engine/types';

// Mock the AI service
vi.mock('@/lib/api/assessments-ai.service', () => ({
  assessmentAIService: {
    getFollowUpQuestions: vi.fn(),
    getPersonalizedRecommendations: vi.fn(),
    getQuestionHelp: vi.fn(),
  },
}));

describe('AI Integration Tests', () => {
  let mockFramework: AssessmentFramework;
  let mockContext: AssessmentContext;
  let engine: QuestionnaireEngine;

  beforeEach(() => {
    vi.clearAllMocks();
    // Clear localStorage before each test
    localStorage.clear();

    mockFramework = {
      id: 'test-framework',
      name: 'Test Framework',
      description: 'Test description',
      version: '1.0',
      categories: [],
      sections: [
        {
          id: 'section-1',
          title: 'Test Section',
          description: 'Test section description',
          weight: 1,
          questions: [
            {
              id: 'q1',
              text: 'Test question',
              type: 'radio',
              options: [
                { value: 'yes', label: 'Yes' },
                { value: 'no', label: 'No' },
              ],
              validation: { required: true },
            },
          ],
        },
      ],
    };

    mockContext = {
      frameworkId: 'test-framework',
      assessmentId: 'test-assessment',
      businessProfileId: 'test-profile',
      answers: new Map(),
      metadata: {},
    };
  });

  describe('AI Follow-up Questions', () => {
    it('should generate AI follow-up questions after answering priority questions', async () => {
      // Mock successful AI response
      const mockAIQuestions: Question[] = [
        {
          id: 'ai-q1',
          text: 'Can you provide more details about your data processing activities?',
          type: 'textarea',
          validation: { required: false },
          metadata: {
            source: 'ai',
            reasoning: 'Based on your previous answer, we need more details',
          },
        },
      ];

      vi.mocked(assessmentAIService.getFollowUpQuestions).mockResolvedValue({
        follow_up_questions: mockAIQuestions,
        reasoning: 'Follow-up needed for compliance assessment',
      });

      engine = new QuestionnaireEngine(mockFramework, mockContext, {
        enableAI: true,
        useMockAIOnError: true,
      });

      // Answer a question that should trigger AI follow-up (using 'no' to trigger)
      engine.answerQuestion('q1', 'no');

      // Navigate to next question (should trigger AI)
      const hasMore = await engine.nextQuestion();

      expect(hasMore).toBe(true);
      expect(engine.isInAIMode()).toBe(true);
      expect(assessmentAIService.getFollowUpQuestions).toHaveBeenCalledWith({
        question_id: 'q1',
        question_text: 'Test question',
        user_answer: 'no',
        assessment_context: expect.objectContaining({
          framework_id: 'test-framework',
          section_id: 'section-1',
          business_profile_id: 'test-profile',
          current_answers: expect.objectContaining({
            q1: expect.objectContaining({
              value: 'no',
              source: 'framework',
            }),
          }),
        }),
      });
    });

    it('should fallback to mock questions when AI service fails', async () => {
      // Mock AI service failure
      vi.mocked(assessmentAIService.getFollowUpQuestions).mockRejectedValue(
        new Error('AI service unavailable'),
      );

      engine = new QuestionnaireEngine(mockFramework, mockContext, {
        enableAI: true,
        useMockAIOnError: true,
      });

      // Answer the question - this triggers shouldTriggerAIFollowUp check
      engine.answerQuestion('q1', 'no');

      // nextQuestion will trigger AI follow-up generation
      const hasMore = await engine.nextQuestion();

      // Wait a tick for the async operations to complete
      await new Promise((resolve) => setTimeout(resolve, 0));

      expect(hasMore).toBe(true);
      expect(engine.isInAIMode()).toBe(true);

      // Should have mock questions
      const currentQuestion = engine.getCurrentAIQuestion();
      expect(currentQuestion).toBeTruthy();
      expect(currentQuestion?.metadata?.['isAIGenerated']).toBe(true);
    });

    it('should handle AI timeout scenarios', { timeout: 15000 }, async () => {
      // Mock slow AI response
      vi.mocked(assessmentAIService.getFollowUpQuestions).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 15000)), // 15 seconds
      );

      engine = new QuestionnaireEngine(mockFramework, mockContext, {
        enableAI: true,
        useMockAIOnError: true,
      });

      engine.answerQuestion('q1', 'no');

      const start = Date.now();
      const hasMore = await engine.nextQuestion();
      const duration = Date.now() - start;

      // Should timeout after ~10 seconds and fallback to mock
      expect(duration).toBeLessThan(12000);
      expect(hasMore).toBe(true);
      expect(engine.isInAIMode()).toBe(true);

      const currentQuestion = engine.getCurrentAIQuestion();
      expect(currentQuestion?.metadata?.['isAIGenerated']).toBe(true);
    });

    it('should navigate through AI questions correctly', async () => {
      // Add a second question to the framework so assessment can continue after AI
      mockFramework.sections[0].questions.push({
        id: 'q2',
        text: 'Second regular question',
        type: 'radio',
        options: [
          { value: 'yes', label: 'Yes' },
          { value: 'no', label: 'No' },
        ],
        validation: { required: true },
      });

      const mockAIQuestions: Question[] = [
        {
          id: 'ai-q1',
          text: 'First AI question',
          type: 'text',
          validation: { required: false },
        },
        {
          id: 'ai-q2',
          text: 'Second AI question',
          type: 'textarea',
          validation: { required: false },
        },
      ];

      vi.mocked(assessmentAIService.getFollowUpQuestions).mockResolvedValue({
        follow_up_questions: mockAIQuestions,
        reasoning: 'Multiple follow-ups needed',
      });

      engine = new QuestionnaireEngine(mockFramework, mockContext, {
        enableAI: true,
        useMockAIOnError: false, // Don't use mock on error - use mocked service
      });

      engine.answerQuestion('q1', 'no');

      // Enter AI mode
      await engine.nextQuestion();
      expect(engine.isInAIMode()).toBe(true);

      const firstAIQuestion = engine.getCurrentAIQuestion();
      expect(firstAIQuestion).toBeTruthy();
      expect(firstAIQuestion?.id).toBe('ai-q1'); // Should match our mock

      // Answer first AI question and move to second
      engine.answerQuestion('ai-q1', 'First answer');
      await engine.nextQuestion();

      const secondAIQuestion = engine.getCurrentAIQuestion();
      expect(secondAIQuestion).toBeTruthy();
      expect(secondAIQuestion?.id).toBe('ai-q2'); // Should match our mock

      // Answer second AI question and continue assessment
      engine.answerQuestion('ai-q2', 'Second answer');
      await engine.nextQuestion();

      // Check if we can continue with the assessment
      // AI mode might still be active if there are more potential follow-ups
      const hasMoreQuestions = engine.isInAIMode() || engine.getCurrentQuestion() !== null;
      expect(hasMoreQuestions).toBe(true);

      // The important thing is that we can navigate through AI questions successfully
    });
  });

  describe('State Persistence with AI Features', () => {
    it('should persist AI questions and answers', () => {
      engine = new QuestionnaireEngine(mockFramework, mockContext, {
        enableAI: true,
        autoSave: true,
      });

      // Answer regular question
      engine.answerQuestion('q1', 'no');

      // Simulate AI question answer
      engine.answerQuestion('ai-q1', 'AI answer');

      const answers = engine.getAnswers();
      expect(answers.get('q1')?.value).toBe('no');
      expect(answers.get('ai-q1')?.value).toBe('AI answer');

      // Test progress persistence
      const progress = engine.getProgress();
      expect(progress.answeredQuestions).toBeGreaterThan(0);
    });

    it('should restore AI state from saved progress', () => {
      // Create engine with some progress
      const firstEngine = new QuestionnaireEngine(mockFramework, mockContext, {
        enableAI: true,
        autoSave: true,
      });

      firstEngine.answerQuestion('q1', 'no');
      firstEngine.answerQuestion('ai-q1', 'AI answer');

      // Force save progress before creating new engine
      firstEngine.destroy(); // This calls saveProgress

      // Create new engine and load progress
      const secondEngine = new QuestionnaireEngine(mockFramework, mockContext, {
        enableAI: true,
        autoSave: true,
      });

      const hasProgress = secondEngine.loadProgress();
      expect(hasProgress).toBe(true);

      const answers = secondEngine.getAnswers();
      expect(answers.get('q1')?.value).toBe('no');
      expect(answers.get('ai-q1')?.value).toBe('AI answer');

      // Cleanup
      secondEngine.destroy();
    });
  });

  describe('AI Recommendations Generation', () => {
    it('should generate AI recommendations in final results', async () => {
      const mockRecommendations = [
        {
          id: 'rec-1',
          title: 'Implement Data Protection Policy',
          description: 'Based on your assessment, you need a comprehensive data protection policy.',
          priority: 'high' as const,
          category: 'Data Protection',
          estimatedEffort: 'Medium',
          timeline: '2-4 weeks',
        },
      ];

      vi.mocked(assessmentAIService.getPersonalizedRecommendations).mockResolvedValue({
        recommendations: mockRecommendations,
        implementation_plan: {
          phases: [],
          total_timeline_weeks: 8,
          resource_requirements: [],
        },
        success_metrics: [],
      });

      engine = new QuestionnaireEngine(mockFramework, mockContext, {
        enableAI: true,
      });

      // Complete assessment
      engine.answerQuestion('q1', 'no');
      await engine.nextQuestion(); // This should complete the assessment

      const results = await engine.calculateResults();

      expect(results.recommendations).toHaveLength(1);
      expect(results.recommendations[0].title).toBe('Implement Data Protection Policy');
      expect(assessmentAIService.getPersonalizedRecommendations).toHaveBeenCalled();
    });
  });

  afterEach(() => {
    if (engine) {
      engine.destroy();
    }
  });
});
