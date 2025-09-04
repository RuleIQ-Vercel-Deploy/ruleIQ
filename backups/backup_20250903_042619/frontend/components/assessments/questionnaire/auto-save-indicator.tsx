'use client';

import { Loader2, Check } from 'lucide-react';
import * as React from 'react';

export function AutoSaveIndicator() {
  const [status, setStatus] = React.useState<'idle' | 'saving' | 'saved'>('saved');

  // Simulate auto-saving
  React.useEffect(() => {
    const interval = setInterval(() => {
      setStatus('saving');
      setTimeout(() => {
        setStatus('saved');
      }, 1500);
    }, 10000); // Auto-save every 10 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      {status === 'saving' && <Loader2 className="h-4 w-4 animate-spin" />}
      {status === 'saved' && <Check className="text-success-foreground h-4 w-4" />}
      <span className="transition-colors duration-300">
        {status === 'saving' ? 'Saving...' : 'All changes saved'}
      </span>
    </div>
  );
}
