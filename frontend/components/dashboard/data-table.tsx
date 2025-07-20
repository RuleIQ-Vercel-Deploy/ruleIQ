"use client"

import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react"
import * as React from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ProgressBar } from "@/components/ui/progress-bar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

interface AssessmentData {
  id: number | string
  assessment: string
  status: "Completed" | "In Progress" | "Overdue" | "Scheduled" | "Under Review"
  progress: number
  date: string
}

// Default sample data for when no assessments are provided
const defaultData: AssessmentData[] = [
  {
    id: 1,
    assessment: "GDPR Data Protection Audit",
    status: "Overdue",
    progress: 75,
    date: "2024-01-15",
  },
  {
    id: 2,
    assessment: "Financial Reporting Compliance",
    status: "In Progress",
    progress: 45,
    date: "2024-02-20",
  },
  {
    id: 3,
    assessment: "Health & Safety Review",
    status: "Scheduled",
    progress: 0,
    date: "2024-03-10",
  },
  {
    id: 4,
    assessment: "ISO 27001 Security Assessment",
    status: "Completed",
    progress: 100,
    date: "2024-01-08",
  },
  {
    id: 5,
    assessment: "Environmental Impact Evaluation",
    status: "In Progress",
    progress: 62,
    date: "2024-02-28",
  },
  {
    id: 6,
    assessment: "Employee Training Compliance",
    status: "Under Review",
    progress: 88,
    date: "2024-01-25",
  },
  {
    id: 7,
    assessment: "Risk Management Framework",
    status: "Completed",
    progress: 100,
    date: "2024-01-12",
  },
  {
    id: 8,
    assessment: "Anti-Money Laundering Check",
    status: "In Progress",
    progress: 33,
    date: "2024-03-05",
  },
  {
    id: 9,
    assessment: "Cybersecurity Policy Review",
    status: "Scheduled",
    progress: 0,
    date: "2024-03-15",
  },
  {
    id: 10,
    assessment: "Quality Management System",
    status: "Overdue",
    progress: 55,
    date: "2024-01-30",
  },
]

const getStatusColor = (status: string) => {
  switch (status) {
    case "Completed":
      return "bg-success/20 text-success border-success/40"
    case "In Progress":
      return "bg-info/20 text-info border-info/40"
    case "Overdue":
      return "bg-error/20 text-error border-error/40"
    case "Scheduled":
      return "bg-muted text-muted-foreground border-border"
    case "Under Review":
      return "bg-warning/20 text-warning border-warning/40"
    default:
      return "bg-muted text-muted-foreground border-border"
  }
}

const getProgressColor = (progress: number, status: string) => {
  if (status === "Completed") return "success"
  if (status === "Overdue") return "error"
  if (progress >= 75) return "success"
  if (progress >= 50) return "warning"
  return "info"
}

interface DataTableProps {
  className?: string
  assessments?: any[]
}

