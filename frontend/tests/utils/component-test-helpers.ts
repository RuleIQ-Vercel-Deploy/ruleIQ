/**
 * Component Test Helpers
 * 
 * Utilities for testing React components with memory leak detection
 */

import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { ReactElement } from 'react';
import { createMemoryLeakDetector, MemoryLeakDetector, setupMemoryLeakMatchers } from './memory-leak-detector';

export interface RenderWithLeakDetectionOptions extends RenderOptions {
  detectLeaks?: boolean;
}

export interface RenderWithLeakDetectionResult extends RenderResult {
  leakDetector: MemoryLeakDetector;
  assertNoLeaks: () => void;
}

/**
 * Enhanced render function with memory leak detection
 */
export function renderWithLeakDetection(
  ui: ReactElement,
  options: RenderWithLeakDetectionOptions = { detectLeaks: true }
): RenderWithLeakDetectionResult {
  const { detectLeaks = true, ...renderOptions } = options;
  
  // Create leak detector if requested
  const leakDetector = detectLeaks ? createMemoryLeakDetector() : null;
  
  if (leakDetector) {
    setupMemoryLeakMatchers();
    leakDetector.setup();
  }
  
  // Render component
  const renderResult = render(ui, renderOptions);
  
  // Enhance unmount to check for leaks
  const originalUnmount = renderResult.unmount;
  renderResult.unmount = () => {
    originalUnmount();
    
    if (leakDetector) {
      // Give a small delay for cleanup to complete
      setTimeout(() => {
        const report = leakDetector.getReport();
        if (leakDetector.hasLeaks()) {
          console.warn('Memory leaks detected after unmount:', report);
        }
      }, 0);
    }
  };
  
  return {
    ...renderResult,
    leakDetector: leakDetector!,
    assertNoLeaks: () => {
      if (leakDetector) {
        expect(leakDetector).toHaveNoMemoryLeaks();
      }
    }
  };
}

/**
 * Test helper for detecting memory leaks in a component lifecycle
 */
export async function testComponentMemoryLeaks(
  Component: React.ComponentType<any>,
  props: any = {},
  testScenario?: (result: RenderResult) => void | Promise<void>
): Promise<void> {
  const { unmount, leakDetector, assertNoLeaks, ...rest } = renderWithLeakDetection(
    <Component {...props} />
  );
  
  // Run test scenario if provided
  if (testScenario) {
    await testScenario({ unmount, ...rest });
  }
  
  // Unmount component
  unmount();
  
  // Wait for async cleanup
  await new Promise(resolve => setTimeout(resolve, 50));
  
  // Assert no leaks
  assertNoLeaks();
  
  // Cleanup leak detector
  leakDetector.teardown();
}

/**
 * Test helper for rapid mount/unmount cycles
 */
export async function testRapidMountUnmount(
  Component: React.ComponentType<any>,
  props: any = {},
  cycles: number = 10
): Promise<void> {
  const leakDetector = createMemoryLeakDetector();
  setupMemoryLeakMatchers();
  leakDetector.setup();
  
  for (let i = 0; i < cycles; i++) {
    const { unmount } = render(<Component {...props} />);
    
    // Small delay to allow effects to run
    await new Promise(resolve => setTimeout(resolve, 10));
    
    unmount();
  }
  
  // Final check for accumulated leaks
  expect(leakDetector).toHaveNoMemoryLeaks();
  
  leakDetector.teardown();
}

/**
 * Hook for testing memory leaks in custom hooks
 */
export function useMemoryLeakTest() {
  const leakDetector = createMemoryLeakDetector();
  
  return {
    setup: () => {
      setupMemoryLeakMatchers();
      leakDetector.setup();
    },
    teardown: () => {
      leakDetector.teardown();
    },
    assertNoLeaks: () => {
      expect(leakDetector).toHaveNoMemoryLeaks();
    },
    getReport: () => leakDetector.getReport()
  };
}