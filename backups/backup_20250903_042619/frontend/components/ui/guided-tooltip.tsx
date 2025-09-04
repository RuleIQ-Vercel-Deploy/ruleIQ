'use client';

import { Info } from 'lucide-react';
import * as React from 'react';

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface GuidedTooltipProps {
  children: React.ReactNode;
  content: string | React.ReactNode;
  step?: {
    current: number;
    total: number;
  };
  side?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
  className?: string;
  showIcon?: boolean;
  delayDuration?: number;
}

export function GuidedTooltip({
  children,
  content,
  step,
  side = 'bottom',
  align = 'center',
  className,
  showIcon = false,
  delayDuration = 0,
}: GuidedTooltipProps) {
  return (
    <TooltipProvider delayDuration={delayDuration}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className={cn('inline-flex items-center gap-1', className)}>
            {children}
            {showIcon && <Info className="h-3.5 w-3.5 text-muted-foreground" />}
          </span>
        </TooltipTrigger>
        <TooltipContent side={side} align={align} sideOffset={8} className="max-w-xs">
          <div className="space-y-2">
            <div className="text-sm">{content}</div>
            {step && (
              <div className="border-t pt-2 text-xs text-muted-foreground">
                Step {step.current} of {step.total}
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

// Specialized tooltip for form fields
interface FormFieldTooltipProps {
  label: string;
  helpText: string;
  required?: boolean;
  children: React.ReactNode;
}

export function FormFieldTooltip({
  label,
  helpText,
  required = false,
  children,
}: FormFieldTooltipProps) {
  return (
    <div className="space-y-2">
      <GuidedTooltip content={helpText} showIcon side="right">
        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          {label}
          {required && <span className="ml-1 text-destructive">*</span>}
        </label>
      </GuidedTooltip>
      {children}
    </div>
  );
}

// Progress indicator for multi-step processes
interface GuidedProgressProps {
  steps: string[];
  currentStep: number;
}

export function GuidedProgress({ steps, currentStep }: GuidedProgressProps) {
  return (
    <div className="relative">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isCompleted = index < currentStep;
          const isCurrent = index === currentStep;

          return (
            <React.Fragment key={step}>
              <GuidedTooltip content={step} side="top">
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-medium transition-colors',
                      isCompleted && 'border-primary bg-primary text-primary-foreground',
                      isCurrent && 'border-primary text-primary',
                      !isCompleted && !isCurrent && 'border-muted text-muted-foreground',
                    )}
                  >
                    {index + 1}
                  </div>
                  <span className="mt-2 max-w-[80px] text-center text-xs text-muted-foreground">
                    {step}
                  </span>
                </div>
              </GuidedTooltip>
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    'h-0.5 flex-1 transition-colors',
                    isCompleted ? 'bg-primary' : 'bg-muted',
                  )}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
