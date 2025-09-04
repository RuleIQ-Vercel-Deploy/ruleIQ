'use client';

import { Trash2, Archive, ShieldCheck } from 'lucide-react';

import { Button } from '@/components/ui/button';

interface BulkActionsBarProps {
  selectedCount: number;
  onClearSelection: () => void;
}

export function BulkActionsBar({ selectedCount, onClearSelection }: BulkActionsBarProps) {
  return (
    <div className="fixed bottom-6 left-1/2 z-50 w-auto -translate-x-1/2">
      <div className="bg-eggshell-white border-oxford-blue/20 flex items-center gap-4 rounded-lg border p-3 shadow-2xl">
        <p className="text-oxford-blue text-sm font-medium">
          <span className="font-bold">{selectedCount}</span> item{selectedCount > 1 ? 's' : ''}{' '}
          selected
        </p>
        <div className="bg-oxford-blue/20 h-6 w-px" />
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <ShieldCheck />
            Change Status
          </Button>
          <Button variant="ghost" size="sm">
            <Archive />
            Archive
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-error hover:bg-error/10 hover:text-error"
          >
            <Trash2 />
            Delete
          </Button>
        </div>
        <div className="bg-oxford-blue/20 h-6 w-px" />
        <Button variant="link" size="sm" onClick={onClearSelection} className="text-oxford-blue">
          Clear
        </Button>
      </div>
    </div>
  );
}
