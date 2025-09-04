import { type Variants } from 'framer-motion';

/**
 * Framer Motion animation variants for consistent animations across the app
 */

// Fade animations
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    y: -10,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

export const fadeInDown: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
};

// Scale animations
export const scaleIn: Variants = {
  hidden: { scale: 0.8, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  exit: {
    scale: 0.9,
    opacity: 0,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

export const scaleHover: Variants = {
  initial: { scale: 1 },
  hover: {
    scale: 1.05,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
  tap: {
    scale: 0.95,
    transition: { duration: 0.1 },
  },
};

// Slide animations
export const slideInRight: Variants = {
  hidden: { x: 100, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
  exit: {
    x: -50,
    opacity: 0,
    transition: { duration: 0.3, ease: 'easeIn' },
  },
};

export const slideInLeft: Variants = {
  hidden: { x: -100, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
};

// Stagger children animations
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

// Card animations
export const cardHover: Variants = {
  initial: {
    scale: 1,
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  },
  hover: {
    scale: 1.02,
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  tap: {
    scale: 0.98,
    transition: { duration: 0.1 },
  },
};

// Button animations
export const buttonPress: Variants = {
  initial: { scale: 1 },
  hover: {
    scale: 1.05,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
  tap: {
    scale: 0.95,
    transition: { duration: 0.1 },
  },
};

export const buttonGlow: Variants = {
  initial: {
    boxShadow: '0 0 0 0 rgba(203, 150, 62, 0)', // Gold color
  },
  hover: {
    boxShadow: '0 0 20px 0 rgba(203, 150, 62, 0.3)',
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

// Page transitions
export const pageTransition: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: { duration: 0.3, ease: 'easeIn' },
  },
};

// Modal/Dialog animations
export const modalOverlay: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

export const modalContent: Variants = {
  hidden: { scale: 0.9, opacity: 0, y: 20 },
  visible: {
    scale: 1,
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: [0.16, 1, 0.3, 1], // Custom easing
    },
  },
  exit: {
    scale: 0.95,
    opacity: 0,
    y: 10,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

// Skeleton loading animation
export const shimmer: Variants = {
  initial: { x: '-100%' },
  animate: {
    x: '100%',
    transition: {
      repeat: Infinity,
      duration: 1.5,
      ease: 'linear',
    },
  },
};

// Notification animations
export const notificationSlide: Variants = {
  initial: { x: 300, opacity: 0 },
  animate: {
    x: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 30,
    },
  },
  exit: {
    x: 300,
    opacity: 0,
    transition: { duration: 0.3, ease: 'easeIn' },
  },
};

// Progress animations
export const progressBar: Variants = {
  initial: { scaleX: 0 },
  animate: (progress: number) => ({
    scaleX: progress,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  }),
};

// Rotate animations
export const rotate360: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

// Accordion animations
export const accordionContent: Variants = {
  closed: {
    height: 0,
    opacity: 0,
    transition: { duration: 0.3, ease: 'easeInOut' },
  },
  open: {
    height: 'auto',
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeInOut' },
  },
};

// Tab animations
export const tabContent: Variants = {
  hidden: { opacity: 0, x: -10 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};

// Floating animation
export const floating: Variants = {
  animate: {
    y: [-5, 5, -5],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Pulse animation for attention
export const pulse: Variants = {
  animate: {
    scale: [1, 1.05, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Error shake animation
export const shake: Variants = {
  initial: { x: 0 },
  shake: {
    x: [-10, 10, -10, 10, 0],
    transition: {
      duration: 0.5,
      ease: 'easeInOut',
    },
  },
};
