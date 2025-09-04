import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProgressBar } from '@/components/ui/progress-bar';
import { cn } from '@/lib/utils';

import type { LucideIcon } from 'lucide-react';

interface RequirementCardProps {
  title: string;
  score: number;
  status: 'compliant' | 'partial' | 'non-compliant';
  icon: LucideIcon;
  color: string;
}

export function RequirementCard({ title, score, icon: Icon, color }: RequirementCardProps) {
  const getProgressColor = (s: number) => {
    if (s >= 90) return 'success';
    if (s >= 70) return 'warning';
    return 'error';
  };

  return (
    <Card className="ruleiq-card flex h-full flex-col border-primary/20 bg-card/50 backdrop-blur-sm">
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <CardTitle className="flex-1 text-base font-semibold">{title}</CardTitle>
        <Icon className={cn('h-6 w-6 shrink-0', color)} />
      </CardHeader>
      <CardContent className="flex flex-1 flex-col justify-between">
        <div className="space-y-2">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-muted-foreground">Score</span>
            <span className="text-2xl font-bold">{score}%</span>
          </div>
          <ProgressBar value={score} color={getProgressColor(score)} className="h-1.5" />
        </div>
        <div className="mt-4 text-right">
          <Button variant="link" className="h-auto p-0 text-sm text-primary hover:text-primary/80">
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
