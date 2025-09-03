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
        // RuleIQ Brand Colors - As Per Spec
        brand: {
          navy: '#103766', // Primary Navy
          teal: '#0B4F6C', // Primary Teal  
          orange: '#F28C28', // Accent Orange (use sparingly)
          'navy-dark': '#0A2340', // Darker navy for hover states
          'navy-light': '#1C4A7D', // Lighter navy
          'teal-dark': '#073A52', // Darker teal for hover states
          'teal-light': '#0F6585', // Lighter teal
          'orange-light': '#F5A554', // Lighter orange
          'orange-dark': '#E67A0F', // Darker orange
        },

        // Legacy brand mappings for gradual migration
        primary: '#0B4F6C', // Primary Teal
        secondary: '#103766', // Primary Navy
        accent: '#F28C28', // Accent Orange

        // Gradient colors using brand palette
        gradient: {
          from: '#103766', // Navy
          via: '#0B4F6C', // Teal
          to: '#0F6585', // Light Teal
          'from-dark': '#0A2340', // Dark Navy
          'via-dark': '#073A52', // Dark Teal
          'to-dark': '#051F2E', // Very Dark Teal
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

        // Text colors (Optimized for light surfaces)
        text: {
          primary: '#111827', // High contrast dark - neutral-900
          secondary: '#4B5563', // Muted gray - neutral-600
          tertiary: '#6B7280', // Even more muted - neutral-500
          inverse: '#FFFFFF', // For dark backgrounds
          brand: '#0B4F6C', // Brand teal text
          accent: '#103766', // Navy accent text
        },

        // Semantic colors
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#0B4F6C', // Using brand teal

        // Glass morphism effects (light theme)
        glass: {
          white: 'rgba(255, 255, 255, 0.8)',
          'white-hover': 'rgba(255, 255, 255, 0.9)',
          border: 'rgba(229, 231, 235, 0.5)', // neutral-200 with transparency
          'border-hover': 'rgba(209, 213, 219, 0.8)', // neutral-300 with transparency
        },

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
        'brand-navy': '#103766',
        'brand-teal': '#0B4F6C',
        'brand-orange': '#F28C28',
      },
      // 8px grid system spacing (as specified)
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
      fontFamily: {
        sans: ['Inter', 'Roboto', 'system-ui', '-apple-system', 'sans-serif'],
        inter: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        roboto: ['Roboto', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        // Typography scale with optimized weights
        xs: ['12px', { lineHeight: '16px', fontWeight: '400' }], // Small
        sm: ['14px', { lineHeight: '20px', fontWeight: '400' }], // Body
        base: ['16px', { lineHeight: '24px', fontWeight: '400' }], // Large body
        lg: ['18px', { lineHeight: '28px', fontWeight: '500' }], // H3
        xl: ['20px', { lineHeight: '28px', fontWeight: '500' }], // Large H3
        '2xl': ['24px', { lineHeight: '32px', fontWeight: '600' }], // H2
        '3xl': ['30px', { lineHeight: '36px', fontWeight: '600' }], // Large H2
        '4xl': ['32px', { lineHeight: '40px', fontWeight: '600' }], // H1
        '5xl': ['48px', { lineHeight: '48px', fontWeight: '600' }], // Display
        '6xl': ['60px', { lineHeight: '60px', fontWeight: '600' }], // Large display
      },
      // Enhanced Shadow System (3-tier elevation)
      boxShadow: {
        xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        sm: '0 2px 4px -1px rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04)',
        md: '0 4px 6px -2px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.04)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.05)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.05)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.15)',
        // New elevation system
        'elevation-low': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'elevation-medium': '0 4px 16px rgba(0, 0, 0, 0.10)',
        'elevation-high': '0 8px 24px rgba(0, 0, 0, 0.12)',
        // Glass morphism shadows
        glass: '0 8px 32px 0 rgba(31, 38, 135, 0.12)',
        'glass-hover': '0 12px 40px 0 rgba(31, 38, 135, 0.16)',
        // Brand glow effect
        'glow-navy': '0 0 20px rgba(16, 55, 102, 0.15)',
        'glow-teal': '0 0 20px rgba(11, 79, 108, 0.15)',
        'glow-orange': '0 0 20px rgba(242, 140, 40, 0.15)',
      },
      // Varied Border Radius for Visual Interest
      borderRadius: {
        none: '0',
        sm: '0.25rem', // 4px - for small elements
        DEFAULT: '0.375rem', // 6px - buttons
        md: '0.5rem', // 8px - inputs
        lg: '0.75rem', // 12px - cards
        xl: '1rem', // 16px - modals
        '2xl': '1.5rem', // 24px - hero sections
        full: '9999px',
      },
      // Backdrop Filters for Glass Effect
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '24px',
      },
      // Glass Morphism Backgrounds
      backgroundColor: {
        'glass-white': 'rgba(255, 255, 255, 0.85)',
        'glass-white-strong': 'rgba(255, 255, 255, 0.95)',
        'glass-navy': 'rgba(16, 55, 102, 0.08)',
        'glass-teal': 'rgba(11, 79, 108, 0.08)',
        'glass-dark': 'rgba(0, 0, 0, 0.4)',
      },
      // Glass Morphism Borders
      borderColor: {
        glass: 'rgba(255, 255, 255, 0.18)',
        'glass-strong': 'rgba(255, 255, 255, 0.3)',
      },
      // Enhanced Animation Timing
      transitionDuration: {
        '50': '50ms',
        '150': '150ms',
        '250': '250ms',
        '350': '350ms',
        '400': '400ms',
      },
      // Spring Animations for Micro-interactions
      transitionTimingFunction: {
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      // Letter Spacing for Premium Typography
      letterSpacing: {
        heading: '0.025em', // For all headings
        body: '0em',
        wide: '0.05em',
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
        // Enhanced micro-interaction animations
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(11, 79, 108, 0.15)' },
          '50%': { boxShadow: '0 0 30px rgba(11, 79, 108, 0.3)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'slide-up-fade': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
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
        // New enhanced animations
        float: 'float 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        shimmer: 'shimmer 2s linear infinite',
        'slide-up-fade': 'slide-up-fade 0.3s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
} satisfies Config;

export default config;