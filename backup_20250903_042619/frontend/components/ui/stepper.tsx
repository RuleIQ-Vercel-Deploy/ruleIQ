'use client';

import { Check } from 'lucide-react';
import * as React from 'react';

import { cn } from '@/lib/utils';

interface StepperProps {
  steps: string[];
  currentStep: number;
  className?: string;
}

export function Stepper({ steps, currentStep, className }: StepperProps) {
  return (
    <div className={cn('flex w-full items-center justify-between', className)}>
      {steps.map((step, index) => {
        const stepNumber = index + 1;
        const isActive = stepNumber === currentStep;
        const isCompleted = stepNumber < currentStep;

        return (
          <React.Fragment key={step}>
            <div className="flex flex-col items-center text-center">
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all duration-300',
                  isCompleted
                    ? 'text-oxford-blue border-gold bg-gold'
                    : isActive
                      ? 'border-gold text-gold'
                      : 'border-grey-600 text-grey-600',
                )}
              >
                {isCompleted ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <span className="font-bold">{stepNumber}</span>
                )}
              </div>
              <p
                className={cn(
                  'mt-2 text-xs font-medium transition-colors duration-300',
                  isActive || isCompleted ? 'text-eggshell-white' : 'text-grey-600',
                )}
              >
                {step}
              </p>
            </div>
            {index < steps.length - 1 && (
              <div
                className={cn(
                  'mx-4 h-0.5 flex-1 transition-colors duration-300',
                  isCompleted ? 'bg-gold' : 'bg-grey-600',
                )}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
