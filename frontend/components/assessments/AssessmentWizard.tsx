'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Save, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { useState, useEffect, useCallback, useMemo, useRef } from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import {
  QuestionnaireEngine,
  type AssessmentFramework,
  type AssessmentContext,
  type AssessmentProgress,
  type AssessmentResult,
  type Question,
} from '@/lib/assessment-engine';

import { AIErrorBoundary } from './AIErrorBoundary';
import { AIGuidancePanel } from './AIGuidancePanel';
import { freemiumService } from '@/lib/api/freemium.service';
import { AssessmentNavigation } from './AssessmentNavigation';
import { FollowUpQuestion } from './FollowUpQuestion';
import { ProgressTracker } from './ProgressTracker';
import { QuestionRenderer } from './QuestionRenderer';

interface AssessmentWizardProps {
  framework: AssessmentFramework;
  assessmentId: string;
  businessProfileId: string;
  onComplete: (result: AssessmentResult) => void;
  onSave?: (progress: AssessmentProgress) => void;
  onExit?: () => void;
  enableIncrementalSubmissions?: boolean;  // Optional prop to enable/disable incremental answer submissions
}

export function AssessmentWizard({
  framework,
  assessmentId,
  businessProfileId,
  onComplete,
  onSave,
  onExit,
  enableIncrementalSubmissions = false,  // Default to false for freemium assessments
}: AssessmentWizardProps) {
  const { toast } = useToast();
  const [engine, setEngine] = useState<QuestionnaireEngine | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [progress, setProgress] = useState<AssessmentProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const loadingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Helper to manage AI loading state with minimum display time
  const setAILoadingState = useCallback((loading: boolean, minDisplayMs = 300) => {
    if (loadingTimeoutRef.current) {
      clearTimeout(loadingTimeoutRef.current);
      loadingTimeoutRef.current = null;
    }
    
    if (loading) {
      setIsLoadingAI(true);
    } else {
      // Ensure minimum display time to avoid flicker
      loadingTimeoutRef.current = setTimeout(() => {
        setIsLoadingAI(false);
        loadingTimeoutRef.current = null;
      }, minDisplayMs);
    }
  }, []);
  const [answersVersion, setAnswersVersion] = useState(0);

  // Initialize engine
  useEffect(() => {
    const context: AssessmentContext = {
      frameworkId: framework.id,
      assessmentId,
      businessProfileId,
      answers: new Map(),
      metadata: {},
    };

    const newEngine = new QuestionnaireEngine(framework, context, {
      autoSave: true,
      autoSaveInterval: 30,
      showProgress: true,
      enableNavigation: true,
      enableAI: true, // Enable AI follow-up questions
      useMockAIOnError: true, // Use mock questions if AI fails
      onProgress: (progress) => {
        setProgress(progress);
        if (onSave) {
          onSave(progress);
        }
      },
      onError: (error: Error) => {
        setError(error.message);
        toast({
          title: 'Error',
          description: error.message,
          variant: 'destructive',
        });
      },
    });

    // Try to load saved progress
    const hasProgress = newEngine.loadProgress();
    if (hasProgress) {
      toast({
        title: 'Progress Restored',
        description: 'Your previous progress has been loaded.',
      });
    }

    setEngine(newEngine);
    setCurrentQuestion(newEngine.getCurrentQuestion());
    setProgress(newEngine.getProgress());

    return () => {
      newEngine.destroy();
      // Clean up any pending progress submission
      if (progressSubmissionTimeout.current) {
        clearTimeout(progressSubmissionTimeout.current);
        progressSubmissionTimeout.current = null;
      }
      // Clean up loading timeout
      if (loadingTimeoutRef.current) {
        clearTimeout(loadingTimeoutRef.current);
        loadingTimeoutRef.current = null;
      }
    };
  }, [framework, assessmentId, businessProfileId, onSave, toast]);

  // Ref for debouncing progress submission
  const progressSubmissionTimeout = useRef<NodeJS.Timeout | null>(null);

  const handleAnswer = useCallback(
    async (value: any) => {
      if (!engine || !currentQuestion) return;

      setValidationError(null);
      engine.answerQuestion(currentQuestion.id, value);
      const newProgress = engine.getProgress();
      setProgress(newProgress);
      setAnswersVersion((prev) => prev + 1); // Force re-render to update button state
      
      // Debounce incremental progress submission (500ms delay)
      if (progressSubmissionTimeout.current) {
        clearTimeout(progressSubmissionTimeout.current);
        progressSubmissionTimeout.current = null;
      }
      
      progressSubmissionTimeout.current = setTimeout(async () => {
        try {
          // Guard against submitting File/Blob objects for file_upload questions
          let answerValue = value;
          if (currentQuestion.type === 'file_upload' && value) {
            // For file uploads, send metadata instead of actual File objects
            if (Array.isArray(value)) {
              answerValue = {
                value: 'file_placeholder',
                metadata: {
                  fileCount: value.length,
                  fileNames: value.map(f => f.name || 'unknown'),
                  fileSizes: value.map(f => f.size || 0),
                  fileTypes: value.map(f => f.type || 'unknown')
                }
              };
            } else if (value instanceof File) {
              answerValue = {
                value: 'file_placeholder',
                metadata: {
                  fileName: value.name || 'unknown',
                  fileSize: value.size || 0,
                  fileType: value.type || 'unknown'
                }
              };
            } else if (value instanceof Blob) {
              answerValue = {
                value: 'file_placeholder',
                metadata: {
                  fileName: 'unknown',
                  fileSize: value.size || 0,
                  fileType: value.type || 'unknown'
                }
              };
            }
          }
          
          // Submit answer to freemium API for incremental progress tracking
          // Only submit if incremental submissions are enabled
          if (enableIncrementalSubmissions) {
            await freemiumService.submitAnswer(assessmentId, {
              session_token: assessmentId,
              question_id: currentQuestion.id,
              answer: answerValue,
              // Include optional timing and confidence data if available
              // Note: Timing and confidence features not yet implemented in engine
              // ...(currentQuestion.metadata?.estimated_time && {
              //   time_spent_seconds: Math.floor((Date.now() - questionStartTime) / 1000)
              // }),
              // ...(engine.getAnswerConfidence?.(currentQuestion.id) && {
              //   confidence_level: engine.getAnswerConfidence(currentQuestion.id)
              // })
            });
          }
        } catch (error) {
          // Log error but don't interrupt user experience
          console.error('Failed to submit incremental progress:', error);
        }
      }, 500);
    },
    [engine, currentQuestion, assessmentId],
  );

  const handleNext = useCallback(async () => {
    if (!engine) return;

    // Clear any pending progress submission timer before proceeding
    if (progressSubmissionTimeout.current) {
      clearTimeout(progressSubmissionTimeout.current);
      progressSubmissionTimeout.current = null;
    }

    try {
      // Only set loading state when we're finishing the assessment (will generate AI recommendations)
      const progress = engine.getProgress();
      const isLastQuestion = progress.answeredQuestions === progress.totalQuestions - 1;
      const isInAIMode = engine.isInAIMode();
      
      // Only show loading for:
      // 1. Last question (will generate AI results)
      // 2. When exiting AI mode back to normal flow
      if (isLastQuestion && !isInAIMode) {
        setAILoadingState(true, 500); // Longer display for final results
      }
      
      const hasMore = await engine.nextQuestion();
      
      // Check if we just entered AI mode (after nextQuestion)
      const justEnteredAIMode = !isInAIMode && engine.isInAIMode();
      if (justEnteredAIMode) {
        // Show loading state briefly for AI transition
        setAILoadingState(true, 300);
        // Clear loading state after transition
        setAILoadingState(false, 300);
      }
      
      if (hasMore) {
        setCurrentQuestion(engine.getCurrentQuestion());
        setValidationError(null);
      } else {
        // Assessment complete - generate results with AI recommendations
        setAILoadingState(true, 1000); // Longer for final results generation
        const result = await engine.calculateResults();
        // Enrich result with answers array
        const enrichedResult = {
          ...result,
          answers: Array.from(engine.getAnswers().values())
        };
        onComplete(enrichedResult);
      }
    } catch (error) {
      // Handle validation errors
      setValidationError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      // Only clear loading if we're not completing the assessment
      if (engine.getCurrentQuestion()) {
        setAILoadingState(false, 300);
      }
    }
  }, [engine, onComplete]);

  const handlePrevious = useCallback(() => {
    if (!engine) return;

    const hasPrevious = engine.previousQuestion();
    if (hasPrevious) {
      setCurrentQuestion(engine.getCurrentQuestion());
      setValidationError(null);
    }
  }, [engine]);

  const handleSaveProgress = useCallback(async () => {
    if (!engine || !progress) return;

    setIsSaving(true);
    try {
      // Save progress using freemiumService
      await freemiumService.saveProgress(assessmentId, progress);

      // Also call the onSave callback if provided
      if (onSave) {
        onSave(progress);
      }

      toast({
        title: 'Progress Saved',
        description: 'Your assessment progress has been saved.',
      });
    } catch (error) {
      console.error('Failed to save assessment progress:', error);
      toast({
        title: 'Save Failed',
        description: error instanceof Error ? error.message : 'Failed to save progress. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  }, [engine, progress, toast, assessmentId, onSave]);

  const handleJumpToSection = useCallback(
    (sectionIndex: number) => {
      if (!engine) return;

      const success = engine.jumpToSection(sectionIndex);
      if (success) {
        setCurrentQuestion(engine.getCurrentQuestion());
        setValidationError(null);
      }
    },
    [engine],
  );

  // Check if current question is answered (using answersVersion to trigger re-evaluation)
  // This hook must be called before any conditional returns
  const currentAnswer = useMemo(() => {
    return currentQuestion && engine ? engine.getAnswers().get(currentQuestion.id)?.value : null;
  }, [currentQuestion, engine, answersVersion]);

  if (!engine || !progress) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-t-2 border-primary"></div>
          <p className="text-muted-foreground">Loading assessment...</p>
        </div>
      </div>
    );
  }

  const currentSection = engine.getCurrentSection();
  const isLastQuestion = progress.answeredQuestions === progress.totalQuestions - 1;
  const isInAIMode = engine?.isInAIMode() || false;
  const currentAIQuestion = engine?.getCurrentAIQuestion();

  const isCurrentQuestionAnswered =
    currentAnswer !== null && currentAnswer !== undefined && currentAnswer !== '';

  // For checkbox questions, check if at least one option is selected
  const isCheckboxAnswered =
    currentQuestion?.type === 'checkbox' &&
    Array.isArray(currentAnswer) &&
    currentAnswer.length > 0;
  const isQuestionAnswered =
    currentQuestion?.type === 'checkbox' ? isCheckboxAnswered : isCurrentQuestionAnswered;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{framework.name}</h1>
          <p className="text-muted-foreground">{framework.description}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleSaveProgress} disabled={isSaving}>
            {isSaving ? (
              <>
                <Clock className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Progress
              </>
            )}
          </Button>
          {onExit && (
            <Button variant="ghost" size="sm" onClick={onExit}>
              Exit
            </Button>
          )}
        </div>
      </div>

      {/* Progress Overview */}
      <ProgressTracker
        progress={progress}
        framework={framework}
        onSectionClick={handleJumpToSection}
      />

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Assessment Card */}
      <Card className="shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{currentSection?.title}</CardTitle>
              <CardDescription>{currentSection?.description}</CardDescription>
            </div>
            <div className="text-sm text-muted-foreground">
              Question {progress.answeredQuestions + 1} of {progress.totalQuestions}
            </div>
          </div>
          <Progress value={progress.percentComplete} className="mt-4" />
        </CardHeader>

        <CardContent>
          <AnimatePresence mode="wait">
            {isLoadingAI && (
              <motion.div
                key="loading-ai"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-12"
              >
                <div className="animate-pulse space-y-4 text-center">
                  <div className="mx-auto h-12 w-12 animate-pulse rounded-full bg-primary/20" />
                  <p className="text-sm text-muted-foreground">
                    AI is analyzing your response and generating follow-up questions...
                  </p>
                </div>
              </motion.div>
            )}

            {!isLoadingAI && currentQuestion && (
              <motion.div
                key={currentQuestion.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {isInAIMode && currentAIQuestion ? (
                  <AIErrorBoundary>
                    <FollowUpQuestion
                      question={currentAIQuestion}
                      value={engine.getAnswers().get(currentAIQuestion.id)?.value}
                      onChange={handleAnswer}
                      error={validationError}
                      frameworkId={framework.id}
                      {...(currentSection?.id && { sectionId: currentSection.id })}
                      userContext={{
                        ...(businessProfileId && { business_profile: { id: businessProfileId } }),
                        current_answers: Object.fromEntries(
                          Array.from(engine.getAnswers().entries()).map(([qid, ans]) => [qid, ans?.value ?? null])
                        ),
                        assessment_progress: progress,
                      }}
                      reasoning={currentAIQuestion.metadata?.['reasoning'] as string}
                    />
                  </AIErrorBoundary>
                ) : (
                  <>
                    <QuestionRenderer
                      question={currentQuestion}
                      value={engine.getAnswers().get(currentQuestion.id)?.value}
                      onChange={handleAnswer}
                      error={validationError}
                      frameworkId={framework.id}
                      {...(currentSection?.id && { sectionId: currentSection.id })}
                      userContext={{
                        ...(businessProfileId && { business_profile: { id: businessProfileId } }),
                        current_answers: Object.fromEntries(
                          Array.from(engine.getAnswers().entries()).map(([qid, ans]) => [qid, ans?.value ?? null])
                        ),
                        assessment_progress: progress,
                      }}
                    />

                    {/* AI Guidance Panel - collapsed by default */}
                    <div className="mt-4">
                      <AIGuidancePanel
                        question={currentQuestion}
                        frameworkId={framework.id}
                        sectionId={currentSection?.id || ''}
                        userContext={{
                          ...(businessProfileId && { business_profile: { id: businessProfileId } }),
                          current_answers: Object.fromEntries(
                          Array.from(engine.getAnswers().entries()).map(([qid, ans]) => [qid, ans?.value ?? null])
                        ),
                          assessment_progress: progress,
                        }}
                      />
                    </div>
                  </>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation */}
          <div className="mt-8 flex items-center justify-between">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={isLoadingAI || (progress.answeredQuestions === 0 && !isInAIMode)}
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>

            <div className="flex items-center gap-2">
              {/* AI Mode Indicator */}
              {isInAIMode && (
                <div className="rounded bg-primary/10 px-2 py-1 text-xs text-muted-foreground">
                  AI Follow-up {engine?.getAIQuestionProgress()?.current || 1} of{' '}
                  {engine?.getAIQuestionProgress()?.total || 1}
                </div>
              )}

              {currentQuestion?.validation?.required === false && !isInAIMode && (
                <Button variant="ghost" onClick={handleNext}>
                  Skip
                </Button>
              )}

              {/* AI questions can always be skipped */}
              {isInAIMode && (
                <Button variant="ghost" onClick={handleNext}>
                  Skip AI Question
                </Button>
              )}

              <Button
                onClick={handleNext}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
                disabled={
                  isLoadingAI ||
                  (!isQuestionAnswered && currentQuestion?.validation?.required !== false)
                }
              >
                {isInAIMode ? (
                  engine?.hasAIQuestionsRemaining() ? (
                    <>
                      Next AI Question
                      <ChevronRight className="ml-2 h-4 w-4" />
                    </>
                  ) : (
                    <>
                      Continue Assessment
                      <ChevronRight className="ml-2 h-4 w-4" />
                    </>
                  )
                ) : isLastQuestion ? (
                  <>
                    Complete Assessment
                    <CheckCircle className="ml-2 h-4 w-4" />
                  </>
                ) : (
                  <>
                    Next
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section Navigation */}
      <AssessmentNavigation
        framework={framework}
        currentSectionIndex={framework.sections.findIndex((s) => s.id === currentSection?.id)}
        progress={progress}
        onSectionClick={handleJumpToSection}
      />
    </div>
  );
}
