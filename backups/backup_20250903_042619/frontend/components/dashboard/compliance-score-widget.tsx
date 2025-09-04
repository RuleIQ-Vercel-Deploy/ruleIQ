'use client';

import { TrendingUp, TrendingDown, Minus, Eye, RefreshCw, Shield, CheckCircle } from 'lucide-react';
import React from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

interface ComplianceScoreData {
  overall_score: number;
  trend?: 'up' | 'down' | 'stable';
  last_updated?: string;
  frameworks?: Array<{
    name: string;
    score: number;
    compliance_percentage: number;
  }>;
}

interface ComplianceScoreWidgetProps {
  data: ComplianceScoreData;
  className?: string;
  isLoading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

export function ComplianceScoreWidget({
  data,
  className,
  isLoading = false,
  error = null,
  onRefresh,
}: ComplianceScoreWidgetProps) {
  // Show loading state
  if (isLoading) {
    return <ComplianceScoreWidgetSkeleton />;
  }

  // Show error state
  if (error) {
    return (
      <Card className={cn('glass-card border-error/50', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-error">
            <Shield className="h-5 w-5" />
            Compliance Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-sm text-muted-foreground">{error}</p>
          {onRefresh && (
            <Button
              onClick={onRefresh}
              variant="outline"
              size="sm"
              className="border-glass-border hover:border-glass-border-hover hover:bg-glass-white"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  const getTrendIcon = () => {
    switch (data.trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-success" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-error" />;
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-success';
    if (score >= 70) return 'text-warning';
    if (score >= 50) return 'text-warning';
    return 'text-error';
  };

  const getScoreBackground = (score: number) => {
    if (score >= 90) return 'bg-success/10';
    if (score >= 70) return 'bg-warning/10';
    if (score >= 50) return 'bg-warning/10';
    return 'bg-error/10';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 90) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 50) return 'Fair';
    return 'Needs Attention';
  };

  return (
    <Card className={cn('glass-card overflow-hidden', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="gradient-text flex items-center gap-2 text-lg font-semibold">
            <Shield className="h-5 w-5 text-primary" />
            Overall Compliance
          </CardTitle>
          <div className="flex items-center gap-2">
            {data.trend && getTrendIcon()}
            {onRefresh && (
              <Button variant="ghost" size="sm" className="h-auto p-1" onClick={onRefresh}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Main Score Display */}
        <div className={cn('rounded-lg py-8 text-center', getScoreBackground(data.overall_score))}>
          <p className={cn('text-5xl font-bold', getScoreColor(data.overall_score))}>
            {data.overall_score}%
          </p>
          <p className="mt-2 text-sm font-medium text-muted-foreground">
            {getScoreLabel(data.overall_score)}
          </p>
        </div>

        {/* Framework Breakdown */}
        {data.frameworks && data.frameworks.length > 0 && (
          <div className="space-y-4 rounded-lg bg-glass-white p-4">
            <h4 className="text-sm font-semibold text-foreground">Framework Breakdown</h4>
            {data.frameworks.map((framework, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{framework.name}</span>
                  <span
                    className={cn(
                      'font-semibold',
                      getScoreColor(framework.compliance_percentage || framework.score),
                    )}
                  >
                    {framework.compliance_percentage || framework.score}%
                  </span>
                </div>
                <Progress
                  value={framework.compliance_percentage || framework.score}
                  className="h-2"
                />
              </div>
            ))}
          </div>
        )}

        {/* Status Badges */}
        <div className="flex flex-wrap gap-2">
          {data.overall_score >= 70 && (
            <Badge variant="outline" className="border-success/40 bg-success/20 text-success">
              <CheckCircle className="mr-1 h-3 w-3" />
              Compliant
            </Badge>
          )}
          {data.trend === 'up' && (
            <Badge variant="outline" className="border-blue-200 bg-blue-50 text-blue-700">
              Improving
            </Badge>
          )}
          {data.trend === 'down' && (
            <Badge variant="outline" className="border-amber-200 bg-amber-50 text-amber-700">
              Declining
            </Badge>
          )}
        </div>

        {/* Last Updated */}
        {data.last_updated && (
          <div className="flex items-center justify-between border-t border-border pt-4 text-xs text-muted-foreground">
            <span>Updated {new Date(data.last_updated).toLocaleDateString()}</span>
            <Button variant="ghost" size="sm" className="h-auto p-1" asChild>
              <a href="/compliance/overview">
                <Eye className="h-3 w-3" />
              </a>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ComplianceScoreWidgetSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-5" />
            <Skeleton className="h-5 w-32" />
          </div>
          <Skeleton className="h-8 w-8" />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <Skeleton className="h-32 w-full rounded-lg" />
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="space-y-2">
              <div className="flex justify-between">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-12" />
              </div>
              <Skeleton className="h-2 w-full" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
