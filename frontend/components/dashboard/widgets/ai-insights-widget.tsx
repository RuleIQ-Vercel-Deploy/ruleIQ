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
        {insights.length === 0 ? (
          <p>AI-powered compliance insights and recommendations.</p>
        ) : (
          <div className="space-y-3">
            {insights.map((insight) => (
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
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
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
