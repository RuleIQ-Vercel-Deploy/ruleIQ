'use client';

import { motion, type HTMLMotionProps } from 'framer-motion';
import { forwardRef, type ReactNode } from 'react';

import { useScrollAnimation } from './hooks';
import {
  fadeIn,
  fadeInUp,
  scaleIn,
  slideInRight,
  slideInLeft,
  staggerItem,
  cardHover,
  buttonPress,
} from './variants';

/**
 * Reusable animated components using Framer Motion
 */

// Animated div with fade in
interface AnimatedDivProps extends HTMLMotionProps<'div'> {
  children: ReactNode;
  delay?: number;
}

export const FadeIn = forwardRef<HTMLDivElement, AnimatedDivProps>(
  ({ children, delay = 0, ...props }, ref) => (
    <motion.div
      ref={ref}
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={fadeIn}
      transition={{ delay }}
      {...props}
    >
      {children}
    </motion.div>
  ),
);
FadeIn.displayName = 'FadeIn';

// Animated div with fade in and up
export const FadeInUp = forwardRef<HTMLDivElement, AnimatedDivProps>(
  ({ children, delay = 0, ...props }, ref) => (
    <motion.div
      ref={ref}
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={fadeInUp}
      transition={{ delay }}
      {...props}
    >
      {children}
    </motion.div>
  ),
);
FadeInUp.displayName = 'FadeInUp';

// Animated div with scale
export const ScaleIn = forwardRef<HTMLDivElement, AnimatedDivProps>(
  ({ children, delay = 0, ...props }, ref) => (
    <motion.div
      ref={ref}
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={scaleIn}
      transition={{ delay }}
      {...props}
    >
      {children}
    </motion.div>
  ),
);
ScaleIn.displayName = 'ScaleIn';

// Slide animations
export const SlideInRight = forwardRef<HTMLDivElement, AnimatedDivProps>(
  ({ children, delay = 0, ...props }, ref) => (
    <motion.div
      ref={ref}
      initial="hidden"
      animate="visible"
      exit="exit"
      variants={slideInRight}
      transition={{ delay }}
      {...props}
    >
      {children}
    </motion.div>
  ),
);
SlideInRight.displayName = 'SlideInRight';

export const SlideInLeft = forwardRef<HTMLDivElement, AnimatedDivProps>(
  ({ children, delay = 0, ...props }, ref) => (
    <motion.div
      ref={ref}
      initial="hidden"
      animate="visible"
      variants={slideInLeft}
      transition={{ delay }}
      {...props}
    >
      {children}
    </motion.div>
  ),
);
SlideInLeft.displayName = 'SlideInLeft';

// Stagger animations container
interface StaggerContainerProps extends HTMLMotionProps<'div'> {
  children: ReactNode;
  staggerChildren?: number;
  delayChildren?: number;
}

export const StaggerContainer = forwardRef<HTMLDivElement, StaggerContainerProps>(
  ({ children, staggerChildren = 0.1, delayChildren = 0, ...props }, ref) => (
    <motion.div
      ref={ref}
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            staggerChildren,
            delayChildren,
          },
        },
      }}
      {...props}
    >
      {children}
    </motion.div>
  ),
);
StaggerContainer.displayName = 'StaggerContainer';

// Stagger item
export const StaggerItem = forwardRef<HTMLDivElement, AnimatedDivProps>(
  ({ children, ...props }, ref) => (
    <motion.div ref={ref} variants={staggerItem} {...props}>
      {children}
    </motion.div>
  ),
);
StaggerItem.displayName = 'StaggerItem';

// Animated card with hover effects
interface AnimatedCardProps extends HTMLMotionProps<'div'> {
  children: ReactNode;
}

export const AnimatedCard = forwardRef<HTMLDivElement, AnimatedCardProps>(
  ({ children, ...props }, ref) => (
    <motion.div
      ref={ref}
      initial="initial"
      whileHover="hover"
      whileTap="tap"
      variants={cardHover}
      {...props}
    >
      {children}
    </motion.div>
  ),
);
AnimatedCard.displayName = 'AnimatedCard';

// Animated button
interface AnimatedButtonProps extends HTMLMotionProps<'button'> {
  children: ReactNode;
}

export const AnimatedButton = forwardRef<HTMLButtonElement, AnimatedButtonProps>(
  ({ children, ...props }, ref) => (
    <motion.button
      ref={ref}
      initial="initial"
      whileHover="hover"
      whileTap="tap"
      variants={buttonPress}
      {...props}
    >
      {children}
    </motion.button>
  ),
);
AnimatedButton.displayName = 'AnimatedButton';

// Scroll-triggered animation wrapper
interface ScrollAnimationProps extends AnimatedDivProps {
  threshold?: number;
}

export const ScrollAnimation: React.FC<ScrollAnimationProps> = ({
  children,
  threshold = 0.1,
  ...props
}) => {
  const animationProps = useScrollAnimation(threshold);

  return (
    <motion.div {...animationProps} {...props}>
      {children}
    </motion.div>
  );
};

// Page transition wrapper
export const PageTransition: React.FC<{ children: ReactNode }> = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.4, ease: 'easeInOut' }}
  >
    {children}
  </motion.div>
);

// Loading spinner
export const LoadingSpinner: React.FC<{ size?: number }> = ({ size = 24 }) => (
  <motion.div
    style={{ width: size, height: size }}
    animate={{ rotate: 360 }}
    transition={{
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    }}
  >
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeDasharray="32"
        strokeDashoffset="32"
        opacity="0.25"
      />
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeDasharray="32"
        strokeDashoffset="0"
      />
    </svg>
  </motion.div>
);