export function DataTable({ className, assessments }: DataTableProps) {
  const [currentPage, setCurrentPage] = React.useState(1)
  const itemsPerPage = 5
  
  // Transform API data to match our interface or use default data
  const data = React.useMemo(() => {
    if (!assessments || assessments.length === 0) {
      return defaultData
    }
    
    // Transform recent activities into assessment format
    return assessments
      .filter(activity => activity.type === 'assessment')
      .slice(0, 10)
      .map((activity, index) => ({
        id: activity.id || index + 1,
        assessment: activity.description || activity.action || 'Assessment',
        status: getStatusFromActivity(activity),
        progress: getProgressFromActivity(activity),
        date: activity.timestamp || new Date().toISOString()
      }))
  }, [assessments])
  
  const totalPages = Math.ceil(data.length / itemsPerPage)

  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentData = data.slice(startIndex, endIndex)

  const goToFirstPage = () => setCurrentPage(1)
  const goToLastPage = () => setCurrentPage(totalPages)
  const goToPreviousPage = () => setCurrentPage(Math.max(1, currentPage - 1))
  const goToNextPage = () => setCurrentPage(Math.min(totalPages, currentPage + 1))
  
  // Helper function to determine status from activity
  function getStatusFromActivity(activity: any): AssessmentData['status'] {
    const action = activity.action?.toLowerCase() || ''
    if (action.includes('completed') || action.includes('passed')) return 'Completed'
    if (action.includes('in progress') || action.includes('started')) return 'In Progress'
    if (action.includes('overdue') || action.includes('expired')) return 'Overdue'
    if (action.includes('scheduled') || action.includes('planned')) return 'Scheduled'
    if (action.includes('review')) return 'Under Review'
    return 'In Progress'
  }
  
  // Helper function to determine progress from activity
  function getProgressFromActivity(activity: any): number {
    const action = activity.action?.toLowerCase() || ''
    if (action.includes('completed') || action.includes('passed')) return 100
    if (action.includes('started')) return 25
    if (action.includes('in progress')) return 50
    if (action.includes('review')) return 75
    return 0
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Table Container */}
      <div className="rounded-lg border border-border overflow-hidden bg-card">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-border bg-muted/50">
              <TableHead className="font-semibold text-left px-6 py-4">
                Assessment
              </TableHead>
              <TableHead className="font-semibold text-center px-6 py-4">
                Status
              </TableHead>
              <TableHead className="font-semibold text-center px-6 py-4">
                Progress
              </TableHead>
              <TableHead className="font-semibold text-right px-6 py-4">
                Date
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {currentData.map((item) => (
              <TableRow
                key={item.id}
                className="hover:bg-muted/50 transition-colors border-b border-border"
              >
                <TableCell className="px-6 py-4">
                  <div className="font-medium">
                    {item.assessment}
                  </div>
                </TableCell>
                <TableCell className="px-6 py-4 text-center">
                  <Badge variant="outline" className={`${getStatusColor(item.status)} font-medium`}>
                    {item.status}
                  </Badge>
                </TableCell>
                <TableCell className="px-6 py-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-medium">
                        {item.progress}%
                      </span>
                    </div>
                    <ProgressBar
                      value={item.progress}
                      color={getProgressColor(item.progress, item.status)}
                      className="h-2"
                    />
                  </div>
                </TableCell>
                <TableCell className="px-6 py-4 text-right">
                  <span className="text-sm font-medium">
                    {new Date(item.date).toLocaleDateString("en-GB", {
                      day: "2-digit",
                      month: "short",
                      year: "numeric",
                    })}
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing {startIndex + 1} to {Math.min(endIndex, data.length)} of {data.length} assessments
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={goToFirstPage}
            disabled={currentPage === 1}
            className="h-8 w-8 p-0"
          >
            <ChevronsLeft className="h-4 w-4" />
            <span className="sr-only">Go to first page</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={goToPreviousPage}
            disabled={currentPage === 1}
            className="h-8 w-8 p-0"
          >
            <ChevronLeft className="h-4 w-4" />
            <span className="sr-only">Go to previous page</span>
          </Button>

          <div className="flex items-center space-x-1">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <Button
                key={page}
                variant={currentPage === page ? "default" : "outline"}
                size="sm"
                onClick={() => setCurrentPage(page)}
                className="h-8 w-8 p-0"
              >
                {page}
              </Button>
            ))}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={goToNextPage}
            disabled={currentPage === totalPages}
            className="h-8 w-8 p-0"
          >
            <ChevronRight className="h-4 w-4" />
            <span className="sr-only">Go to next page</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={goToLastPage}
            disabled={currentPage === totalPages}
            className="h-8 w-8 p-0"
          >
            <ChevronsRight className="h-4 w-4" />
            <span className="sr-only">Go to last page</span>
          </Button>
        </div>
      </div>
    </div>
  )
}
