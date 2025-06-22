import apiClient from "@/lib/api-client"

// Framework types matching backend
export interface ComplianceFramework {
  id: string
  name: string
  description: string
  category: string
  version?: string
  controls: Array<{
    name: string
    description: string
  }>
}

export interface FrameworkRecommendation {
  framework: ComplianceFramework
  relevance_score: number
  reasons: string[]
  priority: string
}

export const frameworksApi = {
  // Get all available frameworks
  getFrameworks: async (): Promise<ComplianceFramework[]> => {
    const response = await apiClient.get("/frameworks/")
    return response.data
  },

  // Get specific framework details
  getFramework: async (frameworkId: string): Promise<ComplianceFramework> => {
    const response = await apiClient.get(`/frameworks/${frameworkId}`)
    return response.data
  },

  // Get framework recommendations for user
  getRecommendations: async (): Promise<FrameworkRecommendation[]> => {
    const response = await apiClient.get("/frameworks/recommendations")
    return response.data
  },

  // Get framework recommendations for specific business profile
  getRecommendationsForProfile: async (businessProfileId: string): Promise<FrameworkRecommendation[]> => {
    const response = await apiClient.get(`/frameworks/recommendations/${businessProfileId}`)
    return response.data
  },
}
