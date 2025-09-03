/**
 * Central export for all animation utilities
 */

// Export all animation variants
export * from './variants';

// Export all animation hooks
export * from './hooks';

// Export all animated components
export * from './components';

// Export animation presets
export const animationPresets = {
  // Timing functions
  easing: {
    easeOut: [0.16, 1, 0.3, 1],
    easeIn: [0.4, 0, 1, 1],
    easeInOut: [0.4, 0, 0.2, 1],
    spring: { type: 'spring', stiffness: 300, damping: 30 },
  },

  // Duration presets
  duration: {
    fast: 0.2,
    normal: 0.3,
    slow: 0.5,
  },

  // Delay presets for stagger
  stagger: {
    fast: 0.05,
    normal: 0.1,
    slow: 0.15,
  },
};
