import { vi } from 'vitest';

// Comprehensive AI service mock
export const mockAIService = {
  generateFollowUpQuestions: vi.fn().mockResolvedValue([
    'What is your data retention policy?',
    'How do you handle data breaches?',
    'Do you have employee training programs?'
  ]),
  
  getEnhancedResponse: vi.fn().mockResolvedValue({
    response: 'This is a mock AI response',
    confidence: 0.85,
    suggestions: ['Consider implementing automated data deletion']
  }),
  
  analyzeCompliance: vi.fn().mockResolvedValue({
    score: 85,
    recommendations: ['Improve data retention policies'],
    risks: ['Missing employee training records']
  }),
  
  // Add timeout handling
  generateFollowUpQuestionsWithTimeout: vi.fn().mockImplementation(async (timeout = 5000) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          'What is your data retention policy?',
          'How do you handle data breaches?',
          'Do you have employee training programs?'
        ]);
      }, 100); // Quick response to avoid timeouts
    });
  })
};

// Mock the AI service module
vi.mock('@/lib/services/ai-service', () => ({
  AIService: mockAIService,
  default: mockAIService
}));

// Mock AI-related utilities
vi.mock('@/lib/assessment-engine/QuestionnaireEngine', () => ({
  QuestionnaireEngine: {
    generateAIFollowUpQuestions: mockAIService.generateFollowUpQuestions,
    getEnhancedAIResponse: mockAIService.getEnhancedResponse
  }
}));
