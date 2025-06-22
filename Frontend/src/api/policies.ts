import apiClient from "@/lib/api-client"

// Policy types matching backend
export interface GeneratedPolicy {
  id: string
  policy_name: string
  content: string
  status: string
  created_at: string
}

export interface PolicyGenerateRequest {
  framework_id: string
  policy_type?: string
  custom_requirements?: string[]
}

export interface PolicyListResponse {
  policies: GeneratedPolicy[]
}

export const policiesApi = {
  // Generate new policy
  generatePolicy: async (request: PolicyGenerateRequest): Promise<GeneratedPolicy> => {
    const response = await apiClient.post("/policies/generate", request)
    return response.data
  },

  // Get all generated policies for user
  getPolicies: async (): Promise<GeneratedPolicy[]> => {
    const response = await apiClient.get("/policies/")
    const data = response.data as PolicyListResponse
    return data.policies
  },

  // Get specific policy
  getPolicy: async (policyId: string): Promise<GeneratedPolicy> => {
    const response = await apiClient.get(`/policies/${policyId}`)
    return response.data
  },

  // Update policy status
  updatePolicyStatus: async (policyId: string, status: string): Promise<GeneratedPolicy> => {
    const response = await apiClient.patch(`/policies/${policyId}/status`, { status })
    return response.data
  },

  // Delete policy
  deletePolicy: async (policyId: string): Promise<void> => {
    await apiClient.delete(`/policies/${policyId}`)
  },
}
