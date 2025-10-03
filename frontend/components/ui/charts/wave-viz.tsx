'use client';

import React, { useState, useEffect } from 'react';
import { LinearGradient } from '@visx/gradient';
import { curveBasis } from '@visx/curve';
import { LinePath } from '@visx/shape';
import { motion } from 'framer-motion';

// WAVE DATA VISUALIZATION - Flowing liquid data
export const WaveDataVisualization = () => {
  const width = 600;
  const height = 300;
  const [data, setData] = useState<{ x: number; y: number }[]>([]);
  
  useEffect(() => {
    const generateWaveData = () => {
      const points = [];
      for (let i = 0; i <= 50; i++) {
        const x = (i / 50) * width;
        const y = height / 2 + 
          Math.sin((i / 10) + Date.now() / 500) * 30 +
          Math.sin((i / 5) + Date.now() / 300) * 20 +
          Math.sin((i / 3) + Date.now() / 700) * 15;
        points.push({ x, y });
      }
      return points;
    };

    const interval = setInterval(() => {
      setData(generateWaveData());
    }, 50);

    return () => clearInterval(interval);
  }, [width, height]);

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20">
      <h3 className="text-xl font-semibold text-white mb-4">Data Flow Dynamics</h3>
      <div className="relative overflow-hidden"style={{ width: '100%', height: '300px' }}>
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
          <LinearGradient id="wave-gradient" from="var(--purple-500)" to="var(--silver-400)" />
          <LinearGradient id="wave-gradient-2" from="var(--silver-400)" to="var(--purple-500)" fromOpacity={0.8} toOpacity={0.3} />
          
          {/* Multiple wave layers for depth */}
          {[0, 1, 2].map((layer) => (
            <g key={layer}>
              <LinePath
                data={data.map(d => ({ 
                  x: d.x, 
                  y: d.y + layer * 20 
                }))}
                curve={curveBasis}
                x={(d) => d.x}
                y={(d) => d.y}
                stroke={`url(#wave-gradient${layer === 1 ? '-2' : ''})`}
                strokeWidth={3 - layer * 0.5}
                opacity={1 - layer * 0.3}
                fill="none"
              />
              <LinePath
                data={data.map(d => ({ 
                  x: d.x, 
                  y: d.y + layer * 20 
                }))}
                curve={curveBasis}
                x={(d) => d.x}
                y={(d) => d.y}
                fill={`url(#wave-gradient${layer === 1 ? '-2' : ''})`}
                fillOpacity={0.1 - layer * 0.03}
                stroke="none"
              />
            </g>
          ))}
          
          {/* Glow effect */}
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
        </svg>
        
        {/* Animated particles overlay */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-purple-400 rounded-full"
              initial={{ 
                x: Math.random() * width, 
                y: Math.random() * height,
                opacity: 0 
              }}
              animate={{ 
                x: [null, Math.random() * width],
                y: [null, Math.random() * height],
                opacity: [0, 1, 0]
              }}
              transition={{ 
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};