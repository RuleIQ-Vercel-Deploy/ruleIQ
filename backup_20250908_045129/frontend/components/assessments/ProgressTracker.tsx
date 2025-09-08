'use client';

import { CheckCircle, Circle, Clock } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { type AssessmentProgress, type AssessmentFramework } from '@/lib/assessment-engine/types';
import { AssessmentUtils } from '@/lib/assessment-engine/utils';
import { cn } from '@/lib/utils';

interface ProgressTrackerProps {
  progress: AssessmentProgress;
  framework: AssessmentFramework;
  onSectionClick?: (sectionIndex: number) => void;
}

export function ProgressTracker({ progress, framework, onSectionClick }: ProgressTrackerProps) {
  const estimatedTime = AssessmentUtils.calculateEstimatedTime(framework);
  const formattedTime = AssessmentUtils.formatDuration(estimatedTime);

  // Calculate section progress
  const sectionProgress = framework.sections.map((section, index) => {
    const sectionQuestions = section.questions.length;
    const answeredInSection = section.questions.filter(
      (_q, qIndex) =>
        // This would need to be passed from the engine
        progress.answeredQuestions > qIndex, // Simplified for now
    ).length;

    return {
      section,
      index,
      progress: sectionQuestions > 0 ? (answeredInSection / sectionQuestions) * 100 : 0,
      isActive: progress.currentSection === section.id,
      isComplete: answeredInSection === sectionQuestions,
    };
  });

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Overall Progress */}
          <div>
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-medium">Overall Progress</h3>
              <span className="text-sm text-muted-foreground">
                {progress.percentComplete}% Complete
              </span>
            </div>
            <Progress value={progress.percentComplete} className="h-2" />
            <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
              <span>
                {progress.answeredQuestions} of {progress.totalQuestions} questions
              </span>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>Est. {formattedTime}</span>
              </div>
            </div>
          </div>

          {/* Section Progress */}
          <div>
            <h3 className="mb-3 text-sm font-medium">Sections</h3>
            <div className="space-y-2">
              {sectionProgress.map(
                ({ section, index, progress: sectionProg, isActive, isComplete }) => (
                  <div
                    key={section.id}
                    className={cn(
                      'flex items-center gap-3 rounded-lg p-2 transition-colors',
                      onSectionClick && 'cursor-pointer hover:bg-muted',
                      isActive && 'bg-muted',
                    )}
                    onClick={() => onSectionClick?.(index)}
                  >
                    <div className="flex-shrink-0">
                      {isComplete ? (
                        <CheckCircle className="h-5 w-5 text-success" />
                      ) : isActive ? (
                        <div className="relative">
                          <Circle className="h-5 w-5 text-primary" />
                          <div className="absolute inset-0 flex items-center justify-center">
                            <div className="h-2 w-2 animate-pulse rounded-full bg-primary" />
                          </div>
                        </div>
                      ) : (
                        <Circle className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between">
                        <p className={cn('truncate text-sm', isActive && 'font-medium')}>
                          {section.title}
                        </p>
                        {isComplete && (
                          <Badge variant="outline" className="ml-2 text-xs">
                            Complete
                          </Badge>
                        )}
                      </div>
                      <Progress value={sectionProg} className="mt-1 h-1" />
                    </div>
                  </div>
                ),
              )}
            </div>
          </div>

          {/* Last Saved */}
          {progress.lastSaved && (
            <div className="border-t pt-2 text-center text-xs text-muted-foreground">
              Last saved: {new Date(progress.lastSaved).toLocaleTimeString()}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
