import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { reportService } from '@/lib/api/reports.service';

import {
  createQueryKey,
  type BaseQueryOptions,
  type BaseMutationOptions,
  type PaginationParams,
  type PaginatedResponse,
} from './base';

import type {
  Report,
  CreateReportRequest,
  UpdateReportRequest,
  ReportTemplate,
  ReportSchedule,
} from '@/types/api';

// Query keys
const REPORT_KEY = 'reports';

export const reportKeys = {
  all: [REPORT_KEY] as const,
  lists: () => [...reportKeys.all, 'list'] as const,
  list: (params?: PaginationParams) => createQueryKey(REPORT_KEY, 'list', params),
  details: () => [...reportKeys.all, 'detail'] as const,
  detail: (id: string) => createQueryKey(REPORT_KEY, 'detail', { id }),
  templates: () => createQueryKey(REPORT_KEY, 'templates'),
  template: (id: string) => createQueryKey(REPORT_KEY, 'template', { id }),
  schedules: () => createQueryKey(REPORT_KEY, 'schedules'),
  schedule: (id: string) => createQueryKey(REPORT_KEY, 'schedule', { id }),
};

// Hook to fetch reports list
export function useReports(
  params?: PaginationParams & {
    framework_id?: string;
    type?: string;
    status?: string;
  },
  options?: BaseQueryOptions<PaginatedResponse<Report>>,
) {
  return useQuery({
    queryKey: reportKeys.list(params),
    queryFn: () => reportService.getReports(params),
    ...options,
  });
}

// Hook to fetch single report
export function useReport(id: string, options?: BaseQueryOptions<Report>) {
  return useQuery({
    queryKey: reportKeys.detail(id),
    queryFn: () => reportService.getReport(id),
    enabled: !!id,
    ...options,
  });
}

// Hook to fetch report templates
export function useReportTemplates(options?: BaseQueryOptions<ReportTemplate[]>) {
  return useQuery({
    queryKey: reportKeys.templates(),
    queryFn: () => reportService.getTemplates(),
    ...options,
  });
}

// Hook to fetch report schedules
export function useReportSchedules(options?: BaseQueryOptions<ReportSchedule[]>) {
  return useQuery({
    queryKey: reportKeys.schedules(),
    queryFn: () => reportService.getSchedules(),
    ...options,
  });
}

// Hook to generate report
export function useGenerateReport(
  options?: BaseMutationOptions<Report, unknown, CreateReportRequest>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateReportRequest) => reportService.generateReport(data),
    onSuccess: (newReport) => {
      // Add to cache and invalidate list
      queryClient.setQueryData(reportKeys.detail(newReport.id), newReport);
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
    },
    ...options,
  });
}

// Hook to update report
export function useUpdateReport(
  options?: BaseMutationOptions<Report, unknown, { id: string; data: UpdateReportRequest }>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => reportService.updateReport(id, data),
    onSuccess: (updatedReport, variables) => {
      // Update cache
      queryClient.setQueryData(reportKeys.detail(variables.id), updatedReport);
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
    },
    ...options,
  });
}

// Hook to delete report
export function useDeleteReport(options?: BaseMutationOptions<void, unknown, string>) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => reportService.deleteReport(id),
    onSuccess: (_, id) => {
      // Remove from cache and invalidate list
      queryClient.removeQueries({ queryKey: reportKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
    },
    ...options,
  });
}

// Hook to download report
export function useDownloadReport() {
  return useMutation({
    mutationFn: ({ id, format }: { id: string; format: 'pdf' | 'excel' | 'csv' }) =>
      reportService.downloadReport(id, format),
  });
}

// Hook to schedule report
export function useScheduleReport(
  options?: BaseMutationOptions<ReportSchedule, unknown, { reportId: string; schedule: any }>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ reportId, schedule }) => reportService.scheduleReport(reportId, schedule),
    onSuccess: () => {
      // Invalidate schedules
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() });
    },
    ...options,
  });
}

// Hook to share report
export function useShareReport(
  options?: BaseMutationOptions<void, unknown, { id: string; emails: string[] }>,
) {
  return useMutation({
    mutationFn: ({ id, emails }) => reportService.shareReport(id, emails),
    ...options,
  });
}
