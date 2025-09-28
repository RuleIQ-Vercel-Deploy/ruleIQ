import { Shield, AlertTriangle, Brain, FileCheck, RefreshCw } from 'lucide-react';
import { Suspense } from 'react';

import { AIInsightsWidget } from '@/components/dashboard/ai-insights-widget';
import {
  ComplianceTrendChart,
  FrameworkBreakdownChart,
  ActivityHeatmap,
  RiskMatrix,
  TaskProgressChart,
} from '@/components/dashboard/charts';
import { DashboardHeader } from '@/components/dashboard/dashboard-header';
import { EnhancedStatsCard } from '@/components/dashboard/enhanced-stats-card';
import { PendingTasksWidget } from '@/components/dashboard/pending-tasks-widget';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { StatsCardSkeleton, ChartSkeleton, InsightsSkeleton } from '@/components/ui/skeletons';

import type { DashboardInsight, DashboardTask } from '@/types/dashboard';

// Server-side data fetching functions
async function getComplianceStats() {
  // Simulate API call - replace with actual data fetching
  await new Promise((resolve) => setTimeout(resolve, 500));

  return {
    score: 87,
    trend: { value: 5, isPositive: true },
    frameworks: 5,
    activeFrameworks: 3,
    pendingTasks: 12,
    completedTasks: 45,
    highRisks: 2,
    totalRisks: 8,
  };
}

async function getAIInsights(): Promise<DashboardInsight[]> {
  await new Promise((resolve) => setTimeout(resolve, 700));

  return [
    {
      id: '1',
      type: 'recommendation',
      title: 'Update Password Policy',
      description:
        "Your password policy hasn't been reviewed in 6 months. Consider updating requirements.",
      priority: 1,
      created_at: new Date().toISOString(),
      dismissible: true,
    },
    {
      id: '2',
      type: 'risk-alert',
      title: 'New GDPR Guidelines',
      description: 'EU has released updated GDPR guidelines affecting data retention.',
      priority: 2,
      created_at: new Date().toISOString(),
      dismissible: true,
    },
    {
      id: '3',
      type: 'tip',
      title: 'ISO 27001 Compliant',
      description: 'All requirements met for ISO 27001 certification renewal.',
      priority: 3,
      created_at: new Date().toISOString(),
      dismissible: true,
    },
  ];
}

async function getPendingTasks(): Promise<DashboardTask[]> {
  await new Promise((resolve) => setTimeout(resolve, 600));

  return [
    {
      id: '1',
      title: 'Complete Risk Assessment',
      description: 'Conduct comprehensive risk assessment for current quarter',
      type: 'assessment' as const,
      due_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
      priority: 'high' as const,
      framework: 'ISO 27001',
      status: 'pending' as const,
    },
    {
      id: '2',
      title: 'Review Access Controls',
      description: 'Audit and update user access permissions',
      type: 'compliance' as const,
      due_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
      priority: 'medium' as const,
      framework: 'SOC 2',
      status: 'pending' as const,
    },
    {
      id: '3',
      title: 'Update Privacy Policy',
      description: 'Revise privacy policy to reflect new data processing requirements',
      type: 'compliance' as const,
      due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      priority: 'low' as const,
      framework: 'GDPR',
      status: 'pending' as const,
    },
  ];
}

// Chart data functions
async function getComplianceTrendData() {
  await new Promise((resolve) => setTimeout(resolve, 300));

  const now = new Date();
  return Array.from({ length: 30 }, (_, i) => {
    const date = new Date(now);
    date.setDate(date.getDate() - (29 - i));
    return {
      date: date.toISOString(),
      score: Math.floor(85 + Math.random() * 10 + Math.sin(i / 5) * 5),
      target: 90,
    };
  });
}

async function getFrameworkBreakdownData() {
  await new Promise((resolve) => setTimeout(resolve, 300));

  return [
    { framework: 'ISO 27001', score: 92, color: '#8B5CF6' },
    { framework: 'GDPR', score: 87, color: '#A78BFA' },
    { framework: 'SOC 2', score: 78, color: '#34FEF7' },
    { framework: 'NIST', score: 65, color: '#D0D5E3' },
  ];
}

