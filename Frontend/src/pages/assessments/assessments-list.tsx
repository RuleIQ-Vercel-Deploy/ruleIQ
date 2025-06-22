"use client"

import { useState } from "react"
import { Link } from "react-router-dom"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Search, Plus, MoreHorizontal, Play, Eye, Trash2, Copy, Calendar } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Assessment } from "@/types/api"

// Mock data - replace with actual API calls
const mockAssessments: Assessment[] = [
  {
    id: "1",
    title: "GDPR Compliance Assessment",
    description: "Comprehensive GDPR readiness evaluation",
    framework: "GDPR",
    business_profile_id: "bp1",
    status: "completed",
    progress: 100,
    score: 142,
    max_score: 180,
    started_at: "2024-01-15T10:00:00Z",
    completed_at: "2024-01-20T16:45:00Z",
    created_at: "2024-01-15T10:00:00Z",
    updated_at: "2024-01-20T16:45:00Z",
    questions_count: 36,
    answered_count: 36,
  },
  {
    id: "2",
    title: "ISO 27001 Security Assessment",
    description: "Information security management evaluation",
    framework: "ISO27001",
    business_profile_id: "bp1",
    status: "in_progress",
    progress: 65,
    started_at: "2024-01-18T09:00:00Z",
    created_at: "2024-01-18T09:00:00Z",
    updated_at: "2024-01-22T14:30:00Z",
    questions_count: 48,
    answered_count: 31,
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
  {
    id: "4",
    title: "HIPAA Security Rule Assessment",
    description: "Healthcare data protection compliance",
    framework: "HIPAA",
    business_profile_id: "bp2",
    status: "reviewed",
    progress: 100,
    score: 89,
    max_score: 120,
    started_at: "2024-01-10T08:00:00Z",
    completed_at: "2024-01-16T17:30:00Z",
    created_at: "2024-01-10T08:00:00Z",
    updated_at: "2024-01-18T10:15:00Z",
    questions_count: 42,
    answered_count: 42,
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

export function AssessmentsList() {
  const [assessments, setAssessments] = useState<Assessment[]>(mockAssessments)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedFramework, setSelectedFramework] = useState<string>("")
  const [selectedStatus, setSelectedStatus] = useState<string>("")
  const [loading, setLoading] = useState(false)

  // Filter assessments based on search and filters
  const filteredAssessments = assessments.filter((assessment) => {
    const matchesSearch =
      assessment.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      assessment.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFramework = !selectedFramework || assessment.framework === selectedFramework
    const matchesStatus = !selectedStatus || assessment.status === selectedStatus

    return matchesSearch && matchesFramework && matchesStatus
  })

  const handleDeleteAssessment = async (id: string) => {
    if (confirm("Are you sure you want to delete this assessment?")) {
      setAssessments((prev) => prev.filter((a) => a.id !== id))
    }
  }

  const handleDuplicateAssessment = async (assessment: Assessment) => {
    const newAssessment: Assessment = {
      ...assessment,
      id: `${assessment.id}_copy_${Date.now()}`,
      title: `${assessment.title} (Copy)`,
      status: "draft",
      progress: 0,
      score: undefined,
      max_score: undefined,
      started_at: undefined,
      completed_at: undefined,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      answered_count: 0,
    }
    setAssessments((prev) => [newAssessment, ...prev])
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Compliance Assessments</h1>
          <p className="text-gray-600 dark:text-gray-300">Manage and track your compliance assessments</p>
        </div>
        <Button asChild>
          <Link to="/app/assessments/new">
            <Plus className="h-4 w-4 mr-2" />
            New Assessment
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search assessments..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedFramework} onValueChange={setSelectedFramework}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="All Frameworks" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Frameworks</SelectItem>
                <SelectItem value="GDPR">GDPR</SelectItem>
                <SelectItem value="ISO27001">ISO 27001</SelectItem>
                <SelectItem value="SOC2">SOC 2</SelectItem>
                <SelectItem value="HIPAA">HIPAA</SelectItem>
                <SelectItem value="PCI-DSS">PCI-DSS</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="reviewed">Reviewed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Assessments List */}
      <div className="space-y-4">
        {filteredAssessments.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <div className="text-gray-500 dark:text-gray-400">
                <Calendar className="mx-auto h-12 w-12 mb-4" />
                <h3 className="text-lg font-medium mb-2">No assessments found</h3>
                <p className="mb-4">
                  {searchQuery || selectedFramework || selectedStatus
                    ? "Try adjusting your search criteria"
                    : "Get started by creating your first assessment"}
                </p>
                <Button asChild>
                  <Link to="/app/assessments/new">
                    <Plus className="h-4 w-4 mr-2" />
                    Create Assessment
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredAssessments.map((assessment) => (
            <Card key={assessment.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                        {assessment.title}
                      </h3>
                      <Badge className={getStatusColor(assessment.status)}>{assessment.status.replace("_", " ")}</Badge>
                      <Badge variant="outline">{assessment.framework}</Badge>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">{assessment.description}</p>
                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <span>
                        Questions: {assessment.answered_count}/{assessment.questions_count}
                      </span>
                      {assessment.score && assessment.max_score && (
                        <span>
                          Score: {assessment.score}/{assessment.max_score}(
                          {Math.round((assessment.score / assessment.max_score) * 100)}%)
                        </span>
                      )}
                      <span>Updated: {new Date(assessment.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4 ml-6">
                    <div className="text-right">
                      <div className="w-32 mb-1">
                        <Progress value={assessment.progress} className="h-2" />
                      </div>
                      <span className="text-xs text-gray-500">{assessment.progress}% complete</span>
                    </div>

                    <div className="flex space-x-2">
                      {assessment.status === "completed" || assessment.status === "reviewed" ? (
                        <Button asChild variant="outline" size="sm">
                          <Link to={`/app/assessments/${assessment.id}/results`}>
                            <Eye className="h-4 w-4 mr-1" />
                            Results
                          </Link>
                        </Button>
                      ) : (
                        <Button asChild size="sm">
                          <Link to={`/app/assessments/${assessment.id}`}>
                            <Play className="h-4 w-4 mr-1" />
                            {assessment.status === "draft" ? "Start" : "Continue"}
                          </Link>
                        </Button>
                      )}

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link to={`/app/assessments/${assessment.id}`}>
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleDuplicateAssessment(assessment)}>
                            <Copy className="h-4 w-4 mr-2" />
                            Duplicate
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => handleDeleteAssessment(assessment.id)}
                            className="text-red-600 dark:text-red-400"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
