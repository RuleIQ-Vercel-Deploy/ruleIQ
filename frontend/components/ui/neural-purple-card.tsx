import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

import { cn } from '@/lib/utils';

const cardVariants = cva(
  'rounded-lg transition-all duration-300 ease-in-out',
  {
    variants: {
      variant: {
        default:
          'bg-white border border-silver-200 hover:border-purple-200/50 hover:shadow-lg hover:shadow-purple-100/20',
        ghost:
          'bg-transparent hover:bg-purple-50/50',
        outlined:
          'bg-transparent border-2 border-purple-200 hover:border-purple-400',
        elevated:
          'bg-white shadow-md hover:shadow-xl hover:shadow-purple-100/30',
        glass:
          'bg-white/80 backdrop-blur-lg border border-silver-200/50 hover:bg-white/90',
        gradient:
          'bg-gradient-to-br from-purple-50 to-silver-100 border border-purple-200/30',
      },
      padding: {
        none: '',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      padding: 'md',
    },
  }
);

export interface NeuralPurpleCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  asChild?: boolean;
  interactive?: boolean;
  disabled?: boolean;
}

const NeuralPurpleCard = React.forwardRef<HTMLDivElement, NeuralPurpleCardProps>(
  ({ className, variant, padding, interactive = false, disabled = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          cardVariants({ variant, padding }),
          interactive && 'cursor-pointer hover:scale-[1.02]',
          disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
          className
        )}
        role={interactive ? 'button' : undefined}
        tabIndex={interactive && !disabled ? 0 : undefined}
        aria-disabled={disabled}
        {...props}
      />
    );
  }
);

NeuralPurpleCard.displayName = 'NeuralPurpleCard';

const NeuralPurpleCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 pb-4', className)}
    {...props}
  />
));

NeuralPurpleCardHeader.displayName = 'NeuralPurpleCardHeader';

const NeuralPurpleCardTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('text-2xl font-extralight text-gray-900', className)}
    {...props}
  />
));

NeuralPurpleCardTitle.displayName = 'NeuralPurpleCardTitle';

const NeuralPurpleCardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('text-sm font-light text-gray-600', className)}
    {...props}
  />
));

NeuralPurpleCardDescription.displayName = 'NeuralPurpleCardDescription';

const NeuralPurpleCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('font-light', className)} {...props} />
));

NeuralPurpleCardContent.displayName = 'NeuralPurpleCardContent';

const NeuralPurpleCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center pt-4 border-t border-silver-200/50 mt-4', className)}
    {...props}
  />
));

NeuralPurpleCardFooter.displayName = 'NeuralPurpleCardFooter';

// Feature Card Component
interface FeatureCardProps extends NeuralPurpleCardProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  badge?: string;
  action?: React.ReactNode;
}

export const FeatureCard = React.forwardRef<HTMLDivElement, FeatureCardProps>(
  ({ icon, title, description, badge, action, children, className, ...props }, ref) => {
    return (
      <NeuralPurpleCard ref={ref} className={cn('group', className)} {...props}>
        <NeuralPurpleCardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              {icon && (
                <div className="p-2 rounded-lg bg-purple-50 text-purple-600 group-hover:bg-purple-100 transition-colors">
                  {icon}
                </div>
              )}
              <div>
                <NeuralPurpleCardTitle className="text-lg font-normal">
                  {title}
                </NeuralPurpleCardTitle>
                {description && (
                  <NeuralPurpleCardDescription>{description}</NeuralPurpleCardDescription>
                )}
              </div>
            </div>
            {badge && (
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-700">
                {badge}
              </span>
            )}
          </div>
        </NeuralPurpleCardHeader>
        {children && <NeuralPurpleCardContent>{children}</NeuralPurpleCardContent>}
        {action && <NeuralPurpleCardFooter>{action}</NeuralPurpleCardFooter>}
      </NeuralPurpleCard>
    );
  }
);

FeatureCard.displayName = 'FeatureCard';

// Stat Card Component
interface StatCardProps extends NeuralPurpleCardProps {
  label: string;
  value: string | number;
  change?: {
    value: string;
    trend: 'up' | 'down' | 'neutral';
  };
  icon?: React.ReactNode;
}

export const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  ({ label, value, change, icon, className, ...props }, ref) => {
    const getTrendColor = (trend: 'up' | 'down' | 'neutral') => {
      switch (trend) {
        case 'up':
          return 'text-emerald-600';
        case 'down':
          return 'text-red-600';
        case 'neutral':
          return 'text-gray-600';
      }
    };

    return (
      <NeuralPurpleCard ref={ref} className={cn('relative overflow-hidden', className)} {...props}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-light text-gray-600">{label}</p>
            <p className="text-3xl font-extralight text-purple-600 mt-2">{value}</p>
            {change && (
              <p className={cn('text-sm font-light mt-2', getTrendColor(change.trend))}>
                {change.trend === 'up' ? '↑' : change.trend === 'down' ? '↓' : '→'} {change.value}
              </p>
            )}
          </div>
          {icon && (
            <div className="p-3 rounded-lg bg-purple-50 text-purple-600">
              {icon}
            </div>
          )}
        </div>
        <div className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-tl from-purple-50 to-transparent opacity-50 rounded-tl-full" />
      </NeuralPurpleCard>
    );
  }
);

StatCard.displayName = 'StatCard';

// Card Grid Component
interface CardGridProps {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const CardGrid: React.FC<CardGridProps> = ({
  children,
  columns = 3,
  gap = 'md',
  className,
}) => {
  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8',
  };

  const columnClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div
      className={cn(
        'grid',
        columnClasses[columns],
        gapClasses[gap],
        className
      )}
    >
      {children}
    </div>
  );
};

export {
  NeuralPurpleCard,
  NeuralPurpleCardHeader,
  NeuralPurpleCardFooter,
  NeuralPurpleCardTitle,
  NeuralPurpleCardDescription,
  NeuralPurpleCardContent,
  cardVariants,
};