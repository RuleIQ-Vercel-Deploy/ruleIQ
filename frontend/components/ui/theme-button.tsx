import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const themeButtonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-light transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-600 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-purple-600 text-white hover:bg-purple-700 active:bg-purple-800',
        secondary: 'bg-purple-100 text-purple-700 hover:bg-purple-200 active:bg-purple-300',
        ghost: 'hover:bg-purple-50 hover:text-purple-600 active:bg-purple-100',
        outline: 'border border-purple-200 bg-transparent hover:bg-purple-50 hover:border-purple-300',
        destructive: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800',
        link: 'text-purple-600 underline-offset-4 hover:underline hover:text-purple-700',
      },
      size: {
        sm: 'h-9 px-3',
        md: 'h-10 px-4 py-2',
        lg: 'h-11 px-8',
        icon: 'h-10 w-10',
      },
      fullWidth: {
        true: 'w-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ThemeButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof themeButtonVariants> {}

const ThemeButton = React.forwardRef<HTMLButtonElement, ThemeButtonProps>(
  ({ className, variant, size, fullWidth, ...props }, ref) => {
    return (
      <button
        className={cn(themeButtonVariants({ variant, size, fullWidth, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);

ThemeButton.displayName = 'ThemeButton';

export { ThemeButton, themeButtonVariants };