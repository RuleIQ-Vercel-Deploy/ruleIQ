'use client';

import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import { ResponsiveBar } from '@nivo/bar';
import { ResponsivePie } from '@nivo/pie';
import { ResponsiveHeatMap } from '@nivo/heatmap';

// Nivo theme for dark mode with purple accent
const purpleTheme = {
  background: 'transparent',
  text: {
    fontSize: 11,
    fill: '#9CA3AF',
  },
  axis: {
    domain: {
      line: {
        stroke: '#4B5563',
        strokeWidth: 1,
      },
    },
    legend: {
      text: {
        fontSize: 12,
        fill: '#9CA3AF',
      },
    },
    ticks: {
      line: {
        stroke: '#4B5563',
        strokeWidth: 1,
      },
      text: {
        fontSize: 11,
        fill: '#9CA3AF',
      },
    },
  },
  grid: {
    line: {
      stroke: '#374151',
      strokeWidth: 0.5,
    },
  },
  legends: {
    title: {
      text: {
        fontSize: 11,
        fill: '#9CA3AF',
      },
    },
    text: {
      fontSize: 11,
      fill: '#9CA3AF',
    },
  },
  tooltip: {
    wrapper: {},
    container: {
      background: '#1F2937',
      color: '#F3F4F6',
      fontSize: 12,
      borderRadius: '8px',
      border: '1px solid #8B5CF6',
    },
  },
};
// Animated Line Chart
export const NivoAnimatedLine = () => {
  const data = [
    {
      id: 'Compliance',
      color: '#8B5CF6',
      data: [
        { x: 'Jan', y: 87 },
        { x: 'Feb', y: 89 },
        { x: 'Mar', y: 92 },
        { x: 'Apr', y: 94 },
        { x: 'May', y: 96 },
        { x: 'Jun', y: 98 },
      ],
    },
    {
      id: 'Security',
      color: '#C0C0C0',
      data: [
        { x: 'Jan', y: 92 },
        { x: 'Feb', y: 88 },
        { x: 'Mar', y: 95 },
        { x: 'Apr', y: 91 },
        { x: 'May', y: 93 },
        { x: 'Jun', y: 97 },
      ],
    },
  ];

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20 h-[400px]">
      <h3 className="text-xl font-semibold text-white mb-4">Trend Analysis</h3>
      <ResponsiveLine
        data={data}
        theme={purpleTheme}
        margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
        xScale={{ type: 'point' }}
        yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: false, reverse: false }}
        curve="catmullRom"
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
        }}
        pointSize={10}
        pointColor={{ theme: 'background' }}
        pointBorderWidth={2}
        pointBorderColor={{ from: 'serieColor' }}
        pointLabelYOffset={-12}
        enableArea={true}
        areaOpacity={0.15}
        useMesh={true}
        legends={[
          {
            anchor: 'bottom-right',
            direction: 'column',
            justify: false,
            translateX: 100,
            translateY: 0,
            itemsSpacing: 0,
            itemDirection: 'left-to-right',
            itemWidth: 80,
            itemHeight: 20,
            itemOpacity: 0.75,
            symbolSize: 12,
            symbolShape: 'circle',
            symbolBorderColor: 'rgba(0, 0, 0, .5)',
          },
        ]}
        animate={true}
        motionConfig="gentle"
      />
    </div>
  );
};