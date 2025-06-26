import { ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format API validation errors into a readable string for toast messages
 */
export function formatValidationErrors(error: any): string {
  // Check if it's a 422 validation error with detail array
  if (error?.response?.status === 422 && error?.response?.data?.detail) {
    const details = error.response.data.detail

    // If detail is an array of validation errors (Pydantic format)
    if (Array.isArray(details)) {
      return details
        .map((err: any) => {
          const field = err.loc ? err.loc.join('.') : 'Field'
          const message = err.msg || 'Invalid value'
          return `${field}: ${message}`
        })
        .join('. ')
    }

    // If detail is a string, return it directly
    if (typeof details === 'string') {
      return details
    }
  }

  // Check for error.error.message (custom error format)
  if (error?.response?.data?.error?.message) {
    return error.response.data.error.message
  }

  // Check for error.response.data.detail (string format)
  if (error?.response?.data?.detail && typeof error.response.data.detail === 'string') {
    return error.response.data.detail
  }

  // Fallback to generic message
  return error?.message || 'An unexpected error occurred'
}
