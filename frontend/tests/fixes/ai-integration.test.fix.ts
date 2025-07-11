// Fix for the AI integration test - the issue is that answerQuestion doesn't trigger AI follow-up
// The AI follow-up is triggered when calling nextQuestion()

// Original failing test:
it('should fallback to mock questions when AI service fails', async () => {
  // Mock AI service failure
  vi.mocked(assessmentAIService.getFollowUpQuestions).mockRejectedValue(
    new Error('AI service unavailable')
  );

  engine = new QuestionnaireEngine(mockFramework, mockContext, {
    enableAI: true,
    useMockAIOnError: true
  });

  engine.answerQuestion('q1', 'no');
  
  const hasMore = await engine.nextQuestion();
  
  expect(hasMore).toBe(true);
  expect(engine.isInAIMode()).toBe(true);
  
  // Should have mock questions
  const currentQuestion = engine.getCurrentAIQuestion();
  expect(currentQuestion).toBeTruthy();
  expect(currentQuestion?.metadata?.isAIGenerated).toBe(true);
});

// The fix:
// The test needs to ensure that the mock framework has the right structure
// and that the answer 'no' will trigger AI follow-up based on shouldTriggerAIFollowUp logic