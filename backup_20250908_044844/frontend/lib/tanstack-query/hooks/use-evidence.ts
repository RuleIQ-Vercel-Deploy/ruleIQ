import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { evidenceService } from '@/lib/api/evidence.service';

import {
  createQueryKey,
  type BaseQueryOptions,
  type BaseMutationOptions,
  type PaginationParams,
  type PaginatedResponse,
} from './base';

import type {
  EvidenceItem,
  CreateEvidenceRequest,
  UpdateEvidenceRequest,
  BulkUpdateRequest,
} from '@/types/api';

// Query keys
const EVIDENCE_KEY = 'evidence';

export const evidenceKeys = {
  all: [EVIDENCE_KEY] as const,
  lists: () => [...evidenceKeys.all, 'list'] as const,
  list: (
    params?: PaginationParams & {
      framework_id?: string;
      control_id?: string;
      status?: string;
      tags?: string[];
    },
  ) => createQueryKey(EVIDENCE_KEY, 'list', params),
  details: () => [...evidenceKeys.all, 'detail'] as const,
  detail: (id: string) => createQueryKey(EVIDENCE_KEY, 'detail', { id }),
  stats: () => createQueryKey(EVIDENCE_KEY, 'stats'),
  controlEvidence: (controlId: string) => createQueryKey(EVIDENCE_KEY, 'control', { controlId }),
};

// Hook to fetch evidence list
export function useEvidence(
  params?: PaginationParams & {
    framework_id?: string;
    control_id?: string;
    status?: string;
    tags?: string[];
  },
  options?: BaseQueryOptions<PaginatedResponse<EvidenceItem>>,
) {
  return useQuery({
    queryKey: evidenceKeys.list(params),
    queryFn: () => evidenceService.getEvidence(params),
    ...options,
  });
}

// Hook to fetch single evidence item
export function useEvidenceItem(id: string, options?: BaseQueryOptions<EvidenceItem>) {
  return useQuery({
    queryKey: evidenceKeys.detail(id),
    queryFn: () => evidenceService.getEvidenceById(id),
    enabled: !!id,
    ...options,
  });
}

// Hook to fetch evidence statistics
export function useEvidenceStats(options?: BaseQueryOptions<any>) {
  return useQuery({
    queryKey: evidenceKeys.stats(),
    queryFn: () => evidenceService.getEvidenceStats(),
    ...options,
  });
}

// Hook to fetch evidence for a specific control
export function useControlEvidence(controlId: string, options?: BaseQueryOptions<EvidenceItem[]>) {
  return useQuery({
    queryKey: evidenceKeys.controlEvidence(controlId),
    queryFn: () => evidenceService.getEvidenceByControl(controlId),
    enabled: !!controlId,
    ...options,
  });
}

// Hook to create evidence
export function useCreateEvidence(
  options?: BaseMutationOptions<EvidenceItem, unknown, CreateEvidenceRequest>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateEvidenceRequest) => evidenceService.createEvidence(data),
    onSuccess: (newEvidence) => {
      // Add to cache and invalidate list
      queryClient.setQueryData(evidenceKeys.detail(newEvidence.id), newEvidence);
      queryClient.invalidateQueries({ queryKey: evidenceKeys.lists() });
      queryClient.invalidateQueries({ queryKey: evidenceKeys.stats() });
    },
    ...options,
  });
}

// Hook to update evidence
export function useUpdateEvidence(
  options?: BaseMutationOptions<EvidenceItem, unknown, { id: string; data: UpdateEvidenceRequest }>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => evidenceService.updateEvidence(id, data),
    onSuccess: (updatedEvidence, variables) => {
      // Update cache
      queryClient.setQueryData(evidenceKeys.detail(variables.id), updatedEvidence);
      queryClient.invalidateQueries({ queryKey: evidenceKeys.lists() });

      // If control_id changed, invalidate control evidence
      if (updatedEvidence.control_id) {
        queryClient.invalidateQueries({
          queryKey: evidenceKeys.controlEvidence(updatedEvidence.control_id),
        });
      }
    },
    ...options,
  });
}

// Hook to upload evidence file
export function useUploadEvidence(options?: BaseMutationOptions<EvidenceItem, unknown, FormData>) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData: FormData) => evidenceService.uploadEvidence(formData),
    onSuccess: (newEvidence) => {
      // Add to cache and invalidate list
      queryClient.setQueryData(evidenceKeys.detail(newEvidence.id), newEvidence);
      queryClient.invalidateQueries({ queryKey: evidenceKeys.lists() });
      queryClient.invalidateQueries({ queryKey: evidenceKeys.stats() });
    },
    ...options,
  });
}

// Hook to delete evidence
export function useDeleteEvidence(options?: BaseMutationOptions<void, unknown, string>) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => evidenceService.deleteEvidence(id),
    onSuccess: (_, id) => {
      // Remove from cache and invalidate list
      queryClient.removeQueries({ queryKey: evidenceKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: evidenceKeys.lists() });
      queryClient.invalidateQueries({ queryKey: evidenceKeys.stats() });
    },
    ...options,
  });
}

// Hook for bulk operations
export function useBulkUpdateEvidence(
  options?: BaseMutationOptions<void, unknown, BulkUpdateRequest>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: BulkUpdateRequest) => evidenceService.bulkUpdate(data),
    onSuccess: () => {
      // Invalidate all evidence queries
      queryClient.invalidateQueries({ queryKey: evidenceKeys.all });
    },
    ...options,
  });
}

// Hook to bulk delete evidence
export function useBulkDeleteEvidence(options?: BaseMutationOptions<void, unknown, string[]>) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ids: string[]) => evidenceService.bulkDelete(ids),
    onSuccess: (_, ids) => {
      // Remove from cache
      ids.forEach((id) => {
        queryClient.removeQueries({ queryKey: evidenceKeys.detail(id) });
      });
      // Invalidate list and stats
      queryClient.invalidateQueries({ queryKey: evidenceKeys.lists() });
      queryClient.invalidateQueries({ queryKey: evidenceKeys.stats() });
    },
    ...options,
  });
}
