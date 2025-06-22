"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useParams, useNavigate, Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { PageHeader } from "@/components/layout/page-header"
import { useToast } from "@/hooks/use-toast"
import {
  FileText,
  Download,
  Edit,
  Trash2,
  Share,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle,
  Calendar,
  Tag,
  BarChart3,
  Eye,
  MessageSquare,
} from "lucide-react"
import { format } from "date-fns"

// Mock evidence data
const mockEvidenceDetail = {
  id: "1",
  title: "Data Protection Policy v2.1",
  description:
    "Comprehensive data protection policy covering GDPR requirements including data processing principles, lawful bases, individual rights, and organizational measures for compliance.",
  framework: "GDPR",
  control_id: "Art. 30",
  evidence_type: "Policy Document",
  status: "approved",
  quality_score: 95,
  tags: ["data-protection", "gdpr", "policy", "privacy", "compliance"],
  created_at: "2024-01-15T10:30:00Z",
  updated_at: "2024-01-15T10:30:00Z",
  file_name: "data-protection-policy-v2.1.pdf",
  file_size: "2.4 MB",
  file_url: "/files/data-protection-policy-v2.1.pdf",
  uploaded_by: "John Doe",
  approved_by: "Jane Smith",
  approved_at: "2024-01-16T09:15:00Z",
  business_profile_id: "bp-1",
  business_profile_name: "TechCorp Ltd",
  source: "Internal Policy Team",
  version: "2.1",
  review_notes: "Policy has been reviewed and approved. All GDPR requirements are adequately covered.",
  related_controls: ["Art. 5", "Art. 6", "Art. 7", "Art. 25", "Art. 32"],
  compliance_score: {
    completeness: 98,
    accuracy: 95,
    relevance: 92,
    timeliness: 90,
  },
  audit_trail: [
    {
      id: "1",
      action: "uploaded",
      user: "John Doe",
      timestamp: "2024-01-15T10:30:00Z",
      details: "Initial upload of policy document",
    },
    {
      id: "2",
      action: "reviewed",
      user: "Jane Smith",
      timestamp: "2024-01-16T08:45:00Z",
      details: "Reviewed for GDPR compliance",
    },
    {
      id: "3",
      action: "approved",
      user: "Jane Smith",
      timestamp: "2024-01-16T09:15:00Z",
      details: "Approved after successful review",
    },
  ],
}

const STATUS_COLORS = {
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  review: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
}

const STATUS_ICONS = {
  approved: CheckCircle,
  pending: Clock,
  review: AlertTriangle,
  rejected: XCircle,
}

