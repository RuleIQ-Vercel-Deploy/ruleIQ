'use client';

import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { type Gap } from '@/lib/assessment-engine/types';
import { cn } from '@/lib/utils';

interface GapAnalysisCardProps {
  gap: Gap;
  index: number;
}

export function GapAnalysisCard({ gap, index }: GapAnalysisCardProps) {
  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'high':
        return {
          icon: AlertTriangle,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          badgeVariant: 'destructive' as const,
        };
      case 'medium':
        return {
          icon: AlertCircle,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          badgeVariant: 'pending' as const,
        };
      default:
        return {
          icon: Info,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          badgeVariant: 'secondary' as const,
        };
    }
  };

  const config = getSeverityConfig(gap.severity);
  const Icon = config.icon;

  return (
    <Card className={cn('transition-all hover:shadow-lg', config.borderColor)}>
      <CardHeader className={cn('pb-3', config.bgColor)}>
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className={cn('rounded-lg bg-white p-2 shadow-sm', config.borderColor, 'border')}>
              <Icon className={cn('h-5 w-5', config.color)} />
            </div>
            <div className="flex-1">
              <div className="mb-1 flex items-center gap-2">
                <span className="text-sm font-medium text-muted-foreground">Gap #{index}</span>
                <Badge variant={config.badgeVariant} className="text-xs">
                  {gap.severity.toUpperCase()}
                </Badge>
              </div>
              <h4 className="font-semibold leading-tight text-navy">{gap.questionText}</h4>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 pt-4">
        <div className="grid gap-3">
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Expected Response
            </p>
            <p className="rounded-md bg-green-50 p-2 text-sm text-green-700">
              {gap.expectedAnswer}
            </p>
          </div>
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Your Response
            </p>
            <p className="rounded-md bg-red-50 p-2 text-sm text-red-700">
              {gap.actualAnswer || 'No response provided'}
            </p>
          </div>
        </div>

        <div className="border-t pt-3">
          <p className="mb-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Impact
          </p>
          <p className="text-sm text-muted-foreground">{gap.impact}</p>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Badge variant="outline" className="text-xs">
            {gap.category.replace('-', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}
