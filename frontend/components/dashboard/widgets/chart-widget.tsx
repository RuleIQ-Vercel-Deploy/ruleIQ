'use client';

import React from 'react';
import {
  Line,
  Bar,
  Area,
  Pie,
  ResponsiveContainer,
  LineChart,
  BarChart,
  AreaChart,
  PieChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
} from 'recharts';

import { cn } from '@/lib/utils';

export type ChartType = 'line' | 'bar' | 'area' | 'pie' | 'radar' | 'polar';

interface ChartWidgetProps {
  data: unknown[];
  type?: ChartType;
  dataKey: string;
  xAxisKey?: string;
  height?: number;
  colors?: string[];
  showGrid?: boolean;
  showLegend?: boolean;
  className?: string;
}

const defaultColors = [
  '#8b5cf6CF6', // purple-500 - primary
  '#8b5cf6AED', // purple-600 - secondary
  '#8b5cf64FC', // purple-400 - bright
  '#8b5cf6BFA', // purple-400 - light
  '#8b5cf68D9', // purple-700 - dark
  '#8b5cf61B6', // purple-800 - darker
];

export function ChartWidget({
  data,
  type = 'line',
  dataKey,
  xAxisKey = 'name',
  height = 200,
  colors = defaultColors,
  showGrid = true,
  showLegend = false,
  className,
}: ChartWidgetProps) {
  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 5, right: 5, left: 5, bottom: 5 },
    };

    const axisProps = {
      stroke: '#8b5cf63AF',
      fontSize: 12,
    };

    const gridProps = {
      strokeDasharray: '3 3',
      stroke: '#8b5cf67EB',
    };

    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid {...gridProps} />}
            <XAxis dataKey={xAxisKey} {...axisProps} />
            <YAxis {...axisProps} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #8b5cf67EB',
                borderRadius: '8px',
              }}
            />
            {showLegend && <Legend />}
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={colors[0]}
              strokeWidth={2}
              dot={{ fill: colors[0], r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid {...gridProps} />}
            <XAxis dataKey={xAxisKey} {...axisProps} />
            <YAxis {...axisProps} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #8b5cf67EB',
                borderRadius: '8px',
              }}
            />
            {showLegend && <Legend />}
            <Bar dataKey={dataKey} fill={colors[0]} radius={[4, 4, 0, 0]} />
          </BarChart>
        );

      case 'area':
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid {...gridProps} />}
            <XAxis dataKey={xAxisKey} {...axisProps} />
            <YAxis {...axisProps} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #8b5cf67EB',
                borderRadius: '8px',
              }}
            />
            {showLegend && <Legend />}
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={colors[0]}
              fill={colors[0]}
              fillOpacity={0.2}
              strokeWidth={2}
            />
          </AreaChart>
        );

      case 'pie':
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={(entry) => `${entry[dataKey]}%`}
              outerRadius={80}
              fill="#8b5cf64d8"
              dataKey={dataKey}
            >
              {data.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #8b5cf67EB',
                borderRadius: '8px',
              }}
            />
            {showLegend && <Legend />}
          </PieChart>
        );

      default:
        return null;
    }
  };

  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        {renderChart() || <div>Unsupported chart type</div>}
      </ResponsiveContainer>
    </div>
  );
}
