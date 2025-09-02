import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import * as React from 'react';

import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md font-medium transition-all duration-250 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 relative overflow-hidden',
  {
    variants: {
      variant: {
        default: cn(
          'bg-gradient-to-r from-teal-700 via-teal-600 to-teal-500',
          'text-white shadow-elevation-low',
          'hover:shadow-elevation-medium hover:scale-[1.02]',
          'active:scale-[0.98]',
          'group',
        ),
        secondary: cn(
          'bg-teal-50 text-teal-700',
          'hover:bg-teal-100 hover:shadow-elevation-low',
          'transition-all duration-250',
        ),
        outline: cn(
          'border-2 border-teal-600/50 bg-transparent text-teal-700',
          'hover:bg-teal-50 hover:border-teal-600',
          'hover:shadow-elevation-low',
          'transition-all duration-250',
        ),
        ghost: cn(
          'text-teal-700 hover:bg-teal-50',
          'hover:text-teal-800',
          'transition-all duration-250',
        ),
        'ghost-ruleiq': 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-teal-600 underline-offset-4 hover:underline hover:text-teal-700',
        destructive: cn(
          'bg-red-600 text-white shadow-elevation-low',
          'hover:bg-red-700 hover:shadow-elevation-medium',
          'hover:scale-[1.02] active:scale-[0.98]',
        ),
        success: cn(
          'bg-green-600 text-white shadow-elevation-low',
          'hover:bg-green-700 hover:shadow-elevation-medium',
          'hover:scale-[1.02] active:scale-[0.98]',
        ),
        // Brand-specific variant using enhanced teal gradient
        accent: cn(
          'bg-gradient-to-r from-teal-400 to-teal-600',
          'text-white shadow-elevation-low',
          'hover:shadow-elevation-medium hover:scale-[1.02]',
          'active:scale-[0.98]',
        ),
      },
      size: {
        default: 'h-11 px-6 py-3 text-sm', // More generous padding
        sm: 'h-9 px-4 py-2 text-xs',
        lg: 'h-12 px-8 py-3 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { className, variant, size, asChild = false, loading = false, children, disabled, ...props },
    ref,
  ) => {
    const Comp = asChild ? Slot : 'button';
    const isDefaultVariant = variant === 'default' || variant === 'accent';

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={loading || disabled}
        aria-busy={loading}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin" aria-hidden="true" />
            <span className="sr-only">Loading</span>
            <span className="relative z-10">{children}</span>
          </>
        ) : (
          <>
            <span className="relative z-10">{children}</span>
            {/* Shimmer effect for gradient buttons */}
            {isDefaultVariant && !disabled && (
              <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
            )}
          </>
        )}
      </Comp>
    );
  },
);
Button.displayName = 'Button';

export { Button, buttonVariants };
