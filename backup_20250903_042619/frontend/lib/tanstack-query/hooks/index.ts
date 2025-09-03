// Base utilities
export * from './base';

// Domain-specific hooks

export * from './use-dashboard';
export * from './use-assessments';
export * from './use-policies';
export * from './use-evidence';
export * from './use-business-profile';
export * from './use-reports';
export * from './use-compliance';
export * from './use-monitoring';
export * from './use-frameworks';
export * from './use-integrations';

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
  useIsMutating,
} from '@tanstack/react-query';
