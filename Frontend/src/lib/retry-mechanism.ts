interface RetryOptions {
  maxAttempts: number
  delay: number
  backoff: "linear" | "exponential"
}

export async function retryRequest<T>(
  requestFn: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  const { maxAttempts, delay, backoff } = options
  let lastError: Error

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error as Error
      
      if (attempt === maxAttempts) {
        throw lastError
      }

      // Calculate delay based on backoff strategy
      const currentDelay = backoff === "exponential" 
        ? delay * Math.pow(2, attempt - 1)
        : delay * attempt

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, currentDelay))
    }
  }

  throw lastError!
}

export function isRetryableError(error: any): boolean {
  // Network errors
  if (error.code === "NETWORK_ERROR" || error.code === "ECONNABORTED") {
    return true
  }

  // Server errors (5xx)
  if (error.response?.status >= 500) {
    return true
  }

  // Timeout errors
  if (error.code === "ECONNRESET" || error.code === "ETIMEDOUT") {
    return true
  }

  return false
}
