import apiClient from "@/lib/api-client"
import type { AssessmentQuestion, AssessmentAnswer, AssessmentResult } from "@/types/api"

// Assessment Session types matching backend
export interface AssessmentSession {
  id: string
  user_id: string
  business_profile_id?: string
  session_type: string
  status: string
  current_stage: number
  total_stages: number
  responses: Record<string, any>
  recommendations: any[]
  started_at: string
  completed_at?: string
}

export interface AssessmentSessionCreate {
  business_profile_id?: string
  session_type?: string
}

export const assessmentsApi = {
  // Assessment Sessions (matching backend endpoints)
  createSession: async (data: AssessmentSessionCreate = {}): Promise<AssessmentSession> => {
    const response = await apiClient.post("/assessments/", {
      session_type: "compliance_scoping",
      ...data
    })
    return response.data
  },

  startSession: async (data: AssessmentSessionCreate = {}): Promise<AssessmentSession> => {
    const response = await apiClient.post("/assessments/start", {
      session_type: "compliance_scoping",
      ...data
    })
    return response.data
  },

  getCurrentSession: async (): Promise<AssessmentSession> => {
    const response = await apiClient.get("/assessments/current")
    return response.data
  },

  // Questions (matching backend endpoints)
  getQuestions: async (stage: number): Promise<AssessmentQuestion[]> => {
    const response = await apiClient.get(`/assessments/questions/${stage}`)
    return response.data
  },

  // Responses (matching backend endpoints)
  submitResponse: async (
    sessionId: string,
    questionId: string,
    response: any
  ): Promise<AssessmentSession> => {
    const apiResponse = await apiClient.post(`/assessments/${sessionId}/responses`, {
      question_id: questionId,
      response: response
    })
    return apiResponse.data
  },

  // Recommendations (matching backend endpoints)
  getRecommendations: async (sessionId: string): Promise<any> => {
    const response = await apiClient.get(`/assessments/${sessionId}/recommendations`)
    return response.data
  },

  // Complete assessment
  completeAssessment: async (sessionId: string): Promise<AssessmentSession> => {
    const response = await apiClient.post(`/assessments/${sessionId}/complete`)
    return response.data
  },
}
