"use client"

import { useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PageHeader } from "@/components/layout/page-header"
import { LoadingLayout } from "@/components/layout/loading-layout"
import { monitoringApi } from "@/api/monitoring"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Database,
  HardDrive,
  MemoryStick,
  Network,
  RefreshCw,
  Server,
  Users,
  Zap,
} from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import type { PerformanceMetrics } from "@/types/api"

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"]

export function MonitoringDashboard() {
  const [selectedTab, setSelectedTab] = useState("overview")
  const [realTimeMetrics, setRealTimeMetrics] = useState<PerformanceMetrics | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const { data: systemHealth, isLoading: healthLoading } = useQuery({
    queryKey: ["system-health"],
    queryFn: monitoringApi.getSystemHealth,
    refetchInterval: autoRefresh ? 30000 : false,
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["monitoring-stats"],
    queryFn: monitoringApi.getStats,
    refetchInterval: autoRefresh ? 60000 : false,
  })

  const { data: performanceMetrics, isLoading: metricsLoading } = useQuery({
    queryKey: ["performance-metrics"],
    queryFn: () =>
      monitoringApi.getPerformanceMetrics({
        interval: "5m",
      }),
    refetchInterval: autoRefresh ? 30000 : false,
  })

  const { data: resourceUsage, isLoading: resourceLoading } = useQuery({
    queryKey: ["resource-usage"],
    queryFn: () =>
      monitoringApi.getResourceUsage({
        interval: "5m",
      }),
    refetchInterval: autoRefresh ? 30000 : false,
  })

  const { data: alerts } = useQuery({
    queryKey: ["alerts"],
    queryFn: () =>
      monitoringApi.getAlerts({
        status: "active",
        limit: 10,
      }),
    refetchInterval: autoRefresh ? 30000 : false,
  })

  // Subscribe to real-time metrics
  useEffect(() => {
    if (!autoRefresh) return

    const unsubscribe = monitoringApi.subscribeToRealTimeMetrics((metrics) => {
      setRealTimeMetrics(metrics)
    })

    return unsubscribe
  }, [autoRefresh])

  if (healthLoading || statsLoading || metricsLoading || resourceLoading) {
    return <LoadingLayout />
  }

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      case "warning":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
      case "critical":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
  }

  const getHealthIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case "critical":
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${days}d ${hours}h ${minutes}m`
  }

  const formatBytes = (bytes: number) => {
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    if (bytes === 0) return "0 Bytes"
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + " " + sizes[i]
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="System Monitoring"
        description="Monitor system health, performance, and user activity"
        actions={
          <div className="flex items-center space-x-2">
            <Button
              variant={autoRefresh ? "default" : "outline"}
              size="sm"
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? "animate-spin" : ""}`} />
              {autoRefresh ? "Auto Refresh On" : "Auto Refresh Off"}
            </Button>
          </div>
        }
      />

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
          <TabsTrigger value="errors">Errors</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* System Health Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Server className="h-5 w-5" />
                <span>System Health</span>
              </CardTitle>
              <CardDescription>Overall system status and service health</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getHealthIcon(systemHealth?.status || "unknown")}
                    <div>
                      <p className="font-medium">Overall Status</p>
                      <p className="text-sm text-muted-foreground">
                        Uptime: {systemHealth?.uptime ? formatUptime(systemHealth.uptime) : "Unknown"}
                      </p>
                    </div>
                  </div>
                  <Badge className={getHealthStatusColor(systemHealth?.status || "unknown")}>
                    {systemHealth?.status || "Unknown"}
                  </Badge>
                </div>

                {systemHealth?.services &&
                  Object.entries(systemHealth.services).map(([service, status]) => (
                    <div key={service} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getHealthIcon(status.status)}
                        <div>
                          <p className="font-medium capitalize">{service.replace("_", " ")}</p>
                          <p className="text-sm text-muted-foreground">
                            {status.response_time ? `${status.response_time}ms` : "N/A"}
                          </p>
                        </div>
                      </div>
                      <Badge className={getHealthStatusColor(status.status)}>{status.status}</Badge>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>

          {/* Key Metrics */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
                <p className="text-xs text-muted-foreground">{stats?.active_users_24h || 0} active in 24h</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Requests (24h)</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_requests_24h?.toLocaleString() || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.error_rate_24h ? `${(stats.error_rate_24h * 100).toFixed(2)}% error rate` : "0% error rate"}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.average_response_time || 0}ms</div>
                <p className="text-xs text-muted-foreground">Last 24 hours</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
                <HardDrive className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {stats?.storage_used ? formatBytes(stats.storage_used) : "0 GB"}
                </div>
                <p className="text-xs text-muted-foreground">
                  of {stats?.storage_total ? formatBytes(stats.storage_total) : "0 GB"}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Performance Overview Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Overview</CardTitle>
              <CardDescription>Response time and system performance over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceMetrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                      formatter={(value: number, name: string) => [
                        name === "response_time" ? `${value}ms` : `${value}%`,
                        name.replace("_", " "),
                      ]}
                    />
                    <Line
                      type="monotone"
                      dataKey="response_time"
                      stroke="#8884d8"
                      strokeWidth={2}
                      name="Response Time"
                    />
                    <Line type="monotone" dataKey="cpu_usage" stroke="#82ca9d" strokeWidth={2} name="CPU Usage" />
                    <Line type="monotone" dataKey="memory_usage" stroke="#ffc658" strokeWidth={2} name="Memory Usage" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Active Alerts */}
          {alerts && alerts.items.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-500" />
                  <span>Active Alerts</span>
                </CardTitle>
                <CardDescription>System alerts requiring attention</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {alerts.items.slice(0, 5).map((alert) => (
                    <div
                      key={alert.id}
                      className="flex items-center justify-between p-4 border rounded-lg bg-yellow-50 dark:bg-yellow-950"
                    >
                      <div className="flex items-center space-x-3">
                        <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        <div>
                          <h4 className="font-medium">{alert.title}</h4>
                          <p className="text-sm text-muted-foreground">{alert.message}</p>
                          <p className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(alert.triggered_at), { addSuffix: true })}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{alert.severity}</Badge>
                        <Button variant="outline" size="sm">
                          View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          {/* Real-time Performance */}
          {realTimeMetrics && (
            <Card>
              <CardHeader>
                <CardTitle>Real-time Performance</CardTitle>
                <CardDescription>Live system performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{realTimeMetrics.response_time}ms</div>
                    <p className="text-sm text-muted-foreground">Response Time</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{realTimeMetrics.cpu_usage}%</div>
                    <p className="text-sm text-muted-foreground">CPU Usage</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600">{realTimeMetrics.memory_usage}%</div>
                    <p className="text-sm text-muted-foreground">Memory Usage</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{realTimeMetrics.requests_per_minute}</div>
                    <p className="text-sm text-muted-foreground">Requests/min</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Performance Charts */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Response Time Trend</CardTitle>
                <CardDescription>Average response time over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={performanceMetrics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
                      <YAxis />
                      <Tooltip
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                        formatter={(value: number) => [`${value}ms`, "Response Time"]}
                      />
                      <Area type="monotone" dataKey="response_time" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Error Rate</CardTitle>
                <CardDescription>Error rate percentage over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={performanceMetrics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
                      <YAxis />
                      <Tooltip
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                        formatter={(value: number) => [`${value}%`, "Error Rate"]}
                      />
                      <Area type="monotone" dataKey="error_rate" stroke="#ff7300" fill="#ff7300" fillOpacity={0.3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Throughput Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Request Throughput</CardTitle>
              <CardDescription>Requests per minute over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performanceMetrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                      formatter={(value: number) => [value, "Requests/min"]}
                    />
                    <Bar dataKey="requests_per_minute" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resources" className="space-y-6">
          {/* Current Resource Usage */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
                <MemoryStick className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemHealth?.performance.cpu_usage || 0}%</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${systemHealth?.performance.cpu_usage || 0}%` }}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemHealth?.performance.memory_usage || 0}%</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${systemHealth?.performance.memory_usage || 0}%` }}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
                <HardDrive className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemHealth?.performance.disk_usage || 0}%</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-yellow-600 h-2 rounded-full"
                    style={{ width: `${systemHealth?.performance.disk_usage || 0}%` }}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Connections</CardTitle>
                <Network className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {resourceUsage && resourceUsage.length > 0
                    ? resourceUsage[resourceUsage.length - 1].active_connections
                    : 0}
                </div>
                <p className="text-xs text-muted-foreground">Current connections</p>
              </CardContent>
            </Card>
          </div>

          {/* Resource Usage Charts */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>CPU & Memory Usage</CardTitle>
                <CardDescription>System resource utilization over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={resourceUsage}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
                      <YAxis />
                      <Tooltip
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                        formatter={(value: number, name: string) => [`${value}%`, name.replace("_", " ")]}
                      />
                      <Line type="monotone" dataKey="cpu_usage" stroke="#8884d8" strokeWidth={2} name="CPU Usage" />
                      <Line
                        type="monotone"
                        dataKey="memory_usage"
                        stroke="#82ca9d"
                        strokeWidth={2}
                        name="Memory Usage"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Network Traffic</CardTitle>
                <CardDescription>Network input/output over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={resourceUsage}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" tickFormatter={(value) => new Date(value).toLocaleTimeString()} />
                      <YAxis />
                      <Tooltip
                        labelFormatter={(value) => new Date(value).toLocaleString()}
                        formatter={(value: number, name: string) => [
                          formatBytes(value),
                          name.replace("_", " ").toUpperCase(),
                        ]}
                      />
                      <Area
                        type="monotone"
                        dataKey="network_in"
                        stackId="1"
                        stroke="#8884d8"
                        fill="#8884d8"
                        name="Network In"
                      />
                      <Area
                        type="monotone"
                        dataKey="network_out"
                        stackId="1"
                        stroke="#82ca9d"
                        fill="#82ca9d"
                        name="Network Out"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>User Activity</CardTitle>
              <CardDescription>Recent user actions and system activity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Activity Monitoring</h3>
                <p className="text-muted-foreground">User activity tracking will be displayed here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Error Logs</CardTitle>
              <CardDescription>System errors and exceptions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Error Monitoring</h3>
                <p className="text-muted-foreground">Error logs and monitoring will be displayed here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Alert Management</CardTitle>
              <CardDescription>System alerts and notifications</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Alert Management</h3>
                <p className="text-muted-foreground">Alert management interface will be displayed here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
