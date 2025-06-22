"use client"

import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { PageHeader } from "@/components/layout/page-header"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "@/hooks/use-toast"
import { FileText, Upload, CheckCircle, Clock, TrendingUp, BarChart3, Filter, Download } from "lucide-react"

// Mock data - replace with actual API calls
const mockStats = {
  totalEvidence: 127,
  approvedEvidence: 89,
  pendingReview: 23,
  rejectedEvidence: 15,
  qualityScore: 78,
  recentUploads: 12,
  frameworkCoverage: {
    GDPR: 85,
    "ISO 27001": 72,
    "SOC 2": 45,
    HIPAA: 90,
  },
  evidenceByType: {
    "Policy Document": 45,
    "Technical Control": 32,
    "Training Record": 28,
    "Audit Report": 22,
  },
  recentActivity: [
    {
      id: "1",
      title: "Data Protection Policy v2.1",
      action: "uploaded",
      framework: "GDPR",
      time: "2 hours ago",
      status: "pending",
    },
    {
      id: "2",
      title: "Security Awareness Training Records",
      action: "approved",
      framework: "ISO 27001",
      time: "4 hours ago",
      status: "approved",
    },
    {
      id: "3",
      title: "Incident Response Procedure",
      action: "updated",
      framework: "SOC 2",
      time: "1 day ago",
      status: "approved",
    },
    {
      id: "4",
      title: "Access Control Matrix",
      action: "uploaded",
      framework: "HIPAA",
      time: "2 days ago",
      status: "review",
    },
  ],
}

const STATUS_COLORS = {
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  review: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
}

export function EvidenceDashboard() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(mockStats)
  const { toast } = useToast()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))
      setStats(mockStats)
    } catch (error) {
      console.error("Failed to load dashboard data:", error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load dashboard data. Please try again.",
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Evidence Management" description="Loading dashboard..." />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16 mb-2" />
                <Skeleton className="h-3 w-20" />
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
        title="Evidence Management"
        description="Manage compliance evidence, documentation, and supporting materials"
        actions={
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
            <Button asChild>
              <Link to="/app/evidence/upload">
                <Upload className="h-4 w-4 mr-2" />
                Upload Evidence
              </Link>
            </Button>
          </div>
        }
      />

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Evidence</CardTitle>
            <FileText className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.totalEvidence}</div>
            <p className="text-xs text-muted-foreground">+{stats.recentUploads} this week</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.approvedEvidence}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((stats.approvedEvidence / stats.totalEvidence) * 100)}% of total
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-yellow-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Review</CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.pendingReview}</div>
            <p className="text-xs text-muted-foreground">Requires attention</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Quality Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats.qualityScore}%</div>
            <p className="text-xs text-muted-foreground">+5% from last month</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Framework Coverage */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Framework Coverage</span>
            </CardTitle>
            <CardDescription>Evidence coverage by compliance framework</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(stats.frameworkCoverage).map(([framework, coverage]) => (
              <div key={framework} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{framework}</span>
                  <span className="text-gray-500">{coverage}%</span>
                </div>
                <Progress value={coverage} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Evidence by Type */}
        <Card>
          <CardHeader>
            <CardTitle>Evidence by Type</CardTitle>
            <CardDescription>Distribution of evidence types</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(stats.evidenceByType).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <span className="text-sm font-medium">{type}</span>
                <Badge variant="secondary">{count}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common evidence management tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Button asChild className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/app/evidence/upload">
                <Upload className="h-5 w-5" />
                <span className="font-medium">Upload Evidence</span>
                <span className="text-xs opacity-80">Add new documentation</span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/app/evidence?status=pending">
                <Clock className="h-5 w-5" />
                <span className="font-medium">Review Pending</span>
                <span className="text-xs opacity-80">{stats.pendingReview} items waiting</span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/app/evidence?view=grid">
                <Filter className="h-5 w-5" />
                <span className="font-medium">Browse All</span>
                <span className="text-xs opacity-80">View and filter evidence</span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/app/reports/evidence">
                <BarChart3 className="h-5 w-5" />
                <span className="font-medium">Generate Report</span>
                <span className="text-xs opacity-80">Evidence summary report</span>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest evidence uploads and updates</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats.recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                <div className="flex-shrink-0">
                  {activity.action === "uploaded" && <Upload className="h-5 w-5 text-blue-500" />}
                  {activity.action === "approved" && <CheckCircle className="h-5 w-5 text-green-500" />}
                  {activity.action === "updated" && <FileText className="h-5 w-5 text-purple-500" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{activity.title}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {activity.framework}
                    </Badge>
                    <span className="text-xs text-gray-500">{activity.time}</span>
                  </div>
                </div>
                <Badge className={STATUS_COLORS[activity.status as keyof typeof STATUS_COLORS]}>
                  {activity.status}
                </Badge>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center">
            <Button variant="outline" asChild>
              <Link to="/app/evidence">View All Evidence</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
