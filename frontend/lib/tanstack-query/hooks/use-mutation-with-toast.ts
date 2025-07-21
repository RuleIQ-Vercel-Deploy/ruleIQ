import { useMutation, type UseMutationOptions, useQueryClient } from '@tanstack/react-query';

import { useToast } from '@/hooks/use-toast';

import { getErrorMessage } from './base';

interface MutationWithToastOptions<TData, TError, TVariables>
  extends Omit<UseMutationOptions<TData, TError, TVariables>, 'onSuccess' | 'onError'> {
  successMessage?: string | ((data: TData) => string);
  errorMessage?: string | ((error: TError) => string);
  loadingMessage?: string;
  invalidateKeys?: string[][];
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: TError, variables: TVariables) => void;
}

/**
 * Enhanced mutation hook with automatic toast notifications
 */
export function useMutationWithToast<TData = unknown, TError = unknown, TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options?: MutationWithToastOptions<TData, TError, TVariables>,
) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const {
    successMessage = 'Operation completed successfully',
    errorMessage = 'An error occurred',
    loadingMessage,
    invalidateKeys = [],
    onSuccess,
    onError,
    ...mutationOptions
  } = options || {};

  return useMutation<TData, TError, TVariables>({
    mutationFn,
    onMutate: (_variables) => {
      if (loadingMessage) {
        toast({
          title: loadingMessage,
          description: 'Please wait...',
        });
      }
    },
    onSuccess: (data, _variables) => {
      // Show success toast
      const message = typeof successMessage === 'function' ? successMessage(data) : successMessage;

      toast({
        title: 'Success',
        description: message,
      });

      // Invalidate queries
      invalidateKeys.forEach((key) => {
        queryClient.invalidateQueries({ queryKey: key });
      });

      // Call custom success handler
      onSuccess?.(data, variables);
    },
    onError: (error, variables) => {
      // Show error toast
      const message =
        typeof errorMessage === 'function' ? errorMessage(error) : getErrorMessage(error);

      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });

      // Call custom error handler
      onError?.(error, variables);
    },
    ...mutationOptions,
  });
}
