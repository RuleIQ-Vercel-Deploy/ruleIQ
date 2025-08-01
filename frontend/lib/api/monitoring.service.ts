import { apiClient } from './client';

import type { UnknownRecord } from '@/types/common';

export interface DatabaseStatus {
  status: 'healthy' | 'degraded' | 'down';
  connected_clients: number;
  active_queries: number;
  pool_size: number;
  available_connections: number;
  response_time_ms: number;
  last_check: string;
}

export interface SystemAlert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  type: string;
  message: string;
  details: UnknownRecord;
  created_at: string;
  resolved: boolean;
  resolved_at?: string;
}

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  request_rate: number;
  error_rate: number;
  average_response_time: number;
  uptime_seconds: number;
}

class MonitoringService {
  /**
   * Get database status (admin only)
   */
  async getDatabaseStatus(): Promise<DatabaseStatus> {
    const response = await apiClient.get<DatabaseStatus>('/monitoring/database/status');
    return response.data;
  }

  /**
   * Get system alerts
   */
  async getSystemAlerts(params?: {
    severity?: string;
    resolved?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<{ alerts: SystemAlert[]; total: number }> {
    const response = await apiClient.get<{ alerts: SystemAlert[]; total: number }>(
      '/monitoring/alerts',
      { params }
    );
    return response.data;
  }

  /**
   * Resolve a system alert
   */
  async resolveAlert(alertId: string, resolution?: string): Promise<SystemAlert> {
    const response = await apiClient.patch<SystemAlert>(`/monitoring/alerts/${alertId}/resolve`, {
      resolution,
    });
    return response.data;
  }

  /**
   * Get system metrics
   */
  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await apiClient.get<SystemMetrics>('/monitoring/metrics');
    return response.data;
  }

  /**
   * Get API performance metrics
   */
  async getApiPerformanceMetrics(params?: {
    endpoint?: string;
    time_range?: 'hour' | 'day' | 'week' | 'month';
  }): Promise<{
    endpoints: Array<{
      path: string;
      method: string;
      avg_response_time: number;
      p95_response_time: number;
      p99_response_time: number;
      success_rate: number;
      request_count: number;
    }>;
    time_series: Array<{
      timestamp: string;
      response_time: number;
      error_rate: number;
      request_count: number;
    }>;
  }> {
    const response = await apiClient.get<UnknownRecord>('/monitoring/api-performance', { params });
    return response.data;
  }

  /**
   * Get error logs
   */
  async getErrorLogs(params?: {
    severity?: 'error' | 'warning' | 'info';
    start_date?: string;
    end_date?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }): Promise<{
    logs: Array<{
      timestamp: string;
      severity: string;
      message: string;
      stack_trace?: string;
      user_id?: string;
      request_id?: string;
      metadata?: UnknownRecord;
    }>;
    total: number;
  }> {
    const response = await apiClient.get<UnknownRecord>('/monitoring/error-logs', { params });
    return response.data;
  }

  /**
   * Get health check status
   */
  async getHealthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    checks: {
      database: boolean;
      cache: boolean;
      storage: boolean;
      external_services: Record<string, boolean>;
    };
    timestamp: string;
  }> {
    const response = await apiClient.get<UnknownRecord>('/monitoring/health');
    return response.data;
  }

  /**
   * Get audit logs
   */
  async getAuditLogs(params?: {
    user_id?: string;
    action?: string;
    resource_type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<{
    logs: Array<{
      id: string;
      user_id: string;
      action: string;
      resource_type: string;
      resource_id: string;
      changes?: UnknownRecord;
      ip_address: string;
      user_agent: string;
      timestamp: string;
    }>;
    total: number;
  }> {
    const response = await apiClient.get<UnknownRecord>('/monitoring/audit-logs', { params });
    return response.data;
  }

  /**
   * Export monitoring data
   */
  async exportMonitoringData(params: {
    data_type: 'alerts' | 'metrics' | 'errors' | 'audit';
    format: 'csv' | 'json';
    start_date: string;
    end_date: string;
  }): Promise<void> {
    await apiClient.download(
      `/monitoring/export?${new URLSearchParams(params)}`,
      `monitoring-${params.data_type}-${params.start_date}-${params.end_date}.${params.format}`
    );
  }
}

export const monitoringService = new MonitoringService();