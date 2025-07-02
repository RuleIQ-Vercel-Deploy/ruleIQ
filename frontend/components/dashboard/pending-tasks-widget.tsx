"use client"

import {
  AlertCircle,
  Clock,
  CheckCircle2,
  FileText,
  Shield,
  Building,
  Eye,
  Filter,
  MoreHorizontal,
  RefreshCw
} from "lucide-react"
import React, { useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

import type { DashboardTask } from "@/lib/api/dashboard.service"

interface PendingTasksWidgetProps {
  tasks: DashboardTask[]
  className?: string
  maxTasks?: number
  isLoading?: boolean
  error?: string | null
  onRefresh?: () => void
  onTaskAction?: (taskId: string, action: string) => void
}

export function PendingTasksWidget({
  tasks = [],
  className,
  maxTasks = 5,
  isLoading = false,
  error = null,
  onRefresh,
  onTaskAction
}: PendingTasksWidgetProps) {
  const [filter, setFilter] = useState<'all' | DashboardTask['type']>('all')

  // Show loading state
  if (isLoading) {
    return <PendingTasksWidgetSkeleton />
  }

  // Show error state
  if (error) {
    return (
      <Card className={cn("border-destructive/50", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <CheckCircle2 className="h-5 w-5" />
            Pending Tasks
          </CardTitle>
          <CardDescription>Error loading tasks</CardDescription>
        </CardHeader>
        <CardContent className="text-center py-8">
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          {onRefresh && (
            <Button onClick={onRefresh} size="sm" variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          )}
        </CardContent>
      </Card>
    )
  }

  const getCategoryIcon = (category: DashboardTask['type']) => {
    switch (category) {
      case 'evidence':
        return <FileText className="h-4 w-4" />
      case 'assessment':
        return <Shield className="h-4 w-4" />
      case 'compliance':
        return <Building className="h-4 w-4" />
      case 'review':
        return <Eye className="h-4 w-4" />
      default:
        return <AlertCircle className="h-4 w-4" />
    }
  }

  const getPriorityBadge = (priority: DashboardTask['priority']) => {
    switch (priority) {
      case 'critical':
        return <Badge variant="destructive">Critical</Badge>
      case 'high':
        return <Badge className="bg-amber-500 hover:bg-amber-600">High</Badge>
      case 'medium':
        return <Badge variant="secondary">Medium</Badge>
      case 'low':
        return <Badge variant="outline">Low</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  const getDueDateStatus = (dueDate: string | null | undefined) => {
    if (!dueDate) return { status: 'none', text: 'No deadline', color: 'text-muted-foreground' }
    
    const now = new Date()
    const due = new Date(dueDate)
    const diffTime = due.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays < 0) {
      return { status: 'overdue', text: 'Overdue', color: 'text-destructive' }
    } else if (diffDays === 0) {
      return { status: 'today', text: 'Due today', color: 'text-amber-500' }
    } else if (diffDays <= 3) {
      return { status: 'soon', text: `Due in ${diffDays} days`, color: 'text-amber-500' }
    } else {
      return { status: 'future', text: `Due in ${diffDays} days`, color: 'text-muted-foreground' }
    }
  }

  const filteredTasks = tasks
    .filter(task => filter === 'all' || task.type === filter)
    .sort((a, b) => {
      // Sort by priority first (critical > high > medium > low)
      const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
      const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority]
      if (priorityDiff !== 0) return priorityDiff
      
      // Then by due date (sooner first)
      if (!a.due_date && !b.due_date) return 0
      if (!a.due_date) return 1
      if (!b.due_date) return -1
      return new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
    })
    .slice(0, maxTasks)

  return (
    <Card className={cn("border-0 shadow-sm hover:shadow-md transition-shadow duration-200", className)}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl font-bold text-navy">Pending Tasks</CardTitle>
            <CardDescription className="text-muted-foreground">
              {tasks.length} tasks requiring attention
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="sm" 
              className="h-auto p-2"
              onClick={() => setFilter(filter === 'all' ? 'compliance' : 'all')}
            >
              <Filter className="h-4 w-4" />
            </Button>
            {onRefresh && (
              <Button variant="ghost" size="sm" className="h-auto p-2" onClick={onRefresh}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {filteredTasks.map((task) => {
          const dueDateStatus = getDueDateStatus(task.due_date)
          
          return (
            <div
              key={task.id}
              className="group rounded-lg border p-3 transition-colors hover:bg-accent/50"
            >
              {/* Task Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-start gap-3 flex-1">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gold/10 mt-0.5">
                    {getCategoryIcon(task.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm leading-tight mb-1">
                      {task.title}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      {task.framework && (
                        <span className="bg-muted px-2 py-0.5 rounded">
                          {task.framework}
                        </span>
                      )}
                      {task.assigned_to && (
                        <>
                          <span>•</span>
                          <span>{task.assigned_to}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {getPriorityBadge(task.priority)}
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-auto p-1 opacity-0 group-hover:opacity-100"
                    onClick={() => onTaskAction?.(task.id, 'view')}
                  >
                    <MoreHorizontal className="h-3 w-3" />
                  </Button>
                </div>
              </div>

              {/* Due Date and Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs">
                  <Clock className="h-3 w-3" />
                  <span className={dueDateStatus.color}>
                    {dueDateStatus.text}
                  </span>
                </div>
                
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-auto px-2 py-1 text-xs"
                    onClick={() => onTaskAction?.(task.id, 'start')}
                  >
                    Start
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-auto px-2 py-1 text-xs"
                    onClick={() => onTaskAction?.(task.id, 'assign')}
                  >
                    Assign
                  </Button>
                </div>
              </div>
            </div>
          )
        })}

        {filteredTasks.length === 0 && (
          <div className="text-center py-6 text-muted-foreground">
            <CheckCircle2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No pending tasks</p>
            <p className="text-xs">Great job staying on top of things!</p>
          </div>
        )}

        {tasks.length > maxTasks && (
          <div className="pt-2 border-t">
            <Button variant="ghost" size="sm" className="w-full">
              View All {tasks.length} Tasks
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function PendingTasksWidgetSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-6 w-32 mb-1" />
            <Skeleton className="h-4 w-48" />
          </div>
          <Skeleton className="h-8 w-8" />
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="rounded-lg border p-3">
            <div className="flex items-start gap-3">
              <Skeleton className="h-8 w-8 rounded-lg" />
              <div className="flex-1">
                <Skeleton className="h-4 w-3/4 mb-2" />
                <Skeleton className="h-3 w-1/2" />
              </div>
              <Skeleton className="h-6 w-16" />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}