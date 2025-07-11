import { render, screen, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { AutoSaveIndicator } from '@/components/assessments/questionnaire/auto-save-indicator';
import { renderWithLeakDetection, testComponentMemoryLeaks, testRapidMountUnmount } from '@/tests/utils/component-test-helpers';

describe('AutoSaveIndicator - Memory Leak Detection', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should cleanup interval on unmount', async () => {
    const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
      <AutoSaveIndicator />
    );

    // Verify component renders with saved status
    expect(screen.getByText(/all changes saved/i)).toBeInTheDocument();

    // Advance time to trigger interval
    act(() => {
      vi.advanceTimersByTime(10000); // 10 seconds
    });

    // Should show saving status
    expect(screen.getByText(/saving/i)).toBeInTheDocument();

    // Advance time to complete save
    act(() => {
      vi.advanceTimersByTime(1500); // 1.5 seconds
    });

    // Should show saved status again
    expect(screen.getByText(/all changes saved/i)).toBeInTheDocument();

    // Unmount component
    unmount();

    // Verify no memory leaks
    assertNoLeaks();
    
    // Check specifically for intervals
    const report = leakDetector.getReport();
    expect(report.intervals.leaked).toBe(0);
    
    leakDetector.teardown();
  });

  it('should cleanup setTimeout calls on unmount', async () => {
    const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
      <AutoSaveIndicator />
    );

    // Trigger the interval to create a setTimeout
    act(() => {
      vi.advanceTimersByTime(10000); // Trigger interval
    });

    // Verify saving state
    expect(screen.getByText(/saving/i)).toBeInTheDocument();

    // Unmount before setTimeout completes
    unmount();

    // Advance time past when setTimeout would have fired
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    // Assert no leaks
    assertNoLeaks();
    
    const report = leakDetector.getReport();
    expect(report.timers.leaked).toBe(0);
    expect(report.intervals.leaked).toBe(0);
    
    leakDetector.teardown();
  });

  it('should handle rapid mount/unmount without leaks', async () => {
    // Use real timers for this test
    vi.useRealTimers();
    
    await testRapidMountUnmount(AutoSaveIndicator, {}, 5);
  });

  it('should not accumulate intervals with multiple renders', () => {
    const { rerender, unmount, leakDetector } = renderWithLeakDetection(
      <AutoSaveIndicator />
    );

    // Get initial interval count
    const initialReport = leakDetector.getReport();
    const initialIntervals = initialReport.intervals.created;

    // Re-render multiple times
    for (let i = 0; i < 5; i++) {
      rerender(<AutoSaveIndicator />);
      
      // Advance time a bit
      act(() => {
        vi.advanceTimersByTime(1000);
      });
    }

    // Get report after rerenders
    const afterRerenderReport = leakDetector.getReport();
    
    // Should still only have one interval (not accumulating)
    expect(afterRerenderReport.intervals.created - initialIntervals).toBe(0);

    unmount();
    
    // Final check
    expect(leakDetector).toHaveNoMemoryLeaks();
    leakDetector.teardown();
  });

  it('should handle component lifecycle correctly', async () => {
    await testComponentMemoryLeaks(
      AutoSaveIndicator,
      {},
      async (result) => {
        // Let the component run through several save cycles
        for (let i = 0; i < 3; i++) {
          // Wait for interval (10 seconds)
          act(() => {
            vi.advanceTimersByTime(10000);
          });
          
          // Verify saving state
          expect(screen.getByText(/saving/i)).toBeInTheDocument();
          
          // Wait for save to complete (1.5 seconds)
          act(() => {
            vi.advanceTimersByTime(1500);
          });
          
          // Verify saved state
          expect(screen.getByText(/all changes saved/i)).toBeInTheDocument();
        }
      }
    );
  });

  it('should properly cleanup when parent component unmounts', () => {
    const ParentComponent = ({ show }: { show: boolean }) => {
      return show ? <AutoSaveIndicator /> : null;
    };

    const { rerender, unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
      <ParentComponent show={true} />
    );

    // Verify indicator is shown
    expect(screen.getByText(/all changes saved/i)).toBeInTheDocument();

    // Hide the indicator
    rerender(<ParentComponent show={false} />);

    // Verify indicator is removed
    expect(screen.queryByText(/all changes saved/i)).not.toBeInTheDocument();

    // Show again
    rerender(<ParentComponent show={true} />);

    // Verify indicator is shown again
    expect(screen.getByText(/all changes saved/i)).toBeInTheDocument();

    // Final unmount
    unmount();

    // Assert no leaks
    assertNoLeaks();
    leakDetector.teardown();
  });

  it('should not leak memory when status changes rapidly', () => {
    const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
      <AutoSaveIndicator />
    );

    // Rapidly trigger status changes
    for (let i = 0; i < 10; i++) {
      act(() => {
        vi.advanceTimersByTime(10000); // Trigger save
        vi.advanceTimersByTime(500);   // Partial save
        vi.advanceTimersByTime(1000);   // Complete save
      });
    }

    unmount();
    assertNoLeaks();
    
    // Detailed check
    const report = leakDetector.getReport();
    console.log('AutoSaveIndicator memory report:', {
      timers: report.timers,
      intervals: report.intervals
    });
    
    leakDetector.teardown();
  });
});