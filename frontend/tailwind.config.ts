import type { Config } from 'tailwindcss';
import { purpleColors, silverColors, semanticColors, neutralColors, brandColors } from './lib/theme/colors';

const config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: '',
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        // Neural Purple Theme Colors from centralized module
        purple: purpleColors,
        silver: silverColors,

        // DISTINCTIVE ruleIQ Brand Colors
        brand: {
          primary: brandColors.primary,
          secondary: brandColors.primaryLight,
          tertiary: purpleColors['300'],
          dark: brandColors.primaryDark,
          light: brandColors.accentLight,
          accent: silverColors.light,
          'accent-light': neutralColors.gray['50'],
          'accent-dark': silverColors.dark,
          glow: purpleColors['200'],
        },

        // Semantic colors
        success: semanticColors.success,
        'success-light': semanticColors.successLight,
        'success-dark': semanticColors.successDark,
        error: semanticColors.error,
        'error-light': semanticColors.errorLight,
        'error-dark': semanticColors.errorDark,
        warning: semanticColors.warning,
        'warning-light': semanticColors.warningLight,
        'warning-dark': semanticColors.warningDark,
        info: semanticColors.info,
        'info-light': semanticColors.infoLight,
        'info-dark': semanticColors.infoDark,

        // Neutral colors
        gray: neutralColors.gray,
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      boxShadow: {
        'glow-purple': '0 0 20px rgba(139, 92, 246, 0.15)',
        'glow-purple-strong': '0 0 30px rgba(139, 92, 246, 0.25)',
        'glow-purple-xl': '0 0 40px rgba(139, 92, 246, 0.35)',
        'glow-silver': '0 0 20px rgba(163, 163, 163, 0.15)',
        'elevation-low': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'elevation-medium': '0 4px 16px rgba(0, 0, 0, 0.10)',
        'elevation-high': '0 8px 24px rgba(0, 0, 0, 0.12)',
      },
      backgroundImage: {
        // Purple gradients
        'purple-gradient': 'linear-gradient(135deg, #7C3AED 0%, #8B5CF6 50%, #A78BFA 100%)',
        'purple-radial': 'radial-gradient(ellipse at top, #A78BFA, #8B5CF6, #7C3AED)',
        'purple-shine': 'linear-gradient(105deg, transparent 40%, rgba(139, 92, 246, 0.7) 50%, transparent 60%)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Monaco', 'Cascadia Code', 'monospace'],
      },
      fontWeight: {
        'extra-light': '200',
        light: '300',
        regular: '400',
        medium: '450',
        semibold: '500',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
} satisfies Config;

export default config;
