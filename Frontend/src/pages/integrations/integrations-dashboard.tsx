"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PageHeader } from "@/components/layout/page-header"
import { LoadingLayout } from "@/components/layout/loading-layout"
import { integrationsApi } from "@/api/integrations"
import { Activity, AlertCircle, CheckCircle, Clock, Plus, RefreshCw, Settings, TrendingUp, Zap } from "lucide-react"
import { Link } from "react-router-dom"
import { formatDistanceToNow } from "date-fns"

export function IntegrationsDashboard() {
  const [selectedTab, setSelectedTab] = useState("overview")

  const { data: integrations, isLoading: integrationsLoading } = useQuery({
    queryKey: ["integrations"],
    queryFn: integrationsApi.getIntegrations,
  })

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ["integrations", "analytics"],
    queryFn: integrationsApi.getAnalytics,
  })

  const { data: providers, isLoading: providersLoading } = useQuery({
    queryKey: ["integration-providers"],
    queryFn: integrationsApi.getProviders,
  })

  if (integrationsLoading || analyticsLoading || providersLoading) {
    return <LoadingLayout />
  }

  const activeIntegrations = integrations?.filter((i) => i.status === "connected") || []
  const errorIntegrations = integrations?.filter((i) => i.status === "error") || []
  const popularProviders = providers?.filter((p) => p.is_popular) || []

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "connected":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      case "error":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Integrations"
        description="Manage your third-party integrations and data connections"
        action={
          <Button asChild>
            <Link to="/app/integrations/marketplace">
              <Plus className="h-4 w-4 mr-2" />
              Add Integration
            </Link>
          </Button>
        }
      />

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="active">Active Integrations</TabsTrigger>
          <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Integrations</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics?.total_integrations || 0}</div>
                <p className="text-xs text-muted-foreground">{analytics?.active_integrations || 0} active</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Sync Success Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics?.sync_success_rate ? `${Math.round(analytics.sync_success_rate * 100)}%` : "0%"}
                </div>
                <Progress
                  value={analytics?.sync_success_rate ? analytics.sync_success_rate * 100 : 0}
                  className="mt-2"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Sync Time</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics?.average_sync_time ? `${Math.round(analytics.average_sync_time)}s` : "0s"}
                </div>
                <p className="text-xs text-muted-foreground">Last 30 days</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Data Synced</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics?.data_volume_synced ? `${(analytics.data_volume_synced / 1000).toFixed(1)}K` : "0"}
                </div>
                <p className="text-xs text-muted-foreground">Records this month</p>
              </CardContent>
            </Card>
          </div>

          {/* Active Integrations */}
          <Card>
            <CardHeader>
              <CardTitle>Active Integrations</CardTitle>
              <CardDescription>Your currently connected integrations</CardDescription>
            </CardHeader>
            <CardContent>
              {activeIntegrations.length === 0 ? (
                <div className="text-center py-8">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No active integrations</h3>
                  <p className="text-muted-foreground mb-4">Connect your first integration to start syncing data</p>
                  <Button asChild>
                    <Link to="/app/integrations/marketplace">Browse Integrations</Link>
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {activeIntegrations.slice(0, 5).map((integration) => (
                    <div key={integration.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(integration.status)}
                          <div>
                            <h4 className="font-medium">{integration.name}</h4>
                            <p className="text-sm text-muted-foreground">{integration.description}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(integration.status)}>{integration.status}</Badge>
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/app/integrations/${integration.id}`}>
                            <Settings className="h-4 w-4" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  ))}
                  {activeIntegrations.length > 5 && (
                    <div className="text-center pt-4">
                      <Button variant="outline" asChild>
                        <Link to="/app/integrations?tab=active">View All ({activeIntegrations.length})</Link>
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Error Integrations */}
          {errorIntegrations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertCircle className="h-5 w-5 text-red-500" />
                  <span>Integrations Requiring Attention</span>
                </CardTitle>
                <CardDescription>These integrations have errors that need to be resolved</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {errorIntegrations.map((integration) => (
                    <div
                      key={integration.id}
                      className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50 dark:bg-red-950 dark:border-red-800"
                    >
                      <div className="flex items-center space-x-4">
                        <AlertCircle className="h-5 w-5 text-red-500" />
                        <div>
                          <h4 className="font-medium">{integration.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {integration.error_message || "Connection error"}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/app/integrations/${integration.id}`}>Fix Issue</Link>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Popular Providers */}
          <Card>
            <CardHeader>
              <CardTitle>Popular Integrations</CardTitle>
              <CardDescription>Most commonly used integrations in your industry</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {popularProviders.slice(0, 6).map((provider) => (
                  <div
                    key={provider.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <img
                        src={provider.logo_url || "/placeholder.svg"}
                        alt={provider.display_name}
                        className="h-8 w-8 rounded"
                      />
                      <div>
                        <h4 className="font-medium">{provider.display_name}</h4>
                        <p className="text-sm text-muted-foreground">{provider.category.replace("_", " ")}</p>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" asChild>
                      <Link to={`/app/integrations/marketplace/${provider.id}`}>Connect</Link>
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="active" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>All Integrations</CardTitle>
              <CardDescription>Manage all your connected integrations</CardDescription>
            </CardHeader>
            <CardContent>
              {integrations && integrations.length > 0 ? (
                <div className="space-y-4">
                  {integrations.map((integration) => (
                    <div key={integration.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(integration.status)}
                          <div>
                            <h4 className="font-medium">{integration.name}</h4>
                            <p className="text-sm text-muted-foreground">{integration.description}</p>
                            {integration.last_activity && (
                              <p className="text-xs text-muted-foreground">
                                Last activity:{" "}
                                {formatDistanceToNow(new Date(integration.last_activity), { addSuffix: true })}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(integration.status)}>{integration.status}</Badge>
                        {integration.sync_settings.auto_sync && (
                          <Badge variant="outline">
                            <RefreshCw className="h-3 w-3 mr-1" />
                            Auto-sync
                          </Badge>
                        )}
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/app/integrations/${integration.id}`}>
                            <Settings className="h-4 w-4" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No integrations yet</h3>
                  <p className="text-muted-foreground mb-4">Connect your first integration to start syncing data</p>
                  <Button asChild>
                    <Link to="/app/integrations/marketplace">Browse Integrations</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="marketplace" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Integration Marketplace</CardTitle>
              <CardDescription>Discover and connect new integrations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {providers?.map((provider) => (
                  <div key={provider.id} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <img
                          src={provider.logo_url || "/placeholder.svg"}
                          alt={provider.display_name}
                          className="h-10 w-10 rounded"
                        />
                        <div>
                          <h3 className="font-semibold">{provider.display_name}</h3>
                          <p className="text-sm text-muted-foreground">{provider.category.replace("_", " ")}</p>
                        </div>
                      </div>
                      {provider.is_popular && <Badge variant="secondary">Popular</Badge>}
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">{provider.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="text-xs">
                          {provider.setup_complexity}
                        </Badge>
                        {provider.is_enterprise && (
                          <Badge variant="outline" className="text-xs">
                            Enterprise
                          </Badge>
                        )}
                      </div>
                      <Button size="sm" asChild>
                        <Link to={`/app/integrations/marketplace/${provider.id}`}>Connect</Link>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
