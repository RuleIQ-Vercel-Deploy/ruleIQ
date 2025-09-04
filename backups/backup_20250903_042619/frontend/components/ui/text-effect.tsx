'use client';

import { motion, type Variants, type AnimationDefinition } from 'framer-motion';
import { useMemo } from 'react';
import { cn } from '@/lib/utils';

type TextEffectProps = {
  children: string;
  per?: 'word' | 'char' | 'line';
  as?: keyof React.JSX.IntrinsicElements;
  variants?: {
    container?: Variants;
    item?: Variants;
  };
  className?: string;
  preset?: 'blur-sm' | 'fade-in-blur' | 'scale' | 'fade' | 'slide';
  delay?: number;
  trigger?: boolean;
  onAnimationComplete?: (definition: AnimationDefinition) => void;
  onAnimationStart?: (definition: AnimationDefinition) => void;
  segmentWrapperClassName?: string;
  speedReveal?: number;
  speedSegment?: number;
};

const defaultContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const presetVariants = {
  fade: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  },
  'fade-in-blur': {
    hidden: { opacity: 0, filter: 'blur(4px)' },
    visible: { opacity: 1, filter: 'blur(0px)' },
  },
  scale: {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 },
  },
  slide: {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  },
  'blur-sm': {
    hidden: { opacity: 0, filter: 'blur(2px)' },
    visible: { opacity: 1, filter: 'blur(0px)' },
  },
};

export function TextEffect({
  children,
  per = 'word',
  as: Component = 'div',
  variants,
  className,
  preset = 'fade',
  delay = 0,
  trigger = true,
  onAnimationComplete,
  onAnimationStart,
  segmentWrapperClassName,
  speedReveal = 1,
  speedSegment = 1,
}: TextEffectProps) {
  const segments = useMemo(() => {
    if (per === 'word') {
      return children.split(' ');
    } else if (per === 'char') {
      return children.split('');
    } else if (per === 'line') {
      return children.split('\n');
    }
    return [children];
  }, [children, per]);

  const containerVariants = variants?.container || defaultContainerVariants;
  const itemVariants = variants?.item || presetVariants[preset];

  const MotionComponent = motion(Component);

  return (
    <MotionComponent
      initial="hidden"
      animate={trigger ? 'visible' : 'hidden'}
      variants={containerVariants}
      {...(onAnimationComplete && { onAnimationComplete })}
      {...(onAnimationStart && { onAnimationStart })}
      className={cn('inline-block', className)}
      style={{
        animationDelay: `${delay}ms`,
        animationDuration: `${1000 / speedReveal}ms`,
      }}
    >
      {segments.map((segment, index) => (
        <motion.span
          key={index}
          variants={itemVariants}
          className={cn('inline-block', segmentWrapperClassName)}
          style={{
            animationDuration: `${1000 / speedSegment}ms`,
          }}
        >
          {segment}
          {per === 'word' && index < segments.length - 1 && ' '}
        </motion.span>
      ))}
    </MotionComponent>
  );
}
