import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';

import { cn } from '@/lib/utils';

const typographyVariants = cva('', {
  variants: {
    variant: {
      h1: 'text-5xl font-bold text-neutral-900 leading-tight',
      h2: 'text-4xl font-bold text-neutral-900 leading-tight',
      h3: 'text-3xl font-semibold text-neutral-900 leading-snug',
      h4: 'text-2xl font-semibold text-neutral-900 leading-normal',
      h5: 'text-xl font-medium text-neutral-900 leading-normal',
      h6: 'text-lg font-medium text-neutral-900 leading-relaxed',
      body: 'text-base font-normal text-neutral-700 leading-relaxed',
      small: 'text-sm font-normal text-neutral-600 leading-normal',
      // Display variants
      'display-lg': 'text-6xl font-bold text-neutral-900 leading-none',
      'display-md': 'text-5xl font-bold text-neutral-900 leading-none',
      // Specialized variants
      'body-lg': 'text-lg font-normal text-neutral-700 leading-relaxed',
      'body-emphasis': 'text-base font-medium text-neutral-900 leading-normal',
      caption: 'text-xs font-normal text-neutral-500 leading-normal',
      overline: 'text-xs font-medium uppercase tracking-wider text-neutral-600',
    },
    color: {
      default: '',
      primary: 'text-teal-600',
      secondary: 'text-neutral-600',
      muted: 'text-neutral-500',
      brand: 'text-teal-600',
      accent: 'text-teal-700',
      error: 'text-error-600',
      success: 'text-success-600',
      warning: 'text-warning-600',
      info: 'text-info-600',
      white: 'text-white',
      dark: 'text-neutral-900',
    },
    align: {
      left: 'text-left',
      center: 'text-center',
      right: 'text-right',
      justify: 'text-justify',
    },
    weight: {
      normal: 'font-normal',
      medium: 'font-medium',
      semibold: 'font-semibold',
      bold: 'font-bold',
    },
  },
  defaultVariants: {
    variant: 'body',
    color: 'default',
    align: 'left',
  },
});

type TypographyProps<T extends React.ElementType = 'p'> = {
  as?: T;
  variant?: VariantProps<typeof typographyVariants>['variant'];
  color?: VariantProps<typeof typographyVariants>['color'];
  align?: VariantProps<typeof typographyVariants>['align'];
  weight?: VariantProps<typeof typographyVariants>['weight'];
  className?: string;
  children?: React.ReactNode;
} & React.ComponentPropsWithoutRef<T>;

const Typography = <T extends React.ElementType = 'p'>({
  as,
  variant = 'body',
  color = 'default',
  align = 'left',
  weight,
  className,
  children,
  ...props
}: TypographyProps<T>) => {
  const Component = as || getDefaultComponent(variant);

  return (
    <Component
      className={cn(typographyVariants({ variant, color, align, weight }), className)}
      {...props}
    >
      {children}
    </Component>
  );
};

// Helper to determine default HTML element based on variant
function getDefaultComponent(variant: TypographyProps['variant']): React.ElementType {
  switch (variant) {
    case 'h1':
    case 'display-lg':
    case 'display-md':
      return 'h1';
    case 'h2':
      return 'h2';
    case 'h3':
      return 'h3';
    case 'body':
    case 'body-lg':
    case 'body-emphasis':
      return 'p';
    case 'small':
    case 'caption':
    case 'overline':
      return 'span';
    default:
      return 'p';
  }
}

// Pre-configured components for convenience
export const H1: React.FC<Omit<TypographyProps<'h1'>, 'variant'>> = (props) => (
  <Typography as="h1" variant="h1" {...props} />
);

export const H2: React.FC<Omit<TypographyProps<'h2'>, 'variant'>> = (props) => (
  <Typography as="h2" variant="h2" {...props} />
);

export const H3: React.FC<Omit<TypographyProps<'h3'>, 'variant'>> = (props) => (
  <Typography as="h3" variant="h3" {...props} />
);

export const Body: React.FC<Omit<TypographyProps<'p'>, 'variant'>> = (props) => (
  <Typography as="p" variant="body" {...props} />
);

export const Small: React.FC<Omit<TypographyProps<'span'>, 'variant'>> = (props) => (
  <Typography as="span" variant="small" {...props} />
);

export const DisplayLarge: React.FC<Omit<TypographyProps<'h1'>, 'variant'>> = (props) => (
  <Typography as="h1" variant="display-lg" {...props} />
);

export const DisplayMedium: React.FC<Omit<TypographyProps<'h1'>, 'variant'>> = (props) => (
  <Typography as="h1" variant="display-md" {...props} />
);

export const Caption: React.FC<Omit<TypographyProps<'span'>, 'variant'>> = (props) => (
  <Typography as="span" variant="caption" {...props} />
);

export const Overline: React.FC<Omit<TypographyProps<'span'>, 'variant'>> = (props) => (
  <Typography as="span" variant="overline" {...props} />
);

export { Typography, typographyVariants };
