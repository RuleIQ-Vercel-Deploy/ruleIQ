'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface TimeSeriesAnalysisChartProps {
  data: Array<{
    date: string;
    score: number;
    target?: number;
    incidents?: number;
    tasks?: number;
  }>;
  title?: string;
  description?: string;
  className?: string;
}

export function TimeSeriesAnalysisChart({
  data,
  title = 'Time Series Analysis',
  description = 'Compliance trends over time',
  className,
}: TimeSeriesAnalysisChartProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatTooltipDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} tickFormatter={formatDate} />
            <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} />
            <Tooltip
              labelFormatter={formatTooltipDate}
              formatter={(value: number, name: string) => [
                `${value}${name.includes('Score') || name.includes('Target') ? '%' : ''}`,
                name,
              ]}
              labelStyle={{ color: '#333' }}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            <Legend />

            {/* Target line */}
            {data.some((item) => item.target) && (
              <ReferenceLine
                y={data[0]?.target || 90}
                stroke="#CB963E"
                strokeDasharray="5 5"
                label={{ value: 'Target', position: 'top' }}
              />
            )}

            {/* Main compliance score line */}
            <Line
              type="monotone"
              dataKey="score"
              stroke="#17255A"
              strokeWidth={3}
              dot={{ fill: '#17255A', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#17255A', strokeWidth: 2 }}
              name="Compliance Score"
            />

            {/* Secondary metrics */}
            {data.some((item) => item.incidents !== undefined) && (
              <Line
                type="monotone"
                dataKey="incidents"
                stroke="#DC3545"
                strokeWidth={2}
                dot={{ fill: '#DC3545', strokeWidth: 1, r: 3 }}
                name="Incidents"
                yAxisId="right"
              />
            )}

            {data.some((item) => item.tasks !== undefined) && (
              <Line
                type="monotone"
                dataKey="tasks"
                stroke="#28A745"
                strokeWidth={2}
                dot={{ fill: '#28A745', strokeWidth: 1, r: 3 }}
                name="Tasks Completed"
                yAxisId="right"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
