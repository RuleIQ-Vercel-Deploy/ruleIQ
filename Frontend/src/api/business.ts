import apiClient from "@/lib/api-client"
import type { BusinessProfile } from "@/types/api"

// Business Profile Input type matching backend schema
export interface BusinessProfileInput {
  company_name: string
  industry: string
  employee_count: number
  annual_revenue?: string
  country?: string
  data_sensitivity?: "Low" | "Moderate" | "High" | "Confidential"
  handles_persona?: boolean  // handles_personal_data (truncated in backend)
  processes_payme?: boolean  // processes_payments (truncated in backend)
  stores_health_d?: boolean  // stores_health_data (truncated in backend)
  provides_financ?: boolean  // provides_financial_services (truncated in backend)
  operates_critic?: boolean  // operates_critical_infrastructure (truncated in backend)
  has_internation?: boolean  // has_international_operations (truncated in backend)
  cloud_providers?: string[]
  saas_tools?: string[]
  development_too?: string[]  // development_tools (truncated in backend)
  existing_framew?: string[]  // existing_frameworks (truncated in backend)
  planned_framewo?: string[]  // planned_frameworks (truncated in backend)
  compliance_budg?: string    // compliance_budget (truncated in backend)
  compliance_time?: string    // compliance_timeline (truncated in backend)
}

export const businessApi = {
  // Get current user's business profile
  getProfile: async (): Promise<BusinessProfile> => {
    const response = await apiClient.get("/business-profiles/")
    return response.data
  },

  // Create business profile for current user
  createProfile: async (data: BusinessProfileInput): Promise<BusinessProfile> => {
    const response = await apiClient.post("/business-profiles/", data)
    return response.data
  },

  // Update current user's business profile
  updateProfile: async (data: Partial<BusinessProfileInput>): Promise<BusinessProfile> => {
    const response = await apiClient.put("/business-profiles/", data)
    return response.data
  },
}
