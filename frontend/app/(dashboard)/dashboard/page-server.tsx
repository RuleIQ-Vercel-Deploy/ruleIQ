import { 
  Shield, 
  AlertTriangle, 
  Brain, 
  FileCheck, 
  RefreshCw
} from "lucide-react"
import { Suspense } from "react"

import { AIInsightsWidget } from "@/components/dashboard/ai-insights-widget"
import { 
  ComplianceTrendChart, 
  FrameworkBreakdownChart, 
  ActivityHeatmap, 
  RiskMatrix, 
  TaskProgressChart 
} from "@/components/dashboard/charts"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { EnhancedStatsCard } from "@/components/dashboard/enhanced-stats-card"
import { PendingTasksWidget } from "@/components/dashboard/pending-tasks-widget"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  StatsCardSkeleton, 
  ChartSkeleton, 
  InsightsSkeleton,
  DashboardSkeleton 
} from "@/components/ui/skeletons"

// Server-side data fetching functions
async function getComplianceStats() {
  // Simulate API call - replace with actual data fetching
  await new Promise(resolve => setTimeout(resolve, 500))
  
  return {
    score: 87,
    trend: 5,
    frameworks: 5,
    activeFrameworks: 3,
    pendingTasks: 12,
    completedTasks: 45,
    highRisks: 2,
    totalRisks: 8,
  }
}

async function getAIInsights() {
  await new Promise(resolve => setTimeout(resolve, 700))
  
  return [
    {
      id: "1",
      type: "recommendation" as const,
      title: "Update Password Policy",
      description: "Your password policy hasn't been reviewed in 6 months. Consider updating requirements.",
      priority: "high" as const,
    },
    {
      id: "2",
      type: "alert" as const,
      title: "New GDPR Guidelines",
      description: "EU has released updated GDPR guidelines affecting data retention.",
      priority: "medium" as const,
    },
    {
      id: "3",
      type: "success" as const,
      title: "ISO 27001 Compliant",
      description: "All requirements met for ISO 27001 certification renewal.",
      priority: "low" as const,
    },
  ]
}

async function getPendingTasks() {
  await new Promise(resolve => setTimeout(resolve, 600))
  
  return [
    {
      id: "1",
      title: "Complete Risk Assessment",
      dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
      priority: "high" as const,
      framework: "ISO 27001",
    },
    {
      id: "2",
      title: "Review Access Controls",
      dueDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
      priority: "medium" as const,
      framework: "SOC 2",
    },
    {
      id: "3",
      title: "Update Privacy Policy",
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      priority: "low" as const,
      framework: "GDPR",
    },
  ]
}

// Async Server Components
async function ComplianceStats() {
  const stats = await getComplianceStats()
  
  return (
    <>
      <EnhancedStatsCard
        title="Compliance Score"
        value={stats.score}
        unit="%"
        trend={stats.trend}
        trendLabel="from last month"
        icon={<Shield className="h-4 w-4" />}
        variant="primary"
      />
      <EnhancedStatsCard
        title="Active Frameworks"
        value={stats.activeFrameworks}
        total={stats.frameworks}
        icon={<FileCheck className="h-4 w-4" />}
        variant="secondary"
      />
      <EnhancedStatsCard
        title="Pending Tasks"
        value={stats.pendingTasks}
        trend={-3}
        trendLabel="from last week"
        icon={<RefreshCw className="h-4 w-4" />}
        variant="warning"
      />
      <EnhancedStatsCard
        title="Risk Items"
        value={stats.highRisks}
        total={stats.totalRisks}
        icon={<AlertTriangle className="h-4 w-4" />}
        variant="error"
      />
    </>
  )
}

async function AIInsights() {
  const insights = await getAIInsights()
  return <AIInsightsWidget insights={insights} />
}

async function PendingTasks() {
  const tasks = await getPendingTasks()
  return <PendingTasksWidget tasks={tasks} />
}

export default async function DashboardPage() {
  return (
    <div className="flex-1 space-y-6 p-6">
      <DashboardHeader />
      
      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Suspense fallback={<StatsCardSkeleton />}>
          <ComplianceStats />
        </Suspense>
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-7">
        {/* Compliance Trend Chart */}
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Compliance Trend</CardTitle>
            <CardDescription>
              Your compliance score over the last 30 days
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <ComplianceTrendChart />
            </Suspense>
          </CardContent>
        </Card>

        {/* AI Insights */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              AI Insights
            </CardTitle>
            <CardDescription>
              Powered by ruleIQ intelligence
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<InsightsSkeleton />}>
              <AIInsights />
            </Suspense>
          </CardContent>
        </Card>
      </div>

      {/* Secondary Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Framework Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Framework Compliance</CardTitle>
            <CardDescription>
              Compliance scores by framework
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <FrameworkBreakdownChart />
            </Suspense>
          </CardContent>
        </Card>

        {/* Pending Tasks */}
        <Card>
          <CardHeader>
            <CardTitle>Pending Tasks</CardTitle>
            <CardDescription>
              Tasks requiring your attention
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<InsightsSkeleton />}>
              <PendingTasks />
            </Suspense>
          </CardContent>
        </Card>
      </div>

      {/* Additional Widgets */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Risk Matrix */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Matrix</CardTitle>
            <CardDescription>
              Current risk assessment overview
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <RiskMatrix />
            </Suspense>
          </CardContent>
        </Card>

        {/* Task Progress */}
        <Card>
          <CardHeader>
            <CardTitle>Task Progress</CardTitle>
            <CardDescription>
              Completion by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <TaskProgressChart />
            </Suspense>
          </CardContent>
        </Card>

        {/* Activity Heatmap */}
        <Card>
          <CardHeader>
            <CardTitle>Activity Heatmap</CardTitle>
            <CardDescription>
              Compliance activities over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <ActivityHeatmap />
            </Suspense>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
