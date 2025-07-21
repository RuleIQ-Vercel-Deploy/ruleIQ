import { apiClient } from './client';

export interface DashboardStats {
  compliance_score: number;
  frameworks_active: number;
  policies_approved: number;
  evidence_collected: number;
  assessments_completed: number;
  tasks_pending: number;
  upcoming_deadlines: number;
  risk_items: number;
}

export interface DashboardActivity {
  id: string;
  timestamp: string;
  type: 'assessment' | 'evidence' | 'policy' | 'task' | 'system';
  action: string;
  description: string;
  user?: string;
  metadata?: any;
}

export interface DashboardTask {
  id: string;
  title: string;
  type: 'compliance' | 'evidence' | 'assessment' | 'review';
  priority: 'critical' | 'high' | 'medium' | 'low';
  due_date?: string;
  assigned_to?: string;
  framework?: string;
  status: 'pending' | 'in_progress' | 'blocked';
}

export interface DashboardInsight {
  id: string;
  type: 'tip' | 'recommendation' | 'risk-alert' | 'optimization';
  title: string;
  description: string;
  action?: {
    label: string;
    route: string;
  };
  priority: number;
  dismissible: boolean;
  created_at: string;
}

export interface FrameworkProgress {
  framework_id: string;
  framework_name: string;
  compliance_percentage: number;
  controls_total: number;
  controls_compliant: number;
  controls_in_progress: number;
  last_assessment_date?: string;
  next_review_date?: string;
  trend: 'improving' | 'stable' | 'declining';
}

class DashboardService {
  /**
   * Get user dashboard data
   */
  async getUserDashboard(): Promise<{
    stats: DashboardStats;
    recent_activity: DashboardActivity[];
    pending_tasks: DashboardTask[];
    ai_insights: DashboardInsight[];
    framework_progress: FrameworkProgress[];
    upcoming_deadlines: Array<{
      date: string;
      title: string;
      type: string;
      days_remaining: number;
    }>;
    compliance_trends: Array<{
      date: string;
      score: number;
    }>;
  }> {
    const response = await apiClient.get<any>('/dashboard');
    return response.data;
  }

  /**
   * Get dashboard widgets configuration
   */
  async getDashboardWidgets(): Promise<{
    widgets: Array<{
      id: string;
      type: string;
      title: string;
      position: { x: number; y: number; w: number; h: number };
      config: any;
      visible: boolean;
    }>;
  }> {
    const response = await apiClient.get<any>('/dashboard/widgets');
    return response.data;
  }

  /**
   * Update dashboard widgets configuration
   */
  async updateDashboardWidgets(widgets: any[]): Promise<void> {
    await apiClient.put('/dashboard/widgets', { widgets });
  }

  /**
   * Dismiss an AI insight
   */
  async dismissInsight(insightId: string): Promise<void> {
    await apiClient.post(`/dashboard/insights/${insightId}/dismiss`);
  }

  /**
   * Bookmark an AI insight
   */
  async bookmarkInsight(insightId: string): Promise<void> {
    await apiClient.post(`/dashboard/insights/${insightId}/bookmark`);
  }

  /**
   * Get dashboard notifications
   */
  async getDashboardNotifications(params?: {
    unread_only?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<{
    notifications: Array<{
      id: string;
      type: string;
      title: string;
      message: string;
      read: boolean;
      created_at: string;
      action_url?: string;
    }>;
    unread_count: number;
    total: number;
  }> {
    const response = await apiClient.get<any>('/dashboard/notifications', { params });
    return response.data;
  }

  /**
   * Mark notification as read
   */
  async markNotificationAsRead(notificationId: string): Promise<void> {
    await apiClient.patch(`/dashboard/notifications/${notificationId}/read`);
  }

  /**
   * Mark all notifications as read
   */
  async markAllNotificationsAsRead(): Promise<void> {
    await apiClient.post('/dashboard/notifications/read-all');
  }

  /**
   * Get quick actions
   */
  async getQuickActions(): Promise<{
    actions: Array<{
      id: string;
      label: string;
      icon: string;
      route: string;
      color: string;
      description: string;
      enabled: boolean;
    }>;
  }> {
    const response = await apiClient.get<any>('/dashboard/quick-actions');
    return response.data;
  }

  /**
   * Get dashboard export
   */
  async exportDashboard(format: 'pdf' | 'excel'): Promise<void> {
    await apiClient.download(
      `/dashboard/export?format=${format}`,
      `dashboard-${new Date().toISOString().split('T')[0]}.${format}`,
    );
  }

  /**
   * Get personalized recommendations
   */
  async getPersonalizedRecommendations(): Promise<{
    recommendations: Array<{
      id: string;
      category: 'compliance' | 'efficiency' | 'risk' | 'cost';
      title: string;
      description: string;
      impact: 'high' | 'medium' | 'low';
      effort: 'high' | 'medium' | 'low';
      savings_potential?: string;
      action_steps: string[];
    }>;
  }> {
    const response = await apiClient.get<any>('/dashboard/recommendations');
    return response.data;
  }

  /**
   * Mock dashboard data for development
   */

  /**
   * Mock widgets data for development
   */
}

export const dashboardService = new DashboardService();
