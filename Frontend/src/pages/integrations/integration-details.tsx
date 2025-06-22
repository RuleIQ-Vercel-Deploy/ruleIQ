"use client"

import { Textarea } from "@/components/ui/textarea"

import { Input } from "@/components/ui/input"

import { Label } from "@/components/ui/label"

import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PageHeader } from "@/components/layout/page-header"
import { LoadingLayout } from "@/components/layout/loading-layout"
import { integrationsApi } from "@/api/integrations"
import { ArrowLeft, RefreshCw, Trash2, AlertCircle, CheckCircle, Clock, Activity, Download, Upload } from "lucide-react"
import { toast } from "@/hooks/use-toast"
import { formatDistanceToNow } from "date-fns"

export function IntegrationDetails() {
  const { integrationId } = useParams<{ integrationId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedTab, setSelectedTab] = useState("overview")

  const { data: integration, isLoading } = useQuery({
    queryKey: ["integration", integrationId],
    queryFn: () => integrationsApi.getIntegration(integrationId!),
    enabled: !!integrationId,
  })

  const { data: logs } = useQuery({
    queryKey: ["integration-logs", integrationId],
    queryFn: () => integrationsApi.getLogs(integrationId!, { limit: 50 }),
    enabled: !!integrationId,
  })

  const { data: syncHistory } = useQuery({
    queryKey: ["integration-sync-history", integrationId],
    queryFn: () => integrationsApi.getSyncHistory(integrationId!),
    enabled: !!integrationId,
  })

  const testConnectionMutation = useMutation({
    mutationFn: () => integrationsApi.testConnection(integrationId!),
    onSuccess: (result) => {
      toast({
        title: result.success ? "Connection successful" : "Connection failed",
        description: result.message,
        variant: result.success ? "default" : "destructive",
      })
    },
  })

  const triggerSyncMutation = useMutation({
    mutationFn: (syncType: "full" | "incremental") => integrationsApi.triggerSync(integrationId!, syncType),
    onSuccess: () => {
      toast({
        title: "Sync started",
        description: "Data synchronization has been initiated.",
      })
      queryClient.invalidateQueries({ queryKey: ["integration-sync-history", integrationId] })
    },
  })

  const updateIntegrationMutation = useMutation({
    mutationFn: (data: any) => integrationsApi.updateIntegration(integrationId!, data),
    onSuccess: () => {
      toast({
        title: "Integration updated",
        description: "Your integration settings have been saved.",
      })
      queryClient.invalidateQueries({ queryKey: ["integration", integrationId] })
    },
  })

  const deleteIntegrationMutation = useMutation({
    mutationFn: () => integrationsApi.deleteIntegration(integrationId!),
    onSuccess: () => {
      toast({
        title: "Integration deleted",
        description: "The integration has been removed from your account.",
      })
      navigate("/app/integrations")
    },
  })

  if (isLoading) {
    return <LoadingLayout />
  }

  if (!integration) {
    return (
      <div className="space-y-6">
        <PageHeader title="Integration not found" />
        <Card>
          <CardContent className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Integration not found</h3>
            <p className="text-muted-foreground mb-4">The requested integration could not be found.</p>
            <Button onClick={() => navigate("/app/integrations")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Integrations
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

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

  const handleAutoSyncToggle = (enabled: boolean) => {
    updateIntegrationMutation.mutate({
      sync_settings: {
        ...integration.sync_settings,
        auto_sync: enabled,
      },
    })
  }

  const handleSyncFrequencyChange = (frequency: string) => {
    updateIntegrationMutation.mutate({
      sync_settings: {
        ...integration.sync_settings,
        sync_frequency: frequency,
      },
    })
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={integration.name}
        description={integration.description}
        action={
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              onClick={() => testConnectionMutation.mutate()}
              disabled={testConnectionMutation.isPending}
            >
              {testConnectionMutation.isPending ? "Testing..." : "Test Connection"}
            </Button>
            <Button variant="outline" onClick={() => navigate("/app/integrations")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>
        }
      />

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="sync">Data Sync</TabsTrigger>
          <TabsTrigger value="logs">Activity Logs</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Status Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                {getStatusIcon(integration.status)}
                <span>Integration Status</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Connection Status</p>
                  <p className="text-sm text-muted-foreground">
                    {integration.connection_status === "active" ? "Active and healthy" : "Connection issues detected"}
                  </p>
                </div>
                <Badge className={getStatusColor(integration.status)}>{integration.status}</Badge>
              </div>

              {integration.error_message && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{integration.error_message}</AlertDescription>
                </Alert>
              )}

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Connected</p>
                  <p className="text-sm">
                    {integration.connected_at
                      ? formatDistanceToNow(new Date(integration.connected_at), { addSuffix: true })
                      : "Not connected"}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Last Activity</p>
                  <p className="text-sm">
                    {integration.last_activity
                      ? formatDistanceToNow(new Date(integration.last_activity), { addSuffix: true })
                      : "No activity"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sync Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Data Synchronization</CardTitle>
              <CardDescription>Overview of data sync settings and recent activity</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Auto Sync</p>
                  <p className="text-sm text-muted-foreground">
                    {integration.sync_settings.auto_sync ? "Enabled" : "Disabled"}
                  </p>
                </div>
                <Switch checked={integration.sync_settings.auto_sync} onCheckedChange={handleAutoSyncToggle} />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Sync Frequency</p>
                  <p className="text-sm capitalize">{integration.sync_settings.sync_frequency.replace("_", " ")}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Last Sync</p>
                  <p className="text-sm">
                    {integration.sync_settings.last_sync
                      ? formatDistanceToNow(new Date(integration.sync_settings.last_sync), { addSuffix: true })
                      : "Never"}
                  </p>
                </div>
              </div>

              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => triggerSyncMutation.mutate("incremental")}
                  disabled={triggerSyncMutation.isPending}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Sync Now
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => triggerSyncMutation.mutate("full")}
                  disabled={triggerSyncMutation.isPending}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Full Sync
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sync" className="space-y-6">
          {/* Sync Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Sync Configuration</CardTitle>
              <CardDescription>Configure how and when data is synchronized</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Enable Auto Sync</p>
                  <p className="text-sm text-muted-foreground">
                    Automatically sync data based on the configured frequency
                  </p>
                </div>
                <Switch checked={integration.sync_settings.auto_sync} onCheckedChange={handleAutoSyncToggle} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="sync-frequency">Sync Frequency</Label>
                <Select value={integration.sync_settings.sync_frequency} onValueChange={handleSyncFrequencyChange}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="realtime">Real-time</SelectItem>
                    <SelectItem value="hourly">Hourly</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex space-x-2">
                <Button
                  onClick={() => triggerSyncMutation.mutate("incremental")}
                  disabled={triggerSyncMutation.isPending}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  {triggerSyncMutation.isPending ? "Syncing..." : "Trigger Sync"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => triggerSyncMutation.mutate("full")}
                  disabled={triggerSyncMutation.isPending}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Full Sync
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Sync History */}
          <Card>
            <CardHeader>
              <CardTitle>Sync History</CardTitle>
              <CardDescription>Recent synchronization activities</CardDescription>
            </CardHeader>
            <CardContent>
              {syncHistory && syncHistory.length > 0 ? (
                <div className="space-y-4">
                  {syncHistory.map((sync) => (
                    <div key={sync.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {sync.status === "completed" ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : sync.status === "failed" ? (
                            <AlertCircle className="h-4 w-4 text-red-500" />
                          ) : (
                            <Clock className="h-4 w-4 text-yellow-500" />
                          )}
                          <div>
                            <p className="font-medium capitalize">{sync.sync_type} Sync</p>
                            <p className="text-sm text-muted-foreground">
                              {formatDistanceToNow(new Date(sync.started_at), { addSuffix: true })}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{sync.records_processed} records processed</p>
                        <p className="text-sm text-muted-foreground">
                          {sync.records_created} created, {sync.records_updated} updated
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No sync history</h3>
                  <p className="text-muted-foreground">
                    Sync history will appear here once data synchronization begins
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Activity Logs</CardTitle>
              <CardDescription>Detailed logs of integration activities and events</CardDescription>
            </CardHeader>
            <CardContent>
              {logs && logs.length > 0 ? (
                <div className="space-y-2">
                  {logs.map((log) => (
                    <div key={log.id} className="flex items-start space-x-3 p-3 border rounded-lg">
                      <div className="flex-shrink-0 mt-1">
                        {log.level === "error" ? (
                          <AlertCircle className="h-4 w-4 text-red-500" />
                        ) : log.level === "warning" ? (
                          <AlertCircle className="h-4 w-4 text-yellow-500" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium capitalize">{log.event_type.replace("_", " ")}</p>
                          <p className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                          </p>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{log.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No activity logs</h3>
                  <p className="text-muted-foreground">Activity logs will appear here as the integration is used</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Integration Settings</CardTitle>
              <CardDescription>Manage integration configuration and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="integration-name">Integration Name</Label>
                  <Input
                    id="integration-name"
                    value={integration.name}
                    onChange={(e) => {
                      updateIntegrationMutation.mutate({ name: e.target.value })
                    }}
                  />
                </div>

                <div>
                  <Label htmlFor="integration-description">Description</Label>
                  <Textarea
                    id="integration-description"
                    value={integration.description || ""}
                    onChange={(e) => {
                      updateIntegrationMutation.mutate({ description: e.target.value })
                    }}
                    rows={3}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-red-600">Danger Zone</CardTitle>
              <CardDescription>Irreversible actions that will affect your integration</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50 dark:bg-red-950 dark:border-red-800">
                <div>
                  <p className="font-medium text-red-600">Delete Integration</p>
                  <p className="text-sm text-red-600/80">
                    This will permanently delete the integration and all associated data
                  </p>
                </div>
                <Button
                  variant="destructive"
                  onClick={() => {
                    if (confirm("Are you sure you want to delete this integration? This action cannot be undone.")) {
                      deleteIntegrationMutation.mutate()
                    }
                  }}
                  disabled={deleteIntegrationMutation.isPending}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  {deleteIntegrationMutation.isPending ? "Deleting..." : "Delete"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
