import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { policyService } from '@/lib/api/policies.service';

import { 
  createQueryKey, 
  type BaseQueryOptions, 
  type BaseMutationOptions,
  type PaginationParams,
  type PaginatedResponse 
} from './base';

import type { 
  Policy,
  GeneratePolicyRequest,
  UpdatePolicyRequest,
  PolicyTemplate
} from '@/types/api';

// Query keys
const POLICY_KEY = 'policies';

export const policyKeys = {
  all: [POLICY_KEY] as const,
  lists: () => [...policyKeys.all, 'list'] as const,
  list: (params?: PaginationParams) => createQueryKey(POLICY_KEY, 'list', params),
  details: () => [...policyKeys.all, 'detail'] as const,
  detail: (id: string) => createQueryKey(POLICY_KEY, 'detail', { id }),
  templates: () => createQueryKey(POLICY_KEY, 'templates'),
  template: (id: string) => createQueryKey(POLICY_KEY, 'template', { id }),
  types: (frameworkId?: string) => createQueryKey(POLICY_KEY, 'types', { frameworkId }),
};

// Hook to fetch policies list
export function usePolicies(
  params?: PaginationParams,
  options?: BaseQueryOptions<PaginatedResponse<Policy>>
) {
  return useQuery({
    queryKey: policyKeys.list(params),
    queryFn: () => policyService.getPolicies(params),
    ...options,
  });
}

// Hook to fetch single policy
export function usePolicy(
  id: string,
  options?: BaseQueryOptions<Policy>
) {
  return useQuery({
    queryKey: policyKeys.detail(id),
    queryFn: () => policyService.getPolicy(id),
    enabled: !!id,
    ...options,
  });
}

// Hook to fetch policy templates
export function usePolicyTemplates(
  options?: BaseQueryOptions<PolicyTemplate[]>
) {
  return useQuery({
    queryKey: policyKeys.templates(),
    queryFn: () => policyService.getTemplates(),
    ...options,
  });
}

// Hook to fetch policy types for a framework
export function usePolicyTypes(
  frameworkId?: string,
  options?: BaseQueryOptions<string[]>
) {
  return useQuery({
    queryKey: policyKeys.types(frameworkId),
    queryFn: () => policyService.getPolicyTypes(frameworkId),
    ...options,
  });
}

// Hook to generate policy
export function useGeneratePolicy(
  options?: BaseMutationOptions<Policy, unknown, GeneratePolicyRequest>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: GeneratePolicyRequest) => policyService.generatePolicy(data),
    onSuccess: (newPolicy) => {
      // Add to cache and invalidate list
      queryClient.setQueryData(policyKeys.detail(newPolicy.id), newPolicy);
      queryClient.invalidateQueries({ queryKey: policyKeys.lists() });
    },
    ...options,
  });
}

// Hook to update policy
export function useUpdatePolicy(
  options?: BaseMutationOptions<Policy, unknown, { id: string; data: UpdatePolicyRequest }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => policyService.updatePolicy(id, data),
    onSuccess: (updatedPolicy, variables) => {
      // Update cache
      queryClient.setQueryData(policyKeys.detail(variables.id), updatedPolicy);
      queryClient.invalidateQueries({ queryKey: policyKeys.lists() });
    },
    ...options,
  });
}

// Hook to delete policy
export function useDeletePolicy(
  options?: BaseMutationOptions<void, unknown, string>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => policyService.deletePolicy(id),
    onSuccess: (_, id) => {
      // Remove from cache and invalidate list
      queryClient.removeQueries({ queryKey: policyKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: policyKeys.lists() });
    },
    ...options,
  });
}

// Hook to download policy
export function useDownloadPolicy() {
  return useMutation({
    mutationFn: ({ id, format }: { id: string; format: 'pdf' | 'docx' | 'txt' }) => 
      policyService.downloadPolicy(id, format),
  });
}

// Hook to clone policy
export function useClonePolicy(
  options?: BaseMutationOptions<Policy, unknown, string>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => policyService.clonePolicy(id),
    onSuccess: (newPolicy) => {
      // Add to cache and invalidate list
      queryClient.setQueryData(policyKeys.detail(newPolicy.id), newPolicy);
      queryClient.invalidateQueries({ queryKey: policyKeys.lists() });
    },
    ...options,
  });
}