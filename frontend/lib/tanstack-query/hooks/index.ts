// Base utilities
export * from './base';

// Domain-specific hooks
export * from './use-auth';
export * from './use-dashboard';
export * from './use-assessments';
export * from './use-policies';
export * from './use-evidence';
export * from './use-business-profile';

// Utility hooks
export * from './use-optimistic';
export * from './use-infinite-scroll';
export * from './use-mutation-with-toast';

// Re-export commonly used utilities
export { 
  useQuery, 
  useMutation, 
  useQueryClient,
  useInfiniteQuery,
  useIsFetching,
  useIsMutating 
} from '@tanstack/react-query';