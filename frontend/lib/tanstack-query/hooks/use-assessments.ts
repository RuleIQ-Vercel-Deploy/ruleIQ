import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { assessmentService } from '@/lib/api/assessments.service';

import { 
  createQueryKey, 
  type BaseQueryOptions, 
  type BaseMutationOptions,
  type PaginationParams,
  type PaginatedResponse 
} from './base';

import type { 
  Assessment, 
  AssessmentQuestion, 
  CreateAssessmentRequest,
  UpdateAssessmentRequest,
  SubmitResponseRequest 
} from '@/types/api';

// Query keys
const ASSESSMENT_KEY = 'assessments';

export const assessmentKeys = {
  all: [ASSESSMENT_KEY] as const,
  lists: () => [...assessmentKeys.all, 'list'] as const,
  list: (params?: PaginationParams) => createQueryKey(ASSESSMENT_KEY, 'list', params),
  details: () => [...assessmentKeys.all, 'detail'] as const,
  detail: (id: string) => createQueryKey(ASSESSMENT_KEY, 'detail', { id }),
  questions: (id: string) => createQueryKey(ASSESSMENT_KEY, 'questions', { id }),
  results: (id: string) => createQueryKey(ASSESSMENT_KEY, 'results', { id }),
  frameworks: () => createQueryKey(ASSESSMENT_KEY, 'frameworks'),
};

// Hook to fetch assessments list
export function useAssessments(
  params?: PaginationParams,
  options?: BaseQueryOptions<PaginatedResponse<Assessment>>
) {
  return useQuery({
    queryKey: assessmentKeys.list(params),
    queryFn: () => assessmentService.getAssessments(params),
    ...options,
  });
}

// Hook to fetch single assessment
export function useAssessment(
  id: string,
  options?: BaseQueryOptions<Assessment>
) {
  return useQuery({
    queryKey: assessmentKeys.detail(id),
    queryFn: () => assessmentService.getAssessment(id),
    enabled: !!id,
    ...options,
  });
}

// Hook to fetch assessment questions
export function useAssessmentQuestions(
  assessmentId: string,
  options?: BaseQueryOptions<AssessmentQuestion[]>
) {
  return useQuery({
    queryKey: assessmentKeys.questions(assessmentId),
    queryFn: () => assessmentService.getAssessmentQuestions(assessmentId),
    enabled: !!assessmentId,
    ...options,
  });
}

// Hook to fetch assessment results
export function useAssessmentResults(
  assessmentId: string,
  options?: BaseQueryOptions<any>
) {
  return useQuery({
    queryKey: assessmentKeys.results(assessmentId),
    queryFn: () => assessmentService.getAssessmentResults(assessmentId),
    enabled: !!assessmentId,
    ...options,
  });
}

// Hook to create assessment
export function useCreateAssessment(
  options?: BaseMutationOptions<Assessment, unknown, CreateAssessmentRequest>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateAssessmentRequest) => assessmentService.createAssessment(data),
    onSuccess: () => {
      // Invalidate assessments list
      queryClient.invalidateQueries({ queryKey: assessmentKeys.lists() });
    },
    ...options,
  });
}

// Hook to update assessment
export function useUpdateAssessment(
  options?: BaseMutationOptions<Assessment, unknown, { id: string; data: UpdateAssessmentRequest }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => assessmentService.updateAssessment(id, data),
    onSuccess: (_, variables) => {
      // Invalidate specific assessment and list
      queryClient.invalidateQueries({ queryKey: assessmentKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: assessmentKeys.lists() });
    },
    ...options,
  });
}

// Hook to submit assessment response
export function useSubmitAssessmentResponse(
  options?: BaseMutationOptions<any, unknown, { assessmentId: string; data: SubmitResponseRequest }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ assessmentId, data }) => 
      assessmentService.submitResponse(assessmentId, data),
    onSuccess: (_, variables) => {
      // Invalidate assessment details and results
      queryClient.invalidateQueries({ queryKey: assessmentKeys.detail(variables.assessmentId) });
      queryClient.invalidateQueries({ queryKey: assessmentKeys.results(variables.assessmentId) });
    },
    ...options,
  });
}

// Hook to delete assessment
export function useDeleteAssessment(
  options?: BaseMutationOptions<void, unknown, string>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => assessmentService.deleteAssessment(id),
    onSuccess: (_, id) => {
      // Remove from cache and invalidate list
      queryClient.removeQueries({ queryKey: assessmentKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: assessmentKeys.lists() });
    },
    ...options,
  });
}

// Hook to start quick assessment
export function useStartQuickAssessment(
  options?: BaseMutationOptions<Assessment, unknown, { framework_id: string }>
) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ framework_id }) => assessmentService.startQuickAssessment(framework_id),
    onSuccess: () => {
      // Invalidate assessments list
      queryClient.invalidateQueries({ queryKey: assessmentKeys.lists() });
    },
    ...options,
  });
}