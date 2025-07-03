"use client";

import { Loader2, CheckCircle, XCircle, Zap } from 'lucide-react';
import React from 'react';

import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface StreamingProgressProps {
  progress: number;
  status: 'idle' | 'streaming' | 'complete' | 'error';
  className?: string;
  showPercentage?: boolean;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  elapsedTime?: number;
}

export function StreamingProgress({
  progress,
  status,
  className,
  showPercentage = true,
  showIcon = true,
  size = 'md',
  message,
  elapsedTime
}: StreamingProgressProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'streaming':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-600" />;
      case 'complete':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Zap className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'streaming':
        return 'bg-blue-600';
      case 'complete':
        return 'bg-green-600';
      case 'error':
        return 'bg-red-600';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusMessage = () => {
    if (message) return message;
    
    switch (status) {
      case 'streaming':
        return 'Generating AI response...';
      case 'complete':
        return 'Analysis complete';
      case 'error':
        return 'An error occurred';
      default:
        return 'Ready to start';
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progressHeight = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  }[size];

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {showIcon && getStatusIcon()}
          <span className={cn(
            "font-medium",
            size === 'sm' && "text-sm",
            size === 'lg' && "text-lg"
          )}>
            {getStatusMessage()}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          {showPercentage && (
            <Badge variant="outline" className="text-xs">
              {Math.round(progress)}%
            </Badge>
          )}
          {elapsedTime !== undefined && (
            <Badge variant="outline" className="text-xs">
              {formatTime(elapsedTime)}
            </Badge>
          )}
        </div>
      </div>
      
      <Progress 
        value={progress} 
        className={cn(progressHeight)}
        indicatorClassName={getStatusColor()}
      />
      
      {status === 'streaming' && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <div className="flex gap-1">
            <div className="w-1 h-1 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="w-1 h-1 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="w-1 h-1 bg-blue-600 rounded-full animate-bounce"></div>
          </div>
          <span>Real-time AI processing</span>
        </div>
      )}
    </div>
  );
}