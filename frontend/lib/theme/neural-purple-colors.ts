/**
 * Neural Purple Theme Color System
 * Based on DESIGN_SYSTEM.md specifications
 */

// Primary Colors - Neural Purple
export const neuralPurple = {
  primary: '#8B5CF6', // Main purple
  dark: '#7C3AED', // Darker variant
  light: '#A78BFA', // Lighter variant
  subtle: '#EDE9FE', // Very light purple for backgrounds
  50: '#FAF5FF',
  100: '#F3E8FF',
  200: '#E9D5FF',
  300: '#D8B4FE',
  400: '#C084FC',
  500: '#A855F7',
  600: '#8B5CF6', // Primary
  700: '#7C3AED', // Dark
  800: '#6B21A8',
  900: '#581C87',
  950: '#3B0764',
} as const;

// Accent Colors - Silver
export const silver = {
  primary: '#C0C0C0', // Main silver
  light: '#E5E5E5', // Light silver
  dark: '#9CA3AF', // Dark silver
  50: '#FAFAFA',
  100: '#F5F5F5',
  200: '#E5E5E5', // Light
  300: '#D4D4D4',
  400: '#C0C0C0', // Primary
  500: '#A3A3A3',
  600: '#9CA3AF', // Dark
  700: '#737373',
  800: '#525252',
  900: '#404040',
} as const;

// Neutral Colors
export const neutral = {
  white: '#FFFFFF',
  black: '#000000',
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
    950: '#030712',
  },
} as const;

// Semantic Colors
export const semantic = {
  success: '#10B981',
  successLight: '#D1FAE5',
  successDark: '#047857',
  error: '#EF4444',
  errorLight: '#FEE2E2',
  errorDark: '#B91C1C',
  warning: '#F59E0B',
  warningLight: '#FED7AA',
  warningDark: '#D97706',
  info: '#3B82F6',
  infoLight: '#DBEAFE',
  infoDark: '#1E40AF',
} as const;

// CSS Custom Properties Export
export const cssVariables = `
  :root {
    /* Neural Purple */
    --purple-primary: ${neuralPurple.primary};
    --purple-dark: ${neuralPurple.dark};
    --purple-light: ${neuralPurple.light};
    --purple-subtle: ${neuralPurple.subtle};
    
    /* Silver */
    --silver-primary: ${silver.primary};
    --silver-light: ${silver.light};
    --silver-dark: ${silver.dark};
    
    /* Neutral */
    --white: ${neutral.white};
    --black: ${neutral.black};
    
    /* Semantic */
    --success: ${semantic.success};
    --error: ${semantic.error};
    --warning: ${semantic.warning};
    --info: ${semantic.info};
  }
`;

// TypeScript Types
export type NeuralPurpleShade = keyof typeof neuralPurple;
export type SilverShade = keyof typeof silver;
export type SemanticColor = keyof typeof semantic;
export type ColorVariant = 'primary' | 'dark' | 'light' | 'subtle';

// Utility Functions
export const getOpacity = (color: string, opacity: number): string => {
  const hex = color.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

export const getHoverColor = (color: string): string => {
  // Darken color by 10% for hover state
  const hex = color.replace('#', '');
  const r = Math.max(0, parseInt(hex.substring(0, 2), 16) - 25);
  const g = Math.max(0, parseInt(hex.substring(2, 4), 16) - 25);
  const b = Math.max(0, parseInt(hex.substring(4, 6), 16) - 25);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
};

export const getFocusColor = (color: string): string => {
  return getOpacity(color, 0.2);
};

export const getDisabledColor = (color: string): string => {
  return getOpacity(color, 0.5);
};

// Chart Color Palettes
export const chartColors = {
  primary: [
    neuralPurple.primary,
    neuralPurple.dark,
    neuralPurple.light,
    silver.primary,
    silver.dark,
  ],
  categorical: [
    neuralPurple.primary,
    semantic.success,
    semantic.warning,
    semantic.info,
    silver.primary,
    neuralPurple.light,
    semantic.successLight,
    semantic.warningLight,
  ],
  gradient: {
    purple: [neuralPurple.subtle, neuralPurple.light, neuralPurple.primary, neuralPurple.dark],
    silver: [silver.light, silver.primary, silver.dark, neutral.gray[700]],
  },
};

// WCAG Contrast Checking
export const getContrastRatio = (color1: string, color2: string): number => {
  const getLuminance = (color: string): number => {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substring(0, 2), 16) / 255;
    const g = parseInt(hex.substring(2, 4), 16) / 255;
    const b = parseInt(hex.substring(4, 6), 16) / 255;
    
    const sRGB = [r, g, b].map((c) => {
      if (c <= 0.03928) return c / 12.92;
      return Math.pow((c + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
  };
  
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  
  return (lighter + 0.05) / (darker + 0.05);
};

export const meetsWCAGAA = (textColor: string, bgColor: string): boolean => {
  const ratio = getContrastRatio(textColor, bgColor);
  return ratio >= 4.5; // WCAG AA standard
};

export const meetsWCAGAAA = (textColor: string, bgColor: string): boolean => {
  const ratio = getContrastRatio(textColor, bgColor);
  return ratio >= 7; // WCAG AAA standard
};

// Tailwind Config Helper
export const tailwindColors = {
  purple: neuralPurple,
  silver,
  ...semantic,
};

// Component Theme Tokens
export const componentTokens = {
  button: {
    primary: {
      background: neuralPurple.primary,
      text: neutral.white,
      hover: neuralPurple.dark,
      disabled: getDisabledColor(neuralPurple.primary),
    },
    secondary: {
      background: 'transparent',
      text: neuralPurple.primary,
      border: silver.primary,
      hover: neuralPurple.subtle,
      disabled: getDisabledColor(silver.primary),
    },
    ghost: {
      background: 'transparent',
      text: neuralPurple.primary,
      hover: neuralPurple.subtle,
      disabled: getDisabledColor(neuralPurple.primary),
    },
  },
  card: {
    background: neutral.white,
    border: silver.light,
    hover: neuralPurple.subtle,
    shadow: getOpacity(neuralPurple.primary, 0.1),
  },
  input: {
    background: neutral.white,
    border: silver.light,
    focus: neuralPurple.primary,
    error: semantic.error,
    disabled: neutral.gray[100],
  },
  navigation: {
    background: neutral.white,
    hover: neuralPurple.subtle,
    active: neuralPurple.primary,
    text: neutral.gray[700],
    activeText: neuralPurple.primary,
  },
};

// Export all theme utilities
export default {
  colors: {
    neuralPurple,
    silver,
    neutral,
    semantic,
  },
  chart: chartColors,
  components: componentTokens,
  utils: {
    getOpacity,
    getHoverColor,
    getFocusColor,
    getDisabledColor,
    getContrastRatio,
    meetsWCAGAA,
    meetsWCAGAAA,
  },
  cssVariables,
  tailwindColors,
};