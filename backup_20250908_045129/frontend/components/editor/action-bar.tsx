'use client';

import { Save, Share, CheckCircle } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { editorData } from '@/lib/data/editor-data';

export function ActionBar() {
  const { status } = editorData.metadata;
  const statusVariant =
    status === 'Approved' ? 'success' : status === 'In Review' ? 'pending' : 'secondary';

  return (
    <div className="flex items-center justify-between border-t border-border bg-background p-2">
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-400">Status:</span>
        <Badge variant={statusVariant}>{status}</Badge>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          className="border-gold bg-transparent text-gold hover:bg-gold/10 hover:text-gold"
        >
          <Save className="mr-2 h-4 w-4" />
          Save
        </Button>
        <Button
          variant="outline"
          className="border-gold bg-transparent text-gold hover:bg-gold/10 hover:text-gold"
        >
          <Share className="mr-2 h-4 w-4" />
          Export
        </Button>
        <Button className="text-oxford-blue bg-gold hover:bg-gold/90">
          <CheckCircle className="mr-2 h-4 w-4" />
          Approve
        </Button>
      </div>
    </div>
  );
}
