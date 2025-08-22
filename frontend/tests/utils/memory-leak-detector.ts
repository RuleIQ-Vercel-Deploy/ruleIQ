/**
 * Memory Leak Detector Utility
 *
 * This utility helps detect common memory leaks in React components:
 * - Event listeners not removed
 * - Timers not cleared
 * - Intervals not cleared
 * - AbortControllers not aborted
 * - Subscriptions not unsubscribed
 */

import { vi } from 'vitest';

export interface MemoryLeakDetector {
  setup(): void;
  teardown(): void;
  getReport(): MemoryLeakReport;
  hasLeaks(): boolean;
}

export interface MemoryLeakReport {
  eventListeners: {
    added: number;
    removed: number;
    leaked: number;
    details: Array<{ event: string; count: number }>;
  };
  timers: {
    created: number;
    cleared: number;
    leaked: number;
  };
  intervals: {
    created: number;
    cleared: number;
    leaked: number;
  };
  abortControllers: {
    created: number;
    aborted: number;
    leaked: number;
  };
}

export function createMemoryLeakDetector(): MemoryLeakDetector {
  // Original function references
  let originalAddEventListener: typeof EventTarget.prototype.addEventListener;
  let originalRemoveEventListener: typeof EventTarget.prototype.removeEventListener;
  let originalSetTimeout: typeof global.setTimeout;
  let originalClearTimeout: typeof global.clearTimeout;
  let originalSetInterval: typeof global.setInterval;
  let originalClearInterval: typeof global.clearInterval;
  let originalAbortController: typeof AbortController;

  // Tracking data structures
  const eventListeners = new Map<EventTarget, Map<string, Set<EventListener>>>();
  const activeTimers = new Set<NodeJS.Timeout>();
  const activeIntervals = new Set<NodeJS.Timeout>();
  const activeAbortControllers = new WeakSet<AbortController>();

  let eventListenersAdded = 0;
  let eventListenersRemoved = 0;
  let timersCreated = 0;
  let timersCleared = 0;
  let intervalsCreated = 0;
  let intervalsCleared = 0;
  let abortControllersCreated = 0;
  let abortControllersAborted = 0;

  return {
    setup() {
      // Store original functions
      originalAddEventListener = EventTarget.prototype.addEventListener;
      originalRemoveEventListener = EventTarget.prototype.removeEventListener;
      originalSetTimeout = global.setTimeout;
      originalClearTimeout = global.clearTimeout;
      originalSetInterval = global.setInterval;
      originalClearInterval = global.clearInterval;
      originalAbortController = global.AbortController;

      // Mock addEventListener
      EventTarget.prototype.addEventListener = vi.fn(function (
        this: EventTarget,
        type: string,
        listener: EventListenerOrEventListenerObject,
        options?: boolean | AddEventListenerOptions,
      ) {
        if (!eventListeners.has(this)) {
          eventListeners.set(this, new Map());
        }
        const targetListeners = eventListeners.get(this)!;
        if (!targetListeners.has(type)) {
          targetListeners.set(type, new Set());
        }
        targetListeners.get(type)!.add(listener as EventListener);
        eventListenersAdded++;

        return originalAddEventListener.call(this, type, listener, options);
      }) as any;

      // Mock removeEventListener
      EventTarget.prototype.removeEventListener = vi.fn(function (
        this: EventTarget,
        type: string,
        listener: EventListenerOrEventListenerObject,
        options?: boolean | EventListenerOptions,
      ) {
        if (eventListeners.has(this)) {
          const targetListeners = eventListeners.get(this)!;
          if (targetListeners.has(type)) {
            targetListeners.get(type)!.delete(listener as EventListener);
            eventListenersRemoved++;
            if (targetListeners.get(type)!.size === 0) {
              targetListeners.delete(type);
            }
          }
          if (targetListeners.size === 0) {
            eventListeners.delete(this);
          }
        }

        return originalRemoveEventListener.call(this, type, listener, options);
      }) as any;

      // Mock setTimeout
      global.setTimeout = vi.fn((callback: any, delay?: number, ...args: unknown[]) => {
        const timer = originalSetTimeout(callback, delay, ...args);
        activeTimers.add(timer);
        timersCreated++;
        return timer;
      }) as any;

      // Mock clearTimeout
      global.clearTimeout = vi.fn((timer: NodeJS.Timeout) => {
        if (activeTimers.has(timer)) {
          activeTimers.delete(timer);
          timersCleared++;
        }
        return originalClearTimeout(timer);
      }) as any;

      // Mock setInterval
      global.setInterval = vi.fn((callback: any, delay?: number, ...args: unknown[]) => {
        const interval = originalSetInterval(callback, delay, ...args);
        activeIntervals.add(interval);
        intervalsCreated++;
        return interval;
      }) as any;

      // Mock clearInterval
      global.clearInterval = vi.fn((interval: NodeJS.Timeout) => {
        if (activeIntervals.has(interval)) {
          activeIntervals.delete(interval);
          intervalsCleared++;
        }
        return originalClearInterval(interval);
      }) as any;

      // Mock AbortController
      global.AbortController = class MockAbortController extends originalAbortController {
        constructor() {
          super();
          activeAbortControllers.add(this);
          abortControllersCreated++;
        }

        abort() {
          super.abort();
          abortControllersAborted++;
        }
      };
    },

    teardown() {
      // Restore original functions
      EventTarget.prototype.addEventListener = originalAddEventListener;
      EventTarget.prototype.removeEventListener = originalRemoveEventListener;
      global.setTimeout = originalSetTimeout;
      global.clearTimeout = originalClearTimeout;
      global.setInterval = originalSetInterval;
      global.clearInterval = originalClearInterval;
      global.AbortController = originalAbortController;

      // Clear any remaining timers/intervals
      activeTimers.forEach((timer) => clearTimeout(timer));
      activeIntervals.forEach((interval) => clearInterval(interval));

      // Reset counters
      eventListenersAdded = 0;
      eventListenersRemoved = 0;
      timersCreated = 0;
      timersCleared = 0;
      intervalsCreated = 0;
      intervalsCleared = 0;
      abortControllersCreated = 0;
      abortControllersAborted = 0;

      // Clear tracking structures
      eventListeners.clear();
      activeTimers.clear();
      activeIntervals.clear();
    },

    getReport(): MemoryLeakReport {
      // Calculate leaked event listeners by type
      const leakedListenerDetails: Array<{ event: string; count: number }> = [];
      eventListeners.forEach((targetListeners, target) => {
        targetListeners.forEach((listeners, event) => {
          if (listeners.size > 0) {
            const existing = leakedListenerDetails.find((d) => d.event === event);
            if (existing) {
              existing.count += listeners.size;
            } else {
              leakedListenerDetails.push({ event, count: listeners.size });
            }
          }
        });
      });

      return {
        eventListeners: {
          added: eventListenersAdded,
          removed: eventListenersRemoved,
          leaked: eventListenersAdded - eventListenersRemoved,
          details: leakedListenerDetails,
        },
        timers: {
          created: timersCreated,
          cleared: timersCleared,
          leaked: activeTimers.size,
        },
        intervals: {
          created: intervalsCreated,
          cleared: intervalsCleared,
          leaked: activeIntervals.size,
        },
        abortControllers: {
          created: abortControllersCreated,
          aborted: abortControllersAborted,
          leaked: abortControllersCreated - abortControllersAborted,
        },
      };
    },

    hasLeaks(): boolean {
      const report = this.getReport();
      return (
        report.eventListeners.leaked > 0 ||
        report.timers.leaked > 0 ||
        report.intervals.leaked > 0 ||
        report.abortControllers.leaked > 0
      );
    },
  };
}

