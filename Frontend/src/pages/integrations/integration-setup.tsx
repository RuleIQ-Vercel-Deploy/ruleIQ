"use client"

import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useQuery, useMutation } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { PageHeader } from "@/components/layout/page-header"
import { LoadingLayout } from "@/components/layout/loading-layout"
import { integrationsApi } from "@/api/integrations"
import { ArrowLeft, ExternalLink, Shield, AlertCircle, CheckCircle } from "lucide-react"
import { toast } from "@/hooks/use-toast"
import type { IntegrationConfigField } from "@/types/api"

export function IntegrationSetup() {
  const { providerId } = useParams<{ providerId: string }>()
  const navigate = useNavigate()
  const [isConnecting, setIsConnecting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)

  const { data: provider, isLoading } = useQuery({
    queryKey: ["integration-provider", providerId],
    queryFn: () => integrationsApi.getProvider(providerId!),
    enabled: !!providerId,
  })

  // Create dynamic form schema based on provider config
  const createFormSchema = (fields: IntegrationConfigField[]) => {
    const schemaFields: Record<string, any> = {}

    fields.forEach((field) => {
      let fieldSchema: any

      switch (field.type) {
        case "text":
        case "password":
        case "url":
          fieldSchema = z.string()
          if (field.validation?.pattern) {
            fieldSchema = fieldSchema.regex(new RegExp(field.validation.pattern))
          }
          break
        case "number":
          fieldSchema = z.number()
          if (field.validation?.min) fieldSchema = fieldSchema.min(field.validation.min)
          if (field.validation?.max) fieldSchema = fieldSchema.max(field.validation.max)
          break
        case "boolean":
          fieldSchema = z.boolean()
          break
        case "select":
        case "multiselect":
          fieldSchema = field.type === "multiselect" ? z.array(z.string()) : z.string()
          break
        default:
          fieldSchema = z.string()
      }

      if (field.required) {
        fieldSchema = fieldSchema.min(1, `${field.label} is required`)
      } else {
        fieldSchema = fieldSchema.optional()
      }

      schemaFields[field.name] = fieldSchema
    })

    return z.object(schemaFields)
  }

  const formSchema = provider ? createFormSchema(provider.config_schema) : z.object({})

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues:
      provider?.config_schema.reduce(
        (acc, field) => {
          acc[field.name] = field.type === "boolean" ? false : field.type === "multiselect" ? [] : ""
          return acc
        },
        {} as Record<string, any>,
      ) || {},
  })

  const createIntegrationMutation = useMutation({
    mutationFn: (data: { provider_id: string; name: string; config: Record<string, any> }) =>
      integrationsApi.createIntegration(data),
    onSuccess: (integration) => {
      toast({
        title: "Integration created successfully",
        description: "Your integration has been configured and is ready to use.",
      })
      navigate(`/app/integrations/${integration.id}`)
    },
    onError: (error: any) => {
      toast({
        title: "Failed to create integration",
        description: error.response?.data?.detail || "An error occurred while creating the integration.",
        variant: "destructive",
      })
    },
  })

  const validateConfigMutation = useMutation({
    mutationFn: (config: Record<string, any>) => integrationsApi.validateConfig(providerId!, config),
    onSuccess: (result) => {
      setTestResult({
        success: result.valid,
        message: result.valid ? "Configuration is valid" : "Configuration has errors",
      })
    },
    onError: () => {
      setTestResult({ success: false, message: "Failed to validate configuration" })
    },
  })

  const initiateOAuthMutation = useMutation({
    mutationFn: () => integrationsApi.initiateOAuth(providerId!),
    onSuccess: (result) => {
      window.location.href = result.auth_url
    },
    onError: (error: any) => {
      toast({
        title: "OAuth initialization failed",
        description: error.response?.data?.detail || "Failed to start OAuth flow.",
        variant: "destructive",
      })
    },
  })

  if (isLoading) {
    return <LoadingLayout />
  }

  if (!provider) {
    return (
      <div className="space-y-6">
        <PageHeader title="Integration not found" />
        <Card>
          <CardContent className="text-center py-12">
            <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Integration provider not found</h3>
            <p className="text-muted-foreground mb-4">The requested integration provider could not be found.</p>
            <Button onClick={() => navigate("/app/integrations/marketplace")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Marketplace
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const handleOAuthConnect = () => {
    setIsConnecting(true)
    initiateOAuthMutation.mutate()
  }

  const handleManualSetup = (data: Record<string, any>) => {
    createIntegrationMutation.mutate({
      provider_id: providerId!,
      name: `${provider.display_name} Integration`,
      config: data,
    })
  }

  const handleTestConnection = () => {
    const formData = form.getValues()
    validateConfigMutation.mutate(formData)
  }

  const renderConfigField = (field: IntegrationConfigField) => {
    const fieldValue = form.watch(field.name)

    switch (field.type) {
      case "text":
      case "url":
        return <Input {...form.register(field.name)} placeholder={field.placeholder} type="text" />

      case "password":
        return <Input {...form.register(field.name)} placeholder={field.placeholder} type="password" />

      case "textarea":
        return <Textarea {...form.register(field.name)} placeholder={field.placeholder} rows={3} />

      case "number":
        return (
          <Input
            {...form.register(field.name, { valueAsNumber: true })}
            placeholder={field.placeholder}
            type="number"
            min={field.validation?.min}
            max={field.validation?.max}
          />
        )

      case "boolean":
        return <Switch checked={fieldValue} onCheckedChange={(checked) => form.setValue(field.name, checked)} />

      case "select":
        return (
          <Select value={fieldValue} onValueChange={(value) => form.setValue(field.name, value)}>
            <SelectTrigger>
              <SelectValue placeholder={field.placeholder} />
            </SelectTrigger>
            <SelectContent>
              {field.options?.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )

      default:
        return <Input {...form.register(field.name)} placeholder={field.placeholder} type="text" />
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Connect ${provider.display_name}`}
        description={provider.description}
        action={
          <Button variant="outline" onClick={() => navigate("/app/integrations/marketplace")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Marketplace
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Provider Information */}
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-3">
              <img
                src={provider.logo_url || "/placeholder.svg"}
                alt={provider.display_name}
                className="h-12 w-12 rounded"
              />
              <div>
                <CardTitle>{provider.display_name}</CardTitle>
                <CardDescription>{provider.category.replace("_", " ")}</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Supported Features</h4>
              <div className="flex flex-wrap gap-1">
                {provider.supported_features.map((feature) => (
                  <span key={feature} className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-muted">
                    {feature}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">Setup Complexity</h4>
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm capitalize">{provider.setup_complexity}</span>
              </div>
            </div>

            <div className="flex flex-col space-y-2">
              <Button variant="outline" size="sm" asChild>
                <a href={provider.documentation_url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Documentation
                </a>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <a href={provider.website_url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Website
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Setup Form */}
        <div className="lg:col-span-2 space-y-6">
          {provider.auth_type === "oauth2" ? (
            <Card>
              <CardHeader>
                <CardTitle>OAuth Authentication</CardTitle>
                <CardDescription>Connect securely using OAuth 2.0 authentication</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <Shield className="h-4 w-4" />
                  <AlertDescription>
                    You will be redirected to {provider.display_name} to authorize the connection. This is the most
                    secure way to connect your account.
                  </AlertDescription>
                </Alert>

                <Button onClick={handleOAuthConnect} disabled={isConnecting} className="w-full">
                  {isConnecting ? "Connecting..." : `Connect with ${provider.display_name}`}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Manual Configuration</CardTitle>
                <CardDescription>Configure your integration manually using API credentials</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={form.handleSubmit(handleManualSetup)} className="space-y-6">
                  {provider.config_schema.map((field) => (
                    <div key={field.name} className="space-y-2">
                      <Label htmlFor={field.name}>
                        {field.label}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                      </Label>
                      {renderConfigField(field)}
                      {field.description && <p className="text-sm text-muted-foreground">{field.description}</p>}
                      {form.formState.errors[field.name] && (
                        <p className="text-sm text-red-500">{form.formState.errors[field.name]?.message as string}</p>
                      )}
                    </div>
                  ))}

                  {testResult && (
                    <Alert variant={testResult.success ? "default" : "destructive"}>
                      {testResult.success ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
                      <AlertDescription>{testResult.message}</AlertDescription>
                    </Alert>
                  )}

                  <div className="flex space-x-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleTestConnection}
                      disabled={validateConfigMutation.isPending}
                    >
                      {validateConfigMutation.isPending ? "Testing..." : "Test Connection"}
                    </Button>
                    <Button type="submit" disabled={createIntegrationMutation.isPending}>
                      {createIntegrationMutation.isPending ? "Creating..." : "Create Integration"}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
