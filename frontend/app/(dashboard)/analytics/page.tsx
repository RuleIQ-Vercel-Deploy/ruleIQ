"use client"

import { format, subDays, startOfMonth, endOfMonth } from "date-fns"
import { CalendarIcon, Download, Filter, RefreshCw } from "lucide-react"
import { useState } from "react"
import { type DateRange } from "react-day-picker"

import { 
  ComplianceTrendChart, 
  FrameworkBreakdownChart, 
  ActivityHeatmap, 
  RiskMatrix, 
  TaskProgressChart 
} from "@/components/dashboard/charts"
import { AdvancedMetricsChart } from "@/components/dashboard/charts/advanced-metrics-chart"
import { ComplianceDistributionChart } from "@/components/dashboard/charts/compliance-distribution-chart"
import { TimeSeriesAnalysisChart } from "@/components/dashboard/charts/time-series-analysis-chart"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { AppSidebar } from "@/components/navigation/app-sidebar"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { cn } from "@/lib/utils"

// Analytics dashboard for Alex persona - data-driven, customizable, with export options
export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: subDays(new Date(), 30),
    to: new Date(),
  })
  const [selectedFramework, setSelectedFramework] = useState<string>("all")
  const [selectedMetric, setSelectedMetric] = useState<string>("compliance")
  const [isLoading, setIsLoading] = useState(false)

  // Mock data for analytics
  const analyticsData = {
    compliance_trends: generateTimeSeriesData(dateRange),
    framework_scores: [
      { framework: "ISO 27001", score: 92, trend: 5 },
      { framework: "GDPR", score: 88, trend: -2 },
      { framework: "Cyber Essentials", score: 95, trend: 8 },
      { framework: "PCI DSS", score: 78, trend: 3 },
      { framework: "SOC 2", score: 85, trend: 1 }
    ],
    advanced_metrics: {
      risk_reduction: 23,
      time_to_compliance: 45,
      automation_rate: 67,
      cost_savings: 34500,
      incidents_prevented: 12
    },
    distribution_data: generateDistributionData(),
    activity_data: generateActivityData()
  }

  function generateTimeSeriesData(range: DateRange | undefined) {
    if (!range?.from || !range?.to) return []
    const data = []
    const days = Math.floor((range.to.getTime() - range.from.getTime()) / (1000 * 60 * 60 * 24))
    
    for (let i = 0; i <= days; i++) {
      const date = new Date(range.from)
      date.setDate(date.getDate() + i)
      data.push({
        date: date.toISOString(),
        score: Math.floor(Math.random() * 20) + 75 + i * 0.3,
        target: 90,
        incidents: Math.floor(Math.random() * 5),
        tasks: Math.floor(Math.random() * 10) + 5
      })
    }
    return data
  }

  function generateDistributionData() {
    return [
      { category: "Policies", compliant: 85, nonCompliant: 15 },
      { category: "Access Control", compliant: 92, nonCompliant: 8 },
      { category: "Data Protection", compliant: 78, nonCompliant: 22 },
      { category: "Incident Response", compliant: 88, nonCompliant: 12 },
      { category: "Business Continuity", compliant: 75, nonCompliant: 25 }
    ]
  }

  function generateActivityData() {
    const data = []
    for (let week = 0; week < 12; week++) {
      for (let day = 0; day < 7; day++) {
        data.push({
          week: `W${week + 1}`,
          day,
          value: Math.floor(Math.random() * 10),
          activity: ["Policy Update", "Assessment", "Evidence Upload"][Math.floor(Math.random() * 3)]
        })
      }
    }
    return data
  }

  const handleExport = (format: string) => {
    // In a real app, this would generate and download the report
    console.log(`Exporting analytics in ${format} format`)
  }

  const handleRefresh = () => {
    setIsLoading(true)
    setTimeout(() => setIsLoading(false), 1000)
  }

  return (
    <div className="flex flex-1">
      <AppSidebar />
      <div className="flex-1 overflow-auto">
        <DashboardHeader />
        <div className="p-6 space-y-6">
          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-navy">Analytics Dashboard</h1>
              <p className="text-muted-foreground">
                Deep insights into your compliance performance and trends
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={isLoading}
              >
                <RefreshCw className={cn("h-4 w-4 mr-2", isLoading && "animate-spin")} />
                Refresh
              </Button>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-40 p-2">
                  <div className="space-y-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => handleExport("pdf")}
                    >
                      Export as PDF
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => handleExport("csv")}
                    >
                      Export as CSV
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start"
                      onClick={() => handleExport("json")}
                    >
                      Export as JSON
                    </Button>
                  </div>
                </PopoverContent>
              </Popover>
            </div>
          </div>

          {/* Filters Section */}
          <Card className="border-gold/20">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Filters</CardTitle>
                <Filter className="h-4 w-4 text-muted-foreground" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                {/* Date Range Picker */}
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "justify-start text-left font-normal",
                        !dateRange && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {dateRange?.from ? (
                        dateRange.to ? (
                          <>
                            {format(dateRange.from, "LLL dd, y")} -{" "}
                            {format(dateRange.to, "LLL dd, y")}
                          </>
                        ) : (
                          format(dateRange.from, "LLL dd, y")
                        )
                      ) : (
                        <span>Pick a date range</span>
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      initialFocus
                      mode="range"
                      defaultMonth={dateRange?.from || new Date()}
                      selected={dateRange}
                      onSelect={setDateRange}
                      numberOfMonths={2}
                    />
                  </PopoverContent>
                </Popover>

                {/* Framework Filter */}
                <Select value={selectedFramework} onValueChange={setSelectedFramework}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select framework" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Frameworks</SelectItem>
                    <SelectItem value="iso27001">ISO 27001</SelectItem>
                    <SelectItem value="gdpr">GDPR</SelectItem>
                    <SelectItem value="cyber-essentials">Cyber Essentials</SelectItem>
                    <SelectItem value="pci-dss">PCI DSS</SelectItem>
                    <SelectItem value="soc2">SOC 2</SelectItem>
                  </SelectContent>
                </Select>

                {/* Metric Filter */}
                <Select value={selectedMetric} onValueChange={setSelectedMetric}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select metric" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="compliance">Compliance Score</SelectItem>
                    <SelectItem value="risk">Risk Score</SelectItem>
                    <SelectItem value="tasks">Task Completion</SelectItem>
                    <SelectItem value="incidents">Incidents</SelectItem>
                  </SelectContent>
                </Select>

                {/* Quick Date Ranges */}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setDateRange({
                      from: subDays(new Date(), 7),
                      to: new Date()
                    })}
                  >
                    Last 7 days
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setDateRange({
                      from: subDays(new Date(), 30),
                      to: new Date()
                    })}
                  >
                    Last 30 days
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setDateRange({
                      from: startOfMonth(new Date()),
                      to: endOfMonth(new Date())
                    })}
                  >
                    This month
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Key Metrics Cards */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5">
            {Object.entries(analyticsData.advanced_metrics).map(([key, value]) => (
              <Card key={key} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-2">
                  <CardDescription className="capitalize">
                    {key.replace(/_/g, " ")}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold text-navy">
                    {key === "cost_savings" ? `$${value.toLocaleString()}` : 
                     key === "time_to_compliance" ? `${value} days` :
                     key.includes("rate") ? `${value}%` : value}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Main Analytics Tabs */}
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="compliance">Compliance</TabsTrigger>
              <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
              <TabsTrigger value="activity">Activity</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid gap-6 lg:grid-cols-2">
                {isLoading ? (
                  <>
                    <Skeleton className="h-[400px]" />
                    <Skeleton className="h-[400px]" />
                  </>
                ) : (
                  <>
                    <ComplianceTrendChart 
                      data={analyticsData.compliance_trends}
                      title="Compliance Score Trend"
                      description="Overall compliance performance over time"
                    />
                    <FrameworkBreakdownChart 
                      data={analyticsData.framework_scores}
                      title="Framework Performance"
                      description="Compliance scores by framework"
                    />
                  </>
                )}
              </div>
              <div className="grid gap-6 lg:grid-cols-3">
                {isLoading ? (
                  <>
                    <Skeleton className="h-[300px]" />
                    <Skeleton className="h-[300px]" />
                    <Skeleton className="h-[300px]" />
                  </>
                ) : (
                  <>
                    <TaskProgressChart 
                      data={[
                        { category: "Policies", completed: 45, pending: 3, overdue: 2 },
                        { category: "Assessments", completed: 23, pending: 1, overdue: 1 },
                        { category: "Evidence", completed: 67, pending: 5, overdue: 3 },
                        { category: "Training", completed: 12, pending: 2, overdue: 1 }
                      ]}
                    />
                    <RiskMatrix 
                      risks={[
                        { id: "1", name: "Data Breach", impact: 4, likelihood: 3, category: "Security" },
                        { id: "2", name: "Compliance Gap", impact: 3, likelihood: 2, category: "Compliance" },
                        { id: "3", name: "System Failure", impact: 4, likelihood: 2, category: "Operational" },
                        { id: "4", name: "Access Control", impact: 3, likelihood: 3, category: "Security" }
                      ]}
                    />
                    <ActivityHeatmap
                      data={analyticsData.activity_data.slice(0, 84).map((item: any) => ({
                        date: `${item.week}-${item.day}`,
                        count: item.value
                      }))}
                    />
                  </>
                )}
              </div>
            </TabsContent>

            <TabsContent value="compliance" className="space-y-6">
              {/* Add more detailed compliance analytics here */}
              <Card>
                <CardHeader>
                  <CardTitle>Compliance Deep Dive</CardTitle>
                  <CardDescription>
                    Detailed analysis of compliance metrics and trends
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Advanced compliance analytics coming soon...
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="risk" className="space-y-6">
              {/* Add risk analytics here */}
              <Card>
                <CardHeader>
                  <CardTitle>Risk Analysis</CardTitle>
                  <CardDescription>
                    Comprehensive risk assessment and mitigation tracking
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Risk analytics coming soon...
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="activity" className="space-y-6">
              {/* Add activity analytics here */}
              <Card>
                <CardHeader>
                  <CardTitle>Activity Analysis</CardTitle>
                  <CardDescription>
                    User activity patterns and engagement metrics
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Activity analytics coming soon...
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}