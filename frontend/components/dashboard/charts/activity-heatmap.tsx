"use client"

import { ResponsiveContainer, Tooltip } from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ActivityHeatmapProps {
  data: Array<{
    date: string
    count: number
  }>
  title?: string
  description?: string
  className?: string
}

export function ActivityHeatmap({
  data,
  title = "Activity Heatmap",
  description = "Your compliance activity over the last 12 weeks",
  className
}: ActivityHeatmapProps) {
  // Group data by week
  const weeks: Array<Array<{ date: string; count: number; day: number }>> = []
  let currentWeek: Array<{ date: string; count: number; day: number }> = []
  
  data.forEach(item => {
    const date = new Date(item.date)
    const day = date.getDay()
    
    if (day === 0 && currentWeek.length > 0) {
      weeks.push(currentWeek)
      currentWeek = []
    }
    
    currentWeek.push({ ...item, day })
  })
  
  if (currentWeek.length > 0) {
    weeks.push(currentWeek)
  }

  const getIntensity = (count: number) => {
    if (count === 0) return "bg-gray-100"
    if (count <= 2) return "bg-cyan/20"
    if (count <= 5) return "bg-cyan/40"
    if (count <= 10) return "bg-cyan/60"
    return "bg-cyan"
  }

  const days = ["S", "M", "T", "W", "T", "F", "S"]

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {/* Day labels */}
          <div className="flex gap-1 text-xs text-muted-foreground mb-2">
            <div className="w-4" />
            {days.map((day, i) => (
              <div key={i} className="w-4 text-center">
                {day}
              </div>
            ))}
          </div>
          
          {/* Heatmap grid */}
          <div className="flex gap-1">
            {weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-1">
                {[0, 1, 2, 3, 4, 5, 6].map(dayIndex => {
                  const dayData = week.find(d => d.day === dayIndex)
                  return (
                    <div
                      key={dayIndex}
                      className={cn(
                        "w-4 h-4 rounded-sm transition-colors",
                        dayData ? getIntensity(dayData.count) : "bg-gray-50"
                      )}
                      title={dayData ? `${dayData.date}: ${dayData.count} activities` : "No data"}
                    />
                  )
                })}
              </div>
            ))}
          </div>
          
          {/* Legend */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground mt-4">
            <span>Less</span>
            <div className="flex gap-1">
              <div className="w-3 h-3 rounded-sm bg-gray-100" />
              <div className="w-3 h-3 rounded-sm bg-cyan/20" />
              <div className="w-3 h-3 rounded-sm bg-cyan/40" />
              <div className="w-3 h-3 rounded-sm bg-cyan/60" />
              <div className="w-3 h-3 rounded-sm bg-cyan" />
            </div>
            <span>More</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}