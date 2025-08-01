// Button variant configuration for teal design system
export const ruleIQButtonConfig = {
  colors: {
    primary: {
      background: '#2C7A7B', // teal-600
      text: '#FFFFFF', // white
      hover: '#285E61', // teal-700
    },
    secondary: {
      background: '#FFFFFF', // white
      text: '#2C7A7B', // teal-600
      border: '#2C7A7B', // teal-600
      hover: {
        background: '#E6FFFA', // teal-50
        text: '#285E61', // teal-700
      },
    },
    ghost: {
      text: '#4B5563', // neutral-600
      hover: '#F3F4F6', // neutral-100
    },
    accent: {
      background: '#319795', // teal-500
      text: '#FFFFFF', // white
      hover: '#2C7A7B', // teal-600
    },
    success: {
      background: '#10B981', // emerald-600
      text: '#FFFFFF',
      hover: '#059669', // emerald-700
    },
    warning: {
      background: '#F59E0B', // amber-600
      text: '#FFFFFF',
      hover: '#D97706', // amber-700
    },
    error: {
      background: '#EF4444', // red-600
      text: '#FFFFFF',
      hover: '#DC2626', // red-700
    },
  },
  sizes: {
    small: {
      height: '2rem', // 32px
      padding: '0.375rem 0.75rem', // 6px 12px
      fontSize: '0.75rem', // 12px
      borderRadius: '0.375rem', // 6px
    },
    medium: {
      height: '2.5rem', // 40px
      padding: '0.5rem 1rem', // 8px 16px
      fontSize: '0.875rem', // 14px
      borderRadius: '0.375rem', // 6px
    },
    large: {
      height: '3rem', // 48px
      padding: '0.75rem 1.5rem', // 12px 24px
      fontSize: '1rem', // 16px
      borderRadius: '0.5rem', // 8px
    },
  },
  transitions: {
    default: 'all 0.2s ease-in-out',
    colors:
      'background-color 0.2s ease-in-out, color 0.2s ease-in-out, border-color 0.2s ease-in-out',
  },
  focus: {
    ring: '2px solid',
    ringOffset: '2px',
    outline: 'none',
  },
} as const;

// Type definitions for better TypeScript support
export type ButtonVariant = keyof typeof ruleIQButtonConfig.colors;
export type ButtonSize = keyof typeof ruleIQButtonConfig.sizes;

// Helper function to get button styles
export function getButtonStyles(variant: ButtonVariant, size: ButtonSize) {
  const colorConfig = ruleIQButtonConfig.colors[variant];
  const sizeConfig = ruleIQButtonConfig.sizes[size];

  return {
    color: colorConfig,
    size: sizeConfig,
    transition: ruleIQButtonConfig.transitions.colors,
    focus: ruleIQButtonConfig.focus,
  };
}
