'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Database, 
  Search, 
  Zap, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Network
} from 'lucide-react';
import { cn } from '@/lib/utils';

type ProcessingStage = 
  | 'analyzing'
  | 'searching_graph'
  | 'evaluating_evidence'
  | 'generating_response'
  | 'completed'
  | 'error';

interface IQProcessingIndicatorProps {
  stage: ProcessingStage;
  progress?: number;
  message?: string;
  estimatedTime?: number;
  className?: string;
}

const stageConfig: Record<ProcessingStage, {
  label: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  description: string;
}> = {
  analyzing: {
    label: 'Analyzing Query',
    icon: Brain,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    description: 'Understanding your compliance question...'
  },
  searching_graph: {
    label: 'Searching Knowledge Graph',
    icon: Network,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    description: 'Traversing compliance frameworks and regulations...'
  },
  evaluating_evidence: {
    label: 'Evaluating Evidence',
    icon: Search,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    description: 'Analyzing relevant regulatory sources...'
  },
  generating_response: {
    label: 'Generating Response',
    icon: Zap,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    description: 'Crafting personalized compliance guidance...'
  },
  completed: {
    label: 'Analysis Complete',
    icon: CheckCircle,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    description: 'Ready to provide compliance insights.'
  },
  error: {
    label: 'Analysis Failed',
    icon: AlertCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    description: 'Unable to complete analysis. Please try again.'
  }
};

export function IQProcessingIndicator({ 
  stage, 
  progress = 0, 
  message,
  estimatedTime,
  className 
}: IQProcessingIndicatorProps) {
  const [displayProgress, setDisplayProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const config = stageConfig[stage];
  const Icon = config.icon;

  // Animate progress
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayProgress(progress);
    }, 100);
    return () => clearTimeout(timer);
  }, [progress]);

  // Track elapsed time
  useEffect(() => {
    if (stage === 'completed' || stage === 'error') {
      return;
    }

    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [stage]);

  // Reset elapsed time when stage changes
  useEffect(() => {
    setElapsedTime(0);
  }, [stage]);

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getProgressSteps = () => {
    const stages: ProcessingStage[] = ['analyzing', 'searching_graph', 'evaluating_evidence', 'generating_response'];
    const currentIndex = stages.indexOf(stage);
    
    return stages.map((stageKey, index) => ({
      ...stageConfig[stageKey],
      isActive: index === currentIndex,
      isCompleted: index < currentIndex,
      step: index + 1
    }));
  };

  return (
    <Card className={cn('border-l-4 border-l-blue-500', className)}>
      <CardContent className="p-6">
        <div className="space-y-6">
          {/* Current Stage Header */}
          <div className="flex items-center gap-3">
            <div className={cn('p-2 rounded-lg', config.bgColor)}>
              {stage === 'error' ? (
                <Icon className={cn('w-5 h-5', config.color)} />
              ) : stage === 'completed' ? (
                <Icon className={cn('w-5 h-5', config.color)} />
              ) : (
                <Icon className={cn('w-5 h-5 animate-pulse', config.color)} />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-lg">{config.label}</h3>
                {stage !== 'completed' && stage !== 'error' && (
                  <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                )}
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {message || config.description}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                <Brain className="w-3 h-3 mr-1" />
                IQ Agent
              </Badge>
              {elapsedTime > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {formatTime(elapsedTime)}
                  {estimatedTime && ` / ~${formatTime(estimatedTime)}`}
                </Badge>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          {stage !== 'completed' && stage !== 'error' && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Processing...</span>
                <span className="text-gray-600">{Math.round(displayProgress)}%</span>
              </div>
              <Progress 
                value={displayProgress} 
                className="h-2"
                indicatorClassName="bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500"
              />
            </div>
          )}

          {/* Stage Steps */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {getProgressSteps().map((step, index) => {
              const StepIcon = step.icon;
              return (
                <div 
                  key={index}
                  className={cn(
                    'flex flex-col items-center text-center p-3 rounded-lg border transition-all',
                    step.isActive && 'border-blue-200 bg-blue-50 scale-105',
                    step.isCompleted && 'border-green-200 bg-green-50',
                    !step.isActive && !step.isCompleted && 'border-gray-200 bg-gray-50'
                  )}
                >
                  <div className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center mb-2 transition-all',
                    step.isActive && 'bg-blue-100',
                    step.isCompleted && 'bg-green-100',
                    !step.isActive && !step.isCompleted && 'bg-gray-100'
                  )}>
                    {step.isCompleted ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : step.isActive ? (
                      <StepIcon className={cn('w-4 h-4 animate-pulse', step.color)} />
                    ) : (
                      <span className="text-xs font-medium text-gray-500">{step.step}</span>
                    )}
                  </div>
                  <span className={cn(
                    'text-xs font-medium',
                    step.isActive && 'text-blue-700',
                    step.isCompleted && 'text-green-700',
                    !step.isActive && !step.isCompleted && 'text-gray-500'
                  )}>
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Additional Context */}
          {stage === 'searching_graph' && (
            <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg border border-purple-200">
              <Database className="w-4 h-4 text-purple-600" />
              <span className="text-sm text-purple-700">
                Analyzing 20+ compliance frameworks and regulatory sources...
              </span>
            </div>
          )}

          {stage === 'evaluating_evidence' && (
            <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
              <Search className="w-4 h-4 text-green-600" />
              <span className="text-sm text-green-700">
                Cross-referencing with primary regulatory sources...
              </span>
            </div>
          )}

          {stage === 'generating_response' && (
            <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg border border-orange-200">
              <Zap className="w-4 h-4 text-orange-600" />
              <span className="text-sm text-orange-700">
                Applying trust gradient and confidence scoring...
              </span>
            </div>
          )}

          {stage === 'error' && (
            <div className="flex items-center gap-2 p-3 bg-red-50 rounded-lg border border-red-200">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <span className="text-sm text-red-700">
                {message || 'An unexpected error occurred during analysis. Please try again.'}
              </span>
            </div>
          )}

          {stage === 'completed' && (
            <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-sm text-green-700">
                GraphRAG analysis completed successfully. Response ready.
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}