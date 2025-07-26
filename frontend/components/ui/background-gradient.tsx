'use client';

import { cn } from '@/lib/utils';

interface BackgroundGradientProps {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
  animate?: boolean;
}

export const BackgroundGradient = ({
  children,
  className,
  containerClassName,
  animate = true,
}: BackgroundGradientProps) => {
  return (
    <div className={cn('relative p-[4px] group', containerClassName)}>
      <div
        className={cn(
          'absolute inset-0 rounded-lg bg-gradient-to-r from-primary/50 via-primary to-primary/50',
          animate && 'animate-pulse',
          className
        )}
      />
      <div className="relative bg-background rounded-lg">
        {children}
      </div>
    </div>
  );
};
