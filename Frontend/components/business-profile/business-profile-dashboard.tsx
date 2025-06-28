"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Edit, Building2, Users, Globe, Shield, Cloud, Code, DollarSign, Calendar, CheckCircle, AlertCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"

import { businessProfileApi } from "@/lib/api/business-profiles"
import { BusinessProfileForm } from "./business-profile-form"
import type { BusinessProfile } from "@/lib/types/api"

interface BusinessProfileDashboardProps {
  onProfileUpdate?: (profile: BusinessProfile) => void
}

export function BusinessProfileDashboard({ onProfileUpdate }: BusinessProfileDashboardProps) {
  const [isEditing, setIsEditing] = useState(false)

  const { data: profile, isLoading, error, refetch } = useQuery({
    queryKey: ["business-profile"],
    queryFn: businessProfileApi.get,
    retry: false,
  })

  const handleEditSuccess = (updatedProfile: BusinessProfile) => {
    setIsEditing(false)
    refetch()
    onProfileUpdate?.(updatedProfile)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-24" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Business Profile</h1>
        </div>
        
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No business profile found. Create one to get started with compliance assessments.
          </AlertDescription>
        </Alert>

        <BusinessProfileForm
          onSuccess={handleEditSuccess}
          onCancel={() => setIsEditing(false)}
        />
      </div>
    )
  }

  if (isEditing) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Edit Business Profile</h1>
        </div>
        
        <BusinessProfileForm
          initialData={profile}
          onSuccess={handleEditSuccess}
          onCancel={() => setIsEditing(false)}
        />
      </div>
    )
  }

  const completionPercentage = calculateCompletionPercentage(profile)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{profile.company_name}</h1>
          <p className="text-muted-foreground">Business Profile Overview</p>
        </div>
        <Button onClick={() => setIsEditing(true)}>
          <Edit className="mr-2 h-4 w-4" />
          Edit Profile
        </Button>
      </div>

      {/* Completion Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Profile Completion
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="flex justify-between text-sm mb-2">
                <span>Completion</span>
                <span>{completionPercentage}%</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{ width: `${completionPercentage}%` }}
                />
              </div>
            </div>
            <Badge variant={completionPercentage === 100 ? "default" : "secondary"}>
              {completionPercentage === 100 ? "Complete" : "Incomplete"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Profile Information Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Company Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Company Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm font-medium">Industry</p>
              <p className="text-sm text-muted-foreground">{profile.industry}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Country</p>
              <p className="text-sm text-muted-foreground">{profile.country}</p>
            </div>
            <div>
              <p className="text-sm font-medium">Employees</p>
              <p className="text-sm text-muted-foreground">{profile.employee_count.toLocaleString()}</p>
            </div>
            {profile.annual_revenue && (
              <div>
                <p className="text-sm font-medium">Annual Revenue</p>
                <p className="text-sm text-muted-foreground">{profile.annual_revenue}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Business Operations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Business Operations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm font-medium">Data Sensitivity</p>
              <Badge variant="outline">{profile.data_sensitivity}</Badge>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Operations</p>
              <div className="flex flex-wrap gap-1">
                {profile.handles_personal_data && <Badge variant="secondary" className="text-xs">Personal Data</Badge>}
                {profile.processes_payments && <Badge variant="secondary" className="text-xs">Payments</Badge>}
                {profile.stores_health_data && <Badge variant="secondary" className="text-xs">Health Data</Badge>}
                {profile.provides_financial_services && <Badge variant="secondary" className="text-xs">Financial Services</Badge>}
                {profile.operates_critical_infrastructure && <Badge variant="secondary" className="text-xs">Critical Infrastructure</Badge>}
                {profile.has_international_operations && <Badge variant="secondary" className="text-xs">International</Badge>}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Technology Stack */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cloud className="h-5 w-5" />
              Technology Stack
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {profile.cloud_providers && profile.cloud_providers.length > 0 && (
              <div>
                <p className="text-sm font-medium">Cloud Providers</p>
                <div className="flex flex-wrap gap-1">
                  {profile.cloud_providers.map((provider) => (
                    <Badge key={provider} variant="outline" className="text-xs">
                      {provider}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {profile.saas_tools && profile.saas_tools.length > 0 && (
              <div>
                <p className="text-sm font-medium">SaaS Tools</p>
                <div className="flex flex-wrap gap-1">
                  {profile.saas_tools.slice(0, 3).map((tool) => (
                    <Badge key={tool} variant="outline" className="text-xs">
                      {tool}
                    </Badge>
                  ))}
                  {profile.saas_tools.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{profile.saas_tools.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Compliance Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Compliance Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {profile.existing_frameworks && profile.existing_frameworks.length > 0 && (
              <div>
                <p className="text-sm font-medium">Current Compliance</p>
                <div className="flex flex-wrap gap-1">
                  {profile.existing_frameworks.map((framework) => (
                    <Badge key={framework} variant="default" className="text-xs">
                      {framework}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {profile.planned_frameworks && profile.planned_frameworks.length > 0 && (
              <div>
                <p className="text-sm font-medium">Planned Compliance</p>
                <div className="flex flex-wrap gap-1">
                  {profile.planned_frameworks.map((framework) => (
                    <Badge key={framework} variant="secondary" className="text-xs">
                      {framework}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Budget & Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Budget & Timeline
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {profile.compliance_budget && (
              <div>
                <p className="text-sm font-medium">Annual Budget</p>
                <p className="text-sm text-muted-foreground">£{profile.compliance_budget.toLocaleString()}</p>
              </div>
            )}
            {profile.compliance_timeline && (
              <div>
                <p className="text-sm font-medium">Timeline</p>
                <p className="text-sm text-muted-foreground">{profile.compliance_timeline}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Profile Metadata */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Profile Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm font-medium">Created</p>
              <p className="text-sm text-muted-foreground">
                {new Date(profile.created_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium">Last Updated</p>
              <p className="text-sm text-muted-foreground">
                {new Date(profile.updated_at).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function calculateCompletionPercentage(profile: BusinessProfile): number {
  const fields = [
    profile.company_name,
    profile.industry,
    profile.employee_count,
    profile.country,
    profile.annual_revenue,
    profile.data_sensitivity,
    profile.cloud_providers?.length,
    profile.saas_tools?.length,
    profile.existing_frameworks?.length || profile.planned_frameworks?.length,
    profile.compliance_timeline,
  ]

  const completedFields = fields.filter(field => 
    field !== undefined && field !== null && field !== "" && field !== 0
  ).length

  return Math.round((completedFields / fields.length) * 100)
}
