import apiClient from "@/lib/api-client"

// Implementation types matching backend
export interface ImplementationPlan {
  id: string
  user_id: string
  business_profile_id: string
  framework_id: string
  title: string
  status: string
  phases: Array<{
    name: string
    description: string
    tasks: Array<{
      id: string
      title: string
      description: string
      status: string
      priority: string
      estimated_hours: number
      assigned_to?: string
      due_date?: string
    }>
  }>
  planned_start_date?: string
  planned_end_date?: string
  actual_start_date?: string
  actual_end_date?: string
  created_at: string
  updated_at: string
}

export interface ImplementationPlanCreate {
  framework_id: string
  control_domain?: string
  timeline_weeks?: number
}

export interface ImplementationPlanListResponse {
  plans: ImplementationPlan[]
}

export const implementationApi = {
  // Generate new implementation plan
  generatePlan: async (request: ImplementationPlanCreate): Promise<ImplementationPlan> => {
    const response = await apiClient.post("/implementation/plans", request)
    return response.data
  },

  // Get all implementation plans for user
  getPlans: async (): Promise<ImplementationPlan[]> => {
    const response = await apiClient.get("/implementation/plans")
    const data = response.data as ImplementationPlanListResponse
    return data.plans
  },

  // Get specific implementation plan
  getPlan: async (planId: string): Promise<ImplementationPlan> => {
    const response = await apiClient.get(`/implementation/plans/${planId}`)
    return response.data
  },

  // Update task progress
  updateTaskProgress: async (
    planId: string, 
    taskId: string, 
    progress: { status?: string; progress?: number; notes?: string }
  ): Promise<{ message: string; plan_id: string; task_id: string }> => {
    const response = await apiClient.patch(`/implementation/plans/${planId}/tasks/${taskId}`, progress)
    return response.data
  },

  // Delete implementation plan
  deletePlan: async (planId: string): Promise<void> => {
    await apiClient.delete(`/implementation/plans/${planId}`)
  },
}
