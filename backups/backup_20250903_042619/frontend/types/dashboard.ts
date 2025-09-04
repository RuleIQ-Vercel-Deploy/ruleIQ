// Dashboard type definitions

export interface DashboardInsight {
  id: string;
  type: 'tip' | 'recommendation' | 'risk-alert' | 'optimization';
  title: string;
  description: string;
  priority: number;
  created_at: string;
  dismissible: boolean;
  action?: {
    label: string;
    route: string;
  };
}

export interface ComplianceTrend {
  date: string;
  score: number;
  target?: number;
}

export interface FrameworkScore {
  framework: string;
  score: number;
}

export interface PendingTask {
  id: string;
  title: string;
  description?: string;
  priority: 'high' | 'medium' | 'low';
  dueDate?: string;
  category: string;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface DashboardTask {
  id: string;
  title: string;
  description?: string;
  type: 'evidence' | 'assessment' | 'compliance' | 'review';
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed';
  due_date?: string;
  framework?: string;
  assigned_to?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DashboardData {
  compliance_score: number;
  active_alerts: number;
  ai_insights_count: number;
  tasks_completed: number;
  total_tasks: number;
  insights: DashboardInsight[];
  compliance_trends: ComplianceTrend[];
  framework_scores: Record<string, number>;
  pending_tasks: PendingTask[];
  recent_activity: unknown[];
  task_progress?: unknown[];
  risks?: unknown[];
  activity_data?: unknown[];
}