async function getRiskMatrixData() {
  await new Promise((resolve) => setTimeout(resolve, 300));

  return [
    {
      id: '1',
      name: 'Data Breach Risk',
      likelihood: 3 as const,
      impact: 5 as const,
      category: 'Security',
    },
    {
      id: '2',
      name: 'Compliance Gap',
      likelihood: 4 as const,
      impact: 3 as const,
      category: 'Regulatory',
    },
    {
      id: '3',
      name: 'Access Control',
      likelihood: 2 as const,
      impact: 4 as const,
      category: 'Security',
    },
    {
      id: '4',
      name: 'Policy Updates',
      likelihood: 5 as const,
      impact: 2 as const,
      category: 'Governance',
    },
  ];
}

async function getTaskProgressData() {
  await new Promise((resolve) => setTimeout(resolve, 300));

  return [
    { category: 'Assessments', completed: 8, pending: 4, overdue: 1 },
    { category: 'Policies', completed: 12, pending: 2, overdue: 0 },
    { category: 'Evidence', completed: 25, pending: 8, overdue: 2 },
    { category: 'Reviews', completed: 6, pending: 3, overdue: 1 },
  ];
}

async function getActivityHeatmapData() {
  await new Promise((resolve) => setTimeout(resolve, 300));

  const now = new Date();
  return Array.from({ length: 84 }, (_, i) => {
    const date = new Date(now);
    date.setDate(date.getDate() - (83 - i));
    return {
      date: date.toISOString().split('T')[0]!,
      count: Math.floor(Math.random() * 10),
    };
  });
}

// Async Server Components
async function ComplianceStats() {
  const stats = await getComplianceStats();

  return (
    <>
      <EnhancedStatsCard
        title="Compliance Score"
        description="Overall compliance rating"
        value={`${stats.score}%`}
        icon={Shield}
        trend={stats.trend}
      />
      <EnhancedStatsCard
        title="Active Frameworks"
        description={`${stats.activeFrameworks} of ${stats.frameworks} frameworks`}
        value={stats.activeFrameworks}
        icon={FileCheck}
      />
      <EnhancedStatsCard
        title="Pending Tasks"
        description="Tasks requiring attention"
        value={stats.pendingTasks}
        icon={RefreshCw}
        trend={{ value: 3, isPositive: false }}
      />
      <EnhancedStatsCard
        title="Risk Items"
        description={`${stats.highRisks} high priority risks`}
        value={stats.highRisks}
        icon={AlertTriangle}
      />
    </>
  );
}

async function AIInsights() {
  const insights = await getAIInsights();
  return <AIInsightsWidget insights={insights} />;
}

async function PendingTasks() {
  const tasks = await getPendingTasks();
  return <PendingTasksWidget tasks={tasks} />;
}

async function ComplianceTrendChartWrapper() {
  const data = await getComplianceTrendData();
  return <ComplianceTrendChart data={data} />;
}

async function FrameworkBreakdownChartWrapper() {
  const data = await getFrameworkBreakdownData();
  return <FrameworkBreakdownChart data={data} />;
}

async function RiskMatrixWrapper() {
  const risks = await getRiskMatrixData();
  return <RiskMatrix risks={risks} />;
}

async function TaskProgressChartWrapper() {
  const data = await getTaskProgressData();
  return <TaskProgressChart data={data} />;
}

async function ActivityHeatmapWrapper() {
  const data = await getActivityHeatmapData();
  return <ActivityHeatmap data={data} />;
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
            <CardDescription>Your compliance score over the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <ComplianceTrendChartWrapper />
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
            <CardDescription>Powered by ruleIQ intelligence</CardDescription>
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
            <CardDescription>Compliance scores by framework</CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <FrameworkBreakdownChartWrapper />
            </Suspense>
          </CardContent>
        </Card>

        {/* Pending Tasks */}
        <Card>
          <CardHeader>
            <CardTitle>Pending Tasks</CardTitle>
            <CardDescription>Tasks requiring your attention</CardDescription>
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
            <CardDescription>Current risk assessment overview</CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <RiskMatrixWrapper />
            </Suspense>
          </CardContent>
        </Card>

        {/* Task Progress */}
        <Card>
          <CardHeader>
            <CardTitle>Task Progress</CardTitle>
            <CardDescription>Completion by category</CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <TaskProgressChartWrapper />
            </Suspense>
          </CardContent>
        </Card>

        {/* Activity Heatmap */}
        <Card>
          <CardHeader>
            <CardTitle>Activity Heatmap</CardTitle>
            <CardDescription>Compliance activities over time</CardDescription>
          </CardHeader>
          <CardContent>
            <Suspense fallback={<ChartSkeleton />}>
              <ActivityHeatmapWrapper />
            </Suspense>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
