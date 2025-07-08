import { toast } from 'sonner'

// Error types that can be handled differently
export type ErrorType = 'network' | 'validation' | 'authorization' | 'server' | 'rate_limit' | 'unknown'

export interface AppError {
  type: ErrorType
  message: string
  originalError?: Error
  retryable: boolean
  statusCode?: number
  details?: Record<string, any>
}

// Create a standardized error from different sources
export function createAppError(error: unknown, context?: string): AppError {
  if (error instanceof Error) {
    // Network errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return {
        type: 'network',
        message: 'Network connection failed. Please check your internet connection.',
        originalError: error,
        retryable: true,
      }
    }

    // Parse API errors
    if ('response' in error && error.response) {
      const response = error.response as any
      const status = response.status || response.statusCode

      if (status === 401 || status === 403) {
        return {
          type: 'authorization',
          message: 'You are not authorized to perform this action.',
          originalError: error,
          retryable: false,
          statusCode: status,
        }
      }

      if (status === 429) {
        const retryAfter = response.headers?.['retry-after']
        return {
          type: 'rate_limit',
          message: `Rate limit exceeded. Please wait ${retryAfter || '60'} seconds before trying again.`,
          originalError: error,
          retryable: true,
          statusCode: status,
          details: { retryAfter },
        }
      }

      if (status >= 400 && status < 500) {
        return {
          type: 'validation',
          message: response.data?.message || 'Invalid request. Please check your input.',
          originalError: error,
          retryable: false,
          statusCode: status,
        }
      }

      if (status >= 500) {
        return {
          type: 'server',
          message: 'Server error. Please try again later.',
          originalError: error,
          retryable: true,
          statusCode: status,
        }
      }
    }
  }

  // Unknown error
  return {
    type: 'unknown',
    message: context ? `An error occurred in ${context}` : 'An unexpected error occurred',
    originalError: error instanceof Error ? error : new Error(String(error)),
    retryable: false,
  }
}

// Retry logic with exponential backoff
export interface RetryOptions {
  maxAttempts?: number
  initialDelay?: number
  maxDelay?: number
  backoffFactor?: number
  retryCondition?: (error: AppError) => boolean
}

export async function withRetry<T>(
  operation: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    retryCondition = (error) => error.retryable,
  } = options

  let lastError: AppError
  let delay = initialDelay

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation()
    } catch (error) {
      lastError = createAppError(error, `Attempt ${attempt}`)
      
      // Don't retry on last attempt or if not retryable
      if (attempt === maxAttempts || !retryCondition(lastError)) {
        throw lastError
      }

      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, Math.min(delay, maxDelay)))
      delay *= backoffFactor
    }
  }

  throw lastError!
}

// Toast notification for errors
export function showErrorToast(error: AppError) {
  const title = getErrorTitle(error.type)
  
  toast.error(title, {
    description: error.message,
    duration: error.type === 'rate_limit' ? 10000 : 5000,
    action: error.retryable ? {
      label: 'Retry',
      onClick: () => {
        // This should be handled by the calling component
        console.log('Retry requested for:', error)
      }
    } : undefined,
  })
}

function getErrorTitle(type: ErrorType): string {
  switch (type) {
    case 'network':
      return 'Connection Error'
    case 'validation':
      return 'Validation Error'
    case 'authorization':
      return 'Authorization Error'
    case 'server':
      return 'Server Error'
    case 'rate_limit':
      return 'Rate Limit Exceeded'
    default:
      return 'Error'
  }
}

// React hook for error handling
export function useErrorHandler() {
  const handleError = (error: unknown, context?: string) => {
    const appError = createAppError(error, context)
    
    // Log error for debugging
    console.error('Application error:', {
      context,
      error: appError,
      stack: appError.originalError?.stack,
    })

    // Show user-friendly toast
    showErrorToast(appError)

    return appError
  }

  const handleAsyncError = async <T>(
    operation: () => Promise<T>,
    context?: string,
    retryOptions?: RetryOptions
  ): Promise<T | null> => {
    try {
      if (retryOptions) {
        return await withRetry(operation, retryOptions)
      }
      return await operation()
    } catch (error) {
      handleError(error, context)
      return null
    }
  }

  return {
    handleError,
    handleAsyncError,
  }
}