"use client"

import { useState, useEffect } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useNavigate, useParams } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { PageHeader } from "@/components/layout/page-header"
import { businessProfileSchema, type BusinessProfileInput } from "@/lib/validators"
import { businessApi } from "@/api/business"
import type { BusinessProfile } from "@/types/api"
import { useToast } from "@/hooks/use-toast"
import {
  Loader2,
  Save,
  X,
  Plus,
  Building2,
  Users,
  DollarSign,
  Shield,
  Globe,
  Settings,
  AlertTriangle,
  CheckCircle,
  Info,
} from "lucide-react"

const REVENUE_OPTIONS = ["Under £1M", "£1M-£5M", "£5M-£10M", "£10M-£50M", "£50M-£100M", "£100M-£500M", "Over £500M"]

const DATA_SENSITIVITY_OPTIONS = [
  { value: "Low", label: "Low", description: "Basic business data with minimal privacy concerns" },
  { value: "Moderate", label: "Moderate", description: "Some personal data or business-sensitive information" },
  { value: "High", label: "High", description: "Significant personal data or confidential business information" },
  { value: "Confidential", label: "Confidential", description: "Highly sensitive data requiring maximum protection" },
]

const COMPLIANCE_FRAMEWORKS = [
  "GDPR",
  "ISO 27001",
  "SOC 2",
  "HIPAA",
  "PCI DSS",
  "NIST",
  "ISO 9001",
  "FedRAMP",
  "CCPA",
  "SOX",
]

const CLOUD_PROVIDERS = ["AWS", "Microsoft Azure", "Google Cloud", "IBM Cloud", "Oracle Cloud", "Other"]

const SAAS_TOOLS = [
  "Salesforce",
  "Microsoft 365",
  "Google Workspace",
  "Slack",
  "Zoom",
  "HubSpot",
  "Atlassian",
  "ServiceNow",
  "Workday",
  "Other",
]

const DEVELOPMENT_TOOLS = [
  "GitHub",
  "GitLab",
  "Bitbucket",
  "Jenkins",
  "Docker",
  "Kubernetes",
  "Terraform",
  "Ansible",
  "Other",
]

const INDUSTRIES = [
  "Technology",
  "Healthcare",
  "Financial Services",
  "Manufacturing",
  "Retail",
  "Education",
  "Government",
  "Non-profit",
  "Other",
]

const COUNTRIES = [
  "United Kingdom",
  "United States",
  "Canada",
  "Germany",
  "France",
  "Netherlands",
  "Australia",
  "Other",
]

interface BusinessProfileFormProps {
  mode: "create" | "edit"
}

