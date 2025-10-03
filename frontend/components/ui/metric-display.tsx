import { TrendingUp, TrendingDown } from 'lucide-react';

import type * as React from 'react';

interface MetricDisplayProps {
  label: string;
  value: string | number;
  change?: {
    value: number;
    isPositive: boolean;
    period?: string;
  };
  icon?: React.ReactNode;
  className?: string;
}

export function MetricDisplay({ label, value, change, icon, className = '' }: MetricDisplayProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium" style={{ color: 'var(--silver-500)' }}>
          {label}
        </span>
        {icon && <div style={{ color: 'var(--silver-500)' }}>{icon}</div>}
      </div>
      <div className="flex items-end justify-between">
        <span className="text-2xl font-bold" style={{ color: 'var(--purple-50)' }}>
          {value}
        </span>
        {change && (
          <div
            className={`flex items-center text-xs ${change.isPositive ? 'text-success' : 'text-error'}`}
          >
            {change.isPositive ? (
              <TrendingUp className="mr-1 h-3 w-3" />
            ) : (
              <TrendingDown className="mr-1 h-3 w-3" />
            )}
            {change.isPositive ? '+' : ''}
            {change.value}%
            {change.period && <span className="ml-1 text-gray-500">{change.period}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
