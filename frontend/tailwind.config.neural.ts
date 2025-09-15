// tailwind.config.ts - Neural Purple Theme Implementation
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Neural Purple Palette
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
        // Silver Palette
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
        // Semantic Colors
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'info': '#8b5cf6',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Consolas', 'monospace'],
      },
      fontSize: {
        'hero': ['4.5rem', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
        'display-lg': ['3.75rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'display': ['3rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'display-sm': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
      },
      fontWeight: {
        'extralight': '200',
        'light': '300',
        'regular': '400',
        'medium': '500',
        'semibold': '600',
      },
      backgroundImage: {
        // Gradient definitions
        'neural-gradient': 'radial-gradient(ellipse at top, #4a0080 0%, #1a0033 50%, #000000 100%)',
        'section-gradient': 'linear-gradient(135deg, #2d0052 0%, #1a0033 100%)',
        'card-gradient': 'linear-gradient(180deg, rgba(139, 92, 246, 0.05) 0%, rgba(0, 0, 0, 0) 100%)',
        'button-gradient': 'linear-gradient(135deg, #8b5cf6 0%, #6b00b5 100%)',
        'button-hover-gradient': 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'fade-up': 'fadeUp 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      boxShadow: {
        'purple-sm': '0 2px 10px rgba(139, 92, 246, 0.1)',
        'purple-md': '0 10px 30px rgba(139, 92, 246, 0.2)',
        'purple-lg': '0 20px 40px rgba(139, 92, 246, 0.3)',
        'silver': '0 10px 30px rgba(192, 192, 192, 0.1)',
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
};

export default config;
