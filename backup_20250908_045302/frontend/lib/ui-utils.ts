/**
 * ruleIQ UI Utilities
 * Provides consistent styling utilities and classname helpers
 *
 * This file contains advanced styling patterns specific to ruleIQ's
 * professional compliance platform design system.
 */

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Already exists in utils.ts, but re-export for compatibility
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Standardized Button Variants (ruleIQ design system)
export const buttonVariants = {
  base: 'inline-flex items-center justify-center rounded-md font-medium transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-outline-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',

  variants: {
    // Primary actions - most important
    primary:
      'bg-midnight text-text-on-midnight hover:bg-midnight-dark active:bg-midnight-dark shadow-sm hover:shadow-md',

    // Secondary actions - less emphasis
    secondary:
      'bg-surface-secondary text-text-on-dark border-2 border-teal-500 hover:bg-teal-500 hover:text-white active:bg-teal-600',

    // Accent actions - teal brand accent
    accent: 'bg-teal-500 text-white hover:bg-teal-600 active:bg-teal-700 shadow-sm hover:shadow-md',

    // Outlined - minimal emphasis
    outline:
      'border-2 border-teal-500 text-teal-600 bg-transparent hover:bg-teal-500/10 active:bg-teal-500/20',

    // Ghost - subtle actions
    ghost: 'text-teal-600 hover:bg-teal-500/10 active:bg-teal-500/15',

    // Destructive - dangerous actions
    destructive: 'bg-error text-white hover:bg-error/90 active:bg-error/80 shadow-sm',

    // Success - positive actions
    success: 'bg-success text-white hover:bg-success/90 active:bg-success/80 shadow-sm',

    // Link - text-only actions
    link: 'text-teal-600 underline-offset-4 hover:underline focus-visible:ring-1',
  },

  sizes: {
    sm: 'h-8 px-3 text-xs',
    default: 'h-10 px-4 py-2 text-sm',
    lg: 'h-12 px-6 text-base',
    xl: 'h-14 px-8 text-lg',
    icon: 'h-10 w-10', // Square icon buttons
  },
};

// Professional Card Styles (Dark Theme)
export const cardStyles = {
  base: 'bg-surface-secondary rounded-lg border border-neutral-medium shadow-sm hover:shadow-md transition-shadow duration-200',
  header: 'px-6 py-4 border-b border-neutral-medium',
  content: 'p-6',
  footer: 'px-6 py-4 border-t border-neutral-medium bg-neutral-light/20',
  trust: 'border-teal-500/20 shadow-[0_0_20px_rgba(44,122,123,0.15)]', // Teal trust shadow
};

// Form Styles
export const formStyles = {
  input:
    'w-full px-3 py-2 rounded-md border border-input bg-background text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50',
  label: 'block text-sm font-medium mb-1.5',
  helper: 'text-xs text-muted-foreground mt-1',
  error: 'text-xs text-destructive mt-1',
  group: 'space-y-2',
  required: 'text-red-500 ml-1', // Required field indicator
};

// Status Badge Styles (Compliance specific)
export const statusStyles = {
  base: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
  variants: {
    compliant: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    partial: 'bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-400',
    'non-compliant': 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    pending: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
    approved: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    rejected: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    active: 'bg-teal-500/20 text-teal-600 dark:bg-teal-500/10 dark:text-teal-500',
    inactive: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
  },
};

// Compliance Score Styles
export const complianceScoreStyles = {
  critical: 'text-red-600 bg-red-50 border-red-200',
  warning: 'text-amber-600 bg-amber-50 border-amber-200',
  good: 'text-green-600 bg-green-50 border-green-200',
  excellent: 'text-green-700 bg-green-100 border-green-300',
};

// Dashboard Widget Styles
export const widgetStyles = {
  base: 'bg-white rounded-lg border border-neutral-light shadow-sm p-6',
  title: 'text-lg font-semibold mb-4 text-primary',
  metric: 'text-3xl font-bold text-primary',
  subtitle: 'text-sm text-muted-foreground',
  content: 'space-y-4',
  icon: 'text-gold opacity-20', // Gold accent for widget icons
};

// Navigation Styles
export const navStyles = {
  item: 'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-teal-500/10 hover:text-teal-600',
  itemActive: 'bg-teal-500/20 text-teal-600 font-semibold', // Teal accent for active
  group: 'space-y-1',
  groupLabel: 'px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider',
};

// Table Styles
export const tableStyles = {
  wrapper: 'relative w-full overflow-auto',
  table: 'w-full caption-bottom text-sm',
  header: 'border-b bg-neutral-light/30',
  headerCell: 'h-12 px-4 text-left align-middle font-medium text-muted-foreground',
  body: 'border-b',
  row: 'border-b transition-colors hover:bg-neutral-light/20 data-[state=selected]:bg-teal-500/10',
  cell: 'p-4 align-middle',
};

// Animation Classes
export const animationClasses = {
  fadeIn: 'animate-[fadeIn_0.5s_ease-out]',
  fadeInUp: 'animate-[fadeInUp_0.6s_ease-out]',
  slideInRight: 'animate-[slideInRight_0.5s_ease-out]',
  pulse: 'animate-pulse',
  spin: 'animate-spin',
  bounce: 'animate-bounce',
  shimmer: 'animate-shimmer', // Teal shimmer loading effect
};

