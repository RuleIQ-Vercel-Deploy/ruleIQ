export const themeColors = {
  purple: {
    primary: '#8B5CF6',
    dark: '#7C3AED',
    light: '#A78BFA',
    subtle: '#EDE9FE',
    50: '#FAF5FF',
    100: '#F3E8FF',
    200: '#E9D5FF',
    300: '#D8B4FE',
    400: '#C084FC',
    500: '#A855F7',
    600: '#9333EA',
    700: '#7E22CE',
    800: '#6B21A8',
    900: '#581C87',
  },
  silver: {
    primary: '#C0C0C0',
    light: '#E5E5E5',
    dark: '#9CA3AF',
  },
  neutral: {
    black: '#000000',
    950: '#030712',
    900: '#111827',
    800: '#1F2937',
    600: '#4B5563',
    400: '#9CA3AF',
    white: '#FFFFFF',
  },
  semantic: {
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  },
} as const;

export type ThemeColors = typeof themeColors;