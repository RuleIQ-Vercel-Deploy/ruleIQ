'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Activity {
  id: string;
  type: 'assessment' | 'evidence' | 'report';
  title: string;
  description: string;
  timestamp: string;
  user: string;
}

interface RecentActivityWidgetProps {
  activities?: Activity[];
  onViewAll?: () => void;
}

export function RecentActivityWidget({ activities = [], onViewAll }: RecentActivityWidgetProps) {
  const defaultActivities = [
    {
      id: '1',
      type: 'assessment' as const,
      title: 'GDPR Assessment Completed',
      description: 'Assessment completed: GDPR Compliance',
      timestamp: '10:00',
      user: 'John Smith',
    },
    {
      id: '2',
      type: 'evidence' as const,
      title: 'Security Policy Updated',
      description: 'Evidence uploaded: Privacy Policy',
      timestamp: '15:30',
      user: 'Jane Doe',
    },
    {
      id: '3',
      type: 'report' as const,
      title: 'Q4 Report Generated',
      description: 'Report generated: Q4 2024',
      timestamp: '5 minutes ago',
      user: 'System',
    },
  ];

  const displayActivities = activities.length > 0 ? activities : defaultActivities;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Recent Activity</CardTitle>
        {onViewAll && (
          <Button variant="outline" size="sm" onClick={onViewAll}>
            View All
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {displayActivities.length === 0 ? (
          <p>No recent activity</p>
        ) : (
          <div className="space-y-2">
            {displayActivities.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-3">
                <div
                  data-testid={`${activity.type === 'assessment' ? 'check' : activity.type === 'evidence' ? 'file' : 'report'}-icon`}
                  className="h-4 w-4 rounded bg-blue-500"
                />
                <div className="flex-1">
                  <div className="text-sm">{activity.description}</div>
                  <div className="text-xs text-gray-500">
                    {activity.timestamp} • {activity.user}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
