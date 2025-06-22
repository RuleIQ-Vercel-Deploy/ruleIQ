"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useParams, useNavigate, Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { PageHeader } from "@/components/layout/page-header"
import { businessApi } from "@/api/business"
import { useToast } from "@/hooks/use-toast"
import type { BusinessProfile } from "@/types/api"
import {
  Edit,
  Trash2,
  Users,
  DollarSign,
  Globe,
  Shield,
  Calendar,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Download,
  Share,
  BarChart3,
} from "lucide-react"
import { format } from "date-fns"

const DATA_SENSITIVITY_COLORS = {
  Low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  Moderate: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  High: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
  Confidential: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
}

export function BusinessProfileDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [profile, setProfile] = useState<BusinessProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadProfile()
    }
  }, [id])

  const loadProfile = async () => {
    if (!id) return

    try {
      setLoading(true)
      const data = await businessApi.getProfile(id)
      setProfile(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load business profile")
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load business profile",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!profile || !id) return

    if (
      window.confirm(
        `Are you sure you want to delete "${profile.company_name}"? This action cannot be undone and will remove all associated data.`,
      )
    ) {
      try {
        await businessApi.deleteProfile(id)
        toast({
          title: "Profile Deleted",
          description: `${profile.company_name} has been deleted successfully.`,
        })
        navigate("/app/business-profiles")
      } catch (err: any) {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to delete profile. Please try again.",
        })
      }
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Loading..." description="Please wait while we load the profile data." />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-1/3" />
                  <Skeleton className="h-4 w-2/3" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Array.from({ length: 3 }).map((_, j) => (
                      <Skeleton key={j} className="h-4 w-full" />
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="space-y-6">
        <PageHeader title="Error" description="Failed to load business profile" />
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error || "Profile not found"}</AlertDescription>
        </Alert>
        <Button onClick={() => navigate("/app/business-profiles")}>Back to Profiles</Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={profile.company_name}
        description={`${profile.industry} • ${profile.employee_count.toLocaleString()} employees`}
        breadcrumbs={[{ label: "Business Profiles", href: "/app/business-profiles" }, { label: profile.company_name }]}
        actions={
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Share className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm" asChild>
              <Link to={`/app/business-profiles/${profile.id}/edit`}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Link>
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Overview */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-4">
                <Avatar className="h-16 w-16">
                  <AvatarFallback className="bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300 text-xl">
                    {profile.company_name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <CardTitle className="text-2xl">{profile.company_name}</CardTitle>
                  <CardDescription className="text-lg">{profile.industry}</CardDescription>
                  <div className="flex items-center space-x-4 mt-2">
                    <Badge className={DATA_SENSITIVITY_COLORS[profile.data_sensitivity]}>
                      {profile.data_sensitivity} Sensitivity
                    </Badge>
                    <span className="text-sm text-gray-500">
                      Created {format(new Date(profile.created_at), "MMMM d, yyyy")}
                    </span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <Users className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                  <div className="text-2xl font-bold">{profile.employee_count.toLocaleString()}</div>
                  <div className="text-sm text-gray-500">Employees</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <DollarSign className="h-6 w-6 mx-auto mb-2 text-green-600" />
                  <div className="text-lg font-bold">{profile.annual_revenue}</div>
                  <div className="text-sm text-gray-500">Revenue</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <Globe className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                  <div className="text-lg font-bold">{profile.country}</div>
                  <div className="text-sm text-gray-500">Location</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <BarChart3 className="h-6 w-6 mx-auto mb-2 text-orange-600" />
                  <div className="text-lg font-bold">£{profile.compliance_budget.toLocaleString()}</div>
                  <div className="text-sm text-gray-500">Budget</div>
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
              <CardDescription>Data handling and operational characteristics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  {
                    key: "handles_personal_data",
                    label: "Handles Personal Data",
                    value: profile.handles_personal_data,
                  },
                  { key: "processes_payments", label: "Processes Payments", value: profile.processes_payments },
                  { key: "stores_health_data", label: "Stores Health Data", value: profile.stores_health_data },
                  {
                    key: "provides_financial_services",
                    label: "Provides Financial Services",
                    value: profile.provides_financial_services,
                  },
                  {
                    key: "operates_critical_infrastructure",
                    label: "Operates Critical Infrastructure",
                    value: profile.operates_critical_infrastructure,
                  },
                  {
                    key: "has_international_operations",
                    label: "Has International Operations",
                    value: profile.has_international_operations,
                  },
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between p-3 border rounded-lg">
                    <span className="text-sm font-medium">{item.label}</span>
                    {item.value ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-gray-400" />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Compliance Frameworks */}
          <Card>
            <CardHeader>
              <CardTitle>Compliance Frameworks</CardTitle>
              <CardDescription>Current and planned compliance implementations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="font-medium mb-3 flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Existing Frameworks</span>
                </h4>
                {profile.existing_frameworks.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {profile.existing_frameworks.map((framework) => (
                      <Badge key={framework} variant="default">
                        {framework}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No existing frameworks</p>
                )}
              </div>

              <Separator />

              <div>
                <h4 className="font-medium mb-3 flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-blue-600" />
                  <span>Planned Frameworks</span>
                </h4>
                {profile.planned_frameworks.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {profile.planned_frameworks.map((framework) => (
                      <Badge key={framework} variant="secondary">
                        {framework}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No planned frameworks</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Technology Stack */}
          <Card>
            <CardHeader>
              <CardTitle>Technology Stack</CardTitle>
              <CardDescription>Cloud providers, SaaS tools, and development technologies</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {[
                { label: "Cloud Providers", items: profile.cloud_providers },
                { label: "SaaS Tools", items: profile.saas_tools },
                { label: "Development Tools", items: profile.development_tools },
              ].map((section) => (
                <div key={section.label}>
                  <h4 className="font-medium mb-3">{section.label}</h4>
                  {section.items.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {section.items.map((item) => (
                        <Badge key={item} variant="outline">
                          {item}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">None specified</p>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button asChild className="w-full">
                <Link to={`/app/business-profiles/${profile.id}/edit`}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Profile
                </Link>
              </Button>
              <Button variant="outline" className="w-full">
                <BarChart3 className="h-4 w-4 mr-2" />
                Generate Report
              </Button>
              <Button variant="outline" className="w-full">
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
              <Separator />
              <Button variant="destructive" className="w-full" onClick={handleDelete}>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Profile
              </Button>
            </CardContent>
          </Card>

          {/* Compliance Planning */}
          <Card>
            <CardHeader>
              <CardTitle>Compliance Planning</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-sm font-medium">Annual Budget</Label>
                <p className="text-2xl font-bold">£{profile.compliance_budget.toLocaleString()}</p>
              </div>
              {profile.compliance_timeline && (
                <div>
                  <Label className="text-sm font-medium">Timeline</Label>
                  <p className="text-lg">{profile.compliance_timeline}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Profile Information */}
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Created</span>
                <span>{format(new Date(profile.created_at), "MMM d, yyyy")}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Last Updated</span>
                <span>{format(new Date(profile.updated_at), "MMM d, yyyy")}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Profile ID</span>
                <span className="font-mono text-xs">{profile.id}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={className}>{children}</div>
}
