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
import { neuralPurple, silver, semantic, chartColors, neutral } from '@/lib/theme/neural-purple-colors';

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
  'ISO 27001': chartColors.primary, // neural purple primary
  GDPR: semantic.success, // semantic success
  'Cyber Essentials': semantic.warning, // semantic warning
  'PCI DSS': semantic.info, // semantic info
  'SOC 2': silver.DEFAULT, // silver default
  HIPAA: chartColors.tertiary, // neural purple light
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
    color: item.color || COLORS[item.framework as keyof typeof COLORS] || '#8b5cf6280',
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
                fill="#8b5cf64d8"
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
              <PolarAngleAxis dataKey="framework" tick={{ fontSize: 12, fill: neutral.gray[600] }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10, fill: neutral.gray[600] }} />
              <Radar
                name="Score"
                dataKey="score"
                stroke={neuralPurple.primaryDark}
                fill={neuralPurple.primary}
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
