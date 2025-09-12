'use client';

import { create } from 'zustand';
import { persist, createJSONStorage, devtools } from 'zustand/middleware';

import { dashboardService } from '@/lib/api/dashboard.service';

import { WidgetsArraySchema, MetricsSchema, LoadingStateSchema, safeValidate } from './schemas';

// Widget Configuration Types
export interface WidgetConfig {
  id: string;
  type: WidgetType;
  position: { x: number; y: number };
  size: { w: number; h: number };
  settings: Record<string, any>;
  isVisible: boolean;
}

export type WidgetType =
  | 'compliance-score'
  | 'framework-progress'
  | 'pending-tasks'
  | 'activity-feed'
  | 'upcoming-deadlines'
  | 'ai-insights';

// Dashboard Data Types (aligned with backend schema)
export interface ComplianceScore {
  overall_score: number; // Matches backend field name
  policy_score: number;
  implementation_score: number;
  evidence_score: number;
  trend: 'up' | 'down' | 'stable';
  lastUpdated: Date;
  domain_scores: Record<string, number>; // JSONB field from backend
  control_scores: Record<string, number>; // JSONB field from backend
  breakdown: {
    framework: string;
    score: number;
    weight: number;
  }[];
}

export interface Task {
  id: string;
  title: string;
  category: 'evidence' | 'assessment' | 'policy' | 'review';
  priority: 'critical' | 'high' | 'medium' | 'low';
  dueDate: Date | null;
  assignee: {
    name: string;
    avatar?: string;
  };
  framework?: string;
  quickActions: string[];
}

export interface Activity {
  id: string;
  type: 'login' | 'change' | 'approval' | 'upload' | 'report';
  actor: {
    id: string;
    name: string;
    avatar?: string;
  };
  action: string;
  target: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface Framework {
  id: string;
  name: string;
  progress: number;
  status: 'not-started' | 'in-progress' | 'complete' | 'expired';
  deadline?: Date;
  description: string;
}

export interface Deadline {
  id: string;
  title: string;
  type: 'compliance' | 'renewal' | 'audit' | 'review';
  dueDate: Date;
  framework?: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  description?: string;
  notificationEnabled: boolean;
}

export interface AIInsight {
  id: string;
  type: 'tip' | 'recommendation' | 'risk-alert' | 'optimization';
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  framework?: string;
  actionable: boolean;
  suggestedActions?: string[];
  confidence: number;
  timestamp: Date;
  dismissed?: boolean;
  bookmarked?: boolean;
}

// Dashboard State Interface
interface DashboardState {
  // Widget Configuration
  widgets: WidgetConfig[];

  // Dashboard Data
  complianceScore: ComplianceScore | null;
  tasks: Task[];
  activities: Activity[];
  frameworks: Framework[];
  deadlines: Deadline[];
  aiInsights: AIInsight[];
  metrics: any; // For test compatibility

  // UI State
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;

  // Widget-specific loading states
  widgetLoading: Record<string, boolean>;
  widgetErrors: Record<string, string | null>;

  // Empty state flags
  hasInitialData: boolean;
  isFirstLoad: boolean;

  // Actions
  fetchDashboardData: () => Promise<void>;
  updateWidgetConfig: (widgetId: string, config: Partial<WidgetConfig>) => void;
  reorderWidgets: (widgets: WidgetConfig[]) => void;
  refreshWidget: (widgetId: string) => Promise<void>;

  // Widget-specific loading actions
  setWidgetLoading: (widgetId: string, loading: boolean) => void;
  setWidgetError: (widgetId: string, error: string | null) => void;
  clearAllErrors: () => void;

  // Data Actions
  setComplianceScore: (score: ComplianceScore) => void;
  setTasks: (tasks: Task[]) => void;
  setActivities: (activities: Activity[]) => void;
  setFrameworks: (frameworks: Framework[]) => void;
  setDeadlines: (deadlines: Deadline[]) => void;
  setAIInsights: (insights: AIInsight[]) => void;

  // Widget Management
  addWidget: (widget: WidgetConfig) => void;
  removeWidget: (widgetId: string) => void;
  toggleWidgetVisibility: (widgetId: string) => void;
  resetWidgets: () => void;

