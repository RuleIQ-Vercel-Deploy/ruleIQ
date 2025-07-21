'use client';

import { ChevronLeft, ChevronRight, Grid } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { type AssessmentFramework, type AssessmentProgress } from '@/lib/assessment-engine/types';
import { cn } from '@/lib/utils';

interface AssessmentNavigationProps {
  framework: AssessmentFramework;
  currentSectionIndex: number;
  progress: AssessmentProgress;
  onSectionClick: (sectionIndex: number) => void;
}

export function AssessmentNavigation({
  framework,
  currentSectionIndex,
  onSectionClick,
}: AssessmentNavigationProps) {
  const hasPreviousSection = currentSectionIndex > 0;
  const hasNextSection = currentSectionIndex < framework.sections.length - 1;

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          {/* Previous Section */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onSectionClick(currentSectionIndex - 1)}
            disabled={!hasPreviousSection}
            className="flex-1 justify-start"
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            <span className="truncate">
              {hasPreviousSection && framework.sections[currentSectionIndex - 1]?.title}
            </span>
          </Button>

          {/* Section Grid */}
          <div className="flex items-center gap-1 px-4">
            {framework.sections.map((_, index) => (
              <button
                key={index}
                onClick={() => onSectionClick(index)}
                className={cn(
                  'h-2 w-2 rounded-full transition-all',
                  index === currentSectionIndex
                    ? 'w-6 bg-primary'
                    : 'bg-muted-foreground/30 hover:bg-muted-foreground/50',
                )}
                aria-label={`Go to section ${index + 1}`}
              />
            ))}
          </div>

          {/* Next Section */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onSectionClick(currentSectionIndex + 1)}
            disabled={!hasNextSection}
            className="flex-1 justify-end"
          >
            <span className="truncate">
              {hasNextSection && framework.sections[currentSectionIndex + 1]?.title}
            </span>
            <ChevronRight className="ml-2 h-4 w-4" />
          </Button>
        </div>

        {/* Quick Navigation */}
        <div className="mt-4 border-t pt-4">
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => {
              // TODO: Open section navigator modal
              onSectionClick(0);
            }}
          >
            <Grid className="mr-2 h-4 w-4" />
            View All Sections ({framework.sections.length})
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
