import { apiClient } from './client';

import type { 
  EvidenceCollectionPlan, 
  EvidenceTask,
  CollectionPlanSummary
} from '@/types/api';

export interface CreateCollectionPlanRequest {
  framework: string;
  target_completion_weeks?: number;
  include_existing_evidence?: boolean;
}

export interface TaskStatusUpdateRequest {
  status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'cancelled';
  completion_notes?: string;
}

export interface AutomationRecommendationsResponse {
  framework: string;
  automation_opportunities: Array<{
    evidence_type: string;
    automation_level: string;
    effort_reduction: string;
    success_rate: string;
    recommended_tools: string[];
  }>;
  recommended_tools: string[];
  estimated_time_savings: number;
}

class EvidenceCollectionService {
  /**
   * Create an AI-driven evidence collection plan
   */
  async createCollectionPlan(data: CreateCollectionPlanRequest): Promise<EvidenceCollectionPlan> {
    const response = await apiClient.post<EvidenceCollectionPlan>(
      '/evidence-collection/plans',
      data
    );
    return response.data;
  }

  /**
   * Get a specific collection plan by ID
   */
  async getCollectionPlan(planId: string): Promise<EvidenceCollectionPlan> {
    const response = await apiClient.get<EvidenceCollectionPlan>(
      `/evidence-collection/plans/${planId}`
    );
    return response.data;
  }

  /**
   * List all collection plans for the current user
   */
  async listCollectionPlans(params?: {
    framework?: string;
    status?: string;
  }): Promise<CollectionPlanSummary[]> {
    const response = await apiClient.get<CollectionPlanSummary[]>(
      '/evidence-collection/plans',
      { params }
    );
    return response.data;
  }

  /**
   * Get priority tasks for a collection plan
   */
  async getPriorityTasks(planId: string, limit: number = 5): Promise<EvidenceTask[]> {
    const response = await apiClient.get<EvidenceTask[]>(
      `/evidence-collection/plans/${planId}/priority-tasks`,
      { params: { limit } }
    );
    return response.data;
  }

  /**
   * Update task status
   */
  async updateTaskStatus(
    planId: string,
    taskId: string,
    data: TaskStatusUpdateRequest
  ): Promise<EvidenceTask> {
    const response = await apiClient.patch<EvidenceTask>(
      `/evidence-collection/plans/${planId}/tasks/${taskId}`,
      data
    );
    return response.data;
  }

  /**
   * Get automation recommendations for a framework
   */
  async getAutomationRecommendations(framework: string): Promise<AutomationRecommendationsResponse> {
    const response = await apiClient.get<AutomationRecommendationsResponse>(
      `/evidence-collection/automation-recommendations/${framework}`
    );
    return response.data;
  }

  /**
   * Calculate estimated time savings for a collection plan
   */
  calculateTimeSavings(plan: EvidenceCollectionPlan): {
    manualHours: number;
    automatedHours: number;
    savedHours: number;
    savedPercentage: number;
  } {
    const manualHours = plan.estimated_total_hours;
    const savedHours = plan.automation_opportunities.effort_savings_hours;
    const automatedHours = manualHours - savedHours;
    const savedPercentage = plan.automation_opportunities.effort_savings_percentage;

    return {
      manualHours,
      automatedHours,
      savedHours,
      savedPercentage
    };
  }

  /**
   * Get task statistics for a collection plan
   */
  getTaskStatistics(plan: EvidenceCollectionPlan): {
    total: number;
    byStatus: Record<string, number>;
    byPriority: Record<string, number>;
    byAutomationLevel: Record<string, number>;
    completionPercentage: number;
  } {
    const stats = {
      total: plan.tasks.length,
      byStatus: {} as Record<string, number>,
      byPriority: {} as Record<string, number>,
      byAutomationLevel: {} as Record<string, number>,
      completionPercentage: 0
    };

    plan.tasks.forEach(task => {
      // Count by status
      stats.byStatus[task.status] = (stats.byStatus[task.status] || 0) + 1;
      
      // Count by priority
      stats.byPriority[task.priority] = (stats.byPriority[task.priority] || 0) + 1;
      
      // Count by automation level
      stats.byAutomationLevel[task.automation_level] = 
        (stats.byAutomationLevel[task.automation_level] || 0) + 1;
    });

    // Calculate completion percentage
    const completedTasks = stats.byStatus['completed'] || 0;
    stats.completionPercentage = Math.round((completedTasks / stats.total) * 100);

    return stats;
  }

  /**
   * Filter tasks by various criteria
   */
  filterTasks(
    tasks: EvidenceTask[],
    criteria: {
      priority?: string[];
      status?: string[];
      automationLevel?: string[];
      evidenceType?: string[];
    }
  ): EvidenceTask[] {
    return tasks.filter(task => {
      if (criteria.priority && !criteria.priority.includes(task.priority)) {
        return false;
      }
      if (criteria.status && !criteria.status.includes(task.status)) {
        return false;
      }
      if (criteria.automationLevel && !criteria.automationLevel.includes(task.automation_level)) {
        return false;
      }
      if (criteria.evidenceType && !criteria.evidenceType.includes(task.evidence_type)) {
        return false;
      }
      return true;
    });
  }

  /**
   * Sort tasks by different criteria
   */
  sortTasks(
    tasks: EvidenceTask[],
    sortBy: 'priority' | 'dueDate' | 'effort' | 'status',
    order: 'asc' | 'desc' = 'asc'
  ): EvidenceTask[] {
    const sorted = [...tasks].sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'priority':
          const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3, deferred: 4 };
          comparison = priorityOrder[a.priority] - priorityOrder[b.priority];
          break;
        
        case 'dueDate':
          if (!a.due_date) return 1;
          if (!b.due_date) return -1;
          comparison = new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
          break;
        
        case 'effort':
          comparison = a.estimated_effort_hours - b.estimated_effort_hours;
          break;
        
        case 'status':
          const statusOrder = { pending: 0, in_progress: 1, blocked: 2, completed: 3, cancelled: 4 };
          comparison = statusOrder[a.status] - statusOrder[b.status];
          break;
      }

      return order === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }
}

export const evidenceCollectionService = new EvidenceCollectionService();