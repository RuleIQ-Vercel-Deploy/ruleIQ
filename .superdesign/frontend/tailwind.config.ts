import type { Config } from 'tailwindcss';

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
        // Modern ruleIQ Brand Colors - Premium Dark Theme
        brand: {
          primary: '#7C3AED', // Vibrant purple - main brand color
          secondary: '#06B6D4', // Cyan - secondary accent
          tertiary: '#10B981', // Emerald - success/positive states
          dark: '#5B21B6', // Darker purple for hover states
          light: '#A78BFA', // Lighter purple for backgrounds
        },

        // Gradient colors for modern effects
        gradient: {
          from: '#7C3AED', // Purple
          via: '#06B6D4', // Cyan
          to: '#10B981', // Emerald
          'from-dark': '#5B21B6', // Dark purple
          'via-dark': '#0891B2', // Dark cyan
          'to-dark': '#059669', // Dark emerald
        },

        // Surface colors (Dark Mode First)
        surface: {
          base: '#0A0A0B', // Near black base
          primary: '#111113', // Primary surface
          secondary: '#18181B', // Secondary surface
          tertiary: '#27272A', // Tertiary surface
          elevated: '#2D2D30', // Elevated components
          overlay: 'rgba(0,0,0,0.8)', // Modal overlays
        },

        // Neutral colors (Modern grayscale)
        neutral: {
          50: '#FAFAFA',
          100: '#F4F4F5',
          200: '#E4E4E7',
          300: '#D4D4D8',
          400: '#A1A1AA',
          500: '#71717A',
          600: '#52525B',
          700: '#3F3F46',
          800: '#27272A',
          900: '#18181B',
          950: '#0A0A0B',
        },

        // Text colors (Optimized for dark surfaces)
        text: {
          primary: '#FAFAFA', // High contrast white
          secondary: '#A1A1AA', // Muted gray
          tertiary: '#71717A', // Even more muted
          inverse: '#0A0A0B', // For light backgrounds
          brand: '#A78BFA', // Brand purple text
          accent: '#67E8F9', // Cyan accent text
        },

        // Semantic colors
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#06B6D4',

        // Glass morphism effects
        glass: {
          white: 'rgba(255, 255, 255, 0.05)',
          'white-hover': 'rgba(255, 255, 255, 0.08)',
          border: 'rgba(255, 255, 255, 0.1)',
          'border-hover': 'rgba(255, 255, 255, 0.2)',
        },

        // Legacy color mappings (for gradual migration)
        navy: '#7C3AED', // Map to brand primary
        gold: '#F59E0B', // Map to warning
        'gold-dark': '#D97706', // Darker gold for hover states
        turquoise: '#06B6D4', // Map to brand secondary
        midnight: '#0A0A0B', // Map to surface base

        // shadcn/ui CSS variables (keep for compatibility)
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
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
      // Extend ring colors to include custom colors
      ringColor: {
        gold: '#F59E0B',
        'gold-dark': '#D97706',
        navy: '#7C3AED',
        turquoise: '#06B6D4',
      },
      // 8px grid system spacing
      spacing: {
        '0.5': '4px', // Half-step when necessary
        '1': '8px', // Base unit
        '1.5': '12px',
        '2': '16px',
        '2.5': '20px',
        '3': '24px',
        '3.5': '28px',
        '4': '32px',
        '5': '40px',
        '6': '48px',
        '7': '56px',
        '8': '64px',
        '9': '72px',
        '10': '80px',
        '11': '88px',
        '12': '96px',
        '14': '112px',
        '16': '128px',
        '20': '160px',
        '24': '192px',
        '28': '224px',
        '32': '256px',
        '36': '288px',
        '40': '320px',
        '44': '352px',
        '48': '384px',
        '52': '416px',
        '56': '448px',
        '60': '480px',
        '64': '512px',
        '72': '576px',
        '80': '640px',
        '96': '768px',
      },
      fontSize: {
        // Typography scale from CLAUDE.md
        xs: ['12px', { lineHeight: '16px', fontWeight: '400' }], // Small
        sm: ['14px', { lineHeight: '20px', fontWeight: '400' }], // Body
        base: ['16px', { lineHeight: '24px', fontWeight: '400' }], // Large body
        lg: ['18px', { lineHeight: '28px', fontWeight: '600' }], // H3
        xl: ['20px', { lineHeight: '28px', fontWeight: '600' }], // Large H3
        '2xl': ['24px', { lineHeight: '32px', fontWeight: '700' }], // H2
        '3xl': ['30px', { lineHeight: '36px', fontWeight: '700' }], // Large H2
        '4xl': ['32px', { lineHeight: '40px', fontWeight: '700' }], // H1
        '5xl': ['48px', { lineHeight: '48px', fontWeight: '700' }], // Display
        '6xl': ['60px', { lineHeight: '60px', fontWeight: '700' }], // Large display
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        scroll: {
          to: {
            transform: 'translate(calc(-50% - 0.5rem))',
          },
        },
        // Micro-interaction animations
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-out': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        'slide-in-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-down': {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'pulse-subtle': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        scroll:
          'scroll var(--animation-duration, 40s) var(--animation-direction, forwards) linear infinite',
        // Micro-interaction animations
        'fade-in': 'fade-in 0.3s ease-out',
        'fade-out': 'fade-out 0.3s ease-out',
        'slide-in-up': 'slide-in-up 0.3s ease-out',
        'slide-in-down': 'slide-in-down 0.3s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
        'pulse-subtle': 'pulse-subtle 2s ease-in-out infinite',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
} satisfies Config;

export default config;
