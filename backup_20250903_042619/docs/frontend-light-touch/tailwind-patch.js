// Tailwind Config Enhancement Patch
// Apply these updates to your existing tailwind.config.ts

const enhancementPatch = {
  theme: {
    extend: {
      // Enhanced Shadow System (3-tier elevation)
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'sm': '0 2px 4px -1px rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04)',
        'md': '0 4px 6px -2px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.04)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.05)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.15)',
        // New elevation system
        'elevation-low': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'elevation-medium': '0 4px 16px rgba(0, 0, 0, 0.10)',
        'elevation-high': '0 8px 24px rgba(0, 0, 0, 0.12)',
        // Glass morphism shadows
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.12)',
        'glass-hover': '0 12px 40px 0 rgba(31, 38, 135, 0.16)',
        // Brand glow effect
        'glow-teal': '0 0 20px rgba(44, 122, 123, 0.15)',
        'glow-teal-strong': '0 0 30px rgba(44, 122, 123, 0.25)',
      },
      
      // Refined Typography with Better Weights
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem', fontWeight: '400' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem', fontWeight: '400' }],
        'base': ['1rem', { lineHeight: '1.5rem', fontWeight: '400' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem', fontWeight: '500' }], // Reduced from 600
        'xl': ['1.25rem', { lineHeight: '1.75rem', fontWeight: '500' }], // Reduced from 600
        '2xl': ['1.5rem', { lineHeight: '2rem', fontWeight: '600' }], // Reduced from 700
        '3xl': ['1.875rem', { lineHeight: '2.25rem', fontWeight: '600' }], // Reduced from 700
        '4xl': ['2.25rem', { lineHeight: '2.5rem', fontWeight: '600' }], // Reduced from 700
        '5xl': ['3rem', { lineHeight: '1', fontWeight: '600' }], // Display
        '6xl': ['3.75rem', { lineHeight: '1', fontWeight: '600' }], // Large display
      },      
      // Letter Spacing for Premium Typography
      letterSpacing: {
        'heading': '0.025em', // For all headings
        'body': '0em',
        'wide': '0.05em',
      },
      
      // Varied Border Radius for Visual Interest
      borderRadius: {
        'none': '0',
        'sm': '0.25rem', // 4px - for small elements
        'DEFAULT': '0.375rem', // 6px - buttons
        'md': '0.5rem', // 8px - inputs
        'lg': '0.75rem', // 12px - cards
        'xl': '1rem', // 16px - modals
        '2xl': '1.5rem', // 24px - hero sections
        'full': '9999px',
      },
      
      // Enhanced Spacing for Breathing Room
      spacing: {
        '18': '4.5rem', // 72px
        '22': '5.5rem', // 88px
        '26': '6.5rem', // 104px
        '30': '7.5rem', // 120px
      },
      
      // Glass Morphism Backgrounds
      backgroundColor: {
        'glass-white': 'rgba(255, 255, 255, 0.85)',
        'glass-white-strong': 'rgba(255, 255, 255, 0.95)',
        'glass-teal': 'rgba(44, 122, 123, 0.08)',
        'glass-dark': 'rgba(0, 0, 0, 0.4)',
      },
      
      // Glass Morphism Borders
      borderColor: {
        'glass': 'rgba(255, 255, 255, 0.18)',
        'glass-strong': 'rgba(255, 255, 255, 0.3)',
      },
      
      // Backdrop Filters for Glass Effect
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '24px',
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
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      
      // Keyframe Animations for Delightful Interactions
      keyframes: {
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(44, 122, 123, 0.15)' },
          '50%': { boxShadow: '0 0 30px rgba(44, 122, 123, 0.3)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'slide-up-fade': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'slide-up-fade': 'slide-up-fade 0.3s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
      },
    },
  },
};

// Export for use in tailwind.config.ts
export default enhancementPatch;