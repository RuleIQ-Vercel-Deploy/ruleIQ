'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface AIInsight {
  id: string;
  type: 'recommendation' | 'risk' | 'compliance';
  title: string;
  description: string;
  confidence: number;
  priority: 'high' | 'medium' | 'low';
}

interface AIInsightsWidgetProps {
  insights?: AIInsight[];
  isLoading?: boolean;
  onInsightClick?: (insightId: string) => void;
  onRefresh?: () => void;
}

export function AIInsightsWidget({
  insights = [],
  isLoading = false,
  onInsightClick,
  onRefresh
}: AIInsightsWidgetProps) {
  const defaultInsights: AIInsight[] = [
    {
      id: '1',
      type: 'recommendation',
      title: 'Improve data retention policies',
      description: 'Consider implementing automated data deletion',
      confidence: 85,
      priority: 'high'
    },
    {
      id: '2',
      type: 'risk',
      title: 'Potential compliance gap',
      description: 'Missing employee training records',
      confidence: 92,
      priority: 'high'
    }
  ];

  const displayInsights = insights.length > 0 ? insights : defaultInsights;

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>AI Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Analyzing compliance data...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>AI Insights</CardTitle>
        {onRefresh && (
          <Button variant="outline" size="sm" onClick={onRefresh}>
            Refresh
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {displayInsights.length === 0 ? (
          <p>AI-powered compliance insights and recommendations.</p>
        ) : (
          <div className="space-y-3">
            {displayInsights.map((insight) => (
              <div
                key={insight.id}
                className="p-3 border rounded cursor-pointer hover:bg-gray-50"
                onClick={() => onInsightClick?.(insight.id)}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{insight.title}</span>
                  <span className="text-sm text-gray-500">{insight.confidence}%</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded capitalize">
                  {insight.type}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
