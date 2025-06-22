import { apiClient } from "@/lib/api-client"
import type {
  SystemHealth,
  PerformanceMetrics,
  UserActivity,
  ErrorLog,
  AuditLog,
  Alert,
  MonitoringStats,
  ResourceUsage,
} from "@/types/api"

export const monitoringApi = {
  // System Health
  getSystemHealth: async (): Promise<SystemHealth> => {
    const response = await apiClient.get("/monitoring/health")
    return response.data
  },

  // Performance Metrics
  getPerformanceMetrics: async (params?: {
    start_date?: string
    end_date?: string
    interval?: "1m" | "5m" | "15m" | "1h" | "1d"
  }): Promise<PerformanceMetrics[]> => {
    const response = await apiClient.get("/monitoring/performance", { params })
    return response.data
  },

  // User Activity
  getUserActivity: async (params?: {
    user_id?: string
    action?: string
    resource_type?: string
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  }): Promise<{
    items: UserActivity[]
    total: number
    page: number
    pages: number
  }> => {
    const response = await apiClient.get("/monitoring/activity", { params })
    return response.data
  },

  // Error Logs
  getErrorLogs: async (params?: {
    level?: string
    resolved?: boolean
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  }): Promise<{
    items: ErrorLog[]
    total: number
    page: number
    pages: number
  }> => {
    const response = await apiClient.get("/monitoring/errors", { params })
    return response.data
  },

  resolveError: async (errorId: string, resolution?: string): Promise<ErrorLog> => {
    const response = await apiClient.post(`/monitoring/errors/${errorId}/resolve`, {
      resolution,
    })
    return response.data
  },

  // Audit Logs
  getAuditLogs: async (params?: {
    user_id?: string
    action?: string
    resource_type?: string
    compliance_relevant?: boolean
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  }): Promise<{
    items: AuditLog[]
    total: number
    page: number
    pages: number
  }> => {
    const response = await apiClient.get("/monitoring/audit", { params })
    return response.data
  },

  exportAuditLogs: async (params: {
    start_date: string
    end_date: string
    format: "csv" | "json" | "pdf"
    compliance_relevant?: boolean
  }): Promise<{ download_url: string }> => {
    const response = await apiClient.post("/monitoring/audit/export", params)
    return response.data
  },

  // Alerts
  getAlerts: async (params?: {
    type?: string
    severity?: string
    status?: string
    limit?: number
    offset?: number
  }): Promise<{
    items: Alert[]
    total: number
    page: number
    pages: number
  }> => {
    const response = await apiClient.get("/monitoring/alerts", { params })
    return response.data
  },

  acknowledgeAlert: async (alertId: string): Promise<Alert> => {
    const response = await apiClient.post(`/monitoring/alerts/${alertId}/acknowledge`)
    return response.data
  },

  resolveAlert: async (alertId: string, resolution?: string): Promise<Alert> => {
    const response = await apiClient.post(`/monitoring/alerts/${alertId}/resolve`, {
      resolution,
    })
    return response.data
  },

  // Statistics
  getStats: async (): Promise<MonitoringStats> => {
    const response = await apiClient.get("/monitoring/stats")
    return response.data
  },

  // Resource Usage
  getResourceUsage: async (params?: {
    start_date?: string
    end_date?: string
    interval?: "1m" | "5m" | "15m" | "1h" | "1d"
  }): Promise<ResourceUsage[]> => {
    const response = await apiClient.get("/monitoring/resources", { params })
    return response.data
  },

  // Real-time data (WebSocket endpoints would be handled separately)
  subscribeToRealTimeMetrics: (callback: (data: PerformanceMetrics) => void) => {
    // WebSocket implementation would go here
    // For now, we'll use polling as a fallback
    const interval = setInterval(async () => {
      try {
        const metrics = await monitoringApi.getPerformanceMetrics({
          interval: "1m",
        })
        if (metrics.length > 0) {
          callback(metrics[metrics.length - 1])
        }
      } catch (error) {
        console.error("Failed to fetch real-time metrics:", error)
      }
    }, 30000) // Poll every 30 seconds

    return () => clearInterval(interval)
  },
}
