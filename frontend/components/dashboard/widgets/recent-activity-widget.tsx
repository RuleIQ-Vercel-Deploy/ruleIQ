'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function RecentActivityWidget() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="text-sm">Assessment completed: GDPR Compliance</div>
          <div className="text-sm">Evidence uploaded: Privacy Policy</div>
          <div className="text-sm">Report generated: Q4 2024</div>
        </div>
      </CardContent>
    </Card>
  );
}
