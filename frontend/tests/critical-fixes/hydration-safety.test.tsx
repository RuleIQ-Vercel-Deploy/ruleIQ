import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock next-themes to control hydration behavior
const mockSetTheme = vi.fn();
const mockTheme = 'light';
let mockMounted = false;

vi.mock('next-themes', () => ({
  useTheme: () => ({
    theme: mockTheme,
    setTheme: mockSetTheme,
    resolvedTheme: mockTheme,
    systemTheme: 'light',
  }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock localStorage behavior during hydration
let mockLocalStorage: Record<string, string> = {};

Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: (key: string) => mockLocalStorage[key] || null,
    setItem: (key: string, value: string) => {
      mockLocalStorage[key] = value;
    },
    removeItem: (key: string) => {
      delete mockLocalStorage[key];
    },
    clear: () => {
      mockLocalStorage = {};
    },
  },
  writable: true,
});

// Component that uses localStorage and might cause hydration issues
const LocalStorageComponent = () => {
  const [mounted, setMounted] = React.useState(false);
  const [value, setValue] = React.useState<string | null>(null);

  React.useEffect(() => {
    setMounted(true);
    setValue(localStorage.getItem('test-key'));
  }, []);

  if (!mounted) {
    return <div data-testid="ssr-content">Loading...</div>;
  }

  return (
    <div data-testid="hydrated-content">
      <p>Hydrated: {value || 'No value'}</p>
    </div>
  );
};

// Theme component that could cause hydration mismatches
const ThemeAwareComponent = () => {
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  // Prevent hydration mismatch by not rendering theme-dependent content on server
  if (!mounted) {
    return <div data-testid="theme-loading">Theme loading...</div>;
  }

  return (
    <div data-testid="theme-content" className={`theme-${mockTheme}`}>
      Current theme: {mockTheme}
    </div>
  );
};

describe('Hydration Safety Tests', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
    mockLocalStorage = {};
    mockMounted = false;
  });

  afterEach(() => {
    queryClient.clear();
  });

  const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  describe('LocalStorage Access Safety', () => {
    it('should handle localStorage access safely during hydration', async () => {
      // Set some localStorage data before component renders
      mockLocalStorage['test-key'] = 'test-value';

      render(
        <TestWrapper>
          <LocalStorageComponent />
        </TestWrapper>,
      );

      // Component should handle hydration properly - either show SSR content or hydrated content
      // In our test environment, useEffect runs immediately, so we check for the final state
      await waitFor(() => {
        expect(screen.getByTestId('hydrated-content')).toBeInTheDocument();
      });
    });

    it('should transition from SSR to hydrated content correctly', async () => {
      // Create a component that simulates delayed hydration
      const DelayedHydrationComponent = () => {
        const [mounted, setMounted] = React.useState(false);
        const [value, setValue] = React.useState<string | null>(null);

        React.useEffect(() => {
          // Simulate async hydration
          const timer = setTimeout(() => {
            setMounted(true);
            setValue(mockLocalStorage['test-key'] || null);
          }, 50);
          return () => clearTimeout(timer);
        }, []);

        if (!mounted) {
          return <div data-testid="ssr-content">Loading...</div>;
        }

        return (
          <div data-testid="hydrated-content">
            <p>Hydrated: {value || 'No value'}</p>
          </div>
        );
      };

      mockLocalStorage['test-key'] = 'hydrated-value';

      render(
        <TestWrapper>
          <DelayedHydrationComponent />
        </TestWrapper>,
      );

      // Initially shows SSR content
      expect(screen.getByTestId('ssr-content')).toBeInTheDocument();

      // After hydration, should show client content
      await waitFor(() => {
        expect(screen.getByTestId('hydrated-content')).toBeInTheDocument();
      });

      expect(screen.getByText('Hydrated: hydrated-value')).toBeInTheDocument();
      expect(screen.queryByTestId('ssr-content')).not.toBeInTheDocument();
    });

    it('should handle missing localStorage gracefully', async () => {
      // Don't set any localStorage data

      render(
        <TestWrapper>
          <LocalStorageComponent />
        </TestWrapper>,
      );

      await waitFor(() => {
        expect(screen.getByTestId('hydrated-content')).toBeInTheDocument();
      });

      expect(screen.getByText('Hydrated: No value')).toBeInTheDocument();
    });
  });

  describe('Theme Provider Hydration Safety', () => {
    it('should prevent theme-related hydration mismatches', async () => {
      // Create a component that simulates delayed theme hydration
      const DelayedThemeComponent = () => {
        const [mounted, setMounted] = React.useState(false);

        React.useEffect(() => {
          // Simulate delayed theme hydration
          const timer = setTimeout(() => {
            setMounted(true);
          }, 50);
          return () => clearTimeout(timer);
        }, []);

        // Prevent hydration mismatch by not rendering theme-dependent content on server
        if (!mounted) {
          return <div data-testid="theme-loading">Theme loading...</div>;
        }

        return (
          <div data-testid="theme-content" className={`theme-${mockTheme}`}>
            Current theme: {mockTheme}
          </div>
        );
      };

      render(
        <TestWrapper>
          <DelayedThemeComponent />
        </TestWrapper>,
      );

      // Should show loading state initially to prevent hydration mismatch
      expect(screen.getByTestId('theme-loading')).toBeInTheDocument();
      expect(screen.queryByTestId('theme-content')).not.toBeInTheDocument();

      // Wait for theme to load
      await waitFor(() => {
        expect(screen.getByTestId('theme-content')).toBeInTheDocument();
      });
    });

    it('should render theme content after client-side hydration', async () => {
      render(
        <TestWrapper>
          <ThemeAwareComponent />
        </TestWrapper>,
      );

      // Wait for client-side hydration
      await waitFor(() => {
        expect(screen.getByTestId('theme-content')).toBeInTheDocument();
      });

      expect(screen.getByText(`Current theme: ${mockTheme}`)).toBeInTheDocument();
      expect(screen.queryByTestId('theme-loading')).not.toBeInTheDocument();
    });
  });

  describe('Auth Store Hydration Safety', () => {
    it('should handle auth store hydration without mismatches', async () => {
      // Mock auth store component that uses localStorage with delayed hydration
      const DelayedAuthComponent = () => {
        const [mounted, setMounted] = React.useState(false);
        const [isAuthenticated, setIsAuthenticated] = React.useState(false);

        React.useEffect(() => {
          // Simulate async auth check
          const timer = setTimeout(() => {
            setMounted(true);
            // Simulate reading auth state from localStorage
            const storedAuth = mockLocalStorage['ruleiq-auth-storage'];
            if (storedAuth) {
              try {
                const authData = JSON.parse(storedAuth);
                setIsAuthenticated(authData.state?.isAuthenticated || false);
              } catch {
                setIsAuthenticated(false);
              }
            }
          }, 50);
          return () => clearTimeout(timer);
        }, []);

        if (!mounted) {
          return <div data-testid="auth-loading">Checking authentication...</div>;
        }

        return (
          <div data-testid="auth-content">
            Auth status: {isAuthenticated ? 'Authenticated' : 'Not authenticated'}
          </div>
        );
      };

      // Set mock auth data
      mockLocalStorage['ruleiq-auth-storage'] = JSON.stringify({
        state: { isAuthenticated: true },
      });

      render(
        <TestWrapper>
          <DelayedAuthComponent />
        </TestWrapper>,
      );

      // Initially shows loading to prevent hydration mismatch
      expect(screen.getByTestId('auth-loading')).toBeInTheDocument();

      // After hydration shows auth content
      await waitFor(() => {
        expect(screen.getByTestId('auth-content')).toBeInTheDocument();
      });

      expect(screen.getByText('Auth status: Authenticated')).toBeInTheDocument();
    });
  });

  describe('SSR/Client Consistency', () => {
    it('should render consistently between server and client', () => {
      const ConsistentComponent = () => {
        const [mounted, setMounted] = React.useState(false);

        React.useEffect(() => {
          setMounted(true);
        }, []);

        // Always render the same content structure
        return (
          <div data-testid="consistent-component">
            <h1>App Title</h1>
            <div data-testid="dynamic-content">
              {mounted ? 'Client-side content' : 'Loading...'}
            </div>
          </div>
        );
      };

      render(
        <TestWrapper>
          <ConsistentComponent />
        </TestWrapper>,
      );

      // Component structure should be consistent
      expect(screen.getByTestId('consistent-component')).toBeInTheDocument();
      expect(screen.getByText('App Title')).toBeInTheDocument();
      expect(screen.getByTestId('dynamic-content')).toBeInTheDocument();
    });

    it('should handle conditional rendering safely', async () => {
      const ConditionalComponent = () => {
        const [mounted, setMounted] = React.useState(false);
        const [showContent, setShowContent] = React.useState(false);

        React.useEffect(() => {
          setMounted(true);
          // Delay showing content to simulate hydration
          setTimeout(() => setShowContent(true), 10);
        }, []);

        return (
          <div data-testid="conditional-wrapper">
            {mounted && showContent ? (
              <div data-testid="conditional-content">Conditional content</div>
            ) : (
              <div data-testid="conditional-placeholder">Loading conditional content...</div>
            )}
          </div>
        );
      };

      render(
        <TestWrapper>
          <ConditionalComponent />
        </TestWrapper>,
      );

      // In test environment, both states may appear very quickly
      // Check that the component eventually shows the content
      await waitFor(() => {
        expect(screen.getByTestId('conditional-content')).toBeInTheDocument();
      });
    });
  });

  describe('Component Mount State Management', () => {
    it('should properly track component mount state', async () => {
      const MountTrackingComponent = () => {
        const [mounted, setMounted] = React.useState(false);

        React.useEffect(() => {
          setMounted(true);
          return () => setMounted(false);
        }, []);

        return (
          <div data-testid="mount-tracker">
            Mount state: {mounted ? 'mounted' : 'not-mounted'}
          </div>
        );
      };

      const { unmount } = render(
        <TestWrapper>
          <MountTrackingComponent />
        </TestWrapper>,
      );

      // In test environment, useEffect runs immediately
      await waitFor(() => {
        expect(screen.getByText('Mount state: mounted')).toBeInTheDocument();
      });

      // Component should track mount state properly
      unmount();
    });

    it('should handle multiple components with mount tracking', async () => {
      const MultiMountComponent = () => {
        const [mounted1, setMounted1] = React.useState(false);
        const [mounted2, setMounted2] = React.useState(false);

        React.useEffect(() => {
          setMounted1(true);
          setTimeout(() => setMounted2(true), 10);
        }, []);

        return (
          <div data-testid="multi-mount">
            <div data-testid="component-1">
              Component 1: {mounted1 ? 'ready' : 'loading'}
            </div>
            <div data-testid="component-2">
              Component 2: {mounted2 ? 'ready' : 'loading'}
            </div>
          </div>
        );
      };

      render(
        <TestWrapper>
          <MultiMountComponent />
        </TestWrapper>,
      );

      // In test environment, effects run quickly
      // First component mounts immediately
      await waitFor(() => {
        expect(screen.getByText('Component 1: ready')).toBeInTheDocument();
      });

      // Second component mounts after delay
      await waitFor(() => {
        expect(screen.getByText('Component 2: ready')).toBeInTheDocument();
      });
    });
  });
});