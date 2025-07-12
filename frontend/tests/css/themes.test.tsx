import { describe, expect, it, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Theme Provider Component
const ThemeProvider = ({ children, theme = 'light' }: { children: React.ReactNode; theme?: 'light' | 'dark' }) => {
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme);
  }, [theme]);

  return <>{children}</>;
};

// Theme Toggle Component
const ThemeToggle = () => {
  const [theme, setTheme] = React.useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeProvider theme={theme}>
      <button 
        onClick={toggleTheme} 
        data-testid="theme-toggle"
        className="bg-primary dark:bg-primary-dark text-white"
      >
        Toggle Theme
      </button>
      <div data-testid="theme-indicator">{theme}</div>
    </ThemeProvider>
  );
};

// CSS Variables Test Component
const CSSVariablesComponent = () => (
  <div>
    <div 
      className="text-[var(--primary)] bg-[var(--background)]"
      data-testid="css-var-primary"
    >
      Primary Color
    </div>
    <div 
      className="text-[var(--secondary)] bg-[var(--surface)]"
      data-testid="css-var-secondary"
    >
      Secondary Color
    </div>
    <div 
      className="text-[var(--accent)] border-[var(--border)]"
      data-testid="css-var-accent"
    >
      Accent Color
    </div>
  </div>
);

// Dark Mode Component
const DarkModeComponent = () => (
  <div className="bg-white dark:bg-gray-900">
    <h1 className="text-gray-900 dark:text-white">Dark Mode Title</h1>
    <p className="text-gray-600 dark:text-gray-300">Dark Mode Text</p>
    <button className="bg-primary dark:bg-primary-light text-white">
      Dark Mode Button
    </button>
    <div className="border border-gray-200 dark:border-gray-700">
      Dark Mode Border
    </div>
  </div>
);

// Custom Properties Component
const CustomPropertiesComponent = () => {
  React.useEffect(() => {
    // Set custom properties
    const root = document.documentElement;
    root.style.setProperty('--primary', '#17255A');
    root.style.setProperty('--primary-dark', '#0F1938');
    root.style.setProperty('--primary-light', '#2B3A6A');
    root.style.setProperty('--gold', '#CB963E');
    root.style.setProperty('--gold-dark', '#A67A2E');
    root.style.setProperty('--gold-light', '#E0B567');
    root.style.setProperty('--cyan', '#34FEF7');
    root.style.setProperty('--neutral-light', '#D0D5E3');
    root.style.setProperty('--neutral-medium', '#C2C2C2');
  }, []);

  return (
    <div>
      <div style={{ color: 'var(--primary)' }} data-testid="primary-var">
        Primary Color
      </div>
      <div style={{ backgroundColor: 'var(--gold)' }} data-testid="gold-var">
        Gold Background
      </div>
      <div style={{ borderColor: 'var(--cyan)' }} className="border-2" data-testid="cyan-var">
        Cyan Border
      </div>
    </div>
  );
};

// Theme Variations Component
const ThemeVariationsComponent = ({ variant }: { variant: 'default' | 'compact' | 'comfortable' }) => {
  const getSpacing = () => {
    switch (variant) {
      case 'compact': return 'p-2 gap-2';
      case 'comfortable': return 'p-8 gap-8';
      default: return 'p-4 gap-4';
    }
  };

  return (
    <div className={`${getSpacing()} flex flex-col`} data-testid={`theme-${variant}`}>
      <button className={`${getSpacing()} bg-primary text-white rounded`}>
        {variant} Button
      </button>
      <div className={`${getSpacing()} bg-gray-100 rounded`}>
        {variant} Content
      </div>
    </div>
  );
};

// Color Scheme Component
const ColorSchemeComponent = ({ scheme }: { scheme: 'primary' | 'secondary' | 'accent' }) => {
  const getColorClasses = () => {
    switch (scheme) {
      case 'primary':
        return 'bg-primary text-white hover:bg-primary-dark';
      case 'secondary':
        return 'bg-gray-200 text-gray-800 hover:bg-gray-300';
      case 'accent':
        return 'bg-gold text-primary hover:bg-gold-dark';
    }
  };

  return (
    <div className={`${getColorClasses()} p-4 rounded transition-colors`} data-testid={`scheme-${scheme}`}>
      {scheme} Color Scheme
    </div>
  );
};

