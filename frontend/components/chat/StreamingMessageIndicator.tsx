'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface StreamingMessageIndicatorProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function StreamingMessageIndicator({
  size = 'sm',
  className
}: StreamingMessageIndicatorProps) {
  const dotSize = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5'
  };

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1',
        className
      )}
      aria-label="Message streaming in progress"
      role="status"
    >
      <span
        className={cn(
          'rounded-full bg-blue-500',
          dotSize[size],
          'animate-pulse'
        )}
        style={{
          animationDelay: '0ms',
          animationDuration: '1.4s'
        }}
      />
      <span
        className={cn(
          'rounded-full bg-blue-500',
          dotSize[size],
          'animate-pulse'
        )}
        style={{
          animationDelay: '200ms',
          animationDuration: '1.4s'
        }}
      />
      <span
        className={cn(
          'rounded-full bg-blue-500',
          dotSize[size],
          'animate-pulse'
        )}
        style={{
          animationDelay: '400ms',
          animationDuration: '1.4s'
        }}
      />
      <span className="sr-only">Streaming message...</span>
    </div>
  );
}