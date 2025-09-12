'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface TypingIndicatorProps {
  agentName?: string;
  className?: string;
}

export function TypingIndicator({ 
  agentName = 'Agent',
  className 
}: TypingIndicatorProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      {/* Agent Avatar */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
        A
      </div>
      
      {/* Typing Bubble */}
      <div className="bg-muted rounded-lg px-4 py-3 flex items-center gap-2">
        <span className="text-sm text-muted-foreground">
          {agentName} is typing
        </span>
        
        {/* Animated Dots */}
        <div className="flex gap-1">
          <span 
            className="w-2 h-2 bg-primary rounded-full animate-bounce"
            style={{ animationDelay: '0ms' }}
          />
          <span 
            className="w-2 h-2 bg-primary rounded-full animate-bounce"
            style={{ animationDelay: '150ms' }}
          />
          <span 
            className="w-2 h-2 bg-primary rounded-full animate-bounce"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  );
}