'use client';

import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { 
  HandHeart, 
  UserCheck, 
  Handshake, 
  Shield, 
  TrendingUp,
  Brain,
  CheckCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

type TrustLevel = 'helper' | 'advisor' | 'partner';

interface IQTrustIndicatorProps {
  trustLevel: TrustLevel;
  confidenceScore: number;
  interactionCount?: number;
  showProgress?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'compact' | 'detailed';
  className?: string;
}

const trustLevelConfig: Record<TrustLevel, {
  label: string;
  description: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  borderColor: string;
  progressColor: string;
  capabilities: string[];
  nextLevel?: {
    name: string;
    requirement: string;
  };
}> = {
  helper: {
    label: 'Transparent Helper',
    description: 'Shows reasoning, asks for confirmation before actions',
    icon: HandHeart,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    progressColor: 'bg-blue-500',
    capabilities: [
      'Provides compliance guidance',
      'Shows source references',
      'Explains reasoning clearly',
      'Asks for confirmation'
    ],
    nextLevel: {
      name: 'Trusted Advisor',
      requirement: 'Build trust through consistent accurate guidance'
    }
  },
  advisor: {
    label: 'Trusted Advisor',
    description: 'Makes confident suggestions, learns your preferences',
    icon: UserCheck,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    progressColor: 'bg-green-500',
    capabilities: [
      'Proactive compliance recommendations',
      'Learns organization preferences',
      'Contextual risk assessments',
      'Streamlined workflows'
    ],
    nextLevel: {
      name: 'Autonomous Partner',
      requirement: 'Demonstrate consistent value and reliability'
    }
  },
  partner: {
    label: 'Autonomous Partner',
    description: 'Takes initiative, prevents issues proactively',
    icon: Handshake,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    progressColor: 'bg-purple-500',
    capabilities: [
      'Autonomous compliance monitoring',
      'Predictive risk prevention',
      'Self-managing workflows',
      'Strategic compliance planning'
    ]
  }
};

export function IQTrustIndicator({
  trustLevel,
  confidenceScore,
  interactionCount = 0,
  showProgress = true,
  size = 'md',
  variant = 'compact',
  className
}: IQTrustIndicatorProps) {
  const [isUpgrading, setIsUpgrading] = useState(false);
  const [displayConfidence, setDisplayConfidence] = useState(0);
  const config = trustLevelConfig[trustLevel];
  const Icon = config.icon;

  // Animate confidence score
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayConfidence(confidenceScore);
    }, 200);
    return () => clearTimeout(timer);
  }, [confidenceScore]);

  // Simulate trust upgrade effect
  useEffect(() => {
    if (confidenceScore >= 85 && trustLevel !== 'partner') {
      setIsUpgrading(true);
      const timer = setTimeout(() => setIsUpgrading(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [confidenceScore, trustLevel]);

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-2',
    lg: 'text-base px-4 py-3',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  const getTrustProgress = () => {
    // Simple trust progression based on confidence and interactions
    const baseProgress = Math.min(confidenceScore, 100);
    const interactionBonus = Math.min(interactionCount * 2, 20);
    return Math.min(baseProgress + interactionBonus, 100);
  };

  if (variant === 'compact') {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge
              variant="outline"
              className={cn(
                'flex items-center gap-2 transition-all duration-300',
                sizeClasses[size],
                config.bgColor,
                config.borderColor,
                isUpgrading && 'animate-pulse scale-105',
                className
              )}
            >
              <Shield className={cn(iconSizes[size], config.color)} />
              <Icon className={cn(iconSizes[size], config.color)} />
              <span className={cn('font-medium', config.color)}>
                {config.label}
              </span>
              <span className="text-xs text-gray-500">
                {displayConfidence}%
              </span>
            </Badge>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-sm">
            <div className="space-y-3 p-2">
              <div>
                <div className="font-semibold text-sm mb-1">
                  {config.label}
                </div>
                <div className="text-xs text-gray-600">
                  {config.description}
                </div>
              </div>
              
              {showProgress && config.nextLevel && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span>Progress to {config.nextLevel.name}</span>
                    <span>{getTrustProgress()}%</span>
                  </div>
                  <Progress
                    value={getTrustProgress()}
                    className="h-1.5"
                    indicatorClassName={config.progressColor}
                  />
                  <div className="text-xs text-gray-500">
                    {config.nextLevel.requirement}
                  </div>
                </div>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <Card className={cn('border-l-4', config.borderColor.replace('border-', 'border-l-'), className)}>
      <CardContent className="p-4 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn('p-2 rounded-lg', config.bgColor)}>
              <Icon className={cn(iconSizes[size], config.color)} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className={cn('font-semibold', config.color)}>
                  {config.label}
                </h3>
                {isUpgrading && (
                  <TrendingUp className="w-4 h-4 text-green-500 animate-bounce" />
                )}
              </div>
              <p className="text-sm text-gray-600">
                {config.description}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className={cn('text-2xl font-bold', config.color)}>
              {displayConfidence}%
            </div>
            <div className="text-xs text-gray-500">
              Confidence
            </div>
          </div>
        </div>

        {/* Trust Progress */}
        {showProgress && config.nextLevel && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Progress to {config.nextLevel.name}</span>
              <span className="text-gray-500">{getTrustProgress()}%</span>
            </div>
            <Progress
              value={getTrustProgress()}
              className="h-2"
              indicatorClassName={cn(config.progressColor, 'transition-all duration-500')}
            />
            <div className="text-xs text-gray-600">
              {config.nextLevel.requirement}
            </div>
          </div>
        )}

        {/* Capabilities */}
        <div>
          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
            <Brain className="w-4 h-4 text-gray-600" />
            Current Capabilities
          </h4>
          <div className="grid grid-cols-1 gap-2">
            {config.capabilities.map((capability, index) => (
              <div key={index} className="flex items-center gap-2 text-sm">
                <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
                <span className="text-gray-700">{capability}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Interaction Stats */}
        {interactionCount > 0 && (
          <div className="flex items-center justify-between pt-2 border-t border-gray-200">
            <span className="text-sm text-gray-600">
              {interactionCount} successful interactions
            </span>
            <Badge variant="secondary" className="text-xs">
              <Shield className="w-3 h-3 mr-1" />
              Trust Building
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
}