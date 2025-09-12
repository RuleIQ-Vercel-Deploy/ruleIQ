import { useInfiniteQuery, type UseInfiniteQueryOptions } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useInView } from 'react-intersection-observer';

import type { PaginatedResponse } from './base';

interface UseInfiniteScrollOptions<TData>
  extends Omit<
    UseInfiniteQueryOptions<PaginatedResponse<TData>>,
    'queryKey' | 'queryFn' | 'getNextPageParam'
  > {
  queryKey: string[];
  queryFn: (params: { page: number; page_size: number }) => Promise<PaginatedResponse<TData>>;
  pageSize?: number;
}

/**
 * Hook for infinite scrolling with automatic loading of next page
 */
export function useInfiniteScroll<TData>({
  queryKey,
  queryFn,
  pageSize = 20,
  ...options
}: UseInfiniteScrollOptions<TData>) {
  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetching,
    isFetchingNextPage,
    status,
    refetch,
  } = useInfiniteQuery({
    queryKey,
    queryFn: ({ pageParam = 1 }) => queryFn({ page: pageParam as number, page_size: pageSize }),
    getNextPageParam: (lastPage, pages) => {
      const currentPage = pages.length;
      const totalPages = Math.ceil(lastPage.total / lastPage.page_size);
      return currentPage < totalPages ? currentPage + 1 : undefined;
    },
    ...options,
  });

  // Set up intersection observer for auto-loading
  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: '100px',
  });

  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, fetchNextPage, hasNextPage, isFetchingNextPage]);

  // Flatten all pages into a single array
  const items = (data as any)?.pages?.flatMap((page: PaginatedResponse<TData>) => page.items) ?? [];
  const total = (data as any)?.pages?.[0]?.total ?? 0;

  return {
    items,
    total,
    error,
    isLoading: status === 'pending',
    isFetching,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    refetch,
    loadMoreRef: ref,
  };
}
