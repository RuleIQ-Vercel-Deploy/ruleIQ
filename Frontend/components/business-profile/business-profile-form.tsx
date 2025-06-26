"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Loader2, Building2, Users, Globe, Shield, Cloud, Code, DollarSign } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/hooks/use-toast"

import { businessProfileSchema, type BusinessProfileInput } from "@/lib/validators"
import { businessProfileApi, INDUSTRY_OPTIONS, EMPLOYEE_COUNT_RANGES, ANNUAL_REVENUE_OPTIONS, COUNTRY_OPTIONS, DATA_SENSITIVITY_OPTIONS, COMPLIANCE_FRAMEWORKS, CLOUD_PROVIDERS, SAAS_TOOLS, DEVELOPMENT_TOOLS, COMPLIANCE_TIMELINE_OPTIONS } from "@/api/business-profiles"
import type { BusinessProfile } from "@/types/api"
import { formatValidationErrors } from "@/lib/utils"

interface BusinessProfileFormProps {
  initialData?: BusinessProfile
  onSuccess?: (profile: BusinessProfile) => void
  onCancel?: () => void
}

export function BusinessProfileForm({ initialData, onSuccess, onCancel }: BusinessProfileFormProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const form = useForm<BusinessProfileInput>({
    resolver: zodResolver(businessProfileSchema),
    defaultValues: {
      company_name: initialData?.company_name || "",
      industry: initialData?.industry || "",
      employee_count: initialData?.employee_count || 1,
      annual_revenue: initialData?.annual_revenue || "",
      country: initialData?.country || "United Kingdom",
      data_sensitivity: initialData?.data_sensitivity || "Low",
      handles_personal_data: initialData?.handles_personal_data || false,
      processes_payments: initialData?.processes_payments || false,
      stores_health_data: initialData?.stores_health_data || false,
      provides_financial_services: initialData?.provides_financial_services || false,
      operates_critical_infrastructure: initialData?.operates_critical_infrastructure || false,
      has_international_operations: initialData?.has_international_operations || false,
      existing_frameworks: initialData?.existing_frameworks || [],
      planned_frameworks: initialData?.planned_frameworks || [],
      cloud_providers: initialData?.cloud_providers || [],
      saas_tools: initialData?.saas_tools || [],
      development_tools: initialData?.development_tools || [],
      compliance_budget: initialData?.compliance_budget || undefined,
      compliance_timeline: initialData?.compliance_timeline || "",
    },
  })

  const mutation = useMutation({
    mutationFn: businessProfileApi.createOrUpdate,
    onSuccess: (data) => {
      toast({
        title: "Success",
        description: "Business profile saved successfully",
      })
      queryClient.invalidateQueries({ queryKey: ["business-profile"] })
      onSuccess?.(data)
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: formatValidationErrors(error),
        variant: "destructive",
      })
    },
  })

  const onSubmit = (data: BusinessProfileInput) => {
    mutation.mutate(data)
  }

  const nextStep = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const steps = [
    { number: 1, title: "Company Info", icon: Building2 },
    { number: 2, title: "Business Details", icon: Users },
    { number: 3, title: "Technology Stack", icon: Cloud },
    { number: 4, title: "Compliance", icon: Shield },
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Steps */}
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const Icon = step.icon
          const isActive = currentStep === step.number
          const isCompleted = currentStep > step.number
          
          return (
            <div key={step.number} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                isActive ? "border-primary bg-primary text-primary-foreground" :
                isCompleted ? "border-green-500 bg-green-500 text-white" :
                "border-muted-foreground text-muted-foreground"
              }`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="ml-2">
                <div className={`text-sm font-medium ${isActive ? "text-primary" : isCompleted ? "text-green-600" : "text-muted-foreground"}`}>
                  {step.title}
                </div>
              </div>
              {index < steps.length - 1 && (
                <div className={`w-16 h-0.5 mx-4 ${isCompleted ? "bg-green-500" : "bg-muted"}`} />
              )}
            </div>
          )
        })}
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Step 1: Company Information */}
          {currentStep === 1 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="w-5 h-5" />
                  Company Information
                </CardTitle>
                <CardDescription>
                  Tell us about your company and its basic details
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <FormField
                  control={form.control}
                  name="company_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Company Name *</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter your company name" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="industry"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Industry *</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select your industry" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {INDUSTRY_OPTIONS.map((industry) => (
                              <SelectItem key={industry} value={industry}>
                                {industry}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="country"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Country</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select your country" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {COUNTRY_OPTIONS.map((country) => (
                              <SelectItem key={country} value={country}>
                                {country}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="employee_count"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Number of Employees *</FormLabel>
                        <Select onValueChange={(value) => field.onChange(parseInt(value))} defaultValue={field.value?.toString()}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select employee count" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {EMPLOYEE_COUNT_RANGES.map((range) => (
                              <SelectItem key={range.value} value={range.value.toString()}>
                                {range.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="annual_revenue"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Annual Revenue</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select revenue range" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {ANNUAL_REVENUE_OPTIONS.map((revenue) => (
                              <SelectItem key={revenue} value={revenue}>
                                {revenue}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 2: Business Details */}
          {currentStep === 2 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Business Details
                </CardTitle>
                <CardDescription>
                  Help us understand your business operations and data handling
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <FormField
                  control={form.control}
                  name="data_sensitivity"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Data Sensitivity Level</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select data sensitivity level" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {DATA_SENSITIVITY_OPTIONS.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormDescription>
                        This helps us recommend appropriate compliance frameworks
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Separator />

                <div>
                  <h4 className="text-sm font-medium mb-4">Business Operations</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="handles_personal_data"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel>Handles Personal Data</FormLabel>
                            <FormDescription>
                              Customer information, employee records, etc.
                            </FormDescription>
                          </div>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="processes_payments"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel>Processes Payments</FormLabel>
                            <FormDescription>
                              Credit cards, bank transfers, etc.
                            </FormDescription>
                          </div>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="stores_health_data"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel>Stores Health Data</FormLabel>
                            <FormDescription>
                              Medical records, health information
                            </FormDescription>
                          </div>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="provides_financial_services"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel>Provides Financial Services</FormLabel>
                            <FormDescription>
                              Banking, insurance, investment services
                            </FormDescription>
                          </div>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="operates_critical_infrastructure"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel>Critical Infrastructure</FormLabel>
                            <FormDescription>
                              Power, water, transportation, etc.
                            </FormDescription>
                          </div>
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="has_international_operations"
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel>International Operations</FormLabel>
                            <FormDescription>
                              Operations outside your home country
                            </FormDescription>
                          </div>
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 3: Technology Stack */}
          {currentStep === 3 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cloud className="w-5 h-5" />
                  Technology Stack
                </CardTitle>
                <CardDescription>
                  Tell us about the technology and tools your organization uses
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <FormLabel className="text-base">Cloud Providers</FormLabel>
                  <FormDescription className="mb-3">
                    Select all cloud providers your organization uses
                  </FormDescription>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {CLOUD_PROVIDERS.map((provider) => (
                      <FormField
                        key={provider}
                        control={form.control}
                        name="cloud_providers"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(provider)}
                                onCheckedChange={(checked) => {
                                  const current = field.value || []
                                  if (checked) {
                                    field.onChange([...current, provider])
                                  } else {
                                    field.onChange(current.filter((item) => item !== provider))
                                  }
                                }}
                              />
                            </FormControl>
                            <FormLabel className="text-sm font-normal">
                              {provider}
                            </FormLabel>
                          </FormItem>
                        )}
                      />
                    ))}
                  </div>
                </div>

                <Separator />

                <div>
                  <FormLabel className="text-base">SaaS Tools</FormLabel>
                  <FormDescription className="mb-3">
                    Select the SaaS tools and platforms you use
                  </FormDescription>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {SAAS_TOOLS.map((tool) => (
                      <FormField
                        key={tool}
                        control={form.control}
                        name="saas_tools"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(tool)}
                                onCheckedChange={(checked) => {
                                  const current = field.value || []
                                  if (checked) {
                                    field.onChange([...current, tool])
                                  } else {
                                    field.onChange(current.filter((item) => item !== tool))
                                  }
                                }}
                              />
                            </FormControl>
                            <FormLabel className="text-sm font-normal">
                              {tool}
                            </FormLabel>
                          </FormItem>
                        )}
                      />
                    ))}
                  </div>
                </div>

                <Separator />

                <div>
                  <FormLabel className="text-base">Development Tools</FormLabel>
                  <FormDescription className="mb-3">
                    Select the development and DevOps tools you use
                  </FormDescription>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {DEVELOPMENT_TOOLS.map((tool) => (
                      <FormField
                        key={tool}
                        control={form.control}
                        name="development_tools"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(tool)}
                                onCheckedChange={(checked) => {
                                  const current = field.value || []
                                  if (checked) {
                                    field.onChange([...current, tool])
                                  } else {
                                    field.onChange(current.filter((item) => item !== tool))
                                  }
                                }}
                              />
                            </FormControl>
                            <FormLabel className="text-sm font-normal">
                              {tool}
                            </FormLabel>
                          </FormItem>
                        )}
                      />
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 4: Compliance */}
          {currentStep === 4 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Compliance Information
                </CardTitle>
                <CardDescription>
                  Tell us about your current and planned compliance requirements
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <FormLabel className="text-base">Existing Compliance Frameworks</FormLabel>
                  <FormDescription className="mb-3">
                    Select frameworks you are currently compliant with
                  </FormDescription>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {COMPLIANCE_FRAMEWORKS.map((framework) => (
                      <FormField
                        key={framework}
                        control={form.control}
                        name="existing_frameworks"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(framework)}
                                onCheckedChange={(checked) => {
                                  const current = field.value || []
                                  if (checked) {
                                    field.onChange([...current, framework])
                                  } else {
                                    field.onChange(current.filter((item) => item !== framework))
                                  }
                                }}
                              />
                            </FormControl>
                            <FormLabel className="text-sm font-normal">
                              {framework}
                            </FormLabel>
                          </FormItem>
                        )}
                      />
                    ))}
                  </div>
                </div>

                <Separator />

                <div>
                  <FormLabel className="text-base">Planned Compliance Frameworks</FormLabel>
                  <FormDescription className="mb-3">
                    Select frameworks you plan to achieve compliance with
                  </FormDescription>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {COMPLIANCE_FRAMEWORKS.map((framework) => (
                      <FormField
                        key={framework}
                        control={form.control}
                        name="planned_frameworks"
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(framework)}
                                onCheckedChange={(checked) => {
                                  const current = field.value || []
                                  if (checked) {
                                    field.onChange([...current, framework])
                                  } else {
                                    field.onChange(current.filter((item) => item !== framework))
                                  }
                                }}
                              />
                            </FormControl>
                            <FormLabel className="text-sm font-normal">
                              {framework}
                            </FormLabel>
                          </FormItem>
                        )}
                      />
                    ))}
                  </div>
                </div>

                <Separator />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="compliance_budget"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Annual Compliance Budget (£)</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="e.g. 50000"
                            {...field}
                            onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                          />
                        </FormControl>
                        <FormDescription>
                          Optional: Helps us recommend cost-effective solutions
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="compliance_timeline"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Compliance Timeline</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select timeline" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {COMPLIANCE_TIMELINE_OPTIONS.map((timeline) => (
                              <SelectItem key={timeline} value={timeline}>
                                {timeline}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormDescription>
                          When do you need to achieve compliance?
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <Button
              type="button"
              variant="outline"
              onClick={currentStep === 1 ? onCancel : prevStep}
            >
              {currentStep === 1 ? "Cancel" : "Previous"}
            </Button>

            {currentStep < 4 ? (
              <Button type="button" onClick={nextStep}>
                Next
              </Button>
            ) : (
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {initialData ? "Update Profile" : "Create Profile"}
              </Button>
            )}
          </div>
        </form>
      </Form>
    </div>
  )
}