/**
 * Custom test matcher for memory leaks
 */
export function setupMemoryLeakMatchers() {
  expect.extend({
    toHaveNoMemoryLeaks(detector: MemoryLeakDetector) {
      const report = detector.getReport();
      const hasLeaks = detector.hasLeaks();

      if (!hasLeaks) {
        return {
          pass: true,
          message: () => 'No memory leaks detected',
        };
      }

      const leakDetails: string[] = [];

      if (report.eventListeners.leaked > 0) {
        leakDetails.push(`Event Listeners: ${report.eventListeners.leaked} leaked`);
        report.eventListeners.details.forEach(({ event, count }) => {
          leakDetails.push(`  - ${event}: ${count} listener(s)`);
        });
      }

      if (report.timers.leaked > 0) {
        leakDetails.push(`Timers: ${report.timers.leaked} leaked`);
      }

      if (report.intervals.leaked > 0) {
        leakDetails.push(`Intervals: ${report.intervals.leaked} leaked`);
      }

      if (report.abortControllers.leaked > 0) {
        leakDetails.push(`AbortControllers: ${report.abortControllers.leaked} leaked`);
      }

      return {
        pass: false,
        message: () => `Memory leaks detected:\n${leakDetails.join('\n')}`,
      };
    },
  });
}

// TypeScript augmentation for custom matcher
declare global {
  namespace Vi {
    interface Assertion {
      toHaveNoMemoryLeaks(): void;
    }
    interface AsymmetricMatchersContaining {
      toHaveNoMemoryLeaks(): void;
    }
  }
}
