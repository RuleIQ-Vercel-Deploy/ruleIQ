import apiClient from "@/lib/api-client"
import type { BusinessProfile } from "@/lib/types/api"

export interface BusinessProfileCreateInput {
  company_name: string
  industry: string
  employee_count: number
  annual_revenue?: string
  country?: string
  data_sensitivity?: "Low" | "Moderate" | "High" | "Confidential"
  handles_personal_data?: boolean
  processes_payments?: boolean
  stores_health_data?: boolean
  provides_financial_services?: boolean
  operates_critical_infrastructure?: boolean
  has_international_operations?: boolean
  existing_frameworks?: string[]
  planned_frameworks?: string[]
  cloud_providers?: string[]
  saas_tools?: string[]
  development_tools?: string[]
  compliance_budget?: number
  compliance_timeline?: string
}

export interface BusinessProfileUpdateInput {
  company_name?: string
  industry?: string
  employee_count?: number
  annual_revenue?: string
  country?: string
  data_sensitivity?: "Low" | "Moderate" | "High" | "Confidential"
  handles_personal_data?: boolean
  processes_payments?: boolean
  stores_health_data?: boolean
  provides_financial_services?: boolean
  operates_critical_infrastructure?: boolean
  has_international_operations?: boolean
  existing_frameworks?: string[]
  planned_frameworks?: string[]
  cloud_providers?: string[]
  saas_tools?: string[]
  development_tools?: string[]
  compliance_budget?: number
  compliance_timeline?: string
}

export const businessProfileApi = {
  // Create or update business profile (backend handles both cases)
  createOrUpdate: async (data: BusinessProfileCreateInput): Promise<BusinessProfile> => {
    const response = await apiClient.post("/business-profiles/", data)
    return response.data
  },

  // Get current user's business profile
  get: async (): Promise<BusinessProfile> => {
    const response = await apiClient.get("/business-profiles/")
    return response.data
  },

  // Get business profile by ID
  getById: async (profileId: string): Promise<BusinessProfile> => {
    const response = await apiClient.get(`/business-profiles/${profileId}/`)
    return response.data
  },

  // Update business profile
  update: async (data: BusinessProfileUpdateInput): Promise<BusinessProfile> => {
    const response = await apiClient.put("/business-profiles/", data)
    return response.data
  },

  // Update business profile by ID
  updateById: async (profileId: string, data: BusinessProfileUpdateInput): Promise<BusinessProfile> => {
    const response = await apiClient.put(`/business-profiles/${profileId}/`, data)
    return response.data
  },

  // Partial update (PATCH)
  patch: async (profileId: string, data: Partial<BusinessProfileUpdateInput>): Promise<BusinessProfile> => {
    const response = await apiClient.patch(`/business-profiles/${profileId}/`, data)
    return response.data
  },

  // Delete business profile
  delete: async (profileId: string): Promise<void> => {
    await apiClient.delete(`/business-profiles/${profileId}/`)
  }
}

// Industry options for the form
export const INDUSTRY_OPTIONS = [
  "Technology",
  "Healthcare",
  "Financial Services",
  "Education",
  "Government",
  "Manufacturing",
  "Retail",
  "Professional Services",
  "Non-profit",
  "Energy",
  "Transportation",
  "Real Estate",
  "Media & Entertainment",
  "Telecommunications",
  "Agriculture",
  "Construction",
  "Hospitality",
  "Other"
]

// Employee count ranges
export const EMPLOYEE_COUNT_RANGES = [
  { label: "1-10", value: 5 },
  { label: "11-50", value: 30 },
  { label: "51-200", value: 125 },
  { label: "201-500", value: 350 },
  { label: "501-1000", value: 750 },
  { label: "1001-5000", value: 3000 },
  { label: "5000+", value: 10000 }
]

// Annual revenue ranges (UK focused)
export const ANNUAL_REVENUE_OPTIONS = [
  "Under £1M",
  "£1M-£5M",
  "£5M-£25M",
  "£25M-£100M",
  "£100M-£500M",
  "Over £500M"
]

// Countries (can be expanded)
export const COUNTRY_OPTIONS = [
  "United Kingdom",
  "United States",
  "Canada",
  "Australia",
  "Germany",
  "France",
  "Netherlands",
  "Ireland",
  "Other"
]

// Data sensitivity levels
export const DATA_SENSITIVITY_OPTIONS = [
  { value: "Low", label: "Low - Public information only" },
  { value: "Moderate", label: "Moderate - Internal business data" },
  { value: "High", label: "High - Sensitive customer data" },
  { value: "Confidential", label: "Confidential - Highly regulated data" }
]

// Common compliance frameworks
export const COMPLIANCE_FRAMEWORKS = [
  "GDPR",
  "SOC 2",
  "ISO 27001",
  "HIPAA",
  "PCI DSS",
  "NIST",
  "FedRAMP",
  "CCPA",
  "UK GDPR",
  "Cyber Essentials",
  "Other"
]

// Cloud providers
export const CLOUD_PROVIDERS = [
  "AWS",
  "Microsoft Azure",
  "Google Cloud Platform",
  "IBM Cloud",
  "Oracle Cloud",
  "DigitalOcean",
  "Linode",
  "Other"
]

// Common SaaS tools
export const SAAS_TOOLS = [
  "Microsoft 365",
  "Google Workspace",
  "Salesforce",
  "HubSpot",
  "Slack",
  "Zoom",
  "Atlassian (Jira/Confluence)",
  "Notion",
  "Asana",
  "Trello",
  "Other"
]

// Development tools
export const DEVELOPMENT_TOOLS = [
  "GitHub",
  "GitLab",
  "Bitbucket",
  "Azure DevOps",
  "Jenkins",
  "Docker",
  "Kubernetes",
  "Terraform",
  "Other"
]

// Compliance timeline options
export const COMPLIANCE_TIMELINE_OPTIONS = [
  "3 months",
  "6 months",
  "12 months",
  "18 months",
  "24 months",
  "Ongoing"
]
