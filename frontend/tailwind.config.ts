import type { Config } from "tailwindcss"

const config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // ruleIQ Brand Colors - Dark Mode Rebrand
        midnight: {
          DEFAULT: "#0F172A", // Midnight blue - primary brand color (dark mode first)
          dark: "#020617",    // Darker variant for deep backgrounds
          light: "#1E293B",   // Lighter variant for elevated surfaces
        },
        turquoise: {
          DEFAULT: "#00BCD4", // Turquoise - secondary accent (from logo)
          dark: "#00838F",    // Darker turquoise for hover states
          light: "#4DD0E1",   // Lighter turquoise for backgrounds
        },
        electric: {
          DEFAULT: "#1E40AF", // Electric blue - supporting accent
          dark: "#1E3A8A",    // Darker blue variant
          light: "#3B82F6",   // Lighter blue variant
        },
        // Neutral colors (Dark Theme Optimized)
        neutral: {
          light: "#334155",   // Dark gray - elevated surfaces
          medium: "#475569",  // Medium gray - borders, dividers
          dark: "#64748B",    // Light gray - secondary text on dark
        },
        // Semantic colors
        success: "#10B981",   // Emerald green for dark theme
        warning: "#F59E0B",   // Amber for warnings
        error: "#EF4444",     // Red for errors
        info: "#00BCD4",      // Use turquoise for info states
        
        // Surface colors (Dark Mode First)
        surface: {
          primary: "#0F172A",     // Dark theme primary surface (midnight)
          secondary: "#1E293B",   // Dark theme secondary surface
          tertiary: "#334155",    // Dark theme tertiary surface
          "primary-light": "#FFFFFF",  // Light theme primary surface
          "secondary-light": "#F8FAFC", // Light theme secondary surface
          "tertiary-light": "#E2E8F0", // Light theme tertiary surface
        },
        
        // Text colors (Dark Mode Optimized)
        "text-on-dark": "#F1F5F9",       // Light text on dark surfaces (primary)
        "text-on-light": "#0F172A",      // Dark text on light surfaces
        "text-on-turquoise": "#FFFFFF",  // White text on turquoise
        "text-on-midnight": "#F1F5F9",   // Light text on midnight blue
        "text-secondary": "#CBD5E1",     // Secondary text color (light on dark)
        "text-muted": "#94A3B8",        // Muted text color (dark theme)
        
        // Outline colors for focus and borders
        outline: {
          primary: "#00BCD4",     // Turquoise outline
          secondary: "#1E40AF",   // Electric blue outline
          muted: "#475569",      // Dark gray outline
        },
        
        // shadcn/ui CSS variables (keep for compatibility)
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      // 8px grid system spacing
      spacing: {
        '0.5': '4px',   // Half-step when necessary
        '1': '8px',     // Base unit
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
        'xs': ['12px', { lineHeight: '16px', fontWeight: '400' }],    // Small
        'sm': ['14px', { lineHeight: '20px', fontWeight: '400' }],    // Body
        'base': ['16px', { lineHeight: '24px', fontWeight: '400' }],  // Large body
        'lg': ['18px', { lineHeight: '28px', fontWeight: '600' }],    // H3
        'xl': ['20px', { lineHeight: '28px', fontWeight: '600' }],    // Large H3
        '2xl': ['24px', { lineHeight: '32px', fontWeight: '700' }],   // H2
        '3xl': ['30px', { lineHeight: '36px', fontWeight: '700' }],   // Large H2
        '4xl': ['32px', { lineHeight: '40px', fontWeight: '700' }],   // H1
        '5xl': ['48px', { lineHeight: '48px', fontWeight: '700' }],   // Display
        '6xl': ['60px', { lineHeight: '60px', fontWeight: '700' }],   // Large display
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        scroll: {
          to: {
            transform: "translate(calc(-50% - 0.5rem))",
          },
        },
        // Micro-interaction animations
        "fade-in": {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        "fade-out": {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        "slide-in-up": {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        "slide-in-down": {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        "scale-in": {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        "pulse-subtle": {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        scroll: "scroll var(--animation-duration, 40s) var(--animation-direction, forwards) linear infinite",
        // Micro-interaction animations
        "fade-in": "fade-in 0.3s ease-out",
        "fade-out": "fade-out 0.3s ease-out",
        "slide-in-up": "slide-in-up 0.3s ease-out",
        "slide-in-down": "slide-in-down 0.3s ease-out",
        "scale-in": "scale-in 0.2s ease-out",
        "pulse-subtle": "pulse-subtle 2s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config
