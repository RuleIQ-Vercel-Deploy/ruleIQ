'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface Risk {
  id: string;
  name: string;
  likelihood: 1 | 2 | 3 | 4 | 5;
  impact: 1 | 2 | 3 | 4 | 5;
  category: string;
}

interface RiskMatrixProps {
  risks: Risk[];
  title?: string;
  description?: string;
  className?: string;
}

export function RiskMatrix({
  risks,
  title = 'Risk Matrix',
  description = 'Current risk assessment overview',
  className,
}: RiskMatrixProps) {
  const likelihoodLabels = ['Very Low', 'Low', 'Medium', 'High', 'Very High'];
  const impactLabels = ['Minimal', 'Minor', 'Moderate', 'Major', 'Severe'];

  const getRiskColor = (likelihood: number, impact: number) => {
    const score = likelihood * impact;
    if (score <= 5) return 'bg-green-100 text-green-900 border-green-200';
    if (score <= 10) return 'bg-yellow-100 text-yellow-900 border-yellow-200';
    if (score <= 15) return 'bg-orange-100 text-orange-900 border-orange-200';
    return 'bg-red-100 text-red-900 border-red-200';
  };

  const getRiskCount = (likelihood: number, impact: number) => {
    return risks.filter((r) => r.likelihood === likelihood && r.impact === impact).length;
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Matrix */}
          <div className="flex">
            {/* Y-axis label */}
            <div className="flex items-center justify-center pr-4">
              <span className="-rotate-90 whitespace-nowrap text-sm font-medium text-muted-foreground">
                Likelihood →
              </span>
            </div>

            {/* Matrix grid */}
            <div className="flex-1">
              <div className="grid grid-cols-5 gap-2">
                {[5, 4, 3, 2, 1].map((likelihood) =>
                  [1, 2, 3, 4, 5].map((impact) => {
                    const count = getRiskCount(likelihood, impact);
                    return (
                      <div
                        key={`${likelihood}-${impact}`}
                        className={cn(
                          'flex aspect-square items-center justify-center rounded-lg border-2 text-lg font-semibold transition-all',
                          getRiskColor(likelihood, impact),
                          count > 0 && 'shadow-md',
                        )}
                      >
                        {count > 0 && count}
                      </div>
                    );
                  }),
                )}
              </div>

              {/* X-axis labels */}
              <div className="mt-2 grid grid-cols-5 gap-2">
                {impactLabels.map((label, i) => (
                  <div key={i} className="text-center text-xs text-muted-foreground">
                    {label}
                  </div>
                ))}
              </div>

              {/* X-axis label */}
              <div className="mt-2 text-center">
                <span className="text-sm font-medium text-muted-foreground">Impact →</span>
              </div>
            </div>

            {/* Y-axis labels */}
            <div className="pl-2">
              {[5, 4, 3, 2, 1].map((_, i) => (
                <div
                  key={i}
                  className="flex h-full items-center text-xs text-muted-foreground"
                  style={{ height: `${100 / 5}%` }}
                >
                  {likelihoodLabels[4 - i]}
                </div>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-center gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded border-2 border-green-200 bg-green-100" />
              <span>Low Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded border-2 border-yellow-200 bg-yellow-100" />
              <span>Medium Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded border-2 border-orange-200 bg-orange-100" />
              <span>High Risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 rounded border-2 border-red-200 bg-red-100" />
              <span>Critical Risk</span>
            </div>
          </div>

          {/* Risk count summary */}
          <div className="text-center text-sm text-muted-foreground">
            Total risks: {risks.length}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
