'use client';

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface FrameworkBreakdownChartProps {
  data: Array<{
    framework: string;
    score: number;
    color?: string;
  }>;
  title?: string;
  description?: string;
  chartType?: 'pie' | 'radar';
  className?: string;
}

const COLORS = {
  'ISO 27001': '#2C7A7B', // teal-600 - primary
  GDPR: '#319795', // teal-500 - secondary
  'Cyber Essentials': '#4FD1C5', // teal-300 - bright accent
  'PCI DSS': '#10B981', // emerald-600 - success
  'SOC 2': '#F59E0B', // amber-600 - warning
  HIPAA: '#6B7280', // neutral-500 - muted
};

export function FrameworkBreakdownChart({
  data,
  title = 'Framework Compliance',
  description = 'Compliance scores by framework',
  chartType = 'radar',
  className,
}: FrameworkBreakdownChartProps) {
  const enhancedData = data.map((item) => ({
    ...item,
    color: item.color || COLORS[item.framework as keyof typeof COLORS] || '#6B7280',
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg border border-gray-200 bg-white p-3 shadow-lg">
          <p className="text-sm font-semibold text-gray-900">{payload[0].payload.framework}</p>
          <p className="text-sm text-primary">
            Score: <span className="font-semibold">{payload[0].value}%</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          {chartType === 'pie' ? (
            <PieChart>
              <Pie
                data={enhancedData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ framework, score }) => `${framework}: ${score}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="score"
              >
                {enhancedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          ) : (
            <RadarChart data={enhancedData}>
              <PolarGrid strokeDasharray="3 3" />
              <PolarAngleAxis dataKey="framework" tick={{ fontSize: 12, fill: '#6B7280' }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#6B7280' }} />
              <Radar
                name="Score"
                dataKey="score"
                stroke="#17255A"
                fill="#17255A"
                fillOpacity={0.6}
                strokeWidth={2}
              />
              <Tooltip content={<CustomTooltip />} />
            </RadarChart>
          )}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