// System Preference Component
const SystemPreferenceComponent = () => {
  const [prefersDark, setPrefersDark] = React.useState(false);

  React.useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setPrefersDark(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => setPrefersDark(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return (
    <div className={prefersDark ? 'dark' : 'light'}>
      <div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white p-4">
        System prefers: {prefersDark ? 'dark' : 'light'} mode
      </div>
    </div>
  );
};

// Semantic Colors Component
const SemanticColorsComponent = () => (
  <div className="space-y-4">
    <div className="text-green-600 dark:text-green-400" data-testid="success-color">
      Success Message
    </div>
    <div className="text-gold dark:text-yellow-400" data-testid="warning-color">
      Warning Message
    </div>
    <div className="text-red-600 dark:text-red-400" data-testid="error-color">
      Error Message
    </div>
    <div className="text-cyan dark:text-cyan-400" data-testid="info-color">
      Info Message
    </div>
  </div>
);

// Import React
import React from 'react';

describe('Theme and Dark Mode Tests', () => {
  beforeEach(() => {
    // Reset document styles
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.style.cssText = '';
  });

  afterEach(() => {
    // Clean up
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.style.cssText = '';
  });

  describe('Theme Switching Functionality', () => {
    it('should toggle between light and dark themes', async () => {
      const user = userEvent.setup();
      render(<ThemeToggle />);

      const toggleButton = screen.getByTestId('theme-toggle');
      const indicator = screen.getByTestId('theme-indicator');

      // Initial state
      expect(indicator).toHaveTextContent('light');
      expect(document.documentElement).toHaveAttribute('data-theme', 'light');
      expect(document.documentElement).toHaveClass('light');

      // Toggle to dark
      await user.click(toggleButton);
      await waitFor(() => {
        expect(indicator).toHaveTextContent('dark');
        expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
        expect(document.documentElement).toHaveClass('dark');
      });

      // Toggle back to light
      await user.click(toggleButton);
      await waitFor(() => {
        expect(indicator).toHaveTextContent('light');
        expect(document.documentElement).toHaveAttribute('data-theme', 'light');
        expect(document.documentElement).toHaveClass('light');
      });
    });

    it('should apply theme-specific classes', () => {
      const { rerender } = render(
        <ThemeProvider theme="light">
          <DarkModeComponent />
        </ThemeProvider>
      );

      // Light mode
      const heading = screen.getByRole('heading');
      expect(heading).toHaveClass('text-gray-900');
      expect(heading).toHaveClass('dark:text-white');

      // Dark mode
      rerender(
        <ThemeProvider theme="dark">
          <DarkModeComponent />
        </ThemeProvider>
      );

      expect(document.documentElement).toHaveClass('dark');
    });
  });

  describe('Dark Mode CSS Variables', () => {
    it('should use CSS custom properties for theming', () => {
      render(<CustomPropertiesComponent />);

      const primaryVar = screen.getByTestId('primary-var');
      const goldVar = screen.getByTestId('gold-var');
      const cyanVar = screen.getByTestId('cyan-var');

      expect(primaryVar).toHaveStyle({ color: 'var(--primary)' });
      expect(goldVar).toHaveStyle({ backgroundColor: 'var(--gold)' });
      expect(cyanVar).toHaveStyle({ borderColor: 'var(--cyan)' });
    });

    it('should have correct CSS variable values', () => {
      render(<CustomPropertiesComponent />);

      const root = document.documentElement;
      expect(root.style.getPropertyValue('--primary')).toBe('#17255A');
      expect(root.style.getPropertyValue('--primary-dark')).toBe('#0F1938');
      expect(root.style.getPropertyValue('--primary-light')).toBe('#2B3A6A');
      expect(root.style.getPropertyValue('--gold')).toBe('#CB963E');
      expect(root.style.getPropertyValue('--gold-dark')).toBe('#A67A2E');
      expect(root.style.getPropertyValue('--gold-light')).toBe('#E0B567');
      expect(root.style.getPropertyValue('--cyan')).toBe('#34FEF7');
      expect(root.style.getPropertyValue('--neutral-light')).toBe('#D0D5E3');
      expect(root.style.getPropertyValue('--neutral-medium')).toBe('#C2C2C2');
    });

    it('should support CSS variables in Tailwind classes', () => {
      render(<CSSVariablesComponent />);

      const primary = screen.getByTestId('css-var-primary');
      const secondary = screen.getByTestId('css-var-secondary');
      const accent = screen.getByTestId('css-var-accent');

      expect(primary).toHaveClass('text-[var(--primary)]');
      expect(primary).toHaveClass('bg-[var(--background)]');
      expect(secondary).toHaveClass('text-[var(--secondary)]');
      expect(secondary).toHaveClass('bg-[var(--surface)]');
      expect(accent).toHaveClass('text-[var(--accent)]');
      expect(accent).toHaveClass('border-[var(--border)]');
    });
  });

  describe('CSS Custom Properties', () => {
    it('should support dynamic CSS property updates', async () => {
      const DynamicPropertiesComponent = () => {
        const [primaryColor, setPrimaryColor] = React.useState('#17255A');

        const updateColor = () => {
          const newColor = '#FF0000';
          setPrimaryColor(newColor);
          document.documentElement.style.setProperty('--primary', newColor);
        };

        return (
          <div>
            <button onClick={updateColor} data-testid="update-color">
              Update Color
            </button>
            <div style={{ color: 'var(--primary)' }} data-testid="dynamic-color">
              Dynamic Color
            </div>
            <div data-testid="color-value">{primaryColor}</div>
          </div>
        );
      };

      const user = userEvent.setup();
      render(<DynamicPropertiesComponent />);

      const updateButton = screen.getByTestId('update-color');
      const colorValue = screen.getByTestId('color-value');

      expect(colorValue).toHaveTextContent('#17255A');

      await user.click(updateButton);

      await waitFor(() => {
        expect(colorValue).toHaveTextContent('#FF0000');
        expect(document.documentElement.style.getPropertyValue('--primary')).toBe('#FF0000');
      });
    });

    it('should handle CSS property inheritance', () => {
      const InheritanceComponent = () => (
        <div style={{ '--parent-color': '#17255A' } as React.CSSProperties}>
          <div style={{ color: 'var(--parent-color)' }} data-testid="child">
            Inherited Color
          </div>
          <div>
            <div style={{ color: 'var(--parent-color)' }} data-testid="nested-child">
              Nested Inherited Color
            </div>
          </div>
        </div>
      );

      render(<InheritanceComponent />);

      const child = screen.getByTestId('child');
      const nestedChild = screen.getByTestId('nested-child');

      expect(child).toHaveStyle({ color: 'var(--parent-color)' });
      expect(nestedChild).toHaveStyle({ color: 'var(--parent-color)' });
    });
  });

  describe('Color Scheme Variations', () => {
    it('should handle different color schemes', () => {
      const schemes = ['primary', 'secondary', 'accent'] as const;

      schemes.forEach(scheme => {
        const { container } = render(<ColorSchemeComponent scheme={scheme} />);
        const element = screen.getByTestId(`scheme-${scheme}`);

        expect(element).toBeInTheDocument();
        expect(element).toHaveTextContent(`${scheme} Color Scheme`);

        if (scheme === 'primary') {
          expect(element).toHaveClass('bg-primary', 'text-white', 'hover:bg-primary-dark');
        } else if (scheme === 'secondary') {
          expect(element).toHaveClass('bg-gray-200', 'text-gray-800', 'hover:bg-gray-300');
        } else if (scheme === 'accent') {
          expect(element).toHaveClass('bg-gold', 'text-primary', 'hover:bg-gold-dark');
        }
      });
    });

    it('should handle theme variations', () => {
      const variants = ['default', 'compact', 'comfortable'] as const;

      variants.forEach(variant => {
        const { container } = render(<ThemeVariationsComponent variant={variant} />);
        const element = screen.getByTestId(`theme-${variant}`);

        expect(element).toBeInTheDocument();

        if (variant === 'compact') {
          expect(element).toHaveClass('p-2', 'gap-2');
        } else if (variant === 'comfortable') {
          expect(element).toHaveClass('p-8', 'gap-8');
        } else {
          expect(element).toHaveClass('p-4', 'gap-4');
        }
      });
    });

    it('should handle semantic colors in different themes', () => {
      const { rerender } = render(
        <ThemeProvider theme="light">
          <SemanticColorsComponent />
        </ThemeProvider>
      );

      const success = screen.getByTestId('success-color');
      const warning = screen.getByTestId('warning-color');
      const error = screen.getByTestId('error-color');
      const info = screen.getByTestId('info-color');

      // Light theme
      expect(success).toHaveClass('text-green-600', 'dark:text-green-400');
      expect(warning).toHaveClass('text-gold', 'dark:text-yellow-400');
      expect(error).toHaveClass('text-red-600', 'dark:text-red-400');
      expect(info).toHaveClass('text-cyan', 'dark:text-cyan-400');

      // Dark theme
      rerender(
        <ThemeProvider theme="dark">
          <SemanticColorsComponent />
        </ThemeProvider>
      );

      expect(document.documentElement).toHaveClass('dark');
    });
  });

  describe('System Preference Detection', () => {
    let originalMatchMedia: typeof window.matchMedia;

    beforeEach(() => {
      originalMatchMedia = window.matchMedia;
    });

    afterEach(() => {
      window.matchMedia = originalMatchMedia;
    });

    it('should detect system color scheme preference', () => {
      // Mock prefers-color-scheme
      window.matchMedia = vi.fn().mockImplementation(query => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));

      render(<SystemPreferenceComponent />);

      const container = screen.getByText(/System prefers:/);
      expect(container).toHaveTextContent('System prefers: dark mode');
    });
  });

  describe('Theme Persistence', () => {
    it('should save theme preference to localStorage', async () => {
      const ThemePersistenceComponent = () => {
        const [theme, setTheme] = React.useState<'light' | 'dark'>(() => {
          const saved = localStorage.getItem('theme');
          return (saved as 'light' | 'dark') || 'light';
        });

        const updateTheme = (newTheme: 'light' | 'dark') => {
          setTheme(newTheme);
          localStorage.setItem('theme', newTheme);
        };

        return (
          <div>
            <button onClick={() => updateTheme('dark')} data-testid="set-dark">
              Set Dark
            </button>
            <button onClick={() => updateTheme('light')} data-testid="set-light">
              Set Light
            </button>
            <div data-testid="current-theme">{theme}</div>
          </div>
        );
      };

      const user = userEvent.setup();
      render(<ThemePersistenceComponent />);

      const currentTheme = screen.getByTestId('current-theme');
      const setDarkButton = screen.getByTestId('set-dark');
      const setLightButton = screen.getByTestId('set-light');

      // Set dark theme
      await user.click(setDarkButton);
      expect(currentTheme).toHaveTextContent('dark');
      expect(localStorage.getItem('theme')).toBe('dark');

      // Set light theme
      await user.click(setLightButton);
      expect(currentTheme).toHaveTextContent('light');
      expect(localStorage.getItem('theme')).toBe('light');
    });
  });

  describe('Advanced Theme Features', () => {
    it('should support theme-aware shadows', () => {
      const { container } = render(
        <div>
          <div className="shadow-sm dark:shadow-white/10">Light Shadow</div>
          <div className="shadow-md dark:shadow-2xl">Medium Shadow</div>
          <div className="shadow-lg dark:shadow-none">Large Shadow</div>
        </div>
      );

      expect(container.querySelector('.shadow-sm')).toHaveClass('dark:shadow-white/10');
      expect(container.querySelector('.shadow-md')).toHaveClass('dark:shadow-2xl');
      expect(container.querySelector('.shadow-lg')).toHaveClass('dark:shadow-none');
    });

    it('should support theme-aware gradients', () => {
      const { container } = render(
        <div>
          <div className="bg-gradient-to-r from-primary to-primary-light dark:from-primary-dark dark:to-primary">
            Theme Gradient
          </div>
          <div className="bg-gradient-to-br from-white to-gray-100 dark:from-gray-900 dark:to-gray-800">
            Background Gradient
          </div>
        </div>
      );

      const gradients = container.querySelectorAll('[class*="bg-gradient"]');
      expect(gradients).toHaveLength(2);
      expect(gradients[0]).toHaveClass('dark:from-primary-dark', 'dark:to-primary');
      expect(gradients[1]).toHaveClass('dark:from-gray-900', 'dark:to-gray-800');
    });

    it('should support theme-aware borders', () => {
      const { container } = render(
        <div>
          <div className="border border-gray-200 dark:border-gray-700">
            Theme Border
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            <div>Item 1</div>
            <div>Item 2</div>
          </div>
        </div>
      );

      expect(container.querySelector('.border')).toHaveClass('dark:border-gray-700');
      expect(container.querySelector('.divide-y')).toHaveClass('dark:divide-gray-700');
    });
  });
});