'use client';

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
  RefreshCw,
} from 'lucide-react';
import React, { useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

import type { DashboardTask } from '@/types/dashboard';

interface PendingTasksWidgetProps {
  tasks: DashboardTask[];
  className?: string;
  maxTasks?: number;
  isLoading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
  onTaskAction?: (taskId: string, action: string) => void;
}

export function PendingTasksWidget({
  tasks = [],
  className,
  maxTasks = 5,
  isLoading = false,
  error = null,
  onRefresh,
  onTaskAction,
}: PendingTasksWidgetProps) {
  const [filter, setFilter] = useState<'all' | DashboardTask['type']>('all');

  // Show loading state
  if (isLoading) {
    return <PendingTasksWidgetSkeleton />;
  }

  // Show error state
  if (error) {
    return (
      <Card className={cn('glass-card border-error/50', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-error">
            <CheckCircle2 className="h-5 w-5" />
            Pending Tasks
          </CardTitle>
          <CardDescription className="text-muted-foreground">Error loading tasks</CardDescription>
        </CardHeader>
        <CardContent className="py-8 text-center">
          <p className="mb-4 text-sm text-muted-foreground">{error}</p>
          {onRefresh && (
            <Button
              onClick={onRefresh}
              size="sm"
              variant="outline"
              className="border-glass-border hover:border-glass-border-hover hover:bg-glass-white"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  const getCategoryIcon = (category: DashboardTask['type']) => {
    switch (category) {
      case 'evidence':
        return <FileText className="h-4 w-4" />;
      case 'assessment':
        return <Shield className="h-4 w-4" />;
      case 'compliance':
        return <Building className="h-4 w-4" />;
      case 'review':
        return <Eye className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getPriorityBadge = (priority: DashboardTask['priority']) => {
    switch (priority) {
      case 'critical':
        return (
          <Badge className="border-error/30 bg-error/20 text-error hover:bg-error/30">
            Critical
          </Badge>
        );
      case 'high':
        return (
          <Badge className="border-warning/30 bg-warning/20 text-warning hover:bg-warning/30">
            High
          </Badge>
        );
      case 'medium':
        return (
          <Badge className="border-primary/30 bg-primary/20 text-primary hover:bg-primary/30">
            Medium
          </Badge>
        );
      case 'low':
        return (
          <Badge className="border-border bg-secondary text-muted-foreground hover:bg-secondary/80">
            Low
          </Badge>
        );
      default:
        return <Badge className="bg-secondary text-muted-foreground">Unknown</Badge>;
    }
  };

  const getDueDateStatus = (dueDate: string | null | undefined) => {
    if (!dueDate) return { status: 'none', text: 'No deadline', color: 'text-muted-foreground' };

    const now = new Date();
    const due = new Date(dueDate);
    const diffTime = due.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return { status: 'overdue', text: 'Overdue', color: 'text-error' };
    } else if (diffDays === 0) {
      return { status: 'today', text: 'Due today', color: 'text-warning' };
    } else if (diffDays <= 3) {
      return { status: 'soon', text: `Due in ${diffDays} days`, color: 'text-warning' };
    } else {
      return { status: 'future', text: `Due in ${diffDays} days`, color: 'text-muted-foreground' };
    }
  };

  const filteredTasks = tasks
    .filter((task) => filter === 'all' || task.type === filter)
    .sort((a, b) => {
      // Sort by priority first (critical > high > medium > low)
      const priorityOrder: Record<DashboardTask['priority'], number> = {
        critical: 4,
        high: 3,
        medium: 2,
        low: 1,
      };
      const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
      if (priorityDiff !== 0) return priorityDiff;

      // Then by due date (sooner first)
      if (!a.due_date && !b.due_date) return 0;
      if (!a.due_date) return 1;
      if (!b.due_date) return -1;
      return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
    })
    .slice(0, maxTasks);

  return (
    <Card
      className={cn(
        'glass-card border-0 shadow-sm transition-all duration-200 hover:shadow-md',
        className,
      )}
    >
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="gradient-text text-xl font-bold">Pending Tasks</CardTitle>
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
          const dueDateStatus = getDueDateStatus(task.due_date);

          return (
            <div
              key={task.id}
              className="border-glass-border hover:border-glass-border-hover group rounded-lg border p-3 transition-all hover:bg-glass-white"
            >
              {/* Task Header */}
              <div className="mb-2 flex items-start justify-between">
                <div className="flex flex-1 items-start gap-3">
                  <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                    {getCategoryIcon(task.type)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="mb-1 text-sm font-medium leading-tight">{task.title}</h4>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      {task.framework && (
                        <span className="rounded bg-muted px-2 py-0.5">{task.framework}</span>
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
                  <span className={dueDateStatus.color}>{dueDateStatus.text}</span>
                </div>

                <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
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
          );
        })}

        {filteredTasks.length === 0 && (
          <div className="py-6 text-center text-muted-foreground">
            <CheckCircle2 className="mx-auto mb-2 h-8 w-8 text-primary opacity-50" />
            <p>No pending tasks</p>
            <p className="text-xs text-muted-foreground">Great job staying on top of things!</p>
          </div>
        )}

        {tasks.length > maxTasks && (
          <div className="border-glass-border border-t pt-2">
            <Button variant="ghost" size="sm" className="w-full hover:bg-glass-white">
              View All {tasks.length} Tasks
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function PendingTasksWidgetSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="mb-1 h-6 w-32" />
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
                <Skeleton className="mb-2 h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
              <Skeleton className="h-6 w-16" />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
