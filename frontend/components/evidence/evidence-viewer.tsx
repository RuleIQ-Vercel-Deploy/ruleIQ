'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface EvidenceViewerProps {
  evidenceId?: string;
}

export function EvidenceViewer({ evidenceId }: EvidenceViewerProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Evidence Viewer</CardTitle>
      </CardHeader>
      <CardContent>
        {evidenceId ? (
          <div className="space-y-4">
            <div className="aspect-video bg-gray-100 rounded flex items-center justify-center">
              <span className="text-gray-500">Document Preview</span>
            </div>
            <div className="flex gap-2">
              <Button>Download</Button>
              <Button variant="outline">Share</Button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Select evidence to view
          </div>
        )}
      </CardContent>
    </Card>
  );
}
