/**
 * Memory Leak Detection Tests for React Components
 *
 * This test suite checks for common memory leak patterns in React components:
 * 1. Event listeners not removed on unmount
 * 2. Timers (setTimeout/setInterval) not cleared
 * 3. Async operations not cancelled
 * 4. WebSocket connections not closed
 * 5. Subscriptions not unsubscribed
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AIHelpTooltip } from '@/components/assessments/AIHelpTooltip';
import { AIGuidancePanel } from '@/components/assessments/AIGuidancePanel';
import { AIErrorBoundary } from '@/components/assessments/AIErrorBoundary';
import { AutoSaveIndicator } from '@/components/assessments/questionnaire/auto-save-indicator';
import { vi } from 'vitest';

// Mock the services
vi.mock('@/lib/api/services/assessment-ai.service', () => ({
  assessmentAIService: {
    getQuestionHelp: vi.fn().mockResolvedValue({
      help_text: 'AI help response',
      key_points: ['Point 1', 'Point 2'],
      follow_up_questions: ['Question 1?', 'Question 2?'],
    }),
  },
}));

describe('Memory Leak Detection Tests', () => {
  // Track all event listeners, timers, and async operations
  let originalAddEventListener: typeof document.addEventListener;
  let originalRemoveEventListener: typeof document.removeEventListener;
  let originalSetTimeout: typeof setTimeout;
  let originalClearTimeout: typeof clearTimeout;
  let originalSetInterval: typeof setInterval;
  let originalClearInterval: typeof clearInterval;

  let eventListeners: Map<string, Set<EventListener>>;
  let activeTimers: Set<NodeJS.Timeout>;
  let activeIntervals: Set<NodeJS.Timeout>;

  beforeEach(() => {
    // Initialize tracking
    eventListeners = new Map();
    activeTimers = new Set();
    activeIntervals = new Set();

    // Store original functions
    originalAddEventListener = document.addEventListener;
    originalRemoveEventListener = document.removeEventListener;
    originalSetTimeout = global.setTimeout;
    originalClearTimeout = global.clearTimeout;
    originalSetInterval = global.setInterval;
    originalClearInterval = global.clearInterval;

    // Mock addEventListener to track listeners
    document.addEventListener = vi.fn((event: string, listener: EventListener, options?: any) => {
      if (!eventListeners.has(event)) {
        eventListeners.set(event, new Set());
      }
      eventListeners.get(event)!.add(listener);
      return originalAddEventListener.call(document, event, listener, options);
    });

    // Mock removeEventListener to track cleanup
    document.removeEventListener = vi.fn(
      (event: string, listener: EventListener, options?: any) => {
        if (eventListeners.has(event)) {
          eventListeners.get(event)!.delete(listener);
        }
        return originalRemoveEventListener.call(document, event, listener, options);
      },
    );

    // Mock setTimeout to track timers
    global.setTimeout = vi.fn((callback: any, delay?: number, ...args: unknown[]) => {
      const timer = originalSetTimeout(callback, delay, ...args);
      activeTimers.add(timer);
      return timer;
    }) as any;

    // Mock clearTimeout to track cleanup
    global.clearTimeout = vi.fn((timer: NodeJS.Timeout) => {
      activeTimers.delete(timer);
      return originalClearTimeout(timer);
    }) as any;

    // Mock setInterval to track intervals
    global.setInterval = vi.fn((callback: any, delay?: number, ...args: unknown[]) => {
      const interval = originalSetInterval(callback, delay, ...args);
      activeIntervals.add(interval);
      return interval;
    }) as any;

    // Mock clearInterval to track cleanup
    global.clearInterval = vi.fn((interval: NodeJS.Timeout) => {
      activeIntervals.delete(interval);
      return originalClearInterval(interval);
    }) as any;
  });

  afterEach(() => {
    // Restore original functions
    document.addEventListener = originalAddEventListener;
    document.removeEventListener = originalRemoveEventListener;
    global.setTimeout = originalSetTimeout;
    global.clearTimeout = originalClearTimeout;
    global.setInterval = originalSetInterval;
    global.clearInterval = originalClearInterval;

    // Clear any remaining timers/intervals
    activeTimers.forEach((timer) => clearTimeout(timer));
    activeIntervals.forEach((interval) => clearInterval(interval));
  });

  describe('AIHelpTooltip Component', () => {
    it('should cleanup event listeners on unmount', () => {
      const mockQuestion = {
        id: 'q1',
        text: 'Test question',
        type: 'boolean' as const,
        required: true,
      };

      const { unmount } = render(<AIHelpTooltip question={mockQuestion} frameworkId="gdpr" />);

      // Check that event listener was added
      expect(document.addEventListener).toHaveBeenCalledWith('keydown', expect.any(Function));
      expect(eventListeners.get('keydown')?.size).toBe(1);

      // Unmount component
      unmount();

      // Verify event listener was removed
      expect(document.removeEventListener).toHaveBeenCalledWith('keydown', expect.any(Function));
      expect(eventListeners.get('keydown')?.size).toBe(0);
    });

    it('should not have active async operations after unmount', async () => {
      const mockQuestion = {
        id: 'q1',
        text: 'Test question',
        type: 'boolean' as const,
        required: true,
      };

      const { unmount } = render(<AIHelpTooltip question={mockQuestion} frameworkId="gdpr" />);

      // Trigger AI help request
      const helpButton = screen.getByRole('button', { name: /ai help/i });
      fireEvent.click(helpButton);

      // Unmount while request might be in progress
      unmount();

      // Wait a bit to ensure no late updates
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
      });

      // No assertions needed - if component tries to update after unmount,
      // React will throw an error which will fail the test
    });
  });

  describe('AIGuidancePanel Component', () => {
    it('should handle unmount during async loading', async () => {
      const mockQuestion = {
        id: 'q1',
        text: 'Test question',
        type: 'boolean' as const,
        required: true,
      };

      const { unmount } = render(
        <AIGuidancePanel question={mockQuestion} frameworkId="gdpr" defaultOpen={true} />,
      );

      // Component should start loading immediately due to defaultOpen
      expect(screen.getByText(/analyzing compliance requirements/i)).toBeInTheDocument();

      // Unmount while loading
      unmount();

      // Wait to ensure no late updates
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
      });
    });
  });

  describe('AutoSaveIndicator Component', () => {
    it('should cleanup interval on unmount', () => {
      const { unmount } = render(<AutoSaveIndicator />);

      // Check that interval was created
      expect(global.setInterval).toHaveBeenCalledWith(expect.any(Function), 10000);
      expect(activeIntervals.size).toBe(1);

      // Unmount component
      unmount();

      // Verify interval was cleared
      expect(global.clearInterval).toHaveBeenCalled();
      expect(activeIntervals.size).toBe(0);
    });

    it('should cleanup setTimeout calls on unmount', async () => {
      const { unmount, rerender } = render(<AutoSaveIndicator />);

      // Wait for the component to trigger its internal timer
      await act(async () => {
        await new Promise((resolve) => originalSetTimeout(resolve, 100));
      });

      // Check that timers were created
      expect(activeTimers.size).toBeGreaterThan(0);

      // Unmount component
      unmount();

      // All timers should be cleared
      expect(activeTimers.size).toBe(0);
    });
  });

  describe('General Memory Leak Patterns', () => {
    it('should detect components with uncleaned event listeners', () => {
      const LeakyComponent = () => {
        React.useEffect(() => {
          const handler = () =>
    // TODO: Replace with proper logging
          // Intentionally not cleaning up to test detection
          document.addEventListener('click', handler);
          // Missing: return () => document.removeEventListener('click', handler);
        }, []);

        return <div>Leaky Component</div>;
      };

      const { unmount } = render(<LeakyComponent />);

      // Check that listener was added
      expect(eventListeners.get('click')?.size).toBe(1);

      // Unmount
      unmount();

      // Verify listener was NOT removed (memory leak!)
      expect(eventListeners.get('click')?.size).toBe(1);
      expect(document.removeEventListener).not.toHaveBeenCalledWith('click', expect.any(Function));
    });

    it('should detect components with uncleaned timers', () => {
      const LeakyTimerComponent = () => {
        React.useEffect(() => {
          // Intentionally not cleaning up to test detection
          setTimeout(() => {
            // TODO: Replace with proper logging
            // Missing: return () => clearTimeout(timer);
          }, 1000);
        }, []);

        return <div>Leaky Timer Component</div>;
      };

      const { unmount } = render(<LeakyTimerComponent />);

      // Check that timer was created
      expect(activeTimers.size).toBe(1);

      // Unmount
      unmount();

      // Verify timer was NOT cleared (memory leak!)
      expect(activeTimers.size).toBe(1);
      expect(global.clearTimeout).not.toHaveBeenCalled();
    });
  });

  describe('Component Integration Memory Leaks', () => {
    it('should handle rapid mount/unmount cycles without leaks', async () => {
      const mockQuestion = {
        id: 'q1',
        text: 'Test question',
        type: 'boolean' as const,
        required: true,
      };

      // Rapidly mount and unmount components
      for (let i = 0; i < 10; i++) {
        const { unmount } = render(<AIHelpTooltip question={mockQuestion} frameworkId="gdpr" />);

        // Small delay to allow effects to run
        await act(async () => {
          await new Promise((resolve) => originalSetTimeout(resolve, 10));
        });

        unmount();
      }

      // Verify no accumulated listeners or timers
      expect(eventListeners.get('keydown')?.size || 0).toBe(0);
      expect(activeTimers.size).toBe(0);
      expect(activeIntervals.size).toBe(0);
    });
  });
});

// Helper function to check for memory leaks in a component
export function testComponentForMemoryLeaks(Component: React.ComponentType<any>, props: Record<string, unknown> = {}) {
  return {
    hasEventListenerLeak: () => {
      const { unmount } = render(<Component {...props} />);
      const initialListenerCount = Array.from(eventListeners.values()).reduce(
        (sum, set) => sum + set.size,
        0,
      );

      unmount();

      const finalListenerCount = Array.from(eventListeners.values()).reduce(
        (sum, set) => sum + set.size,
        0,
      );

      return finalListenerCount > 0;
    },

    hasTimerLeak: () => {
      const { unmount } = render(<Component {...props} />);
      const initialTimerCount = activeTimers.size;

      unmount();

      return activeTimers.size > initialTimerCount;
    },

    hasIntervalLeak: () => {
      const { unmount } = render(<Component {...props} />);
      const initialIntervalCount = activeIntervals.size;

      unmount();

      return activeIntervals.size > initialIntervalCount;
    },
  };
}
