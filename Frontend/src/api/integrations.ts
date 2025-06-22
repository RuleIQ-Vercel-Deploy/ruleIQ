import { apiClient } from "@/lib/api-client"
import type {
  Integration,
  IntegrationProvider,
  IntegrationLog,
  IntegrationSync,
  IntegrationAnalytics,
} from "@/types/api"

export const integrationsApi = {
  // Integration Providers
  getProviders: async (): Promise<IntegrationProvider[]> => {
    const response = await apiClient.get("/integrations/providers")
    return response.data
  },

  getProvider: async (providerId: string): Promise<IntegrationProvider> => {
    const response = await apiClient.get(`/integrations/providers/${providerId}`)
    return response.data
  },

  // Integrations Management
  getIntegrations: async (): Promise<Integration[]> => {
    const response = await apiClient.get("/integrations")
    return response.data
  },

  getIntegration: async (integrationId: string): Promise<Integration> => {
    const response = await apiClient.get(`/integrations/${integrationId}`)
    return response.data
  },

  createIntegration: async (data: {
    provider_id: string
    name: string
    config: Record<string, any>
  }): Promise<Integration> => {
    const response = await apiClient.post("/integrations", data)
    return response.data
  },

  updateIntegration: async (integrationId: string, data: Partial<Integration>): Promise<Integration> => {
    const response = await apiClient.put(`/integrations/${integrationId}`, data)
    return response.data
  },

  deleteIntegration: async (integrationId: string): Promise<void> => {
    await apiClient.delete(`/integrations/${integrationId}`)
  },

  // OAuth Flow
  initiateOAuth: async (providerId: string, redirectUri?: string): Promise<{ auth_url: string }> => {
    const response = await apiClient.post(`/integrations/oauth/initiate`, {
      provider_id: providerId,
      redirect_uri: redirectUri,
    })
    return response.data
  },

  completeOAuth: async (providerId: string, code: string, state?: string): Promise<Integration> => {
    const response = await apiClient.post(`/integrations/oauth/callback`, {
      provider_id: providerId,
      code,
      state,
    })
    return response.data
  },

  refreshOAuthToken: async (integrationId: string): Promise<Integration> => {
    const response = await apiClient.post(`/integrations/${integrationId}/refresh-token`)
    return response.data
  },

  // Connection Testing
  testConnection: async (
    integrationId: string,
  ): Promise<{
    success: boolean
    message: string
    details?: Record<string, any>
  }> => {
    const response = await apiClient.post(`/integrations/${integrationId}/test`)
    return response.data
  },

  // Data Sync
  triggerSync: async (
    integrationId: string,
    syncType: "full" | "incremental" = "incremental",
  ): Promise<IntegrationSync> => {
    const response = await apiClient.post(`/integrations/${integrationId}/sync`, {
      sync_type: syncType,
    })
    return response.data
  },

  getSyncHistory: async (integrationId: string): Promise<IntegrationSync[]> => {
    const response = await apiClient.get(`/integrations/${integrationId}/sync-history`)
    return response.data
  },

  getSyncStatus: async (syncId: string): Promise<IntegrationSync> => {
    const response = await apiClient.get(`/integrations/sync/${syncId}`)
    return response.data
  },

  cancelSync: async (syncId: string): Promise<void> => {
    await apiClient.post(`/integrations/sync/${syncId}/cancel`)
  },

  // Logs
  getLogs: async (
    integrationId: string,
    params?: {
      level?: string
      event_type?: string
      limit?: number
      offset?: number
    },
  ): Promise<IntegrationLog[]> => {
    const response = await apiClient.get(`/integrations/${integrationId}/logs`, { params })
    return response.data
  },

  // Analytics
  getAnalytics: async (): Promise<IntegrationAnalytics> => {
    const response = await apiClient.get("/integrations/analytics")
    return response.data
  },

  // Configuration Validation
  validateConfig: async (
    providerId: string,
    config: Record<string, any>,
  ): Promise<{
    valid: boolean
    errors?: Record<string, string[]>
  }> => {
    const response = await apiClient.post(`/integrations/providers/${providerId}/validate`, config)
    return response.data
  },
}
