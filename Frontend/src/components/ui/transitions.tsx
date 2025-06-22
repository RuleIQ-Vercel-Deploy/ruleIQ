"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface FadeTransitionProps {
  show: boolean
  children: React.ReactNode
  duration?: number
  className?: string
}

export function FadeTransition({ show, children, duration = 300, className }: FadeTransitionProps) {
  const [shouldRender, setShouldRender] = React.useState(show)

  React.useEffect(() => {
    if (show) {
      setShouldRender(true)
    } else {
      const timer = setTimeout(() => setShouldRender(false), duration)
      return () => clearTimeout(timer)
    }
  }, [show, duration])

  if (!shouldRender) return null

  return (
    <div
      className={cn("transition-opacity ease-in-out", show ? "opacity-100" : "opacity-0", className)}
      style={{ transitionDuration: `${duration}ms` }}
    >
      {children}
    </div>
  )
}

interface SlideTransitionProps {
  show: boolean
  children: React.ReactNode
  direction?: "up" | "down" | "left" | "right"
  duration?: number
  className?: string
}

export function SlideTransition({ show, children, direction = "up", duration = 300, className }: SlideTransitionProps) {
  const [shouldRender, setShouldRender] = React.useState(show)

  React.useEffect(() => {
    if (show) {
      setShouldRender(true)
    } else {
      const timer = setTimeout(() => setShouldRender(false), duration)
      return () => clearTimeout(timer)
    }
  }, [show, duration])

  if (!shouldRender) return null

  const directionClasses = {
    up: show ? "translate-y-0" : "translate-y-4",
    down: show ? "translate-y-0" : "-translate-y-4",
    left: show ? "translate-x-0" : "translate-x-4",
    right: show ? "translate-x-0" : "-translate-x-4",
  }

  return (
    <div
      className={cn(
        "transition-all ease-in-out",
        show ? "opacity-100" : "opacity-0",
        directionClasses[direction],
        className,
      )}
      style={{ transitionDuration: `${duration}ms` }}
    >
      {children}
    </div>
  )
}

interface StaggeredTransitionProps {
  show: boolean
  children: React.ReactNode[]
  staggerDelay?: number
  className?: string
}

export function StaggeredTransition({ show, children, staggerDelay = 100, className }: StaggeredTransitionProps) {
  return (
    <div className={className}>
      {children.map((child, index) => (
        <div
          key={index}
          className={cn(
            "transition-all duration-300 ease-out",
            show ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4",
          )}
          style={{
            transitionDelay: show ? `${index * staggerDelay}ms` : "0ms",
          }}
        >
          {child}
        </div>
      ))}
    </div>
  )
}

interface LoadingOverlayProps {
  show: boolean
  message?: string
  progress?: number
  children?: React.ReactNode
  className?: string
}

export function LoadingOverlay({ show, message = "Loading...", progress, children, className }: LoadingOverlayProps) {
  if (!show) return null

  return (
    <div
      className={cn(
        "fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center",
        "animate-in fade-in-0 duration-200",
        className,
      )}
    >
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl max-w-sm w-full mx-4">
        <div className="text-center space-y-4">
          {children || (
            <>
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto" />
              <p className="text-sm font-medium">{message}</p>
              {typeof progress === "number" && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
