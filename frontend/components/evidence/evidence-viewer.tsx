'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Evidence {
  id: string;
  name: string;
  type: string;
  uploadDate: string;
  status: 'pending' | 'approved' | 'rejected';
  fileType?: string;
}

interface EvidenceViewerProps {
  evidence?: Evidence | null;
  onApprove?: (evidenceId: string) => void;
  onReject?: (evidenceId: string) => void;
}

export function EvidenceViewer({ evidence, onApprove, onReject }: EvidenceViewerProps) {
  if (!evidence) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Evidence Viewer</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="py-8 text-center text-gray-500">Select evidence to view</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evidence Viewer</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div
              data-testid="file-icon"
              className="flex h-8 w-8 items-center justify-center rounded bg-blue-100"
            >
              📄
            </div>
            <div>
              <h3 className="font-medium">{evidence.name}</h3>
              <p className="text-sm text-gray-500">Uploaded: {evidence.uploadDate}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span
              className={`rounded px-2 py-1 text-xs ${
                evidence.status === 'approved'
                  ? 'bg-green-100 text-green-800'
                  : evidence.status === 'pending'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
              }`}
            >
              {evidence.status}
            </span>
          </div>

          {evidence.status === 'pending' && (
            <div className="flex gap-2">
              <Button
                onClick={() => onApprove?.(evidence.id)}
                className="bg-green-600 hover:bg-green-700"
              >
                Approve
              </Button>
              <Button
                variant="outline"
                onClick={() => onReject?.(evidence.id)}
                className="border-red-300 text-red-600 hover:bg-red-50"
              >
                Reject
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
