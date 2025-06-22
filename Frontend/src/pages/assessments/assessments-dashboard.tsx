"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { BarChart3, FileText, Clock, CheckCircle, Plus, TrendingUp, Target } from "lucide-react"
import { Link } from "react-router-dom"
import type { Assessment } from "@/types/api"

// Mock data - replace with actual API calls
const mockAssessments: Assessment[] = [
  {
    id: "1",
    title: "GDPR Compliance Assessment",
    description: "Comprehensive GDPR readiness evaluation",
    framework: "GDPR",
    business_profile_id: "bp1",
    status: "in_progress",
    progress: 65,
    score: 78,
    max_score: 120,
    started_at: "2024-01-15T10:00:00Z",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-20T14:30:00Z",
    questions_count: 45,
    answered_count: 29,
  },
  {
    id: "2",
    title: "ISO 27001 Security Assessment",
    description: "Information security management evaluation",
    framework: "ISO27001",
    business_profile_id: "bp1",
    status: "completed",
    progress: 100,
    score: 142,
    max_score: 180,
    started_at: "2024-01-10T09:00:00Z",
    completed_at: "2024-01-18T16:45:00Z",
    created_at: "2024-01-10T09:00:00Z",
    updated_at: "2024-01-18T16:45:00Z",
    questions_count: 60,
    answered_count: 60,
  },
  {
    id: "3",
    title: "SOC 2 Type II Readiness",
    description: "Service organization control assessment",
    framework: "SOC2",
    business_profile_id: "bp1",
    status: "draft",
    progress: 0,
    created_at: "2024-01-22T11:00:00Z",
    updated_at: "2024-01-22T11:00:00Z",
    questions_count: 38,
    answered_count: 0,
  },
]

const getStatusColor = (status: Assessment["status"]) => {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
    case "in_progress":
      return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
    case "reviewed":
      return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300"
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
  }
}

const getStatusIcon = (status: Assessment["status"]) => {
  switch (status) {
    case "completed":
      return <CheckCircle className="h-4 w-4" />
    case "in_progress":
      return <Clock className="h-4 w-4" />
    case "reviewed":
      return <Target className="h-4 w-4" />
    default:
      return <FileText className="h-4 w-4" />
  }
}

export function AssessmentsDashboard() {
  const [assessments, setAssessments] = useState<Assessment[]>(mockAssessments)
  const [loading, setLoading] = useState(false)

  // Calculate dashboard metrics
  const totalAssessments = assessments.length
  const completedAssessments = assessments.filter((a) => a.status === "completed").length
  const inProgressAssessments = assessments.filter((a) => a.status === "in_progress").length
  const averageScore =
    assessments.filter((a) => a.score && a.max_score).reduce((acc, a) => acc + (a.score! / a.max_score!) * 100, 0) /
      assessments.filter((a) => a.score && a.max_score).length || 0

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Compliance Assessments</h1>
        <p className="text-gray-600 dark:text-gray-300">Evaluate your compliance posture across different frameworks</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Assessments</CardTitle>
            <FileText className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{totalAssessments}</div>
            <p className="text-xs text-muted-foreground">Across all frameworks</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{completedAssessments}</div>
            <p className="text-xs text-muted-foreground">Ready for review</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{inProgressAssessments}</div>
            <p className="text-xs text-muted-foreground">Active assessments</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{Math.round(averageScore)}%</div>
            <p className="text-xs text-muted-foreground">Compliance readiness</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Start a new assessment or continue existing ones</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button asChild className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/app/assessments/new">
                <Plus className="h-5 w-5" />
                <span className="font-medium">New Assessment</span>
                <span className="text-xs opacity-80">Start from template</span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/app/assessments/templates">
                <FileText className="h-5 w-5" />
                <span className="font-medium">Browse Templates</span>
                <span className="text-xs opacity-80">Framework-specific assessments</span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-start space-y-2">
              <Link to="/app/assessments/reports">
                <BarChart3 className="h-5 w-5" />
                <span className="font-medium">View Reports</span>
                <span className="text-xs opacity-80">Assessment analytics</span>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Active Assessments */}
      <Card>
        <CardHeader>
          <CardTitle>Your Assessments</CardTitle>
          <CardDescription>Current and completed compliance assessments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {assessments.map((assessment) => (
              <div
                key={assessment.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">{getStatusIcon(assessment.status)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">{assessment.title}</h3>
                      <Badge className={getStatusColor(assessment.status)}>{assessment.status.replace("_", " ")}</Badge>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{assessment.description}</p>
                    <div className="flex items-center space-x-4 mt-2">
                      <span className="text-xs text-gray-500">Framework: {assessment.framework}</span>
                      <span className="text-xs text-gray-500">
                        Progress: {assessment.answered_count}/{assessment.questions_count} questions
                      </span>
                      {assessment.score && assessment.max_score && (
                        <span className="text-xs text-gray-500">
                          Score: {assessment.score}/{assessment.max_score} (
                          {Math.round((assessment.score / assessment.max_score) * 100)}%)
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-24">
                    <Progress value={assessment.progress} className="h-2" />
                    <span className="text-xs text-gray-500 mt-1">{assessment.progress}%</span>
                  </div>
                  <div className="flex space-x-2">
                    {assessment.status === "completed" ? (
                      <Button asChild variant="outline" size="sm">
                        <Link to={`/app/assessments/${assessment.id}/results`}>View Results</Link>
                      </Button>
                    ) : (
                      <Button asChild size="sm">
                        <Link to={`/app/assessments/${assessment.id}`}>
                          {assessment.status === "draft" ? "Start" : "Continue"}
                        </Link>
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Framework Coverage */}
      <Card>
        <CardHeader>
          <CardTitle>Framework Coverage</CardTitle>
          <CardDescription>Your compliance assessment coverage by framework</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {["GDPR", "ISO27001", "SOC2", "HIPAA", "PCI-DSS"].map((framework) => {
              const frameworkAssessments = assessments.filter((a) => a.framework === framework)
              const completedCount = frameworkAssessments.filter((a) => a.status === "completed").length
              const totalCount = frameworkAssessments.length
              const coverage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0

              return (
                <div key={framework} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-sm">{framework}</span>
                    <span className="text-xs text-gray-500">
                      {completedCount}/{totalCount} completed
                    </span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-32">
                      <Progress value={coverage} className="h-2" />
                    </div>
                    <span className="text-xs text-gray-500 w-12 text-right">{Math.round(coverage)}%</span>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
