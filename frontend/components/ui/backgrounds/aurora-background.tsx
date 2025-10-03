"use client";

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface AuroraBackgroundProps {
  children?: ReactNode;
  className?: string;
  showRadialGradient?: boolean;
}

export const AuroraBackground = ({
  children,
  className,
  showRadialGradient = true,
}: AuroraBackgroundProps) => {
  return (
    <div
      className={cn(
        "relative flex min-h-screen w-full flex-col items-center justify-center overflow-hidden",
        "bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900",
        className
      )}
    >
      {/* Aurora effect layers */}
      <div className="absolute inset-0 opacity-50">
        <div className="absolute left-1/4 top-1/4 h-96 w-96 animate-pulse rounded-full bg-purple-500/20 blur-3xl" />
        <div className="absolute right-1/4 top-1/3 h-80 w-80 animate-pulse rounded-full bg-blue-500/20 blur-3xl delay-1000" />
        <div className="absolute bottom-1/4 left-1/3 h-72 w-72 animate-pulse rounded-full bg-indigo-500/20 blur-3xl delay-500" />
      </div>

      {/* Radial gradient overlay */}
      {showRadialGradient && (
        <div className="absolute inset-0 bg-gradient-radial from-transparent via-slate-900/50 to-slate-900" />
      )}

      {/* Content */}
      <div className="relative z-10 w-full">
        {children}
      </div>
    </div>
  );
};