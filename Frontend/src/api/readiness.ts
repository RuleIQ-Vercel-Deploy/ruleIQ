import apiClient from "@/lib/api-client"

// Readiness types matching backend
export interface ReadinessAssessment {
  id: string
  user_id: string
  framework_id: string
  business_profile_id: string
  overall_score: number
  score_breakdown: {
    policy: number
    implementation: number
    evidence: number
  }
  framework_scores: {
    policy: number
    implementation: number
    evidence: number
  }
  risk_level: string
  priority_actions: string[]
  quick_wins: string[]
  recommendations: string[]
  score_trend?: string
  estimated_readiness_date?: string
  created_at: string
  updated_at: string
}

export interface ComplianceReport {
  framework: string
  report_type: string
  format: string
  include_evidence: boolean
  include_recommendations: boolean
  title?: string
}

export interface ComplianceReportResponse {
  report_id: string
  status: string
  download_url: string
  title: string
  format: string
}

export const readinessApi = {
  // Get readiness assessment
  getAssessment: async (frameworkId?: string): Promise<ReadinessAssessment> => {
    const params = frameworkId ? `?framework_id=${frameworkId}` : ""
    const response = await apiClient.get(`/readiness/assessment${params}`)
    return response.data
  },

  // Generate compliance report
  generateReport: async (reportConfig: ComplianceReport): Promise<ComplianceReportResponse> => {
    const response = await apiClient.post("/readiness/reports", reportConfig)
    return response.data
  },

  // Generate compliance report (legacy endpoint)
  generateReportLegacy: async (reportConfig: ComplianceReport): Promise<any> => {
    const response = await apiClient.post("/readiness/report", reportConfig)
    return response.data
  },
}
