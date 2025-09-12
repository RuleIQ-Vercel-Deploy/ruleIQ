'use client';

import React from 'react';
import { TrustLevel } from '@/lib/websocket/types';
import { cn } from '@/lib/utils';
import {
  Lock,
  UserCheck,
  Eye,
  Handshake,
  Star,
  Shield,
  ChevronUp
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Progress } from '@/components/ui/progress';

interface TrustIndicatorProps {
  trustLevel: TrustLevel;
  showProgress?: boolean;
  progressValue?: number;
  size?: 'sm' | 'md' | 'lg';
}

const trustLevelConfig = {
  [TrustLevel.L0_OBSERVED]: {
    label: 'Observed',
    description: 'All actions require explicit approval',
    icon: Lock,
    color: 'text-red-500',
    bgColor: 'bg-red-50 dark:bg-red-950',
    borderColor: 'border-red-200 dark:border-red-800',
    progressColor: 'bg-red-500',
  },
  [TrustLevel.L1_ASSISTED]: {
    label: 'Assisted',
    description: 'Can suggest actions with approval',
    icon: UserCheck,
    color: 'text-orange-500',
    bgColor: 'bg-orange-50 dark:bg-orange-950',
    borderColor: 'border-orange-200 dark:border-orange-800',
    progressColor: 'bg-orange-500',
  },
  [TrustLevel.L2_SUPERVISED]: {
    label: 'Supervised',
    description: 'Can execute with monitoring',
    icon: Eye,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    progressColor: 'bg-yellow-500',
  },
  [TrustLevel.L3_DELEGATED]: {
    label: 'Delegated',
    description: 'Can execute autonomously in scope',
    icon: Handshake,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-950',
    borderColor: 'border-blue-200 dark:border-blue-800',
    progressColor: 'bg-blue-500',
  },
  [TrustLevel.L4_AUTONOMOUS]: {
    label: 'Autonomous',
    description: 'Full autonomous operation',
    icon: Star,
    color: 'text-green-500',
    bgColor: 'bg-green-50 dark:bg-green-950',
    borderColor: 'border-green-200 dark:border-green-800',
    progressColor: 'bg-green-500',
  },
};

export function TrustIndicator({
  trustLevel,
  showProgress = false,
  progressValue = 0,
  size = 'md',
}: TrustIndicatorProps) {
  const config = trustLevelConfig[trustLevel];
  const Icon = config.icon;
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  const [isUpgrading, setIsUpgrading] = React.useState(false);

  // Simulate trust upgrade animation
  React.useEffect(() => {
    if (progressValue >= 100 && trustLevel < TrustLevel.L4_AUTONOMOUS) {
      setIsUpgrading(true);
      setTimeout(() => setIsUpgrading(false), 600);
    }
  }, [progressValue, trustLevel]);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex flex-col gap-2">
            {/* Trust Badge */}
            <div
              className={cn(
                'inline-flex items-center gap-2 rounded-full border transition-all',
                sizeClasses[size],
                config.bgColor,
                config.borderColor,
                isUpgrading && 'animate-pulse scale-105'
              )}
            >
              <Shield className={cn(iconSizes[size], config.color)} />
              <Icon className={cn(iconSizes[size], config.color)} />
              <span className={cn('font-medium', config.color)}>
                L{trustLevel} - {config.label}
              </span>
              {isUpgrading && (
                <ChevronUp className={cn(
                  iconSizes[size],
                  config.color,
                  'animate-bounce'
                )} />
              )}
            </div>

            {/* Progress to Next Level */}
            {showProgress && trustLevel < TrustLevel.L4_AUTONOMOUS && (
              <div className="w-full space-y-1">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Progress to L{trustLevel + 1}</span>
                  <span>{progressValue}%</span>
                </div>
                <Progress
                  value={progressValue}
                  className="h-1.5"
                  indicatorClassName={config.progressColor}
                />
              </div>
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <div className="space-y-1">
            <div className="font-semibold">
              Trust Level {trustLevel}: {config.label}
            </div>
            <div className="text-sm text-muted-foreground">
              {config.description}
            </div>
            {showProgress && trustLevel < TrustLevel.L4_AUTONOMOUS && (
              <div className="text-sm text-muted-foreground pt-1 border-t">
                {100 - progressValue}% more interactions needed for upgrade
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}