// Shadow Classes (Professional)
export const shadowClasses = {
  sm: 'shadow-sm',
  base: 'shadow',
  md: 'shadow-md',
  lg: 'shadow-lg',
  xl: 'shadow-xl',
  '2xl': 'shadow-2xl',
  inner: 'shadow-inner',
  professional: 'shadow-[0_1px_3px_0_rgba(0,0,0,0.1),0_1px_2px_0_rgba(0,0,0,0.06)]',
  trust: 'shadow-[0_0_20px_rgba(23,37,90,0.1)]', // Navy shadow for trust
  gold: 'shadow-[0_0_20px_rgba(203,150,62,0.15)]', // Gold glow effect
};

// Skeleton Loading Styles - Updated with Teal Shimmer
export const skeletonStyles =
  'animate-shimmer bg-gradient-to-r from-neutral-200 via-teal-100 to-neutral-200 bg-[length:200%_100%] rounded';

// Trust Indicator Styles
export const trustStyles = {
  badge:
    'inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-primary/5 text-primary text-xs font-medium border border-primary/10',
  securityIcon: 'inline-flex items-center gap-1.5 text-success text-sm',
  certBadge:
    'inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gold/10 text-gold-dark border border-gold/20 font-medium',
};

// Hero Section Styles
export const heroStyles = {
  container: 'flex flex-col items-center justify-center min-h-[85vh] px-6 py-12',
  badge:
    'inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gold/20 text-gold-dark text-xs font-semibold uppercase tracking-wider mb-6',
  title: 'text-4xl md:text-5xl lg:text-6xl font-bold text-center mb-4 max-w-4xl text-primary',
  tagline: 'text-sm font-light uppercase tracking-[0.3em] text-muted-foreground mb-8',
  description: 'text-lg text-center text-muted-foreground max-w-2xl mb-12',
};

// Persona-Based Styles
export const personaStyles = {
  analytical: {
    layout: 'data-dense high-information',
    features: 'advanced-filters custom-dashboards export-options',
    cardClass: 'border-primary/20', // More data-focused styling
  },
  cautious: {
    layout: 'guided step-by-step progressive-disclosure',
    features: 'help-tooltips confirmation-dialogs security-badges',
    cardClass: 'border-success/20', // Security-focused styling
  },
  principled: {
    layout: 'transparent audit-focused policy-centric',
    features: 'audit-trails version-history compliance-badges',
    cardClass: 'border-gold/20', // Authority-focused styling
  },
};

// Accessibility Classes
export const a11yStyles = {
  srOnly: 'sr-only',
  notSrOnly: 'not-sr-only',
  focusable:
    'focus:not-sr-only focus:absolute focus:inset-x-0 focus:top-0 focus:z-50 focus:bg-background focus:p-4',
};

// Responsive Hide/Show Utilities
export const responsiveStyles = {
  mobileOnly: 'block md:hidden',
  tabletUp: 'hidden md:block',
  desktopUp: 'hidden lg:block',
  mobileHide: 'hidden md:block',
};

// Print Styles
export const printStyles = {
  hide: 'print:hidden',
  only: 'hidden print:block',
  break: 'print:break-after-page',
};

// Utility function to get compliance score style
export function getComplianceScoreStyle(score: number): string {
  if (score <= 40) return complianceScoreStyles.critical;
  if (score <= 70) return complianceScoreStyles.warning;
  if (score <= 90) return complianceScoreStyles.good;
  return complianceScoreStyles.excellent;
}

// Utility function to get compliance score color
export function getComplianceScoreColor(score: number): string {
  if (score <= 40) return 'text-red-600';
  if (score <= 70) return 'text-amber-600';
  if (score <= 90) return 'text-green-600';
  return 'text-green-700';
}

// Utility function to build button className
export function getButtonClassName(
  variant: keyof typeof buttonVariants.variants = 'primary',
  size: keyof typeof buttonVariants.sizes = 'md',
  className?: string,
): string {
  return cn(
    buttonVariants.base,
    buttonVariants.variants[variant],
    buttonVariants.sizes[size],
    className,
  );
}

// Utility function to get status color classes
export function getStatusColor(status: string): string {
  const statusMap: Record<string, string> = {
    completed: 'text-green-600',
    'in-progress': 'text-blue-600',
    pending: 'text-amber-600',
    overdue: 'text-red-600',
    active: 'text-teal-600',
    inactive: 'text-gray-600',
  };
  return statusMap[status.toLowerCase()] || 'text-gray-600';
}

// Export a comprehensive style guide object
export const ruleIQStyles = {
  button: buttonVariants,
  card: cardStyles,
  form: formStyles,
  status: statusStyles,
  compliance: complianceScoreStyles,
  widget: widgetStyles,
  nav: navStyles,
  table: tableStyles,
  animation: animationClasses,
  shadow: shadowClasses,
  skeleton: skeletonStyles,
  trust: trustStyles,
  hero: heroStyles,
  persona: personaStyles,
  a11y: a11yStyles,
  responsive: responsiveStyles,
  print: printStyles,
  focus:
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
};

// Re-export as default for convenience
export default ruleIQStyles;
