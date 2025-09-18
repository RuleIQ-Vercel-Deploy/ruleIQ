import { neuralPurple, silver, semantic, neutral } from './theme/neural-purple-colors';

/**
 * Theme utility functions for the Neural Purple design system
 */
export class ThemeUtils {
  /**
   * Get the Neural Purple theme configuration
   */
  static getThemeConfig() {
    return {
      colors: {
        primary: neuralPurple,
        accent: silver,
        semantic,
        neutral,
      },
    };
  }

  /**
   * Check if dark mode is active
   */
  static isDarkMode(): boolean {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark');
    }
    return false;
  }

  /**
   * Get theme-specific CSS class names
   */
  static getThemeClasses() {
    const isDark = this.isDarkMode();

    return {
      root: 'neural-purple',
      // Common theme classes
      background: isDark ? 'bg-gray-900' : 'bg-gray-50',
      surface: isDark ? 'bg-gray-800' : 'bg-white',
      text: isDark ? 'text-gray-100' : 'text-gray-900',
      primary: 'bg-purple-600 text-white hover:bg-purple-700',
      secondary: 'bg-silver-400 text-gray-900 hover:bg-silver-500',
      border: isDark ? 'border-gray-700' : 'border-gray-200',
      // Neural Purple specific
      accent: 'bg-purple-100 text-purple-900',
      gradient: 'bg-purple-gradient',
    };
  }

  /**
   * Apply dark mode toggle
   */
  static toggleDarkMode() {
    if (typeof window === 'undefined') return;

    const root = document.documentElement;
    const isDark = root.classList.contains('dark');

    if (isDark) {
      root.classList.remove('dark');
      localStorage.setItem('ruleiq-theme-mode', 'light');
    } else {
      root.classList.add('dark');
      localStorage.setItem('ruleiq-theme-mode', 'dark');
    }
  }

  /**
   * Initialize theme from stored preference
   */
  static initializeTheme() {
    if (typeof window === 'undefined') return;

    const stored = localStorage.getItem('ruleiq-theme-mode');
    const root = document.documentElement;

    if (stored === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }

  /**
   * Get theme-specific colors for programmatic use
   */
  static getThemeColors() {
    return {
      primary: neuralPurple.primary,
      primaryDark: neuralPurple.dark,
      primaryLight: neuralPurple.light,
      secondary: silver.primary,
      secondaryLight: silver.light,
      secondaryDark: silver.dark,
      background: neutral.gray['50'],
      surface: neutral.white,
      text: neutral.gray['900'],
      border: neutral.gray['200'],
      success: semantic.success,
      error: semantic.error,
      warning: semantic.warning,
      info: semantic.info,
    };
  }

  /**
   * Get gradient configurations
   */
  static getGradients() {
    return {
      purple: `linear-gradient(135deg, ${neuralPurple.dark} 0%, ${neuralPurple.primary} 50%, ${neuralPurple.light} 100%)`,
      silver: `linear-gradient(135deg, ${silver.dark} 0%, ${silver.primary} 50%, ${silver.light} 100%)`,
      radial: `radial-gradient(ellipse at top, ${neuralPurple.light}, ${neuralPurple.primary}, ${neuralPurple.dark})`,
    };
  }
}

/**
 * Hook-style utility for Neural Purple theme
 */
export function useThemeClasses() {
  const isDarkMode = ThemeUtils.isDarkMode();
  const classes = ThemeUtils.getThemeClasses();
  const colors = ThemeUtils.getThemeColors();
  const gradients = ThemeUtils.getGradients();

  return {
    isDarkMode,
    classes,
    colors,
    gradients,
    toggleDarkMode: ThemeUtils.toggleDarkMode,
  };
}
