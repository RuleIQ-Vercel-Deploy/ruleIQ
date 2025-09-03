'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

type GradientBackgroundProps = {
  children: React.ReactNode;
  containerClassName?: string;
  className?: string;
  animate?: boolean;
};

export function GradientBackground({
  children,
  containerClassName,
  className,
  animate = true,
}: GradientBackgroundProps) {
  return (
    <div className={cn('group relative', containerClassName)}>
      {animate && (
        <motion.div
          className="absolute inset-0 rounded-[inherit] opacity-75 blur-sm"
          style={{
            background: `
              conic-gradient(
                from 0deg at 50% 50%,
                hsl(var(--primary)) 0deg,
                hsl(var(--primary) / 0.8) 60deg,
                hsl(var(--primary) / 0.4) 120deg,
                hsl(var(--primary)) 180deg,
                hsl(var(--primary) / 0.8) 240deg,
                hsl(var(--primary) / 0.4) 300deg,
                hsl(var(--primary)) 360deg
              )
            `,
          }}
          animate={{
            rotate: [0, 360],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      )}

      <div
        className={cn(
          'relative z-10 rounded-[inherit] bg-background/95 backdrop-blur-sm',
          className,
        )}
      >
        {children}
      </div>
    </div>
  );
}
