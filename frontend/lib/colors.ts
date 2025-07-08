/**
 * ruleIQ Design System Colors
 * Consolidated color tokens aligned with Tailwind config
 * Use these tokens for programmatic color access
 */

export const colors = {
  // Brand Colors - Dark Theme Rebrand
  midnight: {
    DEFAULT: "#0F172A", // Midnight blue - primary brand color (dark mode first)
    dark: "#020617",    // Darker variant for deep backgrounds
    light: "#1E293B",   // Lighter variant for elevated surfaces
  },
  turquoise: {
    DEFAULT: "#00BCD4", // Turquoise - secondary accent color (from logo)
    dark: "#00838F",    // Darker turquoise for hover states
    light: "#4DD0E1",   // Lighter turquoise for backgrounds
  },
  electric: {
    DEFAULT: "#1E40AF", // Electric blue - supporting accent
    dark: "#1E3A8A",    // Darker blue variant
    light: "#3B82F6",   // Lighter blue variant
  },
  
  // Neutral Colors (Dark Theme Optimized)
  neutral: {
    light: "#334155",   // Dark gray - elevated surfaces
    medium: "#475569",  // Medium gray - borders, dividers
    dark: "#64748B",    // Light gray - secondary text on dark
  },
  
  // Semantic Colors
  semantic: {
    success: "#10B981",   // Emerald green for dark theme
    warning: "#F59E0B",   // Amber for warnings
    error: "#EF4444",     // Red for errors
    info: "#00BCD4",      // Use turquoise for info states
  },
  
  // Surface Colors (Dark Mode First)
  surface: {
    primary: "#0F172A",     // Dark theme primary surface (midnight)
    secondary: "#1E293B",   // Dark theme secondary surface
    tertiary: "#334155",    // Dark theme tertiary surface
    
    "primary-light": "#FFFFFF",  // Light theme primary surface
    "secondary-light": "#F8FAFC", // Light theme secondary surface
    "tertiary-light": "#E2E8F0", // Light theme tertiary surface
  },
  
  // Text Colors (Dark Mode Optimized)
  text: {
    "on-dark": "#F1F5F9",       // Light text on dark surfaces (primary)
    "on-light": "#0F172A",      // Dark text on light surfaces
    "on-turquoise": "#FFFFFF",  // White text on turquoise
    "on-midnight": "#F1F5F9",   // Light text on midnight blue
    secondary: "#CBD5E1",       // Secondary text color (light on dark)
    muted: "#94A3B8",          // Muted text color (dark theme)
  },
  
  // Legacy support (will be deprecated)
  primary: "#0F172A",
  "primary-dark": "#020617", 
  "primary-light": "#1E293B",
} as const

export type ColorKey = keyof typeof colors