export function EvidenceDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [evidence, setEvidence] = useState(mockEvidenceDetail)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadEvidence()
    }
  }, [id])

  const loadEvidence = async () => {
    try {
      setLoading(true)
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))
      setEvidence(mockEvidenceDetail)
    } catch (err: any) {
      setError("Failed to load evidence details")
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load evidence details",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!evidence || !id) return

    if (window.confirm(`Are you sure you want to delete "${evidence.title}"? This action cannot be undone.`)) {
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 500))
        toast({
          title: "Evidence Deleted",
          description: `${evidence.title} has been deleted successfully.`,
        })
        navigate("/app/evidence")
      } catch (err: any) {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to delete evidence. Please try again.",
        })
      }
    }
  }

  const handleDownload = () => {
    // Simulate file download
    toast({
      title: "Download Started",
      description: `Downloading ${evidence.file_name}...`,
    })
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Loading..." description="Please wait while we load the evidence details." />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-1/3" />
                  <Skeleton className="h-4 w-2/3" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Array.from({ length: 4 }).map((_, j) => (
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

  if (error || !evidence) {
    return (
      <div className="space-y-6">
        <PageHeader title="Error" description="Failed to load evidence details" />
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error || "Evidence not found"}</AlertDescription>
        </Alert>
        <Button onClick={() => navigate("/app/evidence")}>Back to Evidence</Button>
      </div>
    )
  }

  const StatusIcon = STATUS_ICONS[evidence.status as keyof typeof STATUS_ICONS]

  return (
    <div className="space-y-6">
      <PageHeader
        title={evidence.title}
        description={`${evidence.framework} • ${evidence.control_id} • ${evidence.evidence_type}`}
        breadcrumbs={[{ label: "Evidence Management", href: "/app/evidence" }, { label: evidence.title }]}
        actions={
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button variant="outline" size="sm">
              <Share className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button variant="outline" size="sm" asChild>
              <Link to={`/app/evidence/${evidence.id}/edit`}>
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
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-600" />
                  <div>
                    <CardTitle className="text-xl">{evidence.title}</CardTitle>
                    <CardDescription>{evidence.description}</CardDescription>
                  </div>
                </div>
                <Badge className={STATUS_COLORS[evidence.status as keyof typeof STATUS_COLORS]}>
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {evidence.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <BarChart3 className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                  <div className="text-2xl font-bold">{evidence.quality_score}%</div>
                  <div className="text-sm text-gray-500">Quality Score</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <Eye className="h-6 w-6 mx-auto mb-2 text-green-600" />
                  <div className="text-lg font-bold">{evidence.version}</div>
                  <div className="text-sm text-gray-500">Version</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <FileText className="h-6 w-6 mx-auto mb-2 text-purple-600" />
                  <div className="text-lg font-bold">{evidence.file_size}</div>
                  <div className="text-sm text-gray-500">File Size</div>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <Calendar className="h-6 w-6 mx-auto mb-2 text-orange-600" />
                  <div className="text-lg font-bold">{format(new Date(evidence.updated_at), "MMM d")}</div>
                  <div className="text-sm text-gray-500">Last Updated</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Compliance Details */}
          <Card>
            <CardHeader>
              <CardTitle>Compliance Details</CardTitle>
              <CardDescription>Framework and control information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-500">Framework</Label>
                  <p className="text-lg font-medium">{evidence.framework}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Control ID</Label>
                  <p className="text-lg font-medium">{evidence.control_id}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Evidence Type</Label>
                  <p className="text-lg font-medium">{evidence.evidence_type}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Source</Label>
                  <p className="text-lg font-medium">{evidence.source}</p>
                </div>
              </div>

              <Separator />

              <div>
                <Label className="text-sm font-medium text-gray-500 mb-2 block">Related Controls</Label>
                <div className="flex flex-wrap gap-2">
                  {evidence.related_controls.map((control) => (
                    <Badge key={control} variant="outline">
                      {control}
                    </Badge>
                  ))}
                </div>
              </div>

              <Separator />

              <div>
                <Label className="text-sm font-medium text-gray-500 mb-2 block">Tags</Label>
                <div className="flex flex-wrap gap-2">
                  {evidence.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="flex items-center space-x-1">
                      <Tag className="h-3 w-3" />
                      <span>{tag}</span>
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quality Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Quality Metrics</CardTitle>
              <CardDescription>Detailed quality assessment breakdown</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(evidence.compliance_score).map(([metric, score]) => (
                <div key={metric} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium capitalize">{metric}</span>
                    <span className="text-gray-500">{score}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${score}%` }} />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Audit Trail */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5" />
                <span>Audit Trail</span>
              </CardTitle>
              <CardDescription>History of changes and reviews</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {evidence.audit_trail.map((entry, index) => (
                  <div key={entry.id} className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium text-blue-600 dark:text-blue-300">{index + 1}</span>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {entry.action.charAt(0).toUpperCase() + entry.action.slice(1)}
                        </p>
                        <span className="text-sm text-gray-500">by {entry.user}</span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{entry.details}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {format(new Date(entry.timestamp), "MMM d, yyyy 'at' h:mm a")}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
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
              <Button className="w-full" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                Download File
              </Button>
              <Button variant="outline" className="w-full" asChild>
                <Link to={`/app/evidence/${evidence.id}/edit`}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Evidence
                </Link>
              </Button>
              <Button variant="outline" className="w-full">
                <Share className="h-4 w-4 mr-2" />
                Share Evidence
              </Button>
              <Separator />
              <Button variant="destructive" className="w-full" onClick={handleDelete}>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Evidence
              </Button>
            </CardContent>
          </Card>

          {/* File Information */}
          <Card>
            <CardHeader>
              <CardTitle>File Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">File Name</span>
                <span className="font-medium">{evidence.file_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">File Size</span>
                <span className="font-medium">{evidence.file_size}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Uploaded By</span>
                <span className="font-medium">{evidence.uploaded_by}</span>
              </div>
              {evidence.approved_by && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Approved By</span>
                  <span className="font-medium">{evidence.approved_by}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Business Profile */}
          <Card>
            <CardHeader>
              <CardTitle>Business Profile</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="font-medium">{evidence.business_profile_name}</p>
                <Button variant="outline" size="sm" className="w-full" asChild>
                  <Link to={`/app/business-profiles/${evidence.business_profile_id}`}>View Profile</Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Review Notes */}
          {evidence.review_notes && (
            <Card>
              <CardHeader>
                <CardTitle>Review Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">{evidence.review_notes}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={className}>{children}</div>
}
