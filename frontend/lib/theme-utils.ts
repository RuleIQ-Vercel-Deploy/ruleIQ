import { env } from '@/config/env';

export type DesignSystem = 'legacy' | 'teal';

/**
 * Theme utility functions for the design system migration
 */
export class ThemeUtils {
  /**
   * Get the current design system based on environment flags and localStorage
   */
  static getCurrentDesignSystem(): DesignSystem {
    // Check environment flag first
    if (env.NEXT_PUBLIC_USE_NEW_THEME) {
      return 'teal';
    }

    // Check localStorage if on client
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('ruleiq-design-system');
      if (stored === 'teal' || stored === 'legacy') {
        return stored;
      }
    }

    return 'legacy';
  }

  /**
   * Check if the new teal theme is active
   */
  static isNewTheme(): boolean {
    return this.getCurrentDesignSystem() === 'teal';
  }

  /**
   * Get theme-specific CSS class names
   */
  static getThemeClasses(designSystem: DesignSystem = this.getCurrentDesignSystem()) {
    const base = `design-${designSystem}`;

    return {
      root: base,
      // Legacy dark theme classes
      legacy: {
        background: 'bg-surface-base',
        surface: 'bg-surface-primary',
        text: 'text-text-primary',
        primary: 'bg-brand-primary text-white',
        secondary: 'bg-brand-secondary text-white',
        border: 'border-neutral-700',
      },
      // New teal light theme classes
      teal: {
        background: 'bg-neutral-50',
        surface: 'bg-white',
        text: 'text-neutral-900',
        primary: 'bg-brand-primary text-white',
        secondary: 'bg-brand-secondary text-white',
        border: 'border-neutral-200',
      },
    };
  }

  /**
   * Get conditional class names based on current theme
   */
  static cn(
    legacyClasses: string,
    tealClasses: string,
    designSystem: DesignSystem = this.getCurrentDesignSystem(),
  ): string {
    return designSystem === 'teal' ? tealClasses : legacyClasses;
  }

  /**
   * Apply theme to document root
   */
  static applyTheme(designSystem: DesignSystem) {
    if (typeof window === 'undefined') return;

    const root = document.documentElement;

    // Remove existing theme classes
    root.classList.remove('design-legacy', 'design-teal');

    // Add new theme class
    root.classList.add(`design-${designSystem}`);

    // Store preference
    localStorage.setItem('ruleiq-design-system', designSystem);
  }

  /**
   * Get theme-specific colors for programmatic use
   */
  static getThemeColors(designSystem: DesignSystem = this.getCurrentDesignSystem()) {
    const colors = {
      legacy: {
        primary: '#7C3AED',
        secondary: '#06B6D4',
        background: '#0A0A0B',
        surface: '#111113',
        text: '#FAFAFA',
        border: '#3F3F46',
      },
      teal: {
        primary: '#2C7A7B',
        secondary: '#319795',
        background: '#F9FAFB',
        surface: '#FFFFFF',
        text: '#111827',
        border: '#E5E7EB',
      },
    };

    return colors[designSystem];
  }

  /**
   * Check if feature flag allows theme switching
   */
  static canSwitchTheme(): boolean {
    return !env.NEXT_PUBLIC_USE_NEW_THEME; // Allow switching only when not forced by env
  }

  /**
   * Get theme toggle button props
   */
  static getToggleProps(currentTheme: DesignSystem) {
    return {
      'aria-label': `Switch to ${currentTheme === 'legacy' ? 'new teal' : 'legacy'} theme`,
      'data-theme': currentTheme,
      title: `Currently using ${currentTheme} theme. Click to switch.`,
    };
  }
}

/**
 * Hook-style utility for conditional classes
 */
export function useThemeClasses() {
  const designSystem = ThemeUtils.getCurrentDesignSystem();
  const classes = ThemeUtils.getThemeClasses(designSystem);

  return {
    designSystem,
    isNewTheme: designSystem === 'teal',
    classes,
    cn: (legacyClasses: string, tealClasses: string) =>
      ThemeUtils.cn(legacyClasses, tealClasses, designSystem),
    colors: ThemeUtils.getThemeColors(designSystem),
  };
}
