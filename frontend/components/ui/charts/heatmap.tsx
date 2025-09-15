'use client';

import React from 'react';
import { motion } from 'framer-motion';

// Heatmap Chart Component
export const HeatmapChart = () => {
  const data = Array.from({ length: 7 }, () =>
    Array.from({ length: 24 }, () => Math.random())
  );
  
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20">
      <h3 className="text-xl font-semibold text-white mb-4">Activity Heatmap</h3>
      <div className="overflow-x-auto">
        <div className="grid grid-rows-7 gap-1 min-w-[600px]">
          {data.map((row, dayIndex) => (
            <div key={dayIndex} className="flex items-center gap-1">
              <span className="text-xs text-gray-400 w-10">{days[dayIndex]}</span>
              <div className="flex gap-1">
                {row.map((value, hourIndex) => (
                  <motion.div
                    key={`${dayIndex}-${hourIndex}`}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: (dayIndex * 24 + hourIndex) * 0.002 }}
                    className="w-6 h-6 rounded"
                    style={{
                      backgroundColor: `rgba(139, 92, 246, ${value})`,
                      boxShadow: value > 0.7 ? '0 0 10px rgba(139, 92, 246, 0.5)' : 'none'
                    }}
                    title={`${days[dayIndex]} ${hours[hourIndex]}:00 - ${Math.round(value * 100)}%`}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};