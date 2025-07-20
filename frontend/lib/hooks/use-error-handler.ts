/**
 * React hook for handling API errors in components
 * 
 * Provides user-friendly error messages, retry functionality,
 * and toast notifications for different error scenarios.
 */

import { useState, useCallback } from 'react';
import { toast } from 'sonner';

import { ApiError } from '@/lib/api/client';
import { EnhancedApiError, ErrorType, ErrorSeverity, getContextualErrorMessage } from '@/lib/api/error-handler';

interface UseErrorHandlerOptions {
  context?: string;
  showToast?: boolean;
  onError?: (error: EnhancedApiError | ApiError) => void;
  onRetry?: () => void;
}

export function useErrorHandler(options: UseErrorHandlerOptions = {}) {
  const { context, showToast = true, onError, onRetry } = options;
  const [error, setError] = useState<EnhancedApiError | ApiError | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleError = useCallback((error: any) => {
    let processedError: EnhancedApiError | ApiError;

    // Check if it's already an enhanced error
    if (error instanceof EnhancedApiError) {
      processedError = error;
    } else if (error instanceof ApiError) {
      processedError = error;
    } else {
      // Create a generic error
      processedError = new ApiError(
        0,
        error.message || 'An unexpected error occurred',
        error
      );
    }

    setError(processedError);

    // Get appropriate error message
    const message = processedError instanceof EnhancedApiError
      ? getContextualErrorMessage(processedError, context)
      : processedError.detail;

    // Show toast notification
    if (showToast) {
      // Determine toast type based on error severity
      if (processedError instanceof EnhancedApiError) {
        switch (processedError.severity) {
          case ErrorSeverity.CRITICAL:
          case ErrorSeverity.HIGH:
            toast.error(message, {
              duration: 5000,
              action: processedError.retryable ? {
                label: 'Retry',
                onClick: () => retry(),
              } : undefined,
            });
            break;
          case ErrorSeverity.MEDIUM:
            toast.warning(message, {
              duration: 4000,
            });
            break;
          case ErrorSeverity.LOW:
            toast.info(message, {
              duration: 3000,
            });
            break;
        }
      } else {
        toast.error(message, { duration: 5000 });
      }
    }

    // Call custom error handler
    if (onError) {
      onError(processedError);
    }
  }, [context, showToast, onError]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const retry = useCallback(async () => {
    if (!onRetry) return;
    
    setIsRetrying(true);
    try {
      await onRetry();
      clearError();
      toast.success('Operation completed successfully');
    } catch (retryError) {
      handleError(retryError);
    } finally {
      setIsRetrying(false);
    }
  }, [onRetry, clearError, handleError]);

  return {
    error,
    isRetrying,
    handleError,
    clearError,
    retry,
  };
}

// Hook for handling async operations with error handling
export function useAsyncError() {
  const [isLoading, setIsLoading] = useState(false);
  const { error, handleError, clearError } = useErrorHandler();

  const execute = useCallback(async <T,>(
    asyncFunction: () => Promise<T>,
    _options?: UseErrorHandlerOptions
  ): Promise<T | null> => {
    setIsLoading(true);
    clearError();
    
    try {
      const result = await asyncFunction();
      return result;
    } catch (error) {
      handleError(error);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [handleError, clearError]);

  return {
    isLoading,
    error,
    execute,
    clearError,
  };
}

// Hook for form submission with error handling
export function useFormError(context: string = 'form') {
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const { error, handleError, clearError, isRetrying } = useErrorHandler({ 
    context,
    showToast: false, // We'll handle field-specific errors differently
  });

  const handleFormError = useCallback((error: any) => {
    handleError(error);

    // Extract field-specific errors if available
    if (error.response?.data?.errors) {
      const {errors} = error.response.data;
      const fieldErrorMap: Record<string, string> = {};
      
      Object.entries(errors).forEach(([field, messages]) => {
        if (Array.isArray(messages)) {
          fieldErrorMap[field] = messages[0];
        } else {
          fieldErrorMap[field] = String(messages);
        }
      });
      
      setFieldErrors(fieldErrorMap);
    } else if (error instanceof EnhancedApiError && error.type === ErrorType.VALIDATION) {
      // Show general validation error
      toast.error(error.userMessage);
    } else {
      // Show general error
      toast.error(error.message || 'Form submission failed');
    }
  }, [handleError]);

  const clearFieldError = useCallback((field: string) => {
    setFieldErrors(prev => {
      const { [field]: _, ...rest } = prev;
      return rest;
    });
  }, []);

  const clearAllErrors = useCallback(() => {
    clearError();
    setFieldErrors({});
  }, [clearError]);

  return {
    error,
    fieldErrors,
    isRetrying,
    handleFormError,
    clearFieldError,
    clearAllErrors,
  };
}