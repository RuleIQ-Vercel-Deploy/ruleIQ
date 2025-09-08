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
        // Modern ruleIQ Brand Colors - Professional Teal Theme
        brand: {
          primary: '#2C7A7B', // teal-600 - main brand color
          secondary: '#319795', // teal-500 - secondary accent
          tertiary: '#4FD1C5', // teal-300 - bright accent
          dark: '#285E61', // teal-700 - darker for hover states
          light: '#E6FFFA', // teal-50 - light backgrounds
        },

        // Gradient colors for modern teal effects
        gradient: {
          from: '#2C7A7B', // teal-600
          via: '#319795', // teal-500
          to: '#4FD1C5', // teal-300
          'from-dark': '#285E61', // teal-700
          'via-dark': '#234E52', // teal-800
          'to-dark': '#1D4044', // teal-900
        },

        // Surface colors (Light Mode Professional)
        surface: {
          base: '#FFFFFF', // Clean white base
          primary: '#FFFFFF', // Primary surface - white
          secondary: '#F9FAFB', // Secondary surface - neutral-50
          tertiary: '#F3F4F6', // Tertiary surface - neutral-100
          elevated: '#FFFFFF', // Elevated components - white with shadow
          overlay: 'rgba(0,0,0,0.5)', // Modal overlays
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

        // Teal color scale (Primary brand colors)
        teal: {
          50: '#E6FFFA',
          100: '#B2F5EA',
          200: '#81E6D9',
          300: '#4FD1C5',
          400: '#38B2AC',
          500: '#319795',
          600: '#2C7A7B',
          700: '#285E61',
          800: '#234E52',
          900: '#1D4044',
        },

        // Text colors (Optimized for light surfaces)
        text: {
          primary: '#111827', // High contrast dark - neutral-900
          secondary: '#4B5563', // Muted gray - neutral-600
          tertiary: '#6B7280', // Even more muted - neutral-500
          inverse: '#FFFFFF', // For dark backgrounds
          brand: '#2C7A7B', // Brand teal text - teal-600
          accent: '#319795', // Teal accent text - teal-500
        },

        // Semantic colors
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#319795', // teal-500 instead of cyan

        // Glass morphism effects (light theme)
        glass: {
          white: 'rgba(255, 255, 255, 0.8)',
          'white-hover': 'rgba(255, 255, 255, 0.9)',
          border: 'rgba(229, 231, 235, 0.5)', // neutral-200 with transparency
          'border-hover': 'rgba(209, 213, 219, 0.8)', // neutral-300 with transparency
        },

        // Legacy color mappings (for gradual migration)
        navy: '#2C7A7B', // Map to teal-600 (brand primary)
        gold: '#F59E0B', // Map to warning
        'gold-dark': '#D97706', // Darker gold for hover states
        turquoise: '#319795', // Map to teal-500 (brand secondary)
        midnight: '#FFFFFF', // Map to white surface base

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
        navy: '#2C7A7B', // teal-600
        turquoise: '#319795', // teal-500
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
