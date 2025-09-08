'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

export function EnvBadge() {
  const [environment, setEnvironment] = useState<string>('development');

  useEffect(() => {
    // Determine environment from hostname or env variable
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      setEnvironment('development');
    } else if (hostname.includes('staging') || hostname.includes('test')) {
      setEnvironment('staging');
    } else if (hostname.includes('ruleiq.com')) {
      setEnvironment('production');
    } else {
      setEnvironment('development');
    }
  }, []);

  const envConfig = {
    development: {
      label: 'DEV',
      className: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
    },
    staging: {
      label: 'STAGING',
      className: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    },
    production: {
      label: 'PROD',
      className: 'bg-green-500/10 text-green-500 border-green-500/20',
    },
  };

  const config = envConfig[environment as keyof typeof envConfig] || envConfig.development;

  // Don't show badge in production
  if (environment === 'production') {
    return null;
  }

  return (
    <div
      className={cn(
        'fixed bottom-4 left-4 z-50 rounded-md border px-2 py-1 text-xs font-medium',
        config.className
      )}
    >
      {config.label}
    </div>
  );
}