"use client"

import { format } from "date-fns"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface ComplianceTrendChartProps {
  data: Array<{
    date: string
    score: number
    target?: number
  }>
  title?: string
  description?: string
  className?: string
}

export function ComplianceTrendChart({
  data,
  title = "Compliance Score Trend",
  description = "Your compliance score over the last 30 days",
  className
}: ComplianceTrendChartProps) {
  const formattedData = data.map(item => ({
    ...item,
    date: format(new Date(item.date), "MMM dd"),
    target: item.target || 90
  }))

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-900">{label}</p>
          <p className="text-sm text-primary">
            Score: <span className="font-semibold">{payload[0].value}%</span>
          </p>
          {payload[1] && (
            <p className="text-sm text-gray-500">
              Target: <span className="font-semibold">{payload[1].value}%</span>
            </p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={formattedData}>
            <defs>
              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#17255A" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#17255A" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="date" 
              className="text-xs"
              tick={{ fill: '#6B7280' }}
              axisLine={{ stroke: '#E5E7EB' }}
            />
            <YAxis 
              domain={[0, 100]}
              className="text-xs"
              tick={{ fill: '#6B7280' }}
              axisLine={{ stroke: '#E5E7EB' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="score"
              stroke="#17255A"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorScore)"
            />
            <Line
              type="monotone"
              dataKey="target"
              stroke="#CB963E"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}