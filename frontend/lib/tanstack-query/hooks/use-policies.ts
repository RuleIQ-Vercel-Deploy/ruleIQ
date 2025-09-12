import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { 
  policyService,
  type GeneratePolicyRequest,
  type UpdatePolicyStatusRequest,
} from '@/lib/api/policies.service';

import {
  createQueryKey,
  type BaseQueryOptions,
  type BaseMutationOptions,
  type PaginationParams,
  type PaginatedResponse,
} from './base';

import type {
  Policy,
} from '@/types/api';

// Define locally until available in @/types/api
interface PolicyTemplate {
  id: string;
  name: string;
  description: string;
  framework: string;
  sections: string[];
}

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
  options?: BaseQueryOptions<PaginatedResponse<Policy>>,
) {
  return useQuery({
    queryKey: policyKeys.list(params),
    queryFn: async () => {
      const response = await policyService.getPolicies(params);
      // Transform the response to match PaginatedResponse
      return {
        items: response.policies,
        total: response.policies.length,
        page: params?.page || 1,
        page_size: params?.page_size || 20,
        total_pages: Math.ceil(response.policies.length / (params?.page_size || 20)),
      } as PaginatedResponse<Policy>;
    },
    ...options,
  });
}

// Hook to fetch single policy
export function usePolicy(id: string, options?: BaseQueryOptions<Policy>) {
  return useQuery({
    queryKey: policyKeys.detail(id),
    queryFn: () => policyService.getPolicy(id),
    enabled: !!id,
    ...options,
  });
}

// Hook to fetch policy templates
export function usePolicyTemplates(options?: BaseQueryOptions<PolicyTemplate[]>) {
  return useQuery({
    queryKey: policyKeys.templates(),
    queryFn: async () => {
      const response = await policyService.getPolicyTemplates();
      return response.templates.map(t => ({
        ...t,
        [Symbol.for('key')]: t.id,
      })) as PolicyTemplate[];
    },
    ...options,
  });
}

// Hook to fetch policy types for a framework
// TODO: getPolicyTypes doesn't exist in the service, commenting out
// export function usePolicyTypes(frameworkId?: string, options?: BaseQueryOptions<string[]>) {
//   return useQuery({
//     queryKey: policyKeys.types(frameworkId),
//     queryFn: () => policyService.getPolicyTypes(frameworkId),
//     ...options,
//   });
// }

// Hook to generate policy
export function useGeneratePolicy(
  options?: BaseMutationOptions<Policy, unknown, GeneratePolicyRequest>,
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

// Hook to update policy status
export function useUpdatePolicyStatus(
  options?: BaseMutationOptions<{ id: string; status: string; approved: boolean }, unknown, { id: string; data: UpdatePolicyStatusRequest }>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => 
      policyService.updatePolicyStatus(id, data),
    onSuccess: (_, variables) => {
      // Invalidate cache
      queryClient.invalidateQueries({ queryKey: policyKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: policyKeys.lists() });
    },
    ...options,
  });
}

// Hook to archive policy
export function useArchivePolicy(options?: BaseMutationOptions<void, unknown, string>) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => policyService.archivePolicy(id),
    onSuccess: (_, id) => {
      // Remove from cache and invalidate list
      queryClient.removeQueries({ queryKey: policyKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: policyKeys.lists() });
    },
    ...options,
  });
}

// Hook to export policy as PDF
export function useExportPolicyAsPDF() {
  return useMutation({
    mutationFn: (id: string) => policyService.exportPolicyAsPDF(id),
  });
}

// Hook to export policy as Word
export function useExportPolicyAsWord() {
  return useMutation({
    mutationFn: (id: string) => policyService.exportPolicyAsWord(id),
  });
}

// Hook to clone policy
export function useClonePolicy(options?: BaseMutationOptions<Policy, unknown, { id: string; newName: string }>) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, newName }) => policyService.clonePolicy(id, newName),
    onSuccess: (newPolicy) => {
      // Add to cache and invalidate list
      queryClient.setQueryData(policyKeys.detail(newPolicy.id), newPolicy);
      queryClient.invalidateQueries({ queryKey: policyKeys.lists() });
    },
    ...options,
  });
}
