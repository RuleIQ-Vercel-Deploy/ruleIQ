'use client';

import * as CheckboxPrimitive from '@radix-ui/react-checkbox';
import { Check } from 'lucide-react';
import * as React from 'react';

import { cn } from '@/lib/utils';

const Checkbox = React.forwardRef<
  React.ElementRef<typeof CheckboxPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root> & {
    error?: boolean;
    success?: boolean;
  }
>(({ className, error, success, ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={cn(
      'peer h-4 w-4 shrink-0 rounded-sm border ring-offset-background transition-colors disabled:cursor-not-allowed disabled:opacity-50',
      // Default state
      'border-input focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
      // Oxford-blue focus and checked states
      'focus-visible:ring-oxford-blue data-[state=checked]:bg-oxford-blue data-[state=checked]:text-eggshell-white data-[state=checked]:border-oxford-blue',
      // Error state
      error &&
        'border-error focus-visible:ring-error data-[state=checked]:border-error data-[state=checked]:bg-error',
      // Success state
      success &&
        'border-success focus-visible:ring-success data-[state=checked]:border-success data-[state=checked]:bg-success',
      // Custom styling for ruleIQ theme
      'bg-eggshell-white border-oxford-blue/30',
      className,
    )}
    {...props}
  >
    <CheckboxPrimitive.Indicator className={cn('flex items-center justify-center text-current')}>
      <Check className="h-4 w-4" />
    </CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>
));
Checkbox.displayName = CheckboxPrimitive.Root.displayName;

export { Checkbox };
