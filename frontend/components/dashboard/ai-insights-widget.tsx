"use client"

import {
  Brain,
  Lightbulb,
  AlertTriangle,
  TrendingUp,
  Bookmark,
  X,
  RefreshCw,
  ChevronRight,
  Sparkles
} from "lucide-react"
import React, { useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { dashboardService } from "@/lib/api/dashboard.service"
import { cn } from "@/lib/utils"

import type { DashboardInsight } from "@/lib/api/dashboard.service"


interface AIInsightsWidgetProps {
  insights: DashboardInsight[]
  className?: string
  maxInsights?: number
  isLoading?: boolean
  error?: string | null
  onRefresh?: () => void
  onDismiss?: (insightId: string) => void
  onBookmark?: (insightId: string) => void
  complianceProfile?: {
    priorities?: string[];
    maturityLevel?: string;
  }
  onboardingData?: {
    fullName?: string;
    timeline?: string;
  }
}

export function AIInsightsWidget({
  insights = [],
  className,
  maxInsights = 3,
  isLoading = false,
  error = null,
  onRefresh,
  onDismiss,
  onBookmark,
  complianceProfile,
  onboardingData
}: AIInsightsWidgetProps) {
  const [dismissedInsights, setDismissedInsights] = useState<Set<string>>(new Set())
  const [bookmarkedInsights, setBookmarkedInsights] = useState<Set<string>>(new Set())

  // Show loading state
  if (isLoading) {
    return <AIInsightsWidgetSkeleton />
  }

  // Show error state
  if (error) {
    return (
      <Card className={cn("glass-card border-error/50", className)}>
        <CardHeader>
          <CardTitle className="text-error">AI Insights Error</CardTitle>
          <CardDescription className="text-muted-foreground">{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={onRefresh} variant="outline" size="sm" className="border-glass-border hover:border-glass-border-hover hover:bg-glass-white">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    )
  }

  const getInsightIcon = (type: DashboardInsight['type']) => {
    switch (type) {
      case 'tip':
        return <Lightbulb className="h-4 w-4 text-warning" />
      case 'recommendation':
        return <TrendingUp className="h-4 w-4 text-primary" />
      case 'risk-alert':
        return <AlertTriangle className="h-4 w-4 text-error" />
      case 'optimization':
        return <Sparkles className="h-4 w-4 text-primary" />
      default:
        return <Brain className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getInsightBadge = (type: DashboardInsight['type']) => {
    switch (type) {
      case 'tip':
        return <Badge className="bg-warning/20 text-warning border-warning/30">Tip</Badge>
      case 'recommendation':
        return <Badge className="bg-primary/20 text-primary border-primary/30">Recommendation</Badge>
      case 'risk-alert':
        return <Badge className="bg-error/20 text-error border-error/30">Risk Alert</Badge>
      case 'optimization':
        return <Badge className="bg-primary/20 text-primary border-primary/30">Optimization</Badge>
      default:
        return <Badge className="bg-secondary text-muted-foreground">Insight</Badge>
    }
  }

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'border-l-error'
    if (priority >= 6) return 'border-l-warning'
    if (priority >= 4) return 'border-l-brand-secondary'
    return 'border-l-glass-border'
  }

  const handleDismiss = async (insightId: string) => {
    setDismissedInsights(prev => new Set([...prev, insightId]))
    if (onDismiss) {
      onDismiss(insightId)
    } else {
      try {
        await dashboardService.dismissInsight(insightId)
      } catch (error) {
        console.error('Failed to dismiss insight:', error)
      }
    }
  }

  const handleBookmark = async (insightId: string) => {
    setBookmarkedInsights(prev => {
      const newSet = new Set(prev)
      if (newSet.has(insightId)) {
        newSet.delete(insightId)
      } else {
        newSet.add(insightId)
      }
      return newSet
    })
    
    if (onBookmark) {
      onBookmark(insightId)
    } else {
      try {
        await dashboardService.bookmarkInsight(insightId)
      } catch (error) {
        console.error('Failed to bookmark insight:', error)
      }
    }
  }

  // Generate personalized insights based on compliance profile
  const generatePersonalizedInsights = () => {
    const personalizedInsights: DashboardInsight[] = []
    
    if (complianceProfile && insights.length === 0) {
      // Add insights based on priorities from onboarding
      if (complianceProfile.priorities?.includes("GDPR Compliance")) {
        personalizedInsights.push({
          id: "gdpr-start",
          type: "recommendation",
          title: "Start your GDPR compliance journey",
          description: "Based on your profile, GDPR is a top priority. Begin with a data mapping exercise.",
          priority: 9,
          created_at: new Date().toISOString(),
          dismissible: true,
          action: {
            label: "Start Data Mapping",
            route: "/assessments/new?framework=gdpr"
          }
        })
      }
      
      if (complianceProfile.maturityLevel === "beginner") {
        personalizedInsights.push({
          id: "policy-templates",
          type: "tip",
          title: "Use our AI-powered policy templates",
          description: "Save time with pre-built templates tailored to your industry.",
          priority: 8,
          created_at: new Date().toISOString(),
          dismissible: true,
          action: {
            label: "Browse Templates",
            route: "/policies/templates"
          }
        })
      }
      
      if (onboardingData?.timeline === "ASAP (< 1 month)") {
        personalizedInsights.push({
          id: "fast-track",
          type: "optimization",
          title: "Fast-track certification available",
          description: "Your timeline is urgent. Consider our accelerated compliance program.",
          priority: 10,
          created_at: new Date().toISOString(),
          dismissible: true,
          action: {
            label: "Learn More",
            route: "/fast-track"
          }
        })
      }
    }
    
    return [...personalizedInsights, ...insights]
  }

  const allInsights = generatePersonalizedInsights()
  
  const visibleInsights = allInsights
    .filter(insight => !dismissedInsights.has(insight.id))
    .sort((a, b) => {
      // Sort by priority first (higher priority first)
      const priorityDiff = b.priority - a.priority
      if (priorityDiff !== 0) return priorityDiff

      // Then by timestamp (newest first)
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
    .slice(0, maxInsights)

  return (
    <Card className={cn("glass-card border-0 shadow-sm hover:shadow-md transition-all duration-200", className)}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-brand-primary/20 to-brand-secondary/20 flex items-center justify-center">
              <Brain className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold gradient-text">AI Insights</CardTitle>
              <CardDescription className="text-muted-foreground">
                Personalized compliance recommendations
              </CardDescription>
            </div>
          </div>
          {onRefresh && (
            <Button
              variant="ghost"
              size="sm"
              className="h-auto p-2"
              onClick={onRefresh}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {visibleInsights.map((insight) => (
          <div
            key={insight.id}
            className={cn(
              "group rounded-lg border-l-4 bg-glass-white p-4 transition-all hover:bg-glass-white-hover border border-glass-border hover:border-glass-border-hover",
              getPriorityColor(insight.priority)
            )}
          >
            {/* Insight Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start gap-3 flex-1">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-primary/10 to-brand-secondary/10 mt-0.5">
                  {getInsightIcon(insight.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-sm leading-tight">
                      {insight.title}
                    </h4>
                    {getInsightBadge(insight.type)}
                  </div>
                  <p className="text-xs text-muted-foreground mb-2">
                    {insight.description}
                  </p>
                </div>
              </div>
              
              {insight.dismissible && (
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className={cn(
                      "h-auto p-1",
                      bookmarkedInsights.has(insight.id) ? "text-warning" : "text-muted-foreground"
                    )}
                    onClick={() => handleBookmark(insight.id)}
                  >
                    <Bookmark className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-1 text-muted-foreground hover:text-foreground"
                    onClick={() => handleDismiss(insight.id)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </div>

            {/* Action Button */}
            {insight.action && (
              <div className="mt-3">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-auto px-3 py-1.5 text-xs border border-glass-border hover:border-glass-border-hover hover:bg-glass-white"
                  onClick={() => insight.action?.route && (window.location.href = insight.action.route)}
                >
                  {insight.action.label}
                  <ChevronRight className="h-3 w-3 ml-1" />
                </Button>
              </div>
            )}
          </div>
        ))}

        {visibleInsights.length === 0 && (
          <div className="text-center py-6 text-muted-foreground">
            <Brain className="h-8 w-8 mx-auto mb-2 opacity-50 text-primary" />
            <p>No new insights</p>
            <p className="text-xs text-muted-foreground">Check back later for AI-powered recommendations</p>
          </div>
        )}

        {insights.length > maxInsights && (
          <div className="pt-2 border-t border-glass-border">
            <Button variant="ghost" size="sm" className="w-full hover:bg-glass-white">
              View All Insights ({insights.length})
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function AIInsightsWidgetSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div>
              <Skeleton className="h-6 w-32 mb-1" />
              <Skeleton className="h-4 w-48" />
            </div>
          </div>
          <Skeleton className="h-8 w-8" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="border-l-4 border-gray-200 bg-card p-4">
            <div className="flex items-start gap-3">
              <Skeleton className="h-8 w-8 rounded-lg" />
              <div className="flex-1">
                <Skeleton className="h-4 w-3/4 mb-2" />
                <Skeleton className="h-3 w-full mb-1" />
                <Skeleton className="h-3 w-2/3" />
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}