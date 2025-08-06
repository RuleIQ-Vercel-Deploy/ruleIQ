import * as React from 'react';

import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
  elevated?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, glass = false, elevated = false, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        // Base styles
        'rounded-xl transition-all duration-250',
        
        // Conditional styles
        glass ? [
          'glass-white',
          'hover:shadow-elevation-high',
        ] : [
          'bg-card border border-neutral-200/50',
          elevated ? 'shadow-elevation-medium hover:shadow-elevation-high' : 'shadow-elevation-low hover:shadow-elevation-medium',
        ],
        
        // Hover effect
        'hover:-translate-y-0.5',
        
        // Gradient accent line
        'relative overflow-hidden',
        'before:absolute before:inset-x-0 before:top-0 before:h-1',
        'before:bg-gradient-to-r before:from-teal-700 before:via-teal-600 before:to-teal-400',
        'before:opacity-0 hover:before:opacity-100',
        'before:transition-opacity before:duration-300',
        
        className
      )}
      {...props}
    />
  ),
);
Card.displayName = 'Card';

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex flex-col space-y-1.5 p-6 md:p-8', className)} {...props} />
  ),
);
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('text-2xl font-semibold leading-none tracking-tight tracking-heading', className)}
      {...props}
    />
  ),
);
CardTitle.displayName = 'CardTitle';

const CardDescription = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('text-sm text-muted-foreground', className)} {...props} />
  ),
);
CardDescription.displayName = 'CardDescription';

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 md:p-8 pt-0', className)} {...props} />
  ),
);
CardContent.displayName = 'CardContent';

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex items-center p-6 md:p-8 pt-0', className)} {...props} />
  ),
);
CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
