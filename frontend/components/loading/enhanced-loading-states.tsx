'use client';

import { motion } from 'framer-motion';

import { 
  Skeleton,
  TableRowSkeleton,
  StatCardSkeleton,
  AssessmentCardSkeleton,
  PolicyCardSkeleton,
} from '@/components/ui/skeleton-loader';
import { LoadingSpinner } from '@/lib/animations/components';
import { cn } from '@/lib/utils';

// Full page loading with logo animation
export function FullPageLoader() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col items-center gap-4"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          className="h-16 w-16 rounded-full border-4 border-primary border-t-transparent"
        />
        <p className="text-sm text-muted-foreground">Loading ruleIQ...</p>
      </motion.div>
    </div>
  );
}

// Dashboard loading state
export function DashboardLoadingState() {
  return (
    <div className="space-y-6 p-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton variant="text" width={200} height={32} />
          <Skeleton variant="text" width={300} height={16} />
        </div>
        <Skeleton variant="rounded" width={150} height={48} />
      </div>

      {/* Stats grid skeleton */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>

      {/* Table skeleton */}
      <div className="rounded-lg border">
        <div className="p-4">
          <Skeleton variant="text" width={200} height={20} />
        </div>
        <table className="w-full">
          <tbody>
            {Array.from({ length: 5 }).map((_, i) => (
              <TableRowSkeleton key={i} columns={4} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Assessment list loading state
export function AssessmentListLoadingState() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <AssessmentCardSkeleton key={i} />
      ))}
    </div>
  );
}

// Policy list loading state
export function PolicyListLoadingState() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <PolicyCardSkeleton key={i} />
      ))}
    </div>
  );
}

// Inline loading indicator
export function InlineLoader({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <LoadingSpinner size={16} />
      <span className="text-sm text-muted-foreground">Loading...</span>
    </div>
  );
}

// Button loading state
export function ButtonLoader({ 
  text = 'Loading...',
  className 
}: { 
  text?: string;
  className?: string;
}) {
  return (
    <span className={cn('flex items-center gap-2', className)}>
      <LoadingSpinner size={16} />
      {text}
    </span>
  );
}

// Content placeholder with animation
export function ContentPlaceholder({ 
  lines = 3,
  className 
}: { 
  lines?: number;
  className?: string;
}) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton 
          key={i} 
          variant="text" 
          width={i === lines - 1 ? '60%' : '100%'} 
        />
      ))}
    </div>
  );
}

// Lazy loading image placeholder
export function ImagePlaceholder({ 
  aspectRatio = '16/9',
  className 
}: { 
  aspectRatio?: string;
  className?: string;
}) {
  return (
    <div 
      className={cn('relative overflow-hidden rounded-lg bg-muted', className)}
      style={{ aspectRatio }}
    >
      <Skeleton 
        variant="rectangular" 
        width="100%" 
        height="100%" 
        className="absolute inset-0"
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <svg
            className="h-12 w-12 text-muted-foreground/50"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </motion.div>
      </div>
    </div>
  );
}

// Progress loading bar
export function ProgressLoader({ progress = 0 }: { progress?: number }) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">Loading...</span>
        <span className="text-sm text-muted-foreground">{progress}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

// Dots loading animation
export function DotsLoader({ className }: { className?: string }) {
  const dotVariants = {
    initial: { y: 0 },
    animate: { y: [-3, 3, -3] },
  };
  
  const transition = {
    duration: 0.6,
    repeat: Infinity,
    ease: 'easeInOut' as const,
  };

  return (
    <div className={cn('flex items-center gap-1', className)}>
      {[0, 0.1, 0.2].map((delay, i) => (
        <motion.div
          key={i}
          className="h-2 w-2 rounded-full bg-primary"
          variants={dotVariants}
          initial="initial"
          animate="animate"
          transition={{ ...transition, delay }}
        />
      ))}
    </div>
  );
}