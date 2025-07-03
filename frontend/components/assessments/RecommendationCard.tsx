"use client";

import { 
  Clock, 
  Users, 
  Target, 
  TrendingUp,
  ChevronRight
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type Recommendation } from "@/lib/assessment-engine/types";
import { cn } from "@/lib/utils";

interface RecommendationCardProps {
  recommendation: Recommendation;
  onImplement?: () => void;
}

export function RecommendationCard({ 
  recommendation, 
  onImplement 
}: RecommendationCardProps) {
  const getPriorityConfig = (priority: string) => {
    switch (priority) {
      case 'high':
        return {
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          badgeVariant: 'destructive' as const
        };
      case 'medium':
        return {
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50', 
          borderColor: 'border-yellow-200',
          badgeVariant: 'warning' as const
        };
      default:
        return {
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          badgeVariant: 'success' as const
        };
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'policy':
        return '📋';
      case 'technical':
        return '⚙️';
      case 'training':
        return '🎓';
      case 'process':
        return '🔄';
      default:
        return '💡';
    }
  };

  const priorityConfig = getPriorityConfig(recommendation.priority);

  return (
    <Card className="h-full flex flex-col transition-all hover:shadow-lg">
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-3">
            <div className="text-2xl">{getCategoryIcon(recommendation.category)}</div>
            <div className="flex-1">
              <CardTitle className="text-lg leading-tight">
                {recommendation.title}
              </CardTitle>
            </div>
          </div>
          <Badge variant={priorityConfig.badgeVariant}>
            {recommendation.priority.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4">
        <p className="text-sm text-muted-foreground">
          {recommendation.description}
        </p>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Impact</p>
              <p className="text-sm font-medium capitalize">{recommendation.impact}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Effort</p>
              <p className="text-sm font-medium capitalize">{recommendation.effort}</p>
            </div>
          </div>
        </div>

        {/* Timeline & Resources */}
        <div className="space-y-2 pt-2 border-t">
          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Timeline:</span>
            <span className="font-medium">{recommendation.estimatedTime}</span>
          </div>
          <div className="flex items-start gap-2 text-sm">
            <Users className="h-4 w-4 text-muted-foreground mt-0.5" />
            <span className="text-muted-foreground">Resources:</span>
            <span className="font-medium">
              {recommendation.resources.join(', ')}
            </span>
          </div>
        </div>

        {/* Related Gaps */}
        {recommendation.relatedGaps && recommendation.relatedGaps.length > 0 && (
          <div className="text-xs text-muted-foreground">
            Addresses {recommendation.relatedGaps.length} compliance gap{recommendation.relatedGaps.length > 1 ? 's' : ''}
          </div>
        )}

        {/* Action Button */}
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full mt-auto"
          onClick={onImplement}
        >
          Create Implementation Task
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </CardContent>
    </Card>
  );
}