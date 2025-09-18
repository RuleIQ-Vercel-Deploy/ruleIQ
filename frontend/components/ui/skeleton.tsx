import { cn } from '@/lib/utils';

import type React from 'react';

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'animate-shimmer rounded-lg',
        // Purple shimmer effect for new design system
        'bg-gradient-to-r from-neutral-200 via-purple-100 to-neutral-200 bg-[length:200%_100%]',
        className,
      )}
      {...props}
    />
  );
}

export { Skeleton };
