'use client';

import { motion } from 'framer-motion';

import { shimmer } from '@/lib/animations/variants';
import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  animation?: boolean;
}

export function Skeleton({
  className,
  variant = 'text',
  width,
  height,
  animation = true,
}: SkeletonProps) {
  const baseClasses = 'relative overflow-hidden bg-muted';

  const variantClasses = {
    text: 'h-4 w-full rounded',
    circular: 'rounded-full',
    rectangular: '',
    rounded: 'rounded-md',
  };

  const style = {
    width: width || (variant === 'circular' ? 40 : undefined),
    height: height || (variant === 'circular' ? 40 : variant === 'text' ? 16 : 100),
  };

  return (
    <div className={cn(baseClasses, variantClasses[variant], className)} style={style}>
      {animation && (
        <motion.div
          className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent"
          variants={shimmer}
          initial="initial"
          animate="animate"
        />
      )}
    </div>
  );
}

// Composite skeleton loaders for common patterns

// Card skeleton
export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('rounded-lg border bg-card p-6', className)}>
      <div className="space-y-3">
        <Skeleton variant="rectangular" height={200} className="rounded-md" />
        <Skeleton variant="text" width="80%" />
        <Skeleton variant="text" width="60%" />
        <div className="flex items-center gap-2 pt-2">
          <Skeleton variant="circular" width={24} height={24} />
          <Skeleton variant="text" width="40%" />
        </div>
      </div>
    </div>
  );
}

// Table row skeleton
export function TableRowSkeleton({ columns = 4 }: { columns?: number }) {
  return (
    <tr className="border-b">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="p-4">
          <Skeleton variant="text" width="90%" />
        </td>
      ))}
    </tr>
  );
}

// List item skeleton
export function ListItemSkeleton() {
  return (
    <div className="flex items-center space-x-4 p-4">
      <Skeleton variant="circular" width={48} height={48} />
      <div className="flex-1 space-y-2">
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="text" width="40%" />
      </div>
    </div>
  );
}

// Dashboard stat card skeleton
export function StatCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="flex items-center justify-between space-x-4">
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" width="50%" height={12} />
          <Skeleton variant="text" width="30%" height={24} />
          <Skeleton variant="text" width="60%" height={12} />
        </div>
        <Skeleton variant="circular" width={48} height={48} />
      </div>
    </div>
  );
}

// Form skeleton
export function FormSkeleton({ fields = 3 }: { fields?: number }) {
  return (
    <div className="space-y-6">
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton variant="text" width="30%" height={14} />
          <Skeleton variant="rounded" height={40} />
        </div>
      ))}
      <div className="flex gap-4 pt-4">
        <Skeleton variant="rounded" width={100} height={40} />
        <Skeleton variant="rounded" width={100} height={40} />
      </div>
    </div>
  );
}

// Chat message skeleton
export function ChatMessageSkeleton({ isUser = false }: { isUser?: boolean }) {
  return (
    <div className={cn('flex gap-3', isUser && 'flex-row-reverse')}>
      <Skeleton variant="circular" width={40} height={40} />
      <div className={cn('space-y-2', isUser && 'items-end')}>
        <Skeleton variant="rounded" width={200} height={80} />
        <Skeleton variant="text" width={100} height={12} />
      </div>
    </div>
  );
}

// Navigation skeleton
export function NavigationSkeleton() {
  return (
    <nav className="flex items-center space-x-6 p-4">
      <Skeleton variant="circular" width={32} height={32} />
      {Array.from({ length: 4 }).map((_, i) => (
        <Skeleton key={i} variant="text" width={80} height={16} />
      ))}
    </nav>
  );
}

// Assessment card skeleton
export function AssessmentCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="space-y-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <Skeleton variant="text" width="70%" height={20} />
            <Skeleton variant="text" width="50%" height={14} />
          </div>
          <Skeleton variant="rounded" width={80} height={24} />
        </div>
        <Skeleton variant="rounded" height={8} />
        <div className="flex items-center justify-between">
          <Skeleton variant="text" width="30%" height={14} />
          <Skeleton variant="text" width="20%" height={14} />
        </div>
      </div>
    </div>
  );
}

// Policy card skeleton
export function PolicyCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <Skeleton variant="circular" width={40} height={40} />
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="40%" height={14} />
          </div>
        </div>
        <Skeleton variant="text" />
        <Skeleton variant="text" width="80%" />
        <div className="flex gap-2 pt-2">
          <Skeleton variant="rounded" width={60} height={24} />
          <Skeleton variant="rounded" width={60} height={24} />
        </div>
      </div>
    </div>
  );
}
