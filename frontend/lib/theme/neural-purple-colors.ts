/**
 * Neural Purple Theme Colors
 * Central theme configuration for the RuleIQ platform
 */

export const neuralPurple = {
  // Primary purple shades
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
  950: '#3B0764',

  // Semantic colors
  primary: '#8B5CF6',
  primaryHover: '#7C3AED',
  primaryLight: '#C084FC',
  primaryDark: '#6D28D9',

  // Background shades
  background: '#0F0F0F',
  backgroundLight: '#1A1A1A',
  backgroundDark: '#000000',

  // Accent colors (purple variants)
  accent: '#A78BFA',
  accentHover: '#8B5CF6',
  accentLight: '#C4B5FD',
  accentDark: '#7C3AED',

  // Text colors
  text: '#FFFFFF',
  textSecondary: '#E5E7EB',
  textMuted: '#9CA3AF',

  // Border colors
  border: '#374151',
  borderLight: '#4B5563',
  borderDark: '#1F2937',

  // Status colors (with purple tints)
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#8B5CF6', // Changed from teal to purple

  // Chart colors (purple palette)
  chart: {
    primary: '#8B5CF6',
    secondary: '#7C3AED',
    tertiary: '#C084FC',
    quaternary: '#A78BFA',
    quinary: '#6D28D9',
    senary: '#5B21B6',
  }
};

// Legacy color mappings for migration
export const legacyToNeuralPurpleMap = {
  // Teal to Purple mappings
  '#2C7A7B': neuralPurple.primary, // Teal 700 → Primary purple
  '#319795': neuralPurple.primaryLight, // Teal 600 → Light purple
  '#38B2AC': neuralPurple.accent, // Teal 500 → Accent purple
  '#4FD1C5': neuralPurple.accentLight, // Teal 400 → Light accent
  '#81E6D9': neuralPurple[300], // Teal 300 → Purple 300
  '#B2F5EA': neuralPurple[200], // Teal 200 → Purple 200
  '#E6FFFA': neuralPurple[100], // Teal 100 → Purple 100

  // Gold to Purple mappings
  '#CB963E': neuralPurple.accent, // Gold → Accent purple
  '#D4A574': neuralPurple.accentLight, // Light gold → Light accent
  '#B8822F': neuralPurple.accentDark, // Dark gold → Dark accent

  // Navi/Navy to Purple mappings
  '#1E3A8A': neuralPurple.primaryDark, // Navy → Dark purple
  '#1E40AF': neuralPurple[700], // Navy blue → Purple 700
  '#2563EB': neuralPurple[600], // Blue → Purple 600
};

// Tailwind color class mappings
export const tailwindColorMap = {
  // Background colors
  'bg-teal-50': 'bg-purple-50',
  'bg-teal-100': 'bg-purple-100',
  'bg-teal-200': 'bg-purple-200',
  'bg-teal-300': 'bg-purple-300',
  'bg-teal-400': 'bg-purple-400',
  'bg-teal-500': 'bg-purple-500',
  'bg-teal-600': 'bg-purple-600',
  'bg-teal-700': 'bg-purple-700',
  'bg-teal-800': 'bg-purple-800',
  'bg-teal-900': 'bg-purple-900',

  // Text colors
  'text-teal-50': 'text-purple-50',
  'text-teal-100': 'text-purple-100',
  'text-teal-200': 'text-purple-200',
  'text-teal-300': 'text-purple-300',
  'text-teal-400': 'text-purple-400',
  'text-teal-500': 'text-purple-500',
  'text-teal-600': 'text-purple-600',
  'text-teal-700': 'text-purple-700',
  'text-teal-800': 'text-purple-800',
  'text-teal-900': 'text-purple-900',

  // Border colors
  'border-teal-50': 'border-purple-50',
  'border-teal-100': 'border-purple-100',
  'border-teal-200': 'border-purple-200',
  'border-teal-300': 'border-purple-300',
  'border-teal-400': 'border-purple-400',
  'border-teal-500': 'border-purple-500',
  'border-teal-600': 'border-purple-600',
  'border-teal-700': 'border-purple-700',
  'border-teal-800': 'border-purple-800',
  'border-teal-900': 'border-purple-900',

  // Hover states
  'hover:bg-teal-50': 'hover:bg-purple-50',
  'hover:bg-teal-100': 'hover:bg-purple-100',
  'hover:bg-teal-200': 'hover:bg-purple-200',
  'hover:bg-teal-300': 'hover:bg-purple-300',
  'hover:bg-teal-400': 'hover:bg-purple-400',
  'hover:bg-teal-500': 'hover:bg-purple-500',
  'hover:bg-teal-600': 'hover:bg-purple-600',
  'hover:bg-teal-700': 'hover:bg-purple-700',
  'hover:bg-teal-800': 'hover:bg-purple-800',
  'hover:bg-teal-900': 'hover:bg-purple-900',

  'hover:text-teal-50': 'hover:text-purple-50',
  'hover:text-teal-100': 'hover:text-purple-100',
  'hover:text-teal-200': 'hover:text-purple-200',
  'hover:text-teal-300': 'hover:text-purple-300',
  'hover:text-teal-400': 'hover:text-purple-400',
  'hover:text-teal-500': 'hover:text-purple-500',
  'hover:text-teal-600': 'hover:text-purple-600',
  'hover:text-teal-700': 'hover:text-purple-700',
  'hover:text-teal-800': 'hover:text-purple-800',
  'hover:text-teal-900': 'hover:text-purple-900',
};

export default neuralPurple;