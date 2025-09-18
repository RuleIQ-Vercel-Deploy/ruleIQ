'use client';

import React from 'react';
import { ConnectionState } from '@/lib/websocket/types';
import { cn } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';
import { Wifi, WifiOff, Loader2, RefreshCw, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';

interface ConnectionStatusIndicatorProps {
  connectionState: ConnectionState;
  onRetry?: () => void;
  showDetails?: boolean;
}

export function ConnectionStatusIndicator({
  connectionState,
  onRetry,
  showDetails = false
}: ConnectionStatusIndicatorProps) {
  const { connected, connecting, error, retryCount, lastConnectedAt } = connectionState;

  // Determine status color and icon
  const getStatusIndicator = () => {
    if (connecting) {
      return {
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-500',
        icon: <Loader2 className="w-4 h-4 animate-spin" />,
        label: 'Connecting...',
        description: retryCount > 0 ? `Reconnection attempt ${retryCount}` : 'Establishing connection'
      };
    }

    if (connected) {
      return {
        color: 'text-green-500',
        bgColor: 'bg-green-500',
        icon: <Wifi className="w-4 h-4" />,
        label: 'Connected',
        description: lastConnectedAt ? `Since ${format(lastConnectedAt, 'HH:mm:ss')}` : 'Connection established'
      };
    }

    return {
      color: 'text-red-500',
      bgColor: 'bg-red-500',
      icon: <WifiOff className="w-4 h-4" />,
      label: 'Disconnected',
      description: error ? error.message : 'Connection lost'
    };
  };

  const status = getStatusIndicator();

  if (showDetails) {
    return (
      <div className="flex items-center gap-2 text-sm">
        <div className="flex items-center gap-1.5">
          <span className={cn('relative flex h-2 w-2', status.color)}>
            <span className={cn(
              'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
              status.bgColor,
              !connecting && 'hidden'
            )} />
            <span className={cn(
              'relative inline-flex rounded-full h-2 w-2',
              status.bgColor
            )} />
          </span>
          <span className="text-muted-foreground">{status.label}</span>
        </div>

        {/* Retry button for disconnected state */}
        {!connected && !connecting && onRetry && (
          <Button
            size="sm"
            variant="ghost"
            onClick={onRetry}
            className="h-6 px-2"
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            Retry
          </Button>
        )}

        {/* Error indicator */}
        {error && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <AlertCircle className="w-4 h-4 text-destructive" />
              </TooltipTrigger>
              <TooltipContent>
                <p>{error.message}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>
    );
  }

  // Compact view (default)
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex items-center gap-1.5">
            {/* Animated connection indicator */}
            <span className={cn('relative flex h-2 w-2', status.color)}>
              <span className={cn(
                'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
                status.bgColor,
                !connecting && 'hidden'
              )} />
              <span className={cn(
                'relative inline-flex rounded-full h-2 w-2',
                status.bgColor
              )} />
            </span>
            <span className="text-xs text-muted-foreground">
              {status.label}
            </span>
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <div className="space-y-1">
            <p className="font-semibold">{status.label}</p>
            <p className="text-xs">{status.description}</p>
            {retryCount > 0 && (
              <p className="text-xs text-muted-foreground">
                Retry attempts: {retryCount}
              </p>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}