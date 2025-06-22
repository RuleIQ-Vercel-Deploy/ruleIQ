"use client"

import * as React from "react"
import { LoadingSpinner } from "./progress-indicators"
import { FadeTransition, LoadingOverlay } from "./transitions"
import {
  LoadingLayout,
  TableLoadingSkeleton,
  FormLoadingSkeleton,
  CardGridLoadingSkeleton,
} from "../layout/loading-layout"

interface LoadingStateManagerProps {
  loading: boolean
  error?: Error | null
  children: React.ReactNode
  loadingComponent?: React.ReactNode
  errorComponent?: React.ReactNode
  skeleton?: "layout" | "table" | "form" | "cards" | "custom"
  overlay?: boolean
  message?: string
  progress?: number
  className?: string
}

export function LoadingStateManager({
  loading,
  error,
  children,
  loadingComponent,
  errorComponent,
  skeleton = "layout",
  overlay = false,
  message,
  progress,
  className,
}: LoadingStateManagerProps) {
  // Error state
  if (error && !loading) {
    return (
      <FadeTransition show={true} className={className}>
        {errorComponent || (
          <div className="text-center py-8">
            <div className="text-red-500 mb-2">⚠️</div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Something went wrong</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{error.message || "An unexpected error occurred"}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}
      </FadeTransition>
    )
  }

  // Loading state with overlay
  if (loading && overlay) {
    return (
      <>
        {children}
        <LoadingOverlay show={loading} message={message} progress={progress} />
      </>
    )
  }

  // Loading state
  if (loading) {
    return (
      <FadeTransition show={true} className={className}>
        {loadingComponent || (
          <>
            {skeleton === "layout" && <LoadingLayout />}
            {skeleton === "table" && <TableLoadingSkeleton />}
            {skeleton === "form" && <FormLoadingSkeleton />}
            {skeleton === "cards" && <CardGridLoadingSkeleton />}
            {skeleton === "custom" && (
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner size="lg" />
                {message && <span className="ml-3 text-gray-600">{message}</span>}
              </div>
            )}
          </>
        )}
      </FadeTransition>
    )
  }

  // Success state
  return (
    <FadeTransition show={true} className={className}>
      {children}
    </FadeTransition>
  )
}

// Suspense boundary with loading states
interface SuspenseBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  skeleton?: "layout" | "table" | "form" | "cards"
}

export function SuspenseBoundary({ children, fallback, skeleton = "layout" }: SuspenseBoundaryProps) {
  const defaultFallback = React.useMemo(() => {
    switch (skeleton) {
      case "table":
        return <TableLoadingSkeleton />
      case "form":
        return <FormLoadingSkeleton />
      case "cards":
        return <CardGridLoadingSkeleton />
      default:
        return <LoadingLayout />
    }
  }, [skeleton])

  return <React.Suspense fallback={fallback || defaultFallback}>{children}</React.Suspense>
}
