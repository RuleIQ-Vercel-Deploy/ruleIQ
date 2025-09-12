'use client';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export function EnvBadge() {
  const env = process.env.NEXT_PUBLIC_ENV || process.env.NODE_ENV || 'development';
  
  const getEnvConfig = () => {
    switch (env) {
      case 'production':
        return { label: 'PROD', className: 'bg-green-500/10 text-green-500 border-green-500/20' };
      case 'staging':
        return { label: 'STAGING', className: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' };
      case 'development':
      default:
        return { label: 'DEV', className: 'bg-blue-500/10 text-blue-500 border-blue-500/20' };
    }
  };

  const config = getEnvConfig();

  return (
    <Badge 
      variant="outline" 
      className={cn('text-xs font-mono', config.className)}
    >
      {config.label}
    </Badge>
  );
}