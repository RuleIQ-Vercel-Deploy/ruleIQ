'use client';

import { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Slider } from '../ui/slider';
import {
  Loader2,
  ArrowRight,
  } from 'lucide-react';
import { freemiumService } from '../../lib/api/freemium.service';

// Mock question structure for now
interface AssessmentQuestion {
  question_id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'text' | 'yes_no' | 'scale';
  answer_options?: string[];
}

interface FreemiumAssessmentFlowProps {
  token?: string;
  className?: string;
  onComplete?: () => void;
}

export function FreemiumAssessmentFlow({
  token,
  className = '',
  onComplete,
}: FreemiumAssessmentFlowProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState<string | number>('');
  const [answerError, setAnswerError] = useState('');
  const [sessionProgress, setSessionProgress] = useState<any>(null);
  const [currentQuestion, setCurrentQuestion] = useState<AssessmentQuestion | null>(null);

  // Load session data and first question
  useEffect(() => {
    if (token) {
      loadSessionData();
    }
  }, [token]);

  const loadSessionData = async () => {
    if (!token) return;

    try {
      setIsLoading(true);
      setError(null);

      // Get session progress to see current state
      const progress = await freemiumService.getSessionProgress(token);
      setSessionProgress(progress);

      // If there's a current question in the session, use it
      if (progress.current_question_id) {
        // The session response should contain the current question data
        // For now, extract from the progress response
        const question: AssessmentQuestion = {
          question_id: progress.current_question_id,
          question_text: progress.question_text || 'Please describe your compliance needs',
          question_type: progress.question_type || 'text',
          answer_options: progress.answer_options,
        };
        setCurrentQuestion(question);
      } else {
        // Session exists but no current question - might be complete
        setError('Assessment may be complete. Check results.');
      }
    } catch (err) {
      console.error('Failed to load session data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load session');
    } finally {
      setIsLoading(false);
    }
  };

  // Reset answer when question changes
  useEffect(() => {
    if (currentQuestion) {
      setCurrentAnswer('');
      setAnswerError('');
    }
  }, [currentQuestion?.question_id]);

  const handleAnswerChange = (value: string | number) => {
    setCurrentAnswer(value);
    if (answerError) {
      setAnswerError('');
    }
  };

  const handleSubmit = async () => {
    if (!currentQuestion || !token) return;

    // Validate answer
    if (currentAnswer === '' || currentAnswer === null || currentAnswer === undefined) {
      setAnswerError('Please select an answer before continuing');
      return;
    }

    // Submit answer
    setIsSubmitting(true);
    try {
      const response = await freemiumService.submitAnswer(token, {
        question_id: currentQuestion.question_id,
        answer_text: currentAnswer.toString(), // Changed from 'answer' to 'answer_text'
        answer_confidence: 'medium',
        time_spent_seconds: 30,
      });

      // Check response for next question or completion
      if (response.assessment_complete || response.redirect_to_results) {
        // Assessment is complete, redirect to results
        if (onComplete) {
          onComplete();
        } else {
          // If no onComplete handler, redirect to results page
          window.location.href = `/freemium/results?token=${token}`;
        }
      } else if (response.next_question_id) {
        // There's a next question, update the current question
        const nextQuestion: AssessmentQuestion = {
          question_id: response.next_question_id,
          question_text: response.next_question_text || 'Please provide your answer',
          question_type: response.next_question_type || 'text',
          answer_options: response.next_answer_options,
        };
        setCurrentQuestion(nextQuestion);

        // Update progress if provided
        if (response.progress) {
          setSessionProgress(response.progress);
        }
      } else {
        // No next question but not complete - might be an error state
        setError('Unable to continue assessment. Please try again.');
      }
    } catch {
      console.error('Failed to submit answer:', _error);
      setAnswerError(error instanceof Error ? error.message : 'Failed to submit answer');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderQuestion = (question: AssessmentQuestion) => {
    switch (question.question_type) {
      case 'multiple_choice':
        return (
          <RadioGroup
            value={currentAnswer.toString()}
            onValueChange={handleAnswerChange}
            className="space-y-3"
          >
            {question.answer_options?.map((option, index) => (
              <div key={option} className="flex items-center space-x-3">
                <RadioGroupItem value={option} id={`option-${index}`} disabled={isSubmitting} />
                <Label
                  htmlFor={`option-${index}`}
                  className="flex-1 cursor-pointer text-sm font-medium"
                >
                  {option}
                </Label>
              </div>
            ))}
          </RadioGroup>
        );

      case 'text':
        return (
          <Textarea
            placeholder="Please provide your answer..."
            value={currentAnswer.toString()}
            onChange={(e) => handleAnswerChange(e.target.value)}
            className="min-h-[100px] resize-none"
            disabled={isSubmitting}
            maxLength={500}
          />
        );

      case 'yes_no':
        return (
          <RadioGroup
            value={currentAnswer.toString()}
            onValueChange={handleAnswerChange}
            className="space-y-3"
          >
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="true" id="yes" disabled={isSubmitting} />
              <Label htmlFor="yes" className="cursor-pointer text-sm font-medium">
                Yes
              </Label>
            </div>
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="false" id="no" disabled={isSubmitting} />
              <Label htmlFor="no" className="cursor-pointer text-sm font-medium">
                No
              </Label>
            </div>
          </RadioGroup>
        );

      case 'scale':
        return (
          <div className="space-y-4">
            <div className="px-3">
              <Slider
                value={[Number(currentAnswer) || 1]}
                onValueChange={(values) => handleAnswerChange(values[0])}
                max={10}
                min={1}
                step={1}
                className="w-full"
                disabled={isSubmitting}
              />
            </div>
            <div className="flex justify-between px-3 text-xs text-gray-500">
              <span>1 (Very Low)</span>
              <span className="font-medium text-teal-600">{currentAnswer || 1}</span>
              <span>10 (Very High)</span>
            </div>
          </div>
        );

      default:
        return (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Unsupported question type. Please refresh and try again.
            </AlertDescription>
          </Alert>
        );
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <Card className={`mx-auto w-full max-w-2xl ${className}`}>
        <CardContent className="flex flex-col items-center justify-center space-y-4 py-12">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-teal-100">
            <Brain className="h-6 w-6 animate-pulse text-teal-600" />
          </div>
          <div className="space-y-2 text-center">
            <h3 className="text-lg font-semibold text-gray-900">Loading Your Assessment</h3>
            <p className="text-gray-600">
              Preparing personalized questions based on your business...
            </p>
          </div>
          <Loader2 className="h-6 w-6 animate-spin text-teal-600" />
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Card className={`mx-auto w-full max-w-2xl ${className}`}>
        <CardContent className="py-8">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-base">
              {typeof error === 'string' ? error : 'Failed to load assessment. Please try again.'}
            </AlertDescription>
          </Alert>
          <div className="mt-6 text-center">
            <Button
              onClick={() => window.location.reload()}
              className="bg-teal-600 hover:bg-teal-700"
            >
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // No question loaded
  if (!currentQuestion) {
    return (
      <Card className={`mx-auto w-full max-w-2xl ${className}`}>
        <CardContent className="py-8 text-center">
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>Assessment not found. Please start over.</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`mx-auto w-full max-w-2xl ${className}`}>
      {/* Progress Header */}
      <CardHeader className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5 text-teal-600" />
            <span className="text-sm font-medium text-gray-600">AI Compliance Assessment</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Clock className="h-4 w-4" />
            <span>~{Math.max(1, 5 - (sessionProgress?.questions_answered || 0))} min left</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Progress</span>
            <span className="font-medium text-teal-600">
              {Math.round(sessionProgress?.progress_percentage || 0)}%
            </span>
          </div>
          <Progress value={sessionProgress?.progress_percentage || 0} className="h-2" />
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Question */}
        <div className="space-y-4">
          <CardTitle className="text-xl font-semibold leading-7 text-gray-900">
            {currentQuestion.question_text}
          </CardTitle>

          {/* Question Type Indicator */}
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="h-2 w-2 rounded-full bg-teal-500"></div>
            <span>
              {currentQuestion.question_type === 'multiple_choice' && 'Select one option'}
              {currentQuestion.question_type === 'text' && 'Enter your response'}
              {currentQuestion.question_type === 'yes_no' && 'Yes or No'}
              {currentQuestion.question_type === 'scale' && 'Rate from 1 to 10'}
            </span>
          </div>
        </div>

        {/* Answer Input */}
        <div className="space-y-4">
          {renderQuestion(currentQuestion)}

          {answerError && (
            <Alert variant="destructive">
              <AlertDescription>{answerError}</AlertDescription>
            </Alert>
          )}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between border-t border-gray-100 pt-6">
          <div className="text-sm text-gray-500">
            Question {(sessionProgress?.questions_answered || 0) + 1}
          </div>

          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || currentAnswer === ''}
            className="bg-teal-600 px-8 text-white hover:bg-teal-700"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                Next
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>

        {/* AI Indicator */}
        <div className="flex items-center justify-center space-x-2 pt-2 text-xs text-gray-400">
          <Brain className="h-3 w-3" />
          <span>Questions are generated by AI based on your responses</span>
        </div>
      </CardContent>
    </Card>
  );
}

// Minimal progress indicator component for standalone use
interface FreemiumAssessmentProgressProps {
  sessionProgress?: any;
}

export function FreemiumAssessmentProgress({ sessionProgress }: FreemiumAssessmentProgressProps) {
  const progress = sessionProgress?.progress_percentage || 0;
  const questionsAnswered = sessionProgress?.questions_answered || 0;

  return (
    <div className="mx-auto w-full max-w-sm space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">Assessment Progress</span>
        <span className="font-medium text-teal-600">{Math.round(progress)}%</span>
      </div>
      <Progress value={progress} className="h-2" />
      <div className="text-center text-xs text-gray-500">
        {questionsAnswered} questions answered
      </div>
    </div>
  );
}
