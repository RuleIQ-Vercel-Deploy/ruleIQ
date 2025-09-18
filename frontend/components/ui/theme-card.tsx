import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ThemeCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined' | 'silver';
  noPadding?: boolean;
}

const ThemeCard = React.forwardRef<HTMLDivElement, ThemeCardProps>(
  ({ className, variant = 'default', noPadding = false, children, ...props }, ref) => {
    const variantClasses = {
      default: 'bg-white border-purple-100',
      elevated: 'bg-white border-purple-100 shadow-lg',
      outlined: 'bg-transparent border-purple-200',
      silver: 'bg-gray-50 border-purple-100',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg border transition-all duration-200',
          'hover:border-purple-200 hover:shadow-md',
          variantClasses[variant],
          !noPadding && 'p-6',
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

ThemeCard.displayName = 'ThemeCard';

const ThemeCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 pb-6', className)}
    {...props}
  />
));

ThemeCardHeader.displayName = 'ThemeCardHeader';

const ThemeCardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-2xl font-extralight leading-none tracking-tight text-gray-900',
      className
    )}
    {...props}
  >
    {children}
  </h3>
));

ThemeCardTitle.displayName = 'ThemeCardTitle';

const ThemeCardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm font-light text-gray-600', className)}
    {...props}
  />
));

ThemeCardDescription.displayName = 'ThemeCardDescription';

const ThemeCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('', className)} {...props} />
));

ThemeCardContent.displayName = 'ThemeCardContent';

const ThemeCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center pt-6', className)}
    {...props}
  />
));

ThemeCardFooter.displayName = 'ThemeCardFooter';

export {
  ThemeCard,
  ThemeCardHeader,
  ThemeCardTitle,
  ThemeCardDescription,
  ThemeCardContent,
  ThemeCardFooter,
};