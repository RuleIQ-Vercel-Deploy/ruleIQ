import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { ZodSchema } from 'zod';
import { 
  validateApiResponse, 
  ValidationError, 
  safeValidateApiResponse,
  logValidationWarning,
  reportValidationError 
} from '../api/validation';
import { useState, useCallback } from 'react';

// ===========================
// Types
// ===========================

interface UseValidatedQueryOptions<TData> extends Omit<UseQueryOptions<TData>, 'queryFn'> {
  schema: ZodSchema<TData>;
  onValidationError?: (error: ValidationError) => void;
  skipValidation?: boolean;
}

interface UseValidatedMutationOptions<TData, TVariables> 
  extends Omit<UseMutationOptions<TData, Error, TVariables>, 'mutationFn'> {
  responseSchema: ZodSchema<TData>;
  requestSchema?: ZodSchema<TVariables>;
  onValidationError?: (error: ValidationError) => void;
  skipValidation?: boolean;
}

interface ValidationState {
  isValidating: boolean;
  validationError: ValidationError | null;
  validationWarnings: string[];
}

// ===========================
// Hooks
// ===========================

/**
 * React Query hook with automatic response validation
 */
export function useValidatedQuery<TData>(
  queryKey: string[],
  queryFn: () => Promise<unknown>,
  options: UseValidatedQueryOptions<TData>
) {
  const { 
    schema, 
    onValidationError, 
    skipValidation = false,
    ...queryOptions 
  } = options;

  const [validationState, setValidationState] = useState<ValidationState>({
    isValidating: false,
    validationError: null,
    validationWarnings: [],
  });

  const validatedQueryFn = async (): Promise<TData> => {
    setValidationState(prev => ({ ...prev, isValidating: true, validationError: null }));

    try {
      const response = await queryFn();

      if (skipValidation) {
        setValidationState(prev => ({ ...prev, isValidating: false }));
        return response as TData;
      }

      const validatedData = validateApiResponse(response, schema);
      setValidationState(prev => ({ ...prev, isValidating: false }));
      return validatedData;
    } catch (error) {
      setValidationState(prev => ({ ...prev, isValidating: false }));

      if (error instanceof ValidationError) {
        setValidationState(prev => ({ 
          ...prev, 
          validationError: error 
        }));

        if (onValidationError) {
          onValidationError(error);
        }

        logValidationWarning(`Query ${queryKey.join('.')}`, error);
        reportValidationError(`Query ${queryKey.join('.')}`, error);
      }

      throw error;
    }
  };

  const query = useQuery({
    queryKey,
    queryFn: validatedQueryFn,
    ...queryOptions,
  });

  return {
    ...query,
    validationState,
  };
}

/**
 * React Mutation hook with automatic request/response validation
 */
export function useValidatedMutation<TData, TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<unknown>,
  options: UseValidatedMutationOptions<TData, TVariables>
) {
  const { 
    responseSchema,
    requestSchema,
    onValidationError,
    skipValidation = false,
    ...mutationOptions 
  } = options;

  const [validationState, setValidationState] = useState<ValidationState>({
    isValidating: false,
    validationError: null,
    validationWarnings: [],
  });

  const validatedMutationFn = async (variables: TVariables): Promise<TData> => {
    setValidationState(prev => ({ ...prev, isValidating: true, validationError: null }));

    try {
      // Validate request if schema provided
      let validatedVariables = variables;
      if (requestSchema && !skipValidation) {
        validatedVariables = validateApiResponse(variables, requestSchema);
      }

      const response = await mutationFn(validatedVariables);

      if (skipValidation) {
        setValidationState(prev => ({ ...prev, isValidating: false }));
        return response as TData;
      }

      const validatedData = validateApiResponse(response, responseSchema);
      setValidationState(prev => ({ ...prev, isValidating: false }));
      return validatedData;
    } catch (error) {
      setValidationState(prev => ({ ...prev, isValidating: false }));

      if (error instanceof ValidationError) {
        setValidationState(prev => ({ 
          ...prev, 
          validationError: error 
        }));

        if (onValidationError) {
          onValidationError(error);
        }

        logValidationWarning('Mutation', error);
        reportValidationError('Mutation', error);
      }

      throw error;
    }
  };

  const mutation = useMutation({
    mutationFn: validatedMutationFn,
    ...mutationOptions,
  });

  return {
    ...mutation,
    validationState,
  };
}

/**
 * Hook for validating form data
 */
