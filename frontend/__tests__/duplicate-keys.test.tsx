import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'

// Import all pages that might have duplicate key issues
import HomePage from '../app/page'

// Create a test wrapper with all necessary providers
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('Duplicate Key Detection Tests', () => {
  beforeEach(() => {
    // Clear any previous warnings
    if (global.clearReactWarnings) {
      global.clearReactWarnings()
    }
  })

  describe('Homepage Components', () => {
    it('should render HomePage without duplicate keys', () => {
      expect(() => {
        render(
          <TestWrapper>
            <HomePage />
          </TestWrapper>
        )
      }).not.toThrow()
    })
  })

  describe('Component Key Validation', () => {
    it('should detect duplicate keys in array rendering', () => {
      const ComponentWithDuplicateKeys = () => {
        const items = [1, 2, 3]
        return (
          <div>
            {items.map(() => (
              <div key="duplicate">Item</div> // This should fail
            ))}
          </div>
        )
      }

      expect(() => {
        render(<ComponentWithDuplicateKeys />)
      }).toThrow(/DUPLICATE KEY ERROR|MISSING KEY ERROR/)
    })

    it('should pass with unique keys', () => {
      const ComponentWithUniqueKeys = () => {
        const items = [1, 2, 3]
        return (
          <div>
            {items.map((item, index) => (
              <div key={`item-${index}`}>Item {item}</div>
            ))}
          </div>
        )
      }

      expect(() => {
        render(<ComponentWithUniqueKeys />)
      }).not.toThrow()
    })
  })

  describe('Common Patterns That Cause Duplicate Keys', () => {
    it('should catch array index as key with duplicate data', () => {
      const ComponentWithIndexKeys = () => {
        // Simulate data with duplicates that would cause issues
        const items = ['item', 'item', 'different']
        return (
          <div>
            {items.map((item, index) => (
              <div key={index}>{item}</div> // This pattern can cause issues
            ))}
          </div>
        )
      }

      // This should pass but is a warning pattern
      expect(() => {
        render(<ComponentWithIndexKeys />)
      }).not.toThrow()
    })

    it('should catch missing keys in fragments', () => {
      const ComponentWithMissingKeys = () => {
        const items = [1, 2, 3]
        return (
          <div>
            {items.map((item) => (
              <React.Fragment> {/* Missing key here */}
                <div>Item {item}</div>
                <span>Details</span>
              </React.Fragment>
            ))}
          </div>
        )
      }

      expect(() => {
        render(<ComponentWithMissingKeys />)
      }).toThrow(/MISSING KEY ERROR/)
    })
  })
})

// Utility test to scan for potential key issues in components
describe('Component Key Audit', () => {
  const scanComponentForKeyIssues = (Component: React.ComponentType) => {
    const warnings: string[] = []
    const originalConsoleWarn = console.warn
    const originalConsoleError = console.error

    console.warn = (...args) => {
      const message = args.join(' ')
      if (message.includes('key')) {
        warnings.push(message)
      }
    }

    console.error = (...args) => {
      const message = args.join(' ')
      if (message.includes('key')) {
        warnings.push(message)
      }
    }

    try {
      render(
        <TestWrapper>
          <Component />
        </TestWrapper>
      )
    } catch (error) {
      if (error instanceof Error && error.message.includes('key')) {
        warnings.push(error.message)
      }
    } finally {
      console.warn = originalConsoleWarn
      console.error = originalConsoleError
    }

    return warnings
  }

  it('should audit HomePage for key issues', () => {
    const warnings = scanComponentForKeyIssues(HomePage)
    expect(warnings).toEqual([])
  })
})
