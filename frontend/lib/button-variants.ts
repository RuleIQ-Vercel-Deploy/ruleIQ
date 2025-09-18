// Button variant configuration for Neural Purple design system
import { neuralPurple, silver, semantic, neutral } from './theme/neural-purple-colors';

export const ruleIQButtonConfig = {
  colors: {
    primary: {
      background: neuralPurple.primary, // purple-600
      text: neutral.white,
      hover: neuralPurple.dark, // purple-700
    },
    secondary: {
      background: neutral.white,
      text: neuralPurple.primary,
      border: silver.primary,
      hover: {
        background: neuralPurple.subtle, // purple-50
        text: neuralPurple.dark,
      },
    },
    ghost: {
      text: neuralPurple.primary,
      hover: neuralPurple.subtle,
    },
    accent: {
      background: neuralPurple.light, // purple-400
      text: neutral.white,
      hover: neuralPurple.primary, // purple-600
    },
    success: {
      background: semantic.success,
      text: neutral.white,
      hover: semantic.successDark,
    },
    warning: {
      background: semantic.warning,
      text: neutral.white,
      hover: semantic.warningDark,
    },
    error: {
      background: semantic.error,
      text: neutral.white,
      hover: semantic.errorDark,
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
