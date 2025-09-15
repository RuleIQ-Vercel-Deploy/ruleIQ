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
        // Neural Purple Theme - Dark Mode Colors
        'neural-purple': {
          900: '#1a0033',
          800: '#2d0052',
          700: '#4a0080',
          600: '#6b00b5',
          500: '#8b5cf6',
          400: '#a78bfa',
          300: '#c4b5fd',
          200: '#ddd6fe',
          100: '#ede9fe',
        },
        'silver': {
          900: '#1f2937',
          800: '#374151',
          700: '#4b5563',
          600: '#6b7280',
          500: '#9ca3af',
          400: '#c0c0c0',
          300: '#d1d5db',
          200: '#e5e7eb',
          100: '#f3f4f6',
        },
        // DISTINCTIVE ruleIQ Brand Colors - Dark Mode Purple & Silver Theme
        brand: {
          primary: '#8B5CF6', // Bright purple for dark mode (violet-500)
          secondary: '#A78BFA', // Light purple (violet-400)
          tertiary: '#C4B5FD', // Lighter purple (violet-300)
          dark: '#6D28D9', // Dark purple for accents (violet-700)
          light: '#EDE9FE', // Light purple for highlights (violet-100)
          accent: '#E5E7EB', // Silver accent (gray-200)
          'accent-light': '#F9FAFB', // Light silver (gray-50)
          'accent-dark': '#9CA3AF', // Dark silver (gray-400)
          glow: '#DDD6FE', // Purple glow effect (violet-200)
        },
        // Purple color scale (Primary brand colors)
        purple: {
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
          800: '#5B21B6',
          900: '#4C1D95',
        },
        // Silver/Gray accent colors for contrast
        silver: {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
        // Remap teal references to purple (for compatibility)
        teal: {
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
          800: '#5B21B6',
          900: '#4C1D95',
        },
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
        'glow-purple': '0 0 20px rgba(91, 33, 182, 0.15)',
        'glow-purple-strong': '0 0 30px rgba(91, 33, 182, 0.25)',
        'glow-purple-xl': '0 0 40px rgba(91, 33, 182, 0.35)',
        'glow-silver': '0 0 20px rgba(163, 163, 163, 0.15)',
        'elevation-low': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'elevation-medium': '0 4px 16px rgba(0, 0, 0, 0.10)',
        'elevation-high': '0 8px 24px rgba(0, 0, 0, 0.12)',
      },
      backgroundImage: {
        // Purple gradients
        'purple-gradient': 'linear-gradient(135deg, #5B21B6 0%, #7C3AED 50%, #A78BFA 100%)',
        'purple-radial': 'radial-gradient(ellipse at top, #A78BFA, #7C3AED, #5B21B6)',
        'purple-shine': 'linear-gradient(105deg, transparent 40%, rgba(167, 139, 250, 0.7) 50%, transparent 60%)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
} satisfies Config;

export default config;
