import { apiClient } from './client';

export interface ImplementationPlan {
  id: string;
  business_profile_id: string;
  framework_id: string;
  framework_name: string;
  status: 'draft' | 'active' | 'completed' | 'on_hold';
  start_date: string;
  target_completion_date: string;
  actual_completion_date?: string;
  overall_progress: number;
  phases: ImplementationPhase[];
  created_at: string;
  updated_at: string;
}

export interface ImplementationPhase {
  id: string;
  phase_number: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  progress: number;
  status: 'not_started' | 'in_progress' | 'completed' | 'blocked';
  tasks: ImplementationTask[];
  deliverables: string[];
  milestones: ImplementationMilestone[];
}

export interface ImplementationTask {
  id: string;
  title: string;
  description: string;
  assigned_to?: string;
  start_date: string;
  due_date: string;
  effort_hours: number;
  progress: number;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  dependencies: string[];
  blockers?: string[];
}

export interface ImplementationMilestone {
  id: string;
  name: string;
  date: string;
  achieved: boolean;
  achieved_date?: string;
  criteria: string[];
}

export interface CreateImplementationPlanRequest {
  business_profile_id: string;
  framework_id: string;
  start_date?: string;
  target_duration_weeks?: number;
  priority_areas?: string[];
}

class ImplementationService {
  /**
   * Get all implementation plans
   */
  async getImplementationPlans(params?: {
    business_profile_id?: string;
    framework_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ plans: ImplementationPlan[]; total: number }> {
    const response = await apiClient.get<{ plans: ImplementationPlan[]; total: number }>(
      '/implementation/plans',
      { params },
    );
    return response.data;
  }

  /**
   * Get a specific implementation plan
   */
  async getImplementationPlan(planId: string): Promise<ImplementationPlan> {
    const response = await apiClient.get<ImplementationPlan>(`/implementation/plans/${planId}`);
    return response.data;
  }

  /**
   * Create implementation plan
   */
  async createImplementationPlan(
    data: CreateImplementationPlanRequest,
  ): Promise<ImplementationPlan> {
    const response = await apiClient.post<ImplementationPlan>('/implementation/plans', data);
    return response.data;
  }

  /**
   * Update implementation plan
   */
  async updateImplementationPlan(
    planId: string,
    data: Partial<ImplementationPlan>,
  ): Promise<ImplementationPlan> {
    const response = await apiClient.patch<ImplementationPlan>(
      `/implementation/plans/${planId}`,
      data,
    );
    return response.data;
  }

  /**
   * Update task progress
   */
  async updateTaskProgress(
    planId: string,
    taskId: string,
    progress: number,
    notes?: string,
  ): Promise<ImplementationTask> {
    const response = await apiClient.patch<ImplementationTask>(
      `/implementation/plans/${planId}/tasks/${taskId}/progress`,
      { progress, notes },
    );
    return response.data;
  }

  /**
   * Complete a milestone
   */
  async completeMilestone(
    planId: string,
    milestoneId: string,
    evidence?: string[],
  ): Promise<ImplementationMilestone> {
    const response = await apiClient.post<ImplementationMilestone>(
      `/implementation/plans/${planId}/milestones/${milestoneId}/complete`,
      { evidence },
    );
    return response.data;
  }

  /**
   * Get implementation recommendations
   */
  async getImplementationRecommendations(
    businessProfileId: string,
    frameworkId: string,
  ): Promise<{
    recommended_approach: 'phased' | 'big_bang' | 'hybrid';
    estimated_duration: string;
    resource_requirements: {
      internal_team_size: number;
      external_support_needed: boolean;
      key_roles: string[];
      estimated_budget: string;
    };
    priority_controls: Array<{
      control_id: string;
      control_name: string;
      reason: string;
      quick_win: boolean;
    }>;
    risk_factors: string[];
    success_factors: string[];
  }> {
    const response = await apiClient.get<any>('/implementation/recommendations', {
      params: { business_profile_id: businessProfileId, framework_id: frameworkId },
    });
    return response.data;
  }

  /**
   * Get implementation resources
   */
  async getImplementationResources(frameworkId: string): Promise<{
    templates: Array<{
      id: string;
      name: string;
      type: string;
      download_url: string;
    }>;
    guides: Array<{
      id: string;
      title: string;
      category: string;
      url: string;
    }>;
    tools: Array<{
      id: string;
      name: string;
      description: string;
      type: 'free' | 'paid';
      url: string;
    }>;
    training: Array<{
      id: string;
      title: string;
      provider: string;
      duration: string;
      cost: string;
      url: string;
    }>;
  }> {
    const response = await apiClient.get<any>(`/implementation/resources/${frameworkId}`);
    return response.data;
  }

  /**
   * Export implementation plan
   */
  async exportImplementationPlan(
    planId: string,
    format: 'pdf' | 'excel' | 'project',
  ): Promise<void> {
    await apiClient.download(
      `/implementation/plans/${planId}/export?format=${format}`,
      `implementation-plan-${planId}.${format === 'project' ? 'mpp' : format}`,
    );
  }

  /**
   * Get implementation analytics
   */
  async getImplementationAnalytics(planId: string): Promise<{
    burndown_chart: Array<{
      date: string;
      planned_remaining: number;
      actual_remaining: number;
    }>;
    velocity_trend: Array<{
      week: string;
      completed_tasks: number;
      average_velocity: number;
    }>;
    bottlenecks: Array<{
      area: string;
      impact: 'high' | 'medium' | 'low';
      affected_tasks: number;
      recommendation: string;
    }>;
    projected_completion: {
      current_pace_date: string;
      confidence_level: number;
      risks: string[];
    };
  }> {
    const response = await apiClient.get<any>(`/implementation/plans/${planId}/analytics`);
    return response.data;
  }
}

export const implementationService = new ImplementationService();