export function useFormValidation<T>(schema: ZodSchema<T>) {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isValidating, setIsValidating] = useState(false);

  const validate = useCallback(
    async (data: unknown): Promise<{ isValid: boolean; data?: T; errors?: Record<string, string> }> => {
      setIsValidating(true);
      setErrors({});

      const result = safeValidateApiResponse(data, schema);
      
      if (result.success) {
        setIsValidating(false);
        return { isValid: true, data: result.data };
      }

      const fieldErrors: Record<string, string> = {};
      result.error.errors.errors.forEach(issue => {
        const path = issue.path.join('.');
        if (path) {
          fieldErrors[path] = issue.message;
        }
      });

      setErrors(fieldErrors);
      setIsValidating(false);
      
      return { isValid: false, errors: fieldErrors };
    },
    [schema]
  );

  const validateField = useCallback(
    (fieldName: string, value: unknown): string | undefined => {
      try {
        const partialData = { [fieldName]: value };
        schema.partial().parse(partialData);
        
        setErrors(prev => {
          const next = { ...prev };
          delete next[fieldName];
          return next;
        });
        
        return undefined;
      } catch (error) {
        if (error instanceof Error) {
          const message = error.message;
          setErrors(prev => ({ ...prev, [fieldName]: message }));
          return message;
        }
        return 'Validation error';
      }
    },
    [schema]
  );

  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  const clearFieldError = useCallback((fieldName: string) => {
    setErrors(prev => {
      const next = { ...prev };
      delete next[fieldName];
      return next;
    });
  }, []);

  return {
    errors,
    isValidating,
    validate,
    validateField,
    clearErrors,
    clearFieldError,
  };
}

/**
 * Hook for real-time validation as user types
 */
export function useRealtimeValidation<T>(
  schema: ZodSchema<T>,
  debounceMs: number = 300
) {
  const [data, setData] = useState<Partial<T>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isValid, setIsValid] = useState(false);

  const validateData = useCallback(
    (newData: Partial<T>) => {
      const result = safeValidateApiResponse(newData, schema.partial());
      
      if (result.success) {
        setErrors({});
        setIsValid(true);
      } else {
        const fieldErrors: Record<string, string> = {};
        result.error.errors.errors.forEach(issue => {
          const path = issue.path.join('.');
          if (path && touched[path]) {
            fieldErrors[path] = issue.message;
          }
        });
        setErrors(fieldErrors);
        setIsValid(false);
      }
    },
    [schema, touched]
  );

  const updateField = useCallback(
    (fieldName: keyof T, value: T[keyof T]) => {
      const newData = { ...data, [fieldName]: value };
      setData(newData);
      setTouched(prev => ({ ...prev, [fieldName as string]: true }));
      
      // Debounced validation
      const timeoutId = setTimeout(() => {
        validateData(newData);
      }, debounceMs);

      return () => clearTimeout(timeoutId);
    },
    [data, validateData, debounceMs]
  );

  const reset = useCallback(() => {
    setData({});
    setErrors({});
    setTouched({});
    setIsValid(false);
  }, []);

  return {
    data,
    errors,
    touched,
    isValid,
    updateField,
    reset,
  };
}

/**
 * Hook for batch API validation
 */
export function useBatchValidation<T>(schema: ZodSchema<T>) {
  const [results, setResults] = useState<{
    valid: T[];
    invalid: Array<{ index: number; error: string }>;
  }>({ valid: [], invalid: [] });
  
  const [isValidating, setIsValidating] = useState(false);

  const validateBatch = useCallback(
    async (items: unknown[]): Promise<typeof results> => {
      setIsValidating(true);
      
      const valid: T[] = [];
      const invalid: Array<{ index: number; error: string }> = [];

      for (let i = 0; i < items.length; i++) {
        const result = safeValidateApiResponse(items[i], schema);
        
        if (result.success) {
          valid.push(result.data);
        } else {
          invalid.push({
            index: i,
            error: result.error.message,
          });
        }
      }

      const batchResults = { valid, invalid };
      setResults(batchResults);
      setIsValidating(false);
      
      return batchResults;
    },
    [schema]
  );

  return {
    results,
    isValidating,
    validateBatch,
  };
}

/**
 * Hook for API response caching with validation
 */
export function useValidatedCache<T>(
  key: string,
  schema: ZodSchema<T>,
  ttlMs: number = 5 * 60 * 1000 // 5 minutes default
) {
  const [cache, setCache] = useState<{
    data: T | null;
    timestamp: number | null;
  }>({ data: null, timestamp: null });

  const isExpired = useCallback(() => {
    if (!cache.timestamp) return true;
    return Date.now() - cache.timestamp > ttlMs;
  }, [cache.timestamp, ttlMs]);

  const get = useCallback((): T | null => {
    if (isExpired()) {
      return null;
    }
    return cache.data;
  }, [cache.data, isExpired]);

  const set = useCallback(
    (data: unknown) => {
      const result = safeValidateApiResponse(data, schema);
      
      if (result.success) {
        setCache({
          data: result.data,
          timestamp: Date.now(),
        });
        return true;
      }
      
      return false;
    },
    [schema]
  );

  const clear = useCallback(() => {
    setCache({ data: null, timestamp: null });
  }, []);

  return {
    data: cache.data,
    isExpired: isExpired(),
    get,
    set,
    clear,
  };
}

// ===========================
// Export convenience wrappers
// ===========================

export { ValidationError } from '../api/validation';