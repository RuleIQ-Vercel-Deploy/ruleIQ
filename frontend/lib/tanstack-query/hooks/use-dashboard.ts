import { useQuery } from '@tanstack/react-query';

import { dashboardService } from '@/lib/api/dashboard.service';

import { createQueryKey, type BaseQueryOptions } from './base';

import type { UserDashboard, WidgetData } from '@/lib/api/dashboard.service';

// Query keys
const DASHBOARD_KEY = 'dashboard';

export const dashboardKeys = {
  all: [DASHBOARD_KEY] as const,
  main: () => createQueryKey(DASHBOARD_KEY, 'main'),
  widget: (widgetType: string) => createQueryKey(DASHBOARD_KEY, 'widget', { widgetType }),
  insights: () => createQueryKey(DASHBOARD_KEY, 'insights'),
  tasks: () => createQueryKey(DASHBOARD_KEY, 'tasks'),
  score: () => createQueryKey(DASHBOARD_KEY, 'score'),
};

// Hook to fetch main dashboard data
export function useDashboard(options?: BaseQueryOptions<UserDashboard>) {
  return useQuery({
    queryKey: dashboardKeys.main(),
    queryFn: () => dashboardService.getUserDashboard(),
    ...options,
  });
}

// Hook to fetch specific widget data
export function useDashboardWidget(
  widgetType: 'insights' | 'tasks' | 'score' | 'activity',
  options?: BaseQueryOptions<WidgetData>,
) {
  return useQuery({
    queryKey: dashboardKeys.widget(widgetType),
    queryFn: () => dashboardService.getWidgetData(widgetType),
    ...options,
  });
}

// Hook to fetch AI insights
export function useAIInsights(options?: BaseQueryOptions<any>) {
  return useQuery({
    queryKey: dashboardKeys.insights(),
    queryFn: async () => {
      const dashboard = await dashboardService.getUserDashboard();
      return dashboard.insights || [];
    },
    ...options,
  });
}

// Hook to fetch pending tasks
export function usePendingTasks(options?: BaseQueryOptions<any>) {
  return useQuery({
    queryKey: dashboardKeys.tasks(),
    queryFn: async () => {
      const dashboard = await dashboardService.getUserDashboard();
      return dashboard.pending_tasks || [];
    },
    ...options,
  });
}

// Hook to fetch compliance score
export function useDashboardComplianceScore(options?: BaseQueryOptions<any>) {
  return useQuery({
    queryKey: dashboardKeys.score(),
    queryFn: async () => {
      const dashboard = await dashboardService.getUserDashboard();
      return {
        overall_score: dashboard.compliance_score || 0,
        frameworks: dashboard.framework_scores || {},
      };
    },
    ...options,
  });
}
