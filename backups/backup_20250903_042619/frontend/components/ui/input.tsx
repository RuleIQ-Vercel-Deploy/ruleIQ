import * as React from 'react';

import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  success?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, success, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50',
          // Default state
          'border-input focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          // Focus state using design system colors
          'focus-visible:border-ring focus-visible:ring-ring',
          // Error state
          error && 'border-error focus-visible:border-error focus-visible:ring-error',
          // Success state
          success && 'border-success focus-visible:border-success focus-visible:ring-success',
          // Remove hardcoded colors - let theme handle it
          className,
        )}
        aria-invalid={error ? 'true' : undefined}
        ref={ref}
        {...props}
      />
    );
  },
);
Input.displayName = 'Input';

export { Input };
