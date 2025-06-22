"use client"

import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { PageHeader } from "@/components/layout/page-header"
import { businessApi } from "@/api/business"
import { useToast } from "@/hooks/use-toast"
import type { BusinessProfile } from "@/types/api"
import { Plus, Search, Download } from "lucide-react"
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import { ResponsiveCard } from "@/components/ui/responsive-card"
import { ResponsiveTable } from "@/components/ui/responsive-table"
import { useResponsive } from "@/hooks/use-responsive"

const DATA_SENSITIVITY_COLORS = {
  Low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  Moderate: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  High: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
  Confidential: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
}

export function BusinessProfilesList() {
  const [profiles, setProfiles] = useState<BusinessProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [deleteProfile, setDeleteProfile] = useState<BusinessProfile | null>(null)
  const [selectedIndustry, setSelectedIndustry] = useState<string>("")
  const [selectedSensitivity, setSelectedSensitivity] = useState<string>("")
  const { toast } = useToast()
  const navigate = useNavigate()
  const { isMobile } = useResponsive()

  useEffect(() => {
    loadProfiles()
  }, [])

  const loadProfiles = async () => {
    try {
      setLoading(true)
      const data = await businessApi.getProfiles()
      setProfiles(data)
    } catch (error) {
      console.error("Failed to load business profiles:", error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load business profiles. Please try again.",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (profile: BusinessProfile) => {
    try {
      await businessApi.deleteProfile(profile.id)
      setProfiles(profiles.filter((p) => p.id !== profile.id))
      toast({
        title: "Profile Deleted",
        description: `${profile.company_name} has been deleted successfully.`,
      })
    } catch (error) {
      console.error("Failed to delete profile:", error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to delete profile. Please try again.",
      })
    } finally {
      setDeleteProfile(null)
    }
  }

  const filteredProfiles = profiles.filter((profile) => {
    const matchesSearch =
      profile.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      profile.industry.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesIndustry = !selectedIndustry || profile.industry === selectedIndustry
    const matchesSensitivity = !selectedSensitivity || profile.data_sensitivity === selectedSensitivity

    return matchesSearch && matchesIndustry && matchesSensitivity
  })

  const industries = Array.from(new Set(profiles.map((p) => p.industry)))
  const sensitivities = ["Low", "Moderate", "High", "Confidential"]

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Business Profiles" description="Loading profiles..." />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="h-8 w-1/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Business Profiles"
        description="Manage your organization profiles and compliance settings"
        actions={
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button asChild>
              <Link to="/app/business-profiles/new">
                <Plus className="h-4 w-4 mr-2" />
                New Profile
              </Link>
            </Button>
          </div>
        }
      />

      {/* Search and Filters */}
      <ResponsiveCard>
        <div className={cn("flex gap-4", isMobile ? "flex-col" : "flex-row")}>
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search profiles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={cn("pl-10", isMobile && "h-12 text-base")}
            />
          </div>
          <div className={cn("flex gap-2", isMobile && "flex-col")}>
            <select
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className={cn(
                "px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500",
                isMobile && "h-12 text-base",
              )}
            >
              <option value="">All Industries</option>
              {industries.map((industry) => (
                <option key={industry} value={industry}>
                  {industry}
                </option>
              ))}
            </select>
            <select
              value={selectedSensitivity}
              onChange={(e) => setSelectedSensitivity(e.target.value)}
              className={cn(
                "px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500",
                isMobile && "h-12 text-base",
              )}
            >
              <option value="">All Sensitivity Levels</option>
              {sensitivities.map((sensitivity) => (
                <option key={sensitivity} value={sensitivity}>
                  {sensitivity}
                </option>
              ))}
            </select>
          </div>
        </div>
      </ResponsiveCard>

      {/* Profiles Grid */}
      <ResponsiveTable
        data={filteredProfiles}
        columns={[
          {
            key: "company_name",
            label: "Company",
            render: (value, profile) => (
              <div className="flex items-center space-x-3">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300">
                    {value.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="font-medium">{value}</div>
                  <div className="text-sm text-gray-500">{profile.industry}</div>
                </div>
              </div>
            ),
            mobileLabel: "Company",
          },
          {
            key: "data_sensitivity",
            label: "Sensitivity",
            render: (value) => <Badge className={DATA_SENSITIVITY_COLORS[value]}>{value}</Badge>,
            mobileLabel: "Data Sensitivity",
          },
          {
            key: "employee_count",
            label: "Employees",
            render: (value) => value.toLocaleString(),
            mobileLabel: "Employees",
          },
          {
            key: "created_at",
            label: "Created",
            render: (value) => format(new Date(value), "MMM d, yyyy"),
            mobileHidden: true,
          },
        ]}
        onRowClick={(profile) => navigate(`/app/business-profiles/${profile.id}`)}
        onRowAction={(profile) => {
          // Handle row actions
        }}
        loading={loading}
        emptyMessage={
          searchQuery || selectedIndustry || selectedSensitivity
            ? "No profiles match your current filters."
            : "Get started by creating your first business profile."
        }
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteProfile} onOpenChange={() => setDeleteProfile(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Business Profile</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deleteProfile?.company_name}"? This action cannot be undone and will
              remove all associated data.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteProfile && handleDelete(deleteProfile)}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete Profile
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
