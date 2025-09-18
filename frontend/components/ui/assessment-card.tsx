import * as React from 'react';

import { cn } from '@/lib/utils';

import { Badge } from './badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Progress } from './progress';

interface AssessmentCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: string;
  progress?: number;
  status?: 'not-started' | 'in-progress' | 'completed' | 'expired';
  dueDate?: string;
  framework?: string;
  children?: React.ReactNode;
}

const statusConfig = {
  'not-started': {
    label: 'Not Started',
    className: 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200',
  },
  'in-progress': {
    label: 'In Progress',
    className: 'bg-purple-100 text-purple-700 hover:bg-purple-200',
  },
  completed: {
    label: 'Completed',
    className: 'bg-success-100 text-success-700 hover:bg-success-200',
  },
  expired: {
    label: 'Expired',
    className: 'bg-error-100 text-error-700 hover:bg-error-200',
  },
};

const AssessmentCard = React.forwardRef<HTMLDivElement, AssessmentCardProps>(
  (
    {
      className,
      title,
      description,
      progress = 0,
      status = 'not-started',
      dueDate,
      framework,
      children,
      ...props
    },
    ref,
  ) => {
    const config = statusConfig[status];

    return (
      <Card
        ref={ref}
        className={cn(
          'group relative overflow-hidden transition-all duration-300',
          'hover:scale-[1.01] hover:shadow-lg',
          className,
        )}
        {...props}
      >
        <CardHeader className="space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 space-y-1">
              <CardTitle className="text-lg font-semibold text-neutral-900">{title}</CardTitle>
              {description && (
                <CardDescription className="text-sm text-neutral-600">
                  {description}
                </CardDescription>
              )}
            </div>
            <Badge variant="secondary" className={cn('shrink-0', config.className)}>
              {config.label}
            </Badge>
          </div>

          {(framework || dueDate) && (
            <div className="flex flex-wrap gap-4 text-sm text-neutral-600">
              {framework && (
                <div className="flex items-center gap-1">
                  <span className="font-medium">Framework:</span>
                  <span>{framework}</span>
                </div>
              )}
              {dueDate && (
                <div className="flex items-center gap-1">
                  <span className="font-medium">Due:</span>
                  <span>{dueDate}</span>
                </div>
              )}
            </div>
          )}
        </CardHeader>

        <CardContent className="space-y-4">
          {progress !== undefined && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-neutral-700">Progress</span>
                <span className="font-semibold text-purple-600">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" indicatorClassName="bg-purple-600" />
            </div>
          )}

          {children}
        </CardContent>

        {/* Subtle gradient overlay on hover */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-purple-50/0 to-purple-50/0 transition-all duration-300 group-hover:from-purple-50/10 group-hover:to-transparent" />
      </Card>
    );
  },
);

AssessmentCard.displayName = 'AssessmentCard';

export { AssessmentCard };
