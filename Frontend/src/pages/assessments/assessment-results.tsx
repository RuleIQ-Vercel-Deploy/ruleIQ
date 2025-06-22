"use client"

import { useState } from "react"
import { useParams, Link } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Download, Share, AlertTriangle, CheckCircle, Target, FileText } from "lucide-react"
import type { AssessmentResult, Assessment } from "@/types/api"

// Mock data - replace with actual API calls
const mockResult: AssessmentResult = {
  id: "r1",
  assessment_id: "1",
  overall_score: 142,
  max_score: 180,
  percentage: 79,
  section_scores: [
    { section: "Governance", score: 28, max_score: 35, percentage: 80, questions_count: 7, answered_count: 7 },
    { section: "Data Management", score: 32, max_score: 40, percentage: 80, questions_count: 8, answered_count: 8 },
    { section: "Security", score: 45, max_score: 60, percentage: 75, questions_count: 12, answered_count: 12 },
    { section: "Training", score: 18, max_score: 25, percentage: 72, questions_count: 5, answered_count: 5 },
    { section: "Documentation", score: 19, max_score: 20, percentage: 95, questions_count: 4, answered_count: 4 },
  ],
  recommendations: [
    {
      id: "rec1",
      title: "Implement Data Loss Prevention (DLP)",
      description: "Deploy DLP solutions to monitor and protect sensitive data across your organization.",
      priority: "high",
      category: "Security",
      estimated_effort: "2-3 months",
    },
    {
      id: "rec2",
      title: "Enhance Privacy Training Program",
      description: "Develop role-specific privacy training modules and implement regular assessments.",
      priority: "medium",
      category: "Training",
      estimated_effort: "1-2 months",
    },
    {
      id: "rec3",
      title: "Update Incident Response Procedures",
      description: "Review and update incident response procedures to align with GDPR requirements.",
      priority: "medium",
      category: "Governance",
      estimated_effort: "2-4 weeks",
    },
  ],
  gaps: [
    {
      id: "gap1",
      control_reference: "GDPR Art. 32",
      description: "Technical and organizational security measures need improvement",
      current_score: 15,
      target_score: 20,
      impact: "high",
    },
    {
      id: "gap2",
      control_reference: "GDPR Art. 39",
      description: "Privacy awareness training effectiveness could be enhanced",
      current_score: 18,
      target_score: 25,
      impact: "medium",
    },
  ],
  created_at: "2024-01-20T16:45:00Z",
}

const mockAssessment: Assessment = {
  id: "1",
  title: "GDPR Compliance Assessment",
  description: "Comprehensive GDPR readiness evaluation",
  framework: "GDPR",
  business_profile_id: "bp1",
  status: "completed",
  progress: 100,
  score: 142,
  max_score: 180,
  completed_at: "2024-01-20T16:45:00Z",
  created_at: "2024-01-15T10:00:00Z",
  updated_at: "2024-01-20T16:45:00Z",
  questions_count: 36,
  answered_count: 36,
}

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case "critical":
      return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
    case "high":
      return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300"
    case "medium":
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
    default:
      return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
  }
}

const getImpactColor = (impact: string) => {
  switch (impact) {
    case "high":
      return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
    case "medium":
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
    default:
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
  }
}

