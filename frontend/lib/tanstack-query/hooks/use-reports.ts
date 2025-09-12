import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { 
  reportService,
  type GenerateReportRequest,
  type ScheduleReportRequest,
} from '@/lib/api/reports.service';

import {
  createQueryKey,
  type BaseQueryOptions,
  type BaseMutationOptions,
  type PaginationParams,
  type PaginatedResponse,
} from './base';

import type {
  Report,
} from '@/types/api';

// Define locally until available in @/types/api
interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  report_type: string;
  sections: string[];
  preview_url?: string;
}

interface ReportSchedule {
  id: string;
  report_config: GenerateReportRequest;
  schedule: any;
  recipients: string[];
  active: boolean;
  last_run?: string;
  next_run: string;
}

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
    report_type?: string;
  },
  options?: BaseQueryOptions<PaginatedResponse<Report>>,
) {
  return useQuery({
    queryKey: reportKeys.list(params),
    queryFn: async () => {
      const response = await reportService.getReportHistory(params);
      // Transform to PaginatedResponse
      return {
        items: response.items,
        total: response.total,
        page: params?.page || 1,
        page_size: params?.page_size || 20,
        total_pages: Math.ceil(response.total / (params?.page_size || 20)),
      } as PaginatedResponse<Report>;
    },
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
export function useReportTemplates(reportType?: string, options?: BaseQueryOptions<ReportTemplate[]>) {
  return useQuery({
    queryKey: reportKeys.templates(),
    queryFn: async () => {
      const response = await reportService.getReportTemplates(reportType);
      return response.templates as ReportTemplate[];
    },
    ...options,
  });
}

// Hook to fetch report schedules
export function useReportSchedules(options?: BaseQueryOptions<ReportSchedule[]>) {
  return useQuery({
    queryKey: reportKeys.schedules(),
    queryFn: async () => {
      const response = await reportService.getScheduledReports();
      return response.schedules as ReportSchedule[];
    },
    ...options,
  });
}

// Hook to generate report
export function useGenerateReport(
  options?: BaseMutationOptions<Report, unknown, GenerateReportRequest>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: GenerateReportRequest) => reportService.generateReport(data),
    onSuccess: (newReport) => {
      // Add to cache and invalidate list
      queryClient.setQueryData(reportKeys.detail(newReport.id), newReport);
      queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
    },
    ...options,
  });
}

// Hook to schedule report
export function useScheduleReport(
  options?: BaseMutationOptions<{ schedule_id: string; message: string; next_run: string }, unknown, ScheduleReportRequest>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ScheduleReportRequest) => reportService.scheduleReport(data),
    onSuccess: () => {
      // Invalidate schedules list
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() });
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
    mutationFn: (id: string) => reportService.downloadReport(id),
  });
}

// Hook to update scheduled report
export function useUpdateScheduledReport(
  options?: BaseMutationOptions<void, unknown, { scheduleId: string; data: Partial<ScheduleReportRequest> }>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ scheduleId, data }) => reportService.updateScheduledReport(scheduleId, data),
    onSuccess: () => {
      // Invalidate schedules
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() });
    },
    ...options,
  });
}

// Hook to delete scheduled report
export function useDeleteScheduledReport(options?: BaseMutationOptions<void, unknown, string>) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (scheduleId: string) => reportService.deleteScheduledReport(scheduleId),
    onSuccess: () => {
      // Invalidate schedules
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() });
    },
    ...options,
  });
}
