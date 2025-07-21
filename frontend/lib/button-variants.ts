// Button variant configuration for easy customization
export const ruleIQButtonConfig = {
  colors: {
    primary: {
      background: '#002147', // oxford-blue
      text: '#F0EAD6', // eggshell-white
      hover: 'rgba(0, 33, 71, 0.9)',
    },
    secondary: {
      background: '#F0EAD6', // eggshell-white
      text: '#002147', // oxford-blue
      border: '#002147', // oxford-blue
      hover: {
        background: '#002147', // oxford-blue
        text: '#F0EAD6', // eggshell-white
      },
    },
    ghost: {
      text: '#002147', // oxford-blue
      hover: 'rgba(0, 33, 71, 0.1)',
    },
    accent: {
      background: '#FFD700', // gold
      text: '#002147', // oxford-blue
      hover: 'rgba(255, 215, 0, 0.9)',
    },
    success: {
      background: '#28A745',
      text: '#FFFFFF',
      hover: 'rgba(40, 167, 69, 0.9)',
    },
    warning: {
      background: '#FFC107',
      text: '#002147', // oxford-blue
      hover: 'rgba(255, 193, 7, 0.9)',
    },
    error: {
      background: '#DC3545',
      text: '#FFFFFF',
      hover: 'rgba(220, 53, 69, 0.9)',
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