export function AssessmentResults() {
  const { id } = useParams<{ id: string }>()
  const [assessment, setAssessment] = useState<Assessment>(mockAssessment)
  const [result, setResult] = useState<AssessmentResult>(mockResult)
  const [loading, setLoading] = useState(false)

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return "text-green-600"
    if (percentage >= 75) return "text-blue-600"
    if (percentage >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreLabel = (percentage: number) => {
    if (percentage >= 90) return "Excellent"
    if (percentage >= 75) return "Good"
    if (percentage >= 60) return "Fair"
    return "Needs Improvement"
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Assessment Results</h1>
          <p className="text-gray-600 dark:text-gray-300">
            {assessment.title} - Completed on {new Date(assessment.completed_at!).toLocaleDateString()}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Share className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export PDF
          </Button>
          <Button asChild>
            <Link to={`/app/assessments/${assessment.id}`}>Review Answers</Link>
          </Button>
        </div>
      </div>

      {/* Overall Score */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Overall Compliance Score</span>
            <Badge
              className={getPriorityColor(
                result.percentage >= 75 ? "low" : result.percentage >= 60 ? "medium" : "high",
              )}
            >
              {getScoreLabel(result.percentage)}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className={`text-4xl font-bold ${getScoreColor(result.percentage)}`}>{result.percentage}%</div>
              <p className="text-sm text-gray-500">
                {result.overall_score} / {result.max_score} points
              </p>
            </div>
            <div className="flex-1">
              <Progress value={result.percentage} className="h-4" />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="sections">By Section</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="gaps">Gap Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Questions Answered</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{assessment.answered_count}</div>
                <p className="text-xs text-muted-foreground">of {assessment.questions_count} total</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
                <Target className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">100%</div>
                <p className="text-xs text-muted-foreground">All sections completed</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">High Priority Items</CardTitle>
                <AlertTriangle className="h-4 w-4 text-orange-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {result.recommendations.filter((r) => r.priority === "high").length}
                </div>
                <p className="text-xs text-muted-foreground">Require immediate attention</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Framework</CardTitle>
                <FileText className="h-4 w-4 text-purple-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{assessment.framework}</div>
                <p className="text-xs text-muted-foreground">Compliance framework</p>
              </CardContent>
            </Card>
          </div>

          {/* Section Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Section Performance</CardTitle>
              <CardDescription>Breakdown of scores by assessment section</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.section_scores.map((section) => (
                  <div key={section.section} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{section.section}</span>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">
                          {section.score}/{section.max_score}
                        </span>
                        <span className={`font-medium ${getScoreColor(section.percentage)}`}>
                          {section.percentage}%
                        </span>
                      </div>
                    </div>
                    <Progress value={section.percentage} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sections" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.section_scores.map((section) => (
              <Card key={section.section}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{section.section}</span>
                    <Badge
                      className={
                        getScoreColor(section.percentage).includes("green")
                          ? "bg-green-100 text-green-800"
                          : getScoreColor(section.percentage).includes("blue")
                            ? "bg-blue-100 text-blue-800"
                            : getScoreColor(section.percentage).includes("yellow")
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-red-100 text-red-800"
                      }
                    >
                      {section.percentage}%
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span>
                      Score: {section.score} / {section.max_score}
                    </span>
                    <span>
                      Questions: {section.answered_count} / {section.questions_count}
                    </span>
                  </div>
                  <Progress value={section.percentage} className="h-3" />
                  <p className="text-sm text-gray-600">
                    {getScoreLabel(section.percentage)} -{" "}
                    {section.percentage >= 90
                      ? "Excellent compliance in this area"
                      : section.percentage >= 75
                        ? "Good compliance with minor improvements needed"
                        : section.percentage >= 60
                          ? "Fair compliance with several areas for improvement"
                          : "Significant improvements needed in this area"}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <div className="space-y-4">
            {result.recommendations.map((recommendation) => (
              <Card key={recommendation.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-lg">{recommendation.title}</span>
                    <div className="flex space-x-2">
                      <Badge className={getPriorityColor(recommendation.priority)}>{recommendation.priority}</Badge>
                      <Badge variant="outline">{recommendation.category}</Badge>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-gray-600 dark:text-gray-300">{recommendation.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Estimated effort: {recommendation.estimated_effort}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="gaps" className="space-y-6">
          <div className="space-y-4">
            {result.gaps.map((gap) => (
              <Card key={gap.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{gap.control_reference}</span>
                    <Badge className={getImpactColor(gap.impact)}>{gap.impact} impact</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-600 dark:text-gray-300">{gap.description}</p>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Current Score</span>
                      <span>Target Score</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="flex-1">
                        <Progress value={(gap.current_score / gap.target_score) * 100} className="h-2" />
                      </div>
                      <span className="text-sm font-medium">
                        {gap.current_score} / {gap.target_score}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
