'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface ComplianceDistributionChartProps {
  data: Array<{
    category: string;
    compliant: number;
    nonCompliant: number;
  }>;
  title?: string;
  description?: string;
  className?: string;
}

export function ComplianceDistributionChart({
  data,
  title = 'Compliance Distribution',
  description = 'Distribution of compliant vs non-compliant items',
  className,
}: ComplianceDistributionChartProps) {
  // Transform data for pie chart
  const pieData = data.flatMap((item) => [
    {
      name: `${item.category} - Compliant`,
      value: item.compliant,
      category: item.category,
      status: 'compliant',
    },
    {
      name: `${item.category} - Non-Compliant`,
      value: item.nonCompliant,
      category: item.category,
      status: 'non-compliant',
    },
  ]);

  const COLORS = {
    compliant: '#10B981', // emerald-600 - success
    'non-compliant': '#EF4444', // red-600 - error
  };

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
    if (percent < 0.05) return null; // Don't show labels for very small slices

    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.status as keyof typeof COLORS]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, name: string) => [`${value}%`, name]}
              labelStyle={{ color: '#333' }}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value: string) => value.replace(' - ', ': ')}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
