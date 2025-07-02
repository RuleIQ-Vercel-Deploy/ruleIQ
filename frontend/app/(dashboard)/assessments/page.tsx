"use client"

import { Plus, ClipboardCheck, Shield, Clock, CheckCircle, AlertCircle } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"

import { columns } from "@/components/assessments/columns"
import { DataTable } from "@/components/assessments/data-table"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { assessmentService } from "@/lib/api/assessments.service"


import type { Assessment } from "@/types/api"

export default function AssessmentsPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [totalCount, setTotalCount] = useState(0)
  
  useEffect(() => {
    fetchAssessments()
  }, [])
  
  const fetchAssessments = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await assessmentService.getAssessments({
        page: 1,
        page_size: 50
      })
      setAssessments(response.items)
      setTotalCount(response.total)
    } catch (err: any) {
      console.error('Error fetching assessments:', err)
      setError(err.message || 'Failed to load assessments')
    } finally {
      setLoading(false)
    }
  }
  
  // Calculate stats
  const totalAssessments = assessments.length
  const completedAssessments = assessments.filter(a => a.status === "completed").length
  const inProgressAssessments = assessments.filter(a => a.status === "in_progress").length
  const averageScore = Math.round(
    assessments
      .filter(a => a.score !== undefined && a.score !== null)
      .reduce((acc, a) => acc + (a.score || 0), 0) / 
    assessments.filter(a => a.score !== undefined && a.score !== null).length || 0
  )
  
  const handleNewAssessment = () => {
    router.push('/assessments/new')
  }

  return (
    <div className="flex-1 space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-navy">Compliance Assessments</h2>
          <p className="text-muted-foreground">
            Track and manage your compliance assessment progress
          </p>
        </div>
        <Button 
          className="bg-gold hover:bg-gold-dark text-navy"
          onClick={handleNewAssessment}
        >
          <Plus className="mr-2 h-4 w-4" />
          New Assessment
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Assessments</p>
                  <p className="text-2xl font-bold">{totalAssessments}</p>
                </div>
                <Shield className="h-8 w-8 text-gold opacity-20" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Completed</p>
                  <p className="text-2xl font-bold text-success">{completedAssessments}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-success opacity-20" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">In Progress</p>
                  <p className="text-2xl font-bold text-warning">{inProgressAssessments}</p>
                </div>
                <Clock className="h-8 w-8 text-warning opacity-20" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Average Score</p>
                  <p className="text-2xl font-bold">{averageScore}%</p>
                </div>
                <AlertCircle className="h-8 w-8 text-gold opacity-20" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Assessments Table */}
      {loading ? (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      ) : assessments.length > 0 ? (
        <DataTable columns={columns} data={assessments} />
      ) : (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <ClipboardCheck className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Assessments Found</h3>
            <p className="text-sm text-muted-foreground text-center mb-4 max-w-md">
              Get started by creating your first compliance assessment.
            </p>
            <Button 
              className="bg-gold hover:bg-gold-dark text-navy"
              onClick={handleNewAssessment}
            >
              <Plus className="mr-2 h-4 w-4" />
              Start Your First Assessment
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}