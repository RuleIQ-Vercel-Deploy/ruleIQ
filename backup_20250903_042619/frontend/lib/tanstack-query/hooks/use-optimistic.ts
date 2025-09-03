import { useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';

/**
 * Hook for optimistic updates with automatic rollback on error
 */
export function useOptimisticUpdate<TData = unknown>() {
  const queryClient = useQueryClient();

  const optimisticUpdate = useCallback(
    async <TVariables = unknown>(
      queryKey: string[],
      updater: (oldData: TData | undefined, variables: TVariables) => TData,
      variables: TVariables,
    ) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey });

      // Snapshot the previous value
      const previousData = queryClient.getQueryData<TData>(queryKey);

      // Optimistically update to the new value
      queryClient.setQueryData<TData>(queryKey, (old) => updater(old, variables));

      // Return a context object with a rollback function
      return { previousData };
    },
    [queryClient],
  );

  const rollback = useCallback(
    (queryKey: string[], context: { previousData: TData | undefined }) => {
      queryClient.setQueryData(queryKey, context.previousData);
    },
    [queryClient],
  );

  return { optimisticUpdate, rollback };
}

/**
 * Hook for optimistic list updates (add, update, remove items)
 */
export function useOptimisticListUpdate<TItem = unknown>() {
  const { optimisticUpdate, rollback } = useOptimisticUpdate<TItem[]>();

  const addItem = useCallback(
    async (queryKey: string[], newItem: TItem) => {
      return optimisticUpdate(queryKey, (oldData = [], item) => [...oldData, item], newItem);
    },
    [optimisticUpdate],
  );

  const updateItem = useCallback(
    async (queryKey: string[], itemId: string | number, updater: (item: TItem) => TItem) => {
      return optimisticUpdate(
        queryKey,
        (oldData = [], { id, update }) =>
          oldData.map((item: any) => (item.id === id ? update(item) : item)),
        { id: itemId, update: updater },
      );
    },
    [optimisticUpdate],
  );

  const removeItem = useCallback(
    async (queryKey: string[], itemId: string | number) => {
      return optimisticUpdate(
        queryKey,
        (oldData = [], id) => oldData.filter((item: any) => item.id !== id),
        itemId,
      );
    },
    [optimisticUpdate],
  );

  return { addItem, updateItem, removeItem, rollback };
}
