'use client';

import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { motion } from 'framer-motion';

const data = [
  { month: 'Jan', compliance: 87, security: 92, performance: 78, users: 120 },
  { month: 'Feb', compliance: 89, security: 88, performance: 82, users: 145 },
  { month: 'Mar', compliance: 92, security: 95, performance: 88, users: 180 },
  { month: 'Apr', compliance: 94, security: 91, performance: 85, users: 210 },
  { month: 'May', compliance: 96, security: 93, performance: 90, users: 250 },
  { month: 'Jun', compliance: 98, security: 97, performance: 93, users: 320 },
];
const radarData = [
  { subject: 'Security', A: 120, B: 110, fullMark: 150 },
  { subject: 'Performance', A: 98, B: 130, fullMark: 150 },
  { subject: 'Compliance', A: 86, B: 130, fullMark: 150 },
  { subject: 'Reliability', A: 99, B: 100, fullMark: 150 },
  { subject: 'Scalability', A: 85, B: 90, fullMark: 150 },
  { subject: 'UX', A: 65, B: 85, fullMark: 150 },
];

const pieData = [
  { name: 'Critical', value: 400, color: '#8B5CF6' },
  { name: 'High', value: 300, color: '#A855F7' },
  { name: 'Medium', value: 300, color: '#C084FC' },
  { name: 'Low', value: 200, color: '#E9D5FF' },
];

// Glowing Area Chart
export const GlowingAreaChart = () => {
  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20">
      <h3 className="text-xl font-semibold text-white mb-4">Performance Trends</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorCompliance" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.1}/>
            </linearGradient>
            <linearGradient id="colorSecurity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#C0C0C0" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#C0C0C0" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
          <XAxis dataKey="month" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1F2937', 
              border: '1px solid #8B5CF6',
              borderRadius: '8px' 
            }} 
          />
          <Area type="monotone" dataKey="compliance" stroke="#8B5CF6" fillOpacity={1} fill="url(#colorCompliance)" strokeWidth={2} />
          <Area type="monotone" dataKey="security" stroke="#C0C0C0" fillOpacity={1} fill="url(#colorSecurity)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
// Animated Radar Chart
export const AnimatedRadarChart = () => {
  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20">
      <h3 className="text-xl font-semibold text-white mb-4">System Metrics</h3>
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={radarData}>
          <PolarGrid stroke="#374151" strokeDasharray="3 3" />
          <PolarAngleAxis dataKey="subject" stroke="#9CA3AF" />
          <PolarRadiusAxis angle={90} domain={[0, 150]} stroke="#9CA3AF" />
          <Radar name="Current" dataKey="A" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.6} />
          <Radar name="Target" dataKey="B" stroke="#C0C0C0" fill="#C0C0C0" fillOpacity={0.3} />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

// Composed Chart with Bar and Line
export const ComposedDashboardChart = () => {
  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20">
      <h3 className="text-xl font-semibold text-white mb-4">Revenue & Users</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
          <XAxis dataKey="month" stroke="#9CA3AF" />
          <YAxis yAxisId="left" stroke="#9CA3AF" />
          <YAxis yAxisId="right" orientation="right" stroke="#9CA3AF" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1F2937', 
              border: '1px solid #8B5CF6',
              borderRadius: '8px' 
            }} 
          />
          <Legend />
          <Bar yAxisId="left" dataKey="users" fill="#8B5CF6" radius={[8, 8, 0, 0]} />
          <Line yAxisId="right" type="monotone" dataKey="performance" stroke="#C0C0C0" strokeWidth={3} dot={{ fill: '#C0C0C0', r: 6 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};