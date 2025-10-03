'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';

// Dynamically import VegaEmbed to avoid SSR issues
const VegaEmbed = dynamic(
  () => import('react-vega').then((mod) => ({ default: mod.VegaEmbed })),
  {
    ssr: false,
    loading: () => <div className="text-purple-400">Loading chart...</div>,
  }
);

export const VegaLiteVisualization = () => {
  const [spec, setSpec] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVegaSpec();
  }, []);

  const fetchVegaSpec = async () => {
    try {
      const response = await fetch('http://localhost:8000/vega-spec?chart_type=scatter');
      const specData = await response.json();
      setSpec(specData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching Vega spec:', error);
      // Use a default spec if API fails
      setSpec({
        $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
        description: 'Interactive Data Exploration',
        data: {
          values: Array.from({ length: 100 }, () => ({
            x: Math.random() * 100,
            y: Math.random() * 100,
            category: `Category ${Math.floor(Math.random() * 5) + 1}`,
            size: Math.random() * 1000
          }))
        },
        mark: { type: 'circle', opacity: 0.8 },
        encoding: {
          x: {
            field: 'x',
            type: 'quantitative',
            title: 'Performance Score',
            scale: { domain: [0, 100] }
          },
          y: {
            field: 'y',
            type: 'quantitative',
            title: 'Compliance Index',
            scale: { domain: [0, 100] }
          },
          size: {
            field: 'size',
            type: 'quantitative',
            legend: { title: 'Volume' }
          },
          color: {
            field: 'category',
            type: 'nominal',
            scale: {
              range: ['var(--purple-500)', 'var(--purple-500)', 'var(--purple-400)', 'var(--purple-400)', 'var(--purple-600)']
            },
            legend: { title: 'Category' }
          },
          tooltip: [
            { field: 'x', type: 'quantitative', format: '.2f', title: 'Performance' },
            { field: 'y', type: 'quantitative', format: '.2f', title: 'Compliance' },
            { field: 'size', type: 'quantitative', format: ',.0f', title: 'Volume' },
            { field: 'category', type: 'nominal', title: 'Category' }
          ]
        },
        width: 'container',
        height: 400,
        background: 'transparent',
        config: {
          axis: {
            gridColor: 'var(--silver-500)',
            domainColor: 'var(--silver-500)',
            tickColor: 'var(--silver-500)',
            labelColor: 'var(--silver-500)',
            titleColor: 'var(--purple-50)'
          },
          legend: {
            labelColor: 'var(--silver-500)',
            titleColor: 'var(--purple-50)'
          },
          view: {
            stroke: 'transparent'
          }
        }
      });
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20"
    >
      <h3 className="text-xl font-semibold text-white mb-4">Interactive Data Analysis</h3>
      {loading ? (
        <div className="h-[400px] flex items-center justify-center">
          <div className="text-purple-400">Loading visualization...</div>
        </div>
      ) : spec ? (
        <div className="w-full">
          <VegaEmbed spec={spec} />
        </div>
      ) : (
        <div className="h-[400px] flex items-center justify-center">
          <div className="text-red-400">Failed to load visualization</div>
        </div>
      )}
    </motion.div>
  );
};