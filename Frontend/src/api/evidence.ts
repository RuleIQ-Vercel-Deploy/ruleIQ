import apiClient from "@/lib/api-client"

// Evidence types matching backend
export interface EvidenceItem {
  id: string
  title: string
  description?: string
  control_id: string
  framework_id: string
  business_profile_id: string
  source: string
  tags?: string[]
  evidence_type: string
  status: string
  quality_score?: number
  created_at: string
  updated_at: string
}

export interface EvidenceCreate {
  title: string
  description?: string
  control_id: string
  framework_id: string
  business_profile_id?: string
  source?: string
  tags?: string[]
  evidence_type?: string
}

export interface EvidenceUpdate {
  title?: string
  description?: string
  status?: string
  tags?: string[]
}

export interface EvidenceRequirement {
  control_id: string
  evidence_type: string
  title: string
  description: string
  automation_possible: boolean
}

export interface EvidenceRequirementsResponse {
  requirements: EvidenceRequirement[]
}

export const evidenceApi = {
  // Get evidence requirements for a framework
  getRequirements: async (frameworkId: string): Promise<EvidenceRequirement[]> => {
    const response = await apiClient.get(`/evidence/requirements?framework_id=${frameworkId}`)
    const data = response.data as EvidenceRequirementsResponse
    return data.requirements
  },

  // Create new evidence item
  createEvidence: async (data: EvidenceCreate): Promise<EvidenceItem> => {
    const response = await apiClient.post("/evidence/", data)
    return response.data
  },

  // Get all evidence items for user
  getEvidence: async (): Promise<EvidenceItem[]> => {
    const response = await apiClient.get("/evidence/")
    return response.data
  },

  // Get specific evidence item
  getEvidenceItem: async (evidenceId: string): Promise<EvidenceItem> => {
    const response = await apiClient.get(`/evidence/${evidenceId}`)
    return response.data
  },

  // Update evidence item
  updateEvidence: async (evidenceId: string, data: EvidenceUpdate): Promise<EvidenceItem> => {
    const response = await apiClient.put(`/evidence/${evidenceId}`, data)
    return response.data
  },

  // Update evidence status
  updateEvidenceStatus: async (evidenceId: string, data: EvidenceUpdate): Promise<EvidenceItem> => {
    const response = await apiClient.patch(`/evidence/${evidenceId}`, data)
    return response.data
  },

  // Delete evidence item
  deleteEvidence: async (evidenceId: string): Promise<void> => {
    await apiClient.delete(`/evidence/${evidenceId}`)
  },
}
