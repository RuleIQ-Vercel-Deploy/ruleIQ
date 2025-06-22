"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { businessProfileSchema, type BusinessProfileInput } from "@/lib/validators"
import { businessApi } from "@/api/business"
import type { BusinessProfile } from "@/types/api"
import { Loader2 } from "lucide-react"

interface BusinessProfileFormProps {
  profile?: BusinessProfile
  onSuccess?: (profile: BusinessProfile) => void
  onCancel?: () => void
}

const REVENUE_OPTIONS = ["Under £1M", "£1M-£5M", "£5M-£10M", "£10M-£50M", "£50M-£100M", "Over £100M"]

const DATA_SENSITIVITY_OPTIONS = [
  { value: "Low", label: "Low" },
  { value: "Moderate", label: "Moderate" },
  { value: "High", label: "High" },
  { value: "Confidential", label: "Confidential" },
]

export function BusinessProfileForm({ profile, onSuccess, onCancel }: BusinessProfileFormProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<BusinessProfileInput>({
    resolver: zodResolver(businessProfileSchema),
    defaultValues: profile
      ? {
          company_name: profile.company_name,
          industry: profile.industry,
          employee_count: profile.employee_count,
          annual_revenue: profile.annual_revenue,
          country: profile.country,
          data_sensitivity: profile.data_sensitivity,
          handles_personal_data: profile.handles_personal_data,
          processes_payments: profile.processes_payments,
          stores_health_data: profile.stores_health_data,
          provides_financial_services: profile.provides_financial_services,
          operates_critical_infrastructure: profile.operates_critical_infrastructure,
          has_international_operations: profile.has_international_operations,
          existing_frameworks: profile.existing_frameworks,
          planned_frameworks: profile.planned_frameworks,
          cloud_providers: profile.cloud_providers,
          saas_tools: profile.saas_tools,
          development_tools: profile.development_tools,
          compliance_budget: profile.compliance_budget,
          compliance_timeline: profile.compliance_timeline,
        }
      : {
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
        },
  })

  const onSubmit = async (data: BusinessProfileInput) => {
    setIsLoading(true)
    setError(null)

    try {
      let result: BusinessProfile
      if (profile) {
        result = await businessApi.updateProfile(profile.id, data)
      } else {
        result = await businessApi.createProfile(data)
      }
      onSuccess?.(result)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to save business profile")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>{profile ? "Edit Business Profile" : "Create Business Profile"}</CardTitle>
        <CardDescription>
          Provide information about your business to get personalized compliance recommendations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="company_name">Company Name *</Label>
              <Input id="company_name" {...register("company_name")} disabled={isLoading} />
              {errors.company_name && <p className="text-sm text-red-600">{errors.company_name.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="industry">Industry *</Label>
              <Input id="industry" {...register("industry")} disabled={isLoading} />
              {errors.industry && <p className="text-sm text-red-600">{errors.industry.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="employee_count">Employee Count *</Label>
              <Input
                id="employee_count"
                type="number"
                {...register("employee_count", { valueAsNumber: true })}
                disabled={isLoading}
              />
              {errors.employee_count && <p className="text-sm text-red-600">{errors.employee_count.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="annual_revenue">Annual Revenue</Label>
              <Select onValueChange={(value) => setValue("annual_revenue", value)}>
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
            </div>

            <div className="space-y-2">
              <Label htmlFor="country">Country</Label>
              <Input id="country" {...register("country")} disabled={isLoading} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="data_sensitivity">Data Sensitivity</Label>
              <Select onValueChange={(value) => setValue("data_sensitivity", value as any)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select data sensitivity" />
                </SelectTrigger>
                <SelectContent>
                  {DATA_SENSITIVITY_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-4">
            <Label className="text-base font-medium">Business Characteristics</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: "handles_personal_data", label: "Handles Personal Data" },
                { key: "processes_payments", label: "Processes Payments" },
                { key: "stores_health_data", label: "Stores Health Data" },
                { key: "provides_financial_services", label: "Provides Financial Services" },
                { key: "operates_critical_infrastructure", label: "Operates Critical Infrastructure" },
                { key: "has_international_operations", label: "Has International Operations" },
              ].map((item) => (
                <div key={item.key} className="flex items-center space-x-2">
                  <Checkbox id={item.key} {...register(item.key as keyof BusinessProfileInput)} />
                  <Label htmlFor={item.key} className="text-sm">
                    {item.label}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="compliance_budget">Compliance Budget (£)</Label>
              <Input
                id="compliance_budget"
                type="number"
                {...register("compliance_budget", { valueAsNumber: true })}
                disabled={isLoading}
              />
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

          <div className="flex justify-end space-x-4">
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
                Cancel
              </Button>
            )}
            <Button type="submit" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {profile ? "Update Profile" : "Create Profile"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