export function BusinessProfileForm({ mode }: BusinessProfileFormProps) {
  const { id } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingProfile, setIsLoadingProfile] = useState(mode === "edit")
  const [error, setError] = useState<string | null>(null)
  const [profile, setProfile] = useState<BusinessProfile | null>(null)

  const {
    register,
    handleSubmit,
    control,
    setValue,
    watch,
    formState: { errors, isDirty },
    reset,
  } = useForm<BusinessProfileInput>({
    resolver: zodResolver(businessProfileSchema),
    defaultValues: {
      country: "United Kingdom",
      existing_frameworks: [],
      planned_frameworks: [],
      cloud_providers: [],
      saas_tools: [],
      development_tools: [],
      handles_personal_data: false,
      processes_payments: false,
      stores_health_data: false,
      provides_financial_services: false,
      operates_critical_infrastructure: false,
      has_international_operations: false,
      compliance_budget: 0,
    },
  })

  const watchedValues = watch()

  useEffect(() => {
    if (mode === "edit" && id) {
      loadProfile()
    }
  }, [mode, id])

  const loadProfile = async () => {
    if (!id) return

    try {
      setIsLoadingProfile(true)
      const profileData = await businessApi.getProfile(id)
      setProfile(profileData)
      reset({
        company_name: profileData.company_name,
        industry: profileData.industry,
        employee_count: profileData.employee_count,
        annual_revenue: profileData.annual_revenue,
        country: profileData.country,
        data_sensitivity: profileData.data_sensitivity,
        handles_personal_data: profileData.handles_personal_data,
        processes_payments: profileData.processes_payments,
        stores_health_data: profileData.stores_health_data,
        provides_financial_services: profileData.provides_financial_services,
        operates_critical_infrastructure: profileData.operates_critical_infrastructure,
        has_international_operations: profileData.has_international_operations,
        existing_frameworks: profileData.existing_frameworks,
        planned_frameworks: profileData.planned_frameworks,
        cloud_providers: profileData.cloud_providers,
        saas_tools: profileData.saas_tools,
        development_tools: profileData.development_tools,
        compliance_budget: profileData.compliance_budget,
        compliance_timeline: profileData.compliance_timeline,
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load business profile")
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load business profile",
      })
    } finally {
      setIsLoadingProfile(false)
    }
  }

  const onSubmit = async (data: BusinessProfileInput) => {
    setIsLoading(true)
    setError(null)

    try {
      let result: BusinessProfile
      if (mode === "edit" && id) {
        result = await businessApi.updateProfile(id, data)
        toast({
          title: "Profile Updated",
          description: `${data.company_name} has been updated successfully.`,
        })
      } else {
        result = await businessApi.createProfile(data)
        toast({
          title: "Profile Created",
          description: `${data.company_name} has been created successfully.`,
        })
      }
      navigate(`/app/business-profiles/${result.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to ${mode} business profile`)
      toast({
        variant: "destructive",
        title: "Error",
        description: `Failed to ${mode} business profile`,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    if (isDirty) {
      if (window.confirm("You have unsaved changes. Are you sure you want to leave?")) {
        navigate("/app/business-profiles")
      }
    } else {
      navigate("/app/business-profiles")
    }
  }

  const addToArray = (field: keyof BusinessProfileInput, value: string) => {
    const currentValues = watchedValues[field] as string[]
    if (!currentValues.includes(value)) {
      setValue(field, [...currentValues, value], { shouldDirty: true })
    }
  }

  const removeFromArray = (field: keyof BusinessProfileInput, value: string) => {
    const currentValues = watchedValues[field] as string[]
    setValue(
      field,
      currentValues.filter((v) => v !== value),
      { shouldDirty: true },
    )
  }

  if (isLoadingProfile) {
    return (
      <div className="space-y-6">
        <PageHeader title="Loading..." description="Please wait while we load the profile data." />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <div className="h-6 bg-gray-200 rounded animate-pulse" />
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
                </CardHeader>
                <CardContent className="space-y-4">
                  {Array.from({ length: 4 }).map((_, j) => (
                    <div key={j} className="h-10 bg-gray-200 rounded animate-pulse" />
                  ))}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={mode === "edit" ? "Edit Business Profile" : "Create Business Profile"}
        description={
          mode === "edit"
            ? "Update your organization profile and compliance settings"
            : "Set up a new business profile to get personalized compliance recommendations"
        }
        breadcrumbs={[
          { label: "Business Profiles", href: "/app/business-profiles" },
          { label: mode === "edit" ? "Edit Profile" : "New Profile" },
        ]}
      />

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Building2 className="h-5 w-5" />
                  <span>Basic Information</span>
                </CardTitle>
                <CardDescription>Provide basic details about your organization</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="company_name">
                      Company Name <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="company_name"
                      {...register("company_name")}
                      disabled={isLoading}
                      placeholder="Enter company name"
                    />
                    {errors.company_name && <p className="text-sm text-red-600">{errors.company_name.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="industry">
                      Industry <span className="text-red-500">*</span>
                    </Label>
                    <Controller
                      name="industry"
                      control={control}
                      render={({ field }) => (
                        <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select industry" />
                          </SelectTrigger>
                          <SelectContent>
                            {INDUSTRIES.map((industry) => (
                              <SelectItem key={industry} value={industry}>
                                {industry}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    />
                    {errors.industry && <p className="text-sm text-red-600">{errors.industry.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="employee_count">
                      Employee Count <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="employee_count"
                      type="number"
                      {...register("employee_count", { valueAsNumber: true })}
                      disabled={isLoading}
                      placeholder="Number of employees"
                    />
                    {errors.employee_count && <p className="text-sm text-red-600">{errors.employee_count.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="annual_revenue">Annual Revenue</Label>
                    <Controller
                      name="annual_revenue"
                      control={control}
                      render={({ field }) => (
                        <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select revenue range" />
                          </SelectTrigger>
                          <SelectContent>
                            {REVENUE_OPTIONS.map((option) => (
                              <SelectItem key={option} value={option}>
                                {option}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="country">Country</Label>
                    <Controller
                      name="country"
                      control={control}
                      render={({ field }) => (
                        <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select country" />
                          </SelectTrigger>
                          <SelectContent>
                            {COUNTRIES.map((country) => (
                              <SelectItem key={country} value={country}>
                                {country}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="data_sensitivity">Data Sensitivity Level</Label>
                    <Controller
                      name="data_sensitivity"
                      control={control}
                      render={({ field }) => (
                        <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select sensitivity level" />
                          </SelectTrigger>
                          <SelectContent>
                            {DATA_SENSITIVITY_OPTIONS.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                <div>
                                  <div className="font-medium">{option.label}</div>
                                  <div className="text-xs text-gray-500">{option.description}</div>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Business Characteristics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Business Characteristics</span>
                </CardTitle>
                <CardDescription>Select all that apply to your business operations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { key: "handles_personal_data", label: "Handles Personal Data", icon: Users },
                    { key: "processes_payments", label: "Processes Payments", icon: DollarSign },
                    { key: "stores_health_data", label: "Stores Health Data", icon: Shield },
                    { key: "provides_financial_services", label: "Provides Financial Services", icon: DollarSign },
                    {
                      key: "operates_critical_infrastructure",
                      label: "Operates Critical Infrastructure",
                      icon: Settings,
                    },
                    { key: "has_international_operations", label: "Has International Operations", icon: Globe },
                  ].map((item) => {
                    const Icon = item.icon
                    return (
                      <div key={item.key} className="flex items-center space-x-3 p-3 border rounded-lg">
                        <Controller
                          name={item.key as keyof BusinessProfileInput}
                          control={control}
                          render={({ field }) => (
                            <Checkbox
                              id={item.key}
                              checked={field.value as boolean}
                              onCheckedChange={field.onChange}
                              disabled={isLoading}
                            />
                          )}
                        />
                        <Icon className="h-4 w-4 text-gray-500" />
                        <Label htmlFor={item.key} className="text-sm font-medium cursor-pointer">
                          {item.label}
                        </Label>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Compliance Frameworks */}
            <Card>
              <CardHeader>
                <CardTitle>Compliance Frameworks</CardTitle>
                <CardDescription>Select frameworks you currently use or plan to implement</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label className="text-base font-medium">Existing Frameworks</Label>
                  <p className="text-sm text-gray-500 mb-3">Frameworks currently implemented in your organization</p>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {watchedValues.existing_frameworks?.map((framework) => (
                      <Badge key={framework} variant="default" className="flex items-center space-x-1">
                        <span>{framework}</span>
                        <X
                          className="h-3 w-3 cursor-pointer"
                          onClick={() => removeFromArray("existing_frameworks", framework)}
                        />
                      </Badge>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {COMPLIANCE_FRAMEWORKS.filter(
                      (framework) => !watchedValues.existing_frameworks?.includes(framework),
                    ).map((framework) => (
                      <Button
                        key={framework}
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => addToArray("existing_frameworks", framework)}
                        disabled={isLoading}
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        {framework}
                      </Button>
                    ))}
                  </div>
                </div>

                <Separator />

                <div>
                  <Label className="text-base font-medium">Planned Frameworks</Label>
                  <p className="text-sm text-gray-500 mb-3">Frameworks you plan to implement</p>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {watchedValues.planned_frameworks?.map((framework) => (
                      <Badge key={framework} variant="secondary" className="flex items-center space-x-1">
                        <span>{framework}</span>
                        <X
                          className="h-3 w-3 cursor-pointer"
                          onClick={() => removeFromArray("planned_frameworks", framework)}
                        />
                      </Badge>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {COMPLIANCE_FRAMEWORKS.filter(
                      (framework) =>
                        !watchedValues.planned_frameworks?.includes(framework) &&
                        !watchedValues.existing_frameworks?.includes(framework),
                    ).map((framework) => (
                      <Button
                        key={framework}
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => addToArray("planned_frameworks", framework)}
                        disabled={isLoading}
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        {framework}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Technology Stack */}
            <Card>
              <CardHeader>
                <CardTitle>Technology Stack</CardTitle>
                <CardDescription>Select the technologies and tools your organization uses</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {[
                  { key: "cloud_providers", label: "Cloud Providers", options: CLOUD_PROVIDERS },
                  { key: "saas_tools", label: "SaaS Tools", options: SAAS_TOOLS },
                  { key: "development_tools", label: "Development Tools", options: DEVELOPMENT_TOOLS },
                ].map((section) => (
                  <div key={section.key}>
                    <Label className="text-base font-medium">{section.label}</Label>
                    <div className="flex flex-wrap gap-2 mb-3 mt-2">
                      {(watchedValues[section.key as keyof BusinessProfileInput] as string[])?.map((item) => (
                        <Badge key={item} variant="outline" className="flex items-center space-x-1">
                          <span>{item}</span>
                          <X
                            className="h-3 w-3 cursor-pointer"
                            onClick={() => removeFromArray(section.key as keyof BusinessProfileInput, item)}
                          />
                        </Badge>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {section.options
                        .filter(
                          (option) =>
                            !(watchedValues[section.key as keyof BusinessProfileInput] as string[])?.includes(option),
                        )
                        .map((option) => (
                          <Button
                            key={option}
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => addToArray(section.key as keyof BusinessProfileInput, option)}
                            disabled={isLoading}
                          >
                            <Plus className="h-3 w-3 mr-1" />
                            {option}
                          </Button>
                        ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Compliance Planning */}
            <Card>
              <CardHeader>
                <CardTitle>Compliance Planning</CardTitle>
                <CardDescription>Budget and timeline information for compliance initiatives</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="compliance_budget">Annual Compliance Budget (£)</Label>
                    <Input
                      id="compliance_budget"
                      type="number"
                      {...register("compliance_budget", { valueAsNumber: true })}
                      disabled={isLoading}
                      placeholder="0"
                    />
                    {errors.compliance_budget && (
                      <p className="text-sm text-red-600">{errors.compliance_budget.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="compliance_timeline">Compliance Timeline</Label>
                    <Input
                      id="compliance_timeline"
                      {...register("compliance_timeline")}
                      disabled={isLoading}
                      placeholder="e.g., 6 months, 1 year"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Form Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  <Save className="mr-2 h-4 w-4" />
                  {mode === "edit" ? "Update Profile" : "Create Profile"}
                </Button>
                <Button type="button" variant="outline" className="w-full" onClick={handleCancel} disabled={isLoading}>
                  Cancel
                </Button>
              </CardContent>
            </Card>

            {/* Form Status */}
            <Card>
              <CardHeader>
                <CardTitle>Form Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2">
                  {isDirty ? (
                    <>
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm text-yellow-600">Unsaved changes</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm text-green-600">All changes saved</span>
                    </>
                  )}
                </div>
                {Object.keys(errors).length > 0 && (
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <span className="text-sm text-red-600">{Object.keys(errors).length} validation errors</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Help */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Info className="h-4 w-4" />
                  <span>Need Help?</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <p>
                  Business profiles help us provide personalized compliance recommendations based on your organization's
                  specific needs and risk profile.
                </p>
                <Button variant="outline" size="sm" className="w-full">
                  View Documentation
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>
    </div>
  )
}
