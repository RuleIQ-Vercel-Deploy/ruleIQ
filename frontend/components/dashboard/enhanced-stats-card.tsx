import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { MetricDisplay } from "@/components/ui/metric-display"
import { MiniChart } from "@/components/ui/mini-chart"

import type { LucideIcon } from "lucide-react"

interface EnhancedStatsCardProps {
  title: string
  description: string
  value: string | number
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  chartData?: number[]
  chartType?: "line" | "bar" | "area"
  className?: string
}

export function EnhancedStatsCard({
  title,
  description,
  value,
  icon: Icon,
  trend,
  chartData,
  chartType = "line",
  className,
}: EnhancedStatsCardProps) {
  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-foreground">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <MetricDisplay
          label=""
          value={value}
          change={
            trend
              ? {
                  value: trend.value,
                  isPositive: trend.isPositive,
                  period: "vs last month",
                }
              : undefined
          }
        />
        <CardDescription className="mt-2 text-muted-foreground">{description}</CardDescription>
        {chartData && (
          <div className="mt-4">
            <MiniChart
              data={chartData}
              type={chartType}
              color={trend?.isPositive ? "#28A745" : "#FFC107"}
              height={32}
            />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
