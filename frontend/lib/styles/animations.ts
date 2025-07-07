/**
 * Animation utilities for consistent motion across the app
 * Based on accessibility best practices and performance optimization
 */

// Animation durations aligned with user perception
export const duration = {
  instant: 0,
  fast: 150,      // Quick feedback (hover states)
  normal: 250,    // Standard transitions
  slow: 500,      // Complex layout changes
  slower: 750,    // Page transitions
  slowest: 1000,  // Major state changes
} as const

// Easing functions for natural motion
export const easing = {
  // CSS-compatible strings
  linear: "linear",
  ease: "ease",
  easeIn: "ease-in",
  easeOut: "ease-out",
  easeInOut: "ease-in-out",
  
  // Custom cubic-bezier curves
  spring: "cubic-bezier(0.175, 0.885, 0.32, 1.275)",
  bounce: "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
  smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
  snappy: "cubic-bezier(0.4, 0, 0.6, 1)",
} as const

// Framer Motion variants for common patterns
export const variants = {
  // Fade animations
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  
  // Slide animations
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  },
  
  slideDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
  },
  
  slideLeft: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
  },
  
  slideRight: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
  },
  
  // Scale animations
  scaleIn: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 },
  },
  
  // Container animations (for staggered children)
  container: {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  },
  
  item: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
  },
}

// CSS transition classes for Tailwind
export const transitions = {
  // Base transition
  base: "transition-all duration-200 ease-out",
  
  // Specific property transitions
  colors: "transition-colors duration-200 ease-out",
  opacity: "transition-opacity duration-200 ease-out",
  transform: "transition-transform duration-200 ease-out",
  
  // Duration variants
  fast: "transition-all duration-150 ease-out",
  normal: "transition-all duration-250 ease-out",
  slow: "transition-all duration-500 ease-out",
} as const

// Animation helper functions
export const shouldReduceMotion = () => {
  if (typeof window === "undefined") return false
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches
}

// Create animation props with reduced motion support
export const createAnimationProps = (
  variant: keyof typeof variants,
  customDuration?: number
) => {
  if (shouldReduceMotion()) {
    return {
      initial: false,
      animate: variants[variant].animate,
      transition: { duration: 0 },
    }
  }
  
  return {
    ...variants[variant],
    transition: {
      duration: (customDuration || duration.normal) / 1000,
      ease: easing.smooth,
    },
  }
}

// Stagger delay calculator for lists
export const staggerDelay = (index: number, baseDelay: number = 50) => {
  return shouldReduceMotion() ? 0 : index * baseDelay
}

// CSS custom properties for animations
export const animationVars = {
  "--animation-duration": `${duration.normal}ms`,
  "--animation-easing": easing.smooth,
} as const

// Tailwind animation utilities
export const animationClasses = {
  // Entrance animations
  "animate-in": "animate-in",
  "fade-in": "fade-in",
  "slide-in-from-top": "slide-in-from-top-2",
  "slide-in-from-bottom": "slide-in-from-bottom-2",
  "slide-in-from-left": "slide-in-from-left-2",
  "slide-in-from-right": "slide-in-from-right-2",
  "zoom-in": "zoom-in-95",
  
  // Exit animations
  "animate-out": "animate-out",
  "fade-out": "fade-out",
  "slide-out-to-top": "slide-out-to-top-2",
  "slide-out-to-bottom": "slide-out-to-bottom-2",
  "slide-out-to-left": "slide-out-to-left-2",
  "slide-out-to-right": "slide-out-to-right-2",
  "zoom-out": "zoom-out-95",
} as const

export type AnimationDuration = keyof typeof duration
export type AnimationEasing = keyof typeof easing
export type AnimationVariant = keyof typeof variants