  // Test Compatibility Methods
  setWidgets: (widgets: WidgetConfig[]) => void;
  setMetrics: (metrics: any) => void;
  setLoading: (loading: boolean) => void;
}

// Default Widget Configuration
const defaultWidgets: WidgetConfig[] = [
  {
    id: 'compliance-score',
    type: 'compliance-score',
    position: { x: 0, y: 0 },
    size: { w: 1, h: 1 },
    settings: {},
    isVisible: true,
  },
  {
    id: 'framework-progress',
    type: 'framework-progress',
    position: { x: 1, y: 0 },
    size: { w: 2, h: 1 },
    settings: {},
    isVisible: true,
  },
  {
    id: 'pending-tasks',
    type: 'pending-tasks',
    position: { x: 0, y: 1 },
    size: { w: 1, h: 1 },
    settings: { maxTasks: 5 },
    isVisible: true,
  },
  {
    id: 'activity-feed',
    type: 'activity-feed',
    position: { x: 1, y: 1 },
    size: { w: 1, h: 1 },
    settings: { maxActivities: 10 },
    isVisible: true,
  },
  {
    id: 'upcoming-deadlines',
    type: 'upcoming-deadlines',
    position: { x: 2, y: 1 },
    size: { w: 1, h: 1 },
    settings: { maxDeadlines: 5 },
    isVisible: true,
  },
  {
    id: 'ai-insights',
    type: 'ai-insights',
    position: { x: 0, y: 2 },
    size: { w: 2, h: 1 },
    settings: { maxInsights: 3 },
    isVisible: true,
  },
];

export const useDashboardStore = create<DashboardState>()(
  devtools(
    persist(
      (set, _get) => ({
        // Initial State
        widgets: defaultWidgets,
        complianceScore: null,
        tasks: [],
        activities: [],
        frameworks: [],
        deadlines: [],
        aiInsights: [],
        metrics: {},
        isLoading: false,
        error: null,
        lastUpdated: null,

        // Widget-specific states
        widgetLoading: {},
        widgetErrors: {},

        // Empty state flags
        hasInitialData: false,
        isFirstLoad: true,

        // Main Data Fetching
        fetchDashboardData: async () => {
          set(
            { isLoading: true, error: null, widgetErrors: {} },
            false,
            'fetchDashboardData/start',
          );

          try {
            // Load dashboard data from API
            const userDashboard = await dashboardService.getUserDashboard();
            const dashboardData = userDashboard.stats;
            const recentActivities = userDashboard.recent_activity;

            // Transform API data to match our state structure
            const complianceScore: ComplianceScore = {
              overall_score: dashboardData.compliance_score || 0,
              policy_score: (dashboardData as any).policy_score || 0,
              implementation_score: (dashboardData as any).implementation_score || 0,
              evidence_score: (dashboardData as any).evidence_score || 0,
              trend: (dashboardData as any).compliance_trend || 'stable',
              lastUpdated: new Date(),
              domain_scores: (dashboardData as any).domain_scores || {},
              control_scores: (dashboardData as any).control_scores || {},
              breakdown: (dashboardData as any).framework_scores || [],
            };

            // Transform tasks from API
            const tasks: Task[] =
              (userDashboard.pending_tasks || []).map((task: any) => ({
                id: task.id,
                title: task.title,
                category: task.category,
                priority: task.priority,
                dueDate: task.due_date ? new Date(task.due_date) : null,
                assignee: {
                  name: task.assignee_name || 'Unassigned',
                  avatar: task.assignee_avatar,
                },
                framework: task.framework,
                quickActions: task.quick_actions || [],
              })) || [];

            // Transform activities
            const activities: Activity[] = recentActivities.map((activity: any) => ({
              id: activity.id,
              type: activity.type,
              actor: {
                id: activity.user_id,
                name: activity.user_name || 'System',
                avatar: activity.user_avatar,
              },
              action: activity.action,
              target: activity.target,
              timestamp: new Date(activity.timestamp),
              metadata: activity.metadata,
            }));

            // Set all data
            set(
              {
                isLoading: false,
                lastUpdated: new Date(),
                error: null,
                hasInitialData: true,
                isFirstLoad: false,
                complianceScore,
                tasks,
                activities,
                frameworks: (userDashboard.framework_progress || []).map((fp) => ({
                  id: fp.framework_id,
                  name: fp.framework_name,
                  progress: fp.compliance_percentage,
                  status: fp.compliance_percentage === 100 ? 'complete' as const :
                          fp.compliance_percentage === 0 ? 'not-started' as const : 'in-progress' as const,
                  deadline: fp.next_review_date ? new Date(fp.next_review_date) : undefined,
                  description: `${fp.controls_compliant}/${fp.controls_total} controls compliant`,
                })),
                deadlines: (userDashboard.upcoming_deadlines || []).map((d, index) => ({
                  id: `deadline-${index}`,
                  title: d.title,
                  type: (d.type as 'compliance' | 'renewal' | 'audit' | 'review') || 'review',
                  dueDate: new Date(d.date),
                  framework: undefined,
                  priority: d.days_remaining <= 7 ? 'critical' as const : 
                           d.days_remaining <= 30 ? 'high' as const : 'medium' as const,
                  description: undefined,
                  notificationEnabled: true,
                })),
                aiInsights: (userDashboard.ai_insights || []).map((insight) => ({
                  id: insight.id,
                  type: insight.type,
                  title: insight.title,
                  description: insight.description,
                  priority: insight.priority === 1 ? 'critical' as const :
                           insight.priority === 2 ? 'high' as const :
                           insight.priority === 3 ? 'medium' as const : 'low' as const,
                  framework: undefined,
                  actionable: !!insight.action,
                  suggestedActions: insight.action ? [insight.action.label] : undefined,
                  confidence: 0.8,
                  timestamp: new Date(insight.created_at),
                })),
              },
              false,
              'fetchDashboardData/success',
            );
          } catch (error: unknown) {
            set(
              {
                isLoading: false,
                error: 
                  error && typeof error === 'object' && 'detail' in error
                    ? (error as any).detail
                    : error && typeof error === 'object' && 'message' in error
                      ? (error as any).message
                      : 'Failed to fetch dashboard data',
              },
              false,
              'fetchDashboardData/error',
            );
          }
        },

        // Widget Configuration Actions
        updateWidgetConfig: (widgetId, config) => {
          set(
            (state) => ({
              widgets: state.widgets.map((widget) =>
                widget.id === widgetId ? { ...widget, ...config } : widget,
              ),
            }),
            false,
            'updateWidgetConfig',
          );
        },

        reorderWidgets: (widgets) => {
          set({ widgets }, false, 'reorderWidgets');
        },

        refreshWidget: async (widgetId) => {
          set(
            (state) => ({
              widgetLoading: { ...state.widgetLoading, [widgetId]: true },
              widgetErrors: { ...state.widgetErrors, [widgetId]: null },
            }),
            false,
            'refreshWidget/start',
          );

          try {
            // Refresh specific widget data based on widget type
            switch (widgetId) {
              case 'compliance-score':
                const userDashboardForWidget = await dashboardService.getUserDashboard();
                const metrics = userDashboardForWidget.stats;
                const complianceScore: ComplianceScore = {
                  overall_score: metrics.compliance_score || 0,
                  policy_score: (metrics as any).policy_score || 0,
                  implementation_score: (metrics as any).implementation_score || 0,
                  evidence_score: (metrics as any).evidence_score || 0,
                  trend: (metrics as any).compliance_trend || 'stable',
                  lastUpdated: new Date(),
                  domain_scores: (metrics as any).domain_scores || {},
                  control_scores: (metrics as any).control_scores || {},
                  breakdown: (metrics as any).framework_scores || [],
                };
                set({ complianceScore });
                break;

              case 'activity-feed':
                const dashboardDataForActivities = await dashboardService.getUserDashboard();
                const activities = dashboardDataForActivities.recent_activity;
                set({
                  activities: activities.map((activity: any) => ({
                    id: activity.id,
                    type: activity.type,
                    actor: {
                      id: activity.user_id,
                      name: activity.user_name || 'System',
                      avatar: activity.user_avatar,
                    },
                    action: activity.action,
                    target: activity.target,
                    timestamp: new Date(activity.timestamp),
                    metadata: activity.metadata,
                  })),
                });
                break;

              // Add other widget-specific refresh logic as needed
            }

            set(
              (state) => ({
                widgetLoading: { ...state.widgetLoading, [widgetId]: false },
              }),
              false,
              'refreshWidget/success',
            );
          } catch (error: unknown) {
            set(
              (state) => ({
                widgetLoading: { ...state.widgetLoading, [widgetId]: false },
                widgetErrors: {
                  ...state.widgetErrors,
                  [widgetId]: 
                    error && typeof error === 'object' && 'detail' in error
                      ? (error as any).detail
                      : error && typeof error === 'object' && 'message' in error
                        ? (error as any).message
                        : 'Refresh failed',
                },
              }),
              false,
              'refreshWidget/error',
            );
          }
        },

        // Data Setters
        setComplianceScore: (complianceScore) =>
          set({ complianceScore }, false, 'setComplianceScore'),
        setTasks: (tasks) => set({ tasks }, false, 'setTasks'),
        setActivities: (activities) => set({ activities }, false, 'setActivities'),
        setFrameworks: (frameworks) => set({ frameworks }, false, 'setFrameworks'),
        setDeadlines: (deadlines) => set({ deadlines }, false, 'setDeadlines'),
        setAIInsights: (aiInsights) => set({ aiInsights }, false, 'setAIInsights'),

        // Widget Management
        addWidget: (widget) => {
          set(
            (state) => ({
              widgets: [...state.widgets, widget],
            }),
            false,
            'addWidget',
          );
        },

        removeWidget: (widgetId) => {
          set(
            (state) => ({
              widgets: state.widgets.filter((widget) => widget.id !== widgetId),
            }),
            false,
            'removeWidget',
          );
        },

        toggleWidgetVisibility: (widgetId) => {
          set(
            (state) => ({
              widgets: state.widgets.map((widget) =>
                widget.id === widgetId ? { ...widget, isVisible: !widget.isVisible } : widget,
              ),
            }),
            false,
            'toggleWidgetVisibility',
          );
        },

        resetWidgets: () => {
          set({ widgets: defaultWidgets }, false, 'resetWidgets');
        },

        // Test Compatibility Methods
        setWidgets: (widgets) => {
          const validatedWidgets = safeValidate(WidgetsArraySchema, widgets, 'setWidgets');
          set({ widgets: validatedWidgets }, false, 'setWidgets');
        },

        setMetrics: (metrics) => {
          const validatedMetrics = safeValidate(MetricsSchema, metrics, 'setMetrics');
          set({ metrics: validatedMetrics }, false, 'setMetrics');
        },

        setLoading: (loading) => {
          const validatedLoading = safeValidate(LoadingStateSchema, loading, 'setLoading');
          set({ isLoading: validatedLoading }, false, 'setLoading');
        },

        // Widget-specific loading actions
        setWidgetLoading: (widgetId, loading) => {
          set(
            (state) => ({
              widgetLoading: { ...state.widgetLoading, [widgetId]: loading },
            }),
            false,
            'setWidgetLoading',
          );
        },

        setWidgetError: (widgetId, error) => {
          set(
            (state) => ({
              widgetErrors: { ...state.widgetErrors, [widgetId]: error },
            }),
            false,
            'setWidgetError',
          );
        },

        clearAllErrors: () => {
          set({ error: null, widgetErrors: {} }, false, 'clearAllErrors');
        },
      }),
      {
        name: 'ruleiq-dashboard-storage',
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          // Only persist widget configuration, not data
          widgets: state.widgets,
        }),
        skipHydration: true,
      },
    ),
    {
      name: 'dashboard-store',
    },
  ),
);

// Selector hooks for specific state slices
export const useComplianceScore = () => useDashboardStore((state) => state.complianceScore);
export const useTasks = () => useDashboardStore((state) => state.tasks);
export const useActivities = () => useDashboardStore((state) => state.activities);
export const useFrameworks = () => useDashboardStore((state) => state.frameworks);
export const useDeadlines = () => useDashboardStore((state) => state.deadlines);
export const useAIInsights = () => useDashboardStore((state) => state.aiInsights);
export const useWidgets = () => useDashboardStore((state) => state.widgets);
export const useDashboardLoading = () =>
  useDashboardStore((state) => ({
    isLoading: state.isLoading,
    widgetLoading: state.widgetLoading,
    error: state.error,
    widgetErrors: state.widgetErrors,
  }));
