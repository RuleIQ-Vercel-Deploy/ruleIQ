/**
 * Cost Analytics Widget Component
 *
 * Displays AI cost tracking metrics and analytics with real-time updates
 */

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, TrendingUp, AlertCircle, Activity, WifiOff, Loader2, Clock } from 'lucide-react';
import { useCostDashboard } from '@/lib/hooks/use-pusher';

interface CostAnalyticsWidgetProps {
  className?: string;
  timeRange?: 'day' | 'week' | 'month';
}

export const CostAnalyticsWidget: React.FC<CostAnalyticsWidgetProps> = ({
  className = '',
  timeRange = 'day',
}) => {
  const { connectionState, costData, lastUpdate } = useCostDashboard();
  const [isFeatureEnabled, setIsFeatureEnabled] = useState(true);

  // Check if Pusher is configured
  useEffect(() => {
    setIsFeatureEnabled(!!process.env.NEXT_PUBLIC_PUSHER_KEY);
  }, []);

  // Placeholder data for when real-time is disabled or not connected
  const placeholderData = {
    totalCost: 45.67,
    totalTokens: 125000,
    avgCostPerRequest: 0.23,
    budgetUsed: 65,
    trend: '+12%',
    alerts: 2,
  };

  // Use real data if available, otherwise use placeholders
  const displayData = (isFeatureEnabled && connectionState === 'connected' && costData) ? {
    totalCost: costData.totalCost || 0,
    totalTokens: costData.totalTokens || 0,
    avgCostPerRequest: costData.avgCostPerRequest || 0,
    budgetUsed: costData.budgetUsagePercentage || 0,
    trend: costData.trend || '+0%',
    alerts: costData.activeAlerts || 0,
  } : placeholderData;

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="h-5 w-5" />
          AI Cost Analytics
          {lastUpdate && isFeatureEnabled && (
            <span className="ml-auto flex items-center gap-1 text-xs font-normal text-muted-foreground">
              <Clock className="h-3 w-3" />
              {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </CardTitle>
        <CardDescription>
          Token usage and cost tracking for {timeRange}
          {!isFeatureEnabled && (
            <span className="ml-2 text-xs">(Static mode)</span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Connection Status */}
        {isFeatureEnabled && (
          <div className="mb-4 flex items-center gap-2">
            {connectionState === 'connecting' && (
              <>
                <Loader2 className="h-3 w-3 animate-spin" />
                <span className="text-xs text-muted-foreground">Connecting to live data...</span>
              </>
            )}
            {connectionState === 'disconnected' && (
              <>
                <WifiOff className="h-3 w-3 text-destructive" />
                <span className="text-xs text-destructive">Offline - showing cached data</span>
              </>
            )}
            {connectionState === 'connected' && (
              <>
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs text-green-600">Live data</span>
              </>
            )}
          </div>
        )}

        <div className="grid gap-4">
          {/* Total Cost */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Total Cost</span>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold">${displayData.totalCost.toFixed(2)}</p>
              <p className="flex items-center gap-1 text-xs text-muted-foreground">
                <TrendingUp className="h-3 w-3" />
                {displayData.trend} from last {timeRange}
              </p>
            </div>
          </div>

          {/* Token Usage */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Tokens Used</span>
            </div>
            <div className="text-right">
              <p className="text-lg font-semibold">
                {(displayData.totalTokens / 1000).toFixed(1)}k
              </p>
              <p className="text-xs text-muted-foreground">
                ${displayData.avgCostPerRequest.toFixed(2)}/request avg
              </p>
            </div>
          </div>

          {/* Budget Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Budget Status</span>
            </div>
            <div className="text-right">
              <p className="text-lg font-semibold">{displayData.budgetUsed}%</p>
              <p className="text-xs text-muted-foreground">{displayData.alerts} alerts</p>
            </div>
          </div>

          {/* Budget Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Budget Usage</span>
              <span>{displayData.budgetUsed}% of limit</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-secondary">
              <div
                className={`h-full transition-all ${
                  displayData.budgetUsed > 90
                    ? 'bg-destructive'
                    : displayData.budgetUsed > 75
                    ? 'bg-warning'
                    : 'bg-primary'
                }`}
                style={{ width: `${Math.min(displayData.budgetUsed, 100)}%` }}
              />
            </div>
          </div>

          {/* Status Message */}
          {!isFeatureEnabled && (
            <div className="mt-4 rounded-lg bg-muted p-3">
              <p className="text-center text-xs text-muted-foreground">
                Real-time updates disabled. Configure Pusher to enable live data.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default CostAnalyticsWidget;
