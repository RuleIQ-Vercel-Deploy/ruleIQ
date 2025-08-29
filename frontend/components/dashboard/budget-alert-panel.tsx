/**
 * Budget Alert Panel Component
 * 
 * Displays budget alerts, warnings, and optimization recommendations.
 * This is a placeholder component for Phase 2.2: Cost Tracking & Token Budgets
 * 
 * TODO: Implement the following:
 * - Real-time alert streaming via WebSocket
 * - Alert acknowledgment and dismissal
 * - Budget threshold configuration
 * - Cost optimization suggestions
 */

import React from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  AlertTriangle, 
  TrendingUp, 
  Lightbulb, 
  X,
  Bell,
  DollarSign 
} from 'lucide-react';

interface BudgetAlert {
  id: string;
  type: 'warning' | 'critical' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  acknowledged: boolean;
}

interface BudgetAlertPanelProps {
  className?: string;
  maxAlerts?: number;
}

export const BudgetAlertPanel: React.FC<BudgetAlertPanelProps> = ({
  className = '',
  maxAlerts = 5
}) => {
  // TODO: Connect to budget alert service
  // const { data: alerts, acknowledge, dismiss } = useBudgetAlerts();

  // Placeholder alerts
  const placeholderAlerts: BudgetAlert[] = [
    {
      id: '1',
      type: 'warning',
      title: 'Approaching Daily Budget Limit',
      message: 'You have used 85% of your daily AI budget ($85 of $100)',
      timestamp: new Date(),
      acknowledged: false
    },
    {
      id: '2',
      type: 'critical',
      title: 'High Cost Spike Detected',
      message: 'Cost per request increased by 150% in the last hour',
      timestamp: new Date(Date.now() - 3600000),
      acknowledged: false
    },
    {
      id: '3',
      type: 'info',
      title: 'Cost Optimization Available',
      message: 'Switch to GPT-3.5 for routine queries to save ~40% on costs',
      timestamp: new Date(Date.now() - 7200000),
      acknowledged: true
    }
  ];

  const getAlertIcon = (type: BudgetAlert['type']) => {
    switch (type) {
      case 'critical':
        return <AlertTriangle className="h-4 w-4" />;
      case 'warning':
        return <TrendingUp className="h-4 w-4" />;
      case 'info':
        return <Lightbulb className="h-4 w-4" />;
    }
  };

  const getAlertVariant = (type: BudgetAlert['type']) => {
    switch (type) {
      case 'critical':
        return 'destructive';
      case 'warning':
        return 'default';
      case 'info':
        return 'default';
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Budget Alerts
        </CardTitle>
        <CardDescription>
          Cost warnings and optimization recommendations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {placeholderAlerts.slice(0, maxAlerts).map((alert) => (
            <Alert 
              key={alert.id} 
              variant={getAlertVariant(alert.type)}
              className={alert.acknowledged ? 'opacity-60' : ''}
            >
              <div className="flex items-start justify-between">
                <div className="flex gap-2">
                  {getAlertIcon(alert.type)}
                  <div className="space-y-1">
                    <AlertTitle className="text-sm font-medium">
                      {alert.title}
                    </AlertTitle>
                    <AlertDescription className="text-xs">
                      {alert.message}
                    </AlertDescription>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline" className="text-xs">
                        {alert.type}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0"
                  onClick={() => {
                    // TODO: Implement dismiss functionality
                    console.log('Dismiss alert:', alert.id);
                  }}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </Alert>
          ))}

          {/* Budget Settings Quick Access */}
          <div className="mt-4 p-3 border rounded-lg bg-muted/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Daily Budget</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold">$100.00</span>
                <Button variant="outline" size="sm">
                  Configure
                </Button>
              </div>
            </div>
          </div>

          {/* Placeholder Message */}
          <div className="mt-4 p-3 bg-muted rounded-lg">
            <p className="text-xs text-muted-foreground text-center">
              🚧 Alert system placeholder. 
              Connect to WebSocket for real-time budget alerts.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default BudgetAlertPanel;