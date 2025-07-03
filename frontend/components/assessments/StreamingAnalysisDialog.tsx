"use client";

import React, { useEffect, useRef } from 'react';

import { StreamingProgress } from '@/components/shared/streaming-progress';
import { StreamingResponse, type StreamingResponseRef } from '@/components/shared/streaming-response';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { assessmentAIService } from '@/lib/api/assessments-ai.service';
import { useStreaming } from '@/lib/hooks/use-streaming';

import type { 
  AIAnalysisRequest, 
  AIRecommendationRequest,
  Gap 
} from '@/lib/api/assessments-ai.service';
import type { AssessmentProgress } from '@/lib/assessment-engine/types';

interface StreamingAnalysisDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  assessmentProgress: AssessmentProgress;
  businessProfileId: string;
  frameworkId: string;
  onAnalysisComplete?: (analysis: string) => void;
  onRecommendationsComplete?: (recommendations: string) => void;
}

export function StreamingAnalysisDialog({
  open,
  onOpenChange,
  assessmentProgress,
  businessProfileId,
  frameworkId,
  onAnalysisComplete,
  onRecommendationsComplete
}: StreamingAnalysisDialogProps) {
  const [analysisState, analysisControls] = useStreaming();
  const [recommendationsState, recommendationsControls] = useStreaming();
  const analysisRef = useRef<StreamingResponseRef>(null);
  const recommendationsRef = useRef<StreamingResponseRef>(null);

  const startAnalysis = async () => {
    const analysisRequest: AIAnalysisRequest = {
      assessment_results: Object.entries(assessmentProgress.answers).map(([questionId, answer]) => ({
        question_id: questionId,
        answer,
        section_id: assessmentProgress.currentSection || 'unknown'
      })),
      framework_id: frameworkId,
      business_profile_id: businessProfileId
    };

    await analysisControls.start(async (options) => {
      await assessmentAIService.analyzeAssessmentWithStreaming(analysisRequest, options);
    });
  };

  const startRecommendations = async (gaps: Gap[]) => {
    const recommendationsRequest: AIRecommendationRequest = {
      gaps,
      business_profile: {
        id: businessProfileId,
        // Add other business profile fields as needed
      }
    };

    await recommendationsControls.start(async (options) => {
      await assessmentAIService.getRecommendationsWithStreaming(recommendationsRequest, options);
    });
  };

  // Auto-start analysis when dialog opens
  useEffect(() => {
    if (open && !analysisState.isStreaming && !analysisState.isComplete) {
      startAnalysis();
    }
  }, [open]);

  // Start recommendations after analysis completes
  useEffect(() => {
    if (analysisState.isComplete && !analysisState.error && analysisState.content) {
      onAnalysisComplete?.(analysisState.content);
      
      // Extract gaps from analysis content (this would need proper parsing)
      // For demo purposes, we'll start recommendations with mock gaps
      const mockGaps: Gap[] = [
        {
          id: 'gap-1',
          section: 'data-protection',
          severity: 'high',
          description: 'Missing data retention policies',
          impact: 'High compliance risk',
          current_state: 'No formal policies',
          target_state: 'Comprehensive retention schedule'
        }
      ];
      
      if (!recommendationsState.isStreaming && !recommendationsState.isComplete) {
        startRecommendations(mockGaps);
      }
    }
  }, [analysisState.isComplete, analysisState.content]);

  // Complete recommendations
  useEffect(() => {
    if (recommendationsState.isComplete && !recommendationsState.error) {
      onRecommendationsComplete?.(recommendationsState.content);
    }
  }, [recommendationsState.isComplete, recommendationsState.content]);

  const getOverallProgress = () => {
    if (!analysisState.isStreaming && !analysisState.isComplete) return 0;
    if (analysisState.isStreaming || (!recommendationsState.isStreaming && !recommendationsState.isComplete)) {
      return analysisState.progress / 2;
    }
    return 50 + (recommendationsState.progress / 2);
  };

  const getOverallStatus = () => {
    if (analysisState.error || recommendationsState.error) return 'error';
    if (recommendationsState.isComplete) return 'complete';
    if (analysisState.isStreaming || recommendationsState.isStreaming) return 'streaming';
    return 'idle';
  };

  const getCurrentMessage = () => {
    if (analysisState.error) return `Analysis error: ${analysisState.error}`;
    if (recommendationsState.error) return `Recommendations error: ${recommendationsState.error}`;
    if (recommendationsState.isComplete) return 'Analysis and recommendations complete';
    if (recommendationsState.isStreaming) return 'Generating personalized recommendations...';
    if (analysisState.isComplete) return 'Analysis complete, starting recommendations...';
    if (analysisState.isStreaming) return 'Analyzing assessment responses...';
    return 'Starting AI analysis...';
  };

  const handleRetry = () => {
    analysisControls.reset();
    recommendationsControls.reset();
    analysisRef.current?.reset();
    recommendationsRef.current?.reset();
    startAnalysis();
  };

  const handleClose = () => {
    if (analysisState.isStreaming) {
      analysisControls.stop();
    }
    if (recommendationsState.isStreaming) {
      recommendationsControls.stop();
    }
    onOpenChange(false);
  };

  const canClose = !analysisState.isStreaming && !recommendationsState.isStreaming;

  return (
    <Dialog open={open} onOpenChange={canClose ? onOpenChange : undefined}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle>AI-Powered Assessment Analysis</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Overall Progress */}
          <StreamingProgress
            progress={getOverallProgress()}
            status={getOverallStatus()}
            message={getCurrentMessage()}
            elapsedTime={analysisState.elapsedTime + recommendationsState.elapsedTime}
            size="lg"
          />

          {/* Analysis Section */}
          <StreamingResponse
            ref={analysisRef}
            title="Gap Analysis & Risk Assessment"
            description="Analyzing your assessment responses to identify compliance gaps and risks"
            showProgress={true}
            showControls={true}
            onRetry={handleRetry}
            className="min-h-[200px]"
          />

          {/* Recommendations Section */}
          {(analysisState.isComplete || recommendationsState.isStreaming || recommendationsState.isComplete) && (
            <StreamingResponse
              ref={recommendationsRef}
              title="Personalized Recommendations"
              description="Generating tailored implementation guidance based on your specific context"
              showProgress={true}
              showControls={true}
              onRetry={handleRetry}
              className="min-h-[200px]"
            />
          )}

          {/* Action Buttons */}
          <div className="flex justify-between pt-4 border-t">
            <div>
              {(analysisState.error || recommendationsState.error) && (
                <Button variant="outline" onClick={handleRetry}>
                  Retry Analysis
                </Button>
              )}
            </div>
            
            <div className="flex gap-2">
              {canClose && (
                <Button variant="outline" onClick={handleClose}>
                  {recommendationsState.isComplete ? 'Close' : 'Cancel'}
                </Button>
              )}
              
              {recommendationsState.isComplete && (
                <Button onClick={handleClose}>
                  View Results
                </Button>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );

  // Sync streaming states with StreamingResponse components
  useEffect(() => {
    if (analysisRef.current) {
      if (analysisState.metadata) {
        analysisRef.current.setMetadata(analysisState.metadata);
      }
      analysisState.chunks.forEach(chunk => {
        analysisRef.current?.addChunk(chunk);
      });
      if (analysisState.error) {
        analysisRef.current.setError(analysisState.error);
      }
      if (analysisState.isComplete && !analysisState.error) {
        analysisRef.current.setComplete();
      }
    }
  }, [analysisState]);

  useEffect(() => {
    if (recommendationsRef.current) {
      if (recommendationsState.metadata) {
        recommendationsRef.current.setMetadata(recommendationsState.metadata);
      }
      recommendationsState.chunks.forEach(chunk => {
        recommendationsRef.current?.addChunk(chunk);
      });
      if (recommendationsState.error) {
        recommendationsRef.current.setError(recommendationsState.error);
      }
      if (recommendationsState.isComplete && !recommendationsState.error) {
        recommendationsRef.current.setComplete();
      }
    }
  }, [recommendationsState]);
}