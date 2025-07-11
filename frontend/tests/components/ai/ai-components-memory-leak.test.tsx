import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { AIHelpTooltip } from '@/components/assessments/AIHelpTooltip';
import { AIGuidancePanel } from '@/components/assessments/AIGuidancePanel';
import { AIErrorBoundary } from '@/components/assessments/AIErrorBoundary';
import { renderWithLeakDetection, testComponentMemoryLeaks, testRapidMountUnmount } from '@/tests/utils/component-test-helpers';

// Mock the AI service
vi.mock('@/lib/api/services/assessment-ai.service', () => ({
  assessmentAIService: {
    getQuestionHelp: vi.fn().mockResolvedValue({
      help_text: 'AI help response',
      key_points: ['Point 1', 'Point 2'],
      follow_up_questions: ['Question 1?', 'Question 2?']
    })
  }
}));

// Mock the toast hook
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn()
  })
}));

const mockQuestion = {
  id: 'q1',
  text: 'Do you process personal data?',
  type: 'boolean' as const,
  required: true
};

const mockUserContext = {
  company_name: 'Test Corp',
  industry: 'Technology'
};

describe('AI Components - Memory Leak Detection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('AIHelpTooltip Memory Leaks', () => {
    it('should cleanup keyboard event listeners on unmount', async () => {
      await testComponentMemoryLeaks(
        AIHelpTooltip,
        {
          question: mockQuestion,
          frameworkId: 'gdpr',
          userContext: mockUserContext
        },
        async (result) => {
          // Test keyboard shortcut
          fireEvent.keyDown(document, { key: 'h', ctrlKey: true });
          
          // Wait for any effects
          await waitFor(() => {
            expect(screen.getByRole('button', { name: /ai help/i })).toBeInTheDocument();
          });
        }
      );
    });

    it('should cleanup async operations when unmounting during request', async () => {
      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <AIHelpTooltip
          question={mockQuestion}
          frameworkId="gdpr"
          userContext={mockUserContext}
        />
      );

      // Make the AI service slow
      vi.mocked(assessmentAIService.getQuestionHelp).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      // Trigger help request
      const helpButton = screen.getByRole('button', { name: /ai help/i });
      fireEvent.click(helpButton);

      // Verify loading state
      expect(screen.getByText(/getting ai help/i)).toBeInTheDocument();

      // Unmount while request is in progress
      unmount();

      // Wait to ensure no late updates
      await new Promise(resolve => setTimeout(resolve, 100));

      // Assert no leaks
      assertNoLeaks();
      leakDetector.teardown();
    });

    it('should handle rapid open/close cycles without leaks', async () => {
      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <AIHelpTooltip
          question={mockQuestion}
          frameworkId="gdpr"
          userContext={mockUserContext}
        />
      );

      // Rapidly open and close tooltip
      for (let i = 0; i < 10; i++) {
        const helpButton = screen.getByRole('button', { name: /ai help/i });
        fireEvent.click(helpButton);
        
        // If tooltip is open, close it
        const closeButton = screen.queryByRole('button', { name: /close/i });
        if (closeButton) {
          fireEvent.click(closeButton);
        }
      }

      unmount();
      assertNoLeaks();
      leakDetector.teardown();
    });

    it('should cleanup all event listeners including document listeners', () => {
      const { unmount, leakDetector } = renderWithLeakDetection(
        <AIHelpTooltip
          question={mockQuestion}
          frameworkId="gdpr"
        />
      );

      // Get initial report
      const initialReport = leakDetector.getReport();
      
      // Unmount
      unmount();

      // Get final report
      const finalReport = leakDetector.getReport();

      // Check specifically for keyboard event listeners
      const keyboardListeners = finalReport.eventListeners.details.filter(
        detail => detail.event === 'keydown'
      );

      expect(keyboardListeners).toHaveLength(0);
      expect(leakDetector).toHaveNoMemoryLeaks();
      
      leakDetector.teardown();
    });
  });

  describe('AIGuidancePanel Memory Leaks', () => {
    it('should cleanup when unmounting during initial load', async () => {
      await testComponentMemoryLeaks(
        AIGuidancePanel,
        {
          question: mockQuestion,
          frameworkId: 'gdpr',
          defaultOpen: true,
          userContext: mockUserContext
        }
      );
    });

    it('should cleanup loading states properly', async () => {
      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <AIGuidancePanel
          question={mockQuestion}
          frameworkId="gdpr"
          defaultOpen={false}
        />
      );

      // Open panel
      const toggleButton = screen.getByRole('button');
      fireEvent.click(toggleButton);

      // Panel should be loading
      await waitFor(() => {
        expect(screen.getByText(/loading guidance/i)).toBeInTheDocument();
      });

      // Close panel before loading completes
      fireEvent.click(toggleButton);

      unmount();
      assertNoLeaks();
      leakDetector.teardown();
    });

    it('should handle error states without leaks', async () => {
      // Make AI service fail
      vi.mocked(assessmentAIService.getQuestionHelp).mockRejectedValue(
        new Error('AI service error')
      );

      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <AIGuidancePanel
          question={mockQuestion}
          frameworkId="gdpr"
          defaultOpen={true}
        />
      );

      // Wait for error state
      await waitFor(() => {
        expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
      });

      unmount();
      assertNoLeaks();
      leakDetector.teardown();
    });
  });

  describe('AIErrorBoundary Memory Leaks', () => {
    const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
      if (shouldThrow) {
        throw new Error('Test error');
      }
      return <div>No error</div>;
    };

    it('should cleanup error state on unmount', async () => {
      const onError = vi.fn();
      
      await testComponentMemoryLeaks(
        () => (
          <AIErrorBoundary onError={onError}>
            <ThrowError shouldThrow={true} />
          </AIErrorBoundary>
        ),
        {},
        async (result) => {
          // Wait for error boundary to catch error
          await waitFor(() => {
            expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
          });
          
          // Try to recover
          const retryButton = screen.getByRole('button', { name: /try again/i });
          fireEvent.click(retryButton);
        }
      );
    });

    it('should cleanup error logging mechanisms', () => {
      const onError = vi.fn();
      const { unmount, leakDetector, assertNoLeaks } = renderWithLeakDetection(
        <AIErrorBoundary onError={onError}>
          <ThrowError shouldThrow={true} />
        </AIErrorBoundary>
      );

      // Verify error was caught
      expect(onError).toHaveBeenCalled();

      unmount();
      assertNoLeaks();
      leakDetector.teardown();
    });
  });

  describe('Combined AI Components Memory Leaks', () => {
    it('should handle nested AI components without leaks', async () => {
      const NestedAIComponents = () => (
        <AIErrorBoundary>
          <AIGuidancePanel
            question={mockQuestion}
            frameworkId="gdpr"
            defaultOpen={true}
          >
            <AIHelpTooltip
              question={mockQuestion}
              frameworkId="gdpr"
            />
          </AIGuidancePanel>
        </AIErrorBoundary>
      );

      await testComponentMemoryLeaks(NestedAIComponents);
    });

    it('should handle rapid mount/unmount of AI components', async () => {
      await testRapidMountUnmount(
        () => (
          <div>
            <AIHelpTooltip question={mockQuestion} frameworkId="gdpr" />
            <AIGuidancePanel question={mockQuestion} frameworkId="gdpr" />
          </div>
        ),
        {},
        10
      );
    });
  });

  describe('Performance and Memory Monitoring', () => {
    it('should not accumulate memory with repeated AI requests', async () => {
      const { unmount, leakDetector } = renderWithLeakDetection(
        <AIHelpTooltip
          question={mockQuestion}
          frameworkId="gdpr"
        />
      );

      // Make multiple AI requests
      for (let i = 0; i < 5; i++) {
        const helpButton = screen.getByRole('button', { name: /ai help/i });
        fireEvent.click(helpButton);
        
        // Wait for response
        await waitFor(() => {
          expect(screen.getByText(/ai help response/i)).toBeInTheDocument();
        });
        
        // Close tooltip
        const closeButton = screen.getByRole('button', { name: /close/i });
        fireEvent.click(closeButton);
        
        // Small delay between requests
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      // Get memory report before unmount
      const beforeUnmount = leakDetector.getReport();
      console.log('Memory usage before unmount:', beforeUnmount);

      unmount();

      // Final check
      expect(leakDetector).toHaveNoMemoryLeaks();
      leakDetector.teardown();
    });
  });
});