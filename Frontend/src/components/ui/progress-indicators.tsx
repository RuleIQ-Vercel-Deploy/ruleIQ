"use client"

import * as React from "react"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import { CheckCircle, Circle, Loader2 } from "lucide-react"

interface ProgressBarProps {
  value: number
  max?: number
  label?: string
  showPercentage?: boolean
  size?: "sm" | "md" | "lg"
  variant?: "default" | "success" | "warning" | "error"
  animated?: boolean
  className?: string
}

export function ProgressBar({
  value,
  max = 100,
  label,
  showPercentage = true,
  size = "md",
  variant = "default",
  animated = false,
  className,
}: ProgressBarProps) {
  const percentage = Math.round((value / max) * 100)

  const sizeClasses = {
    sm: "h-2",
    md: "h-3",
    lg: "h-4",
  }

  const variantClasses = {
    default: "",
    success: "[&>div]:bg-green-500",
    warning: "[&>div]:bg-yellow-500",
    error: "[&>div]:bg-red-500",
  }

  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <div className="flex justify-between items-center text-sm">
          <span className="font-medium">{label}</span>
          {showPercentage && <span className="text-muted-foreground">{percentage}%</span>}
        </div>
      )}
      <Progress
        value={percentage}
        className={cn(
          sizeClasses[size],
          variantClasses[variant],
          animated && "transition-all duration-300 ease-out",
          className,
        )}
      />
    </div>
  )
}

interface StepIndicatorProps {
  steps: Array<{
    id: string
    title: string
    description?: string
    status: "pending" | "current" | "completed" | "error"
  }>
  orientation?: "horizontal" | "vertical"
  className?: string
}

export function StepIndicator({ steps, orientation = "horizontal", className }: StepIndicatorProps) {
  return (
    <div
      className={cn(
        "flex",
        orientation === "horizontal" ? "flex-row items-center justify-between" : "flex-col space-y-4",
        className,
      )}
    >
      {steps.map((step, index) => (
        <React.Fragment key={step.id}>
          <div
            className={cn(
              "flex items-center",
              orientation === "vertical" && "flex-row",
              orientation === "horizontal" && "flex-col text-center",
            )}
          >
            <div
              className={cn(
                "flex items-center justify-center rounded-full border-2 transition-all duration-200",
                step.status === "completed" && "bg-green-500 border-green-500 text-white",
                step.status === "current" && "bg-blue-500 border-blue-500 text-white",
                step.status === "error" && "bg-red-500 border-red-500 text-white",
                step.status === "pending" && "bg-gray-100 border-gray-300 text-gray-500",
                orientation === "horizontal" ? "w-8 h-8 mb-2" : "w-8 h-8 mr-3",
              )}
            >
              {step.status === "completed" ? (
                <CheckCircle className="w-4 h-4" />
              ) : step.status === "current" ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Circle className="w-4 h-4" />
              )}
            </div>
            <div className={cn(orientation === "vertical" && "flex-1")}>
              <div
                className={cn(
                  "font-medium text-sm",
                  step.status === "current" && "text-blue-600",
                  step.status === "completed" && "text-green-600",
                  step.status === "error" && "text-red-600",
                  step.status === "pending" && "text-gray-500",
                )}
              >
                {step.title}
              </div>
              {step.description && <div className="text-xs text-muted-foreground mt-1">{step.description}</div>}
            </div>
          </div>

          {index < steps.length - 1 && (
            <div
              className={cn(
                "transition-all duration-200",
                orientation === "horizontal" ? "flex-1 h-px bg-gray-300 mx-4" : "w-px h-8 bg-gray-300 ml-4",
                (steps[index].status === "completed" || steps[index + 1].status === "completed") && "bg-green-500",
              )}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  )
}

interface CircularProgressProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  label?: string
  showPercentage?: boolean
  variant?: "default" | "success" | "warning" | "error"
  className?: string
}

export function CircularProgress({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  label,
  showPercentage = true,
  variant = "default",
  className,
}: CircularProgressProps) {
  const percentage = Math.round((value / max) * 100)
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const variantColors = {
    default: "stroke-blue-500",
    success: "stroke-green-500",
    warning: "stroke-yellow-500",
    error: "stroke-red-500",
  }

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-gray-200"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className={cn("transition-all duration-300 ease-out", variantColors[variant])}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {showPercentage && <span className="text-2xl font-bold">{percentage}%</span>}
        {label && <span className="text-sm text-muted-foreground">{label}</span>}
      </div>
    </div>
  )
}

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg"
  variant?: "default" | "dots" | "pulse"
  className?: string
}

export function LoadingSpinner({ size = "md", variant = "default", className }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  }

  if (variant === "dots") {
    return (
      <div className={cn("flex space-x-1", className)}>
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "rounded-full bg-current animate-pulse",
              size === "sm" && "w-1 h-1",
              size === "md" && "w-2 h-2",
              size === "lg" && "w-3 h-3",
            )}
            style={{ animationDelay: `${i * 0.2}s` }}
          />
        ))}
      </div>
    )
  }

  if (variant === "pulse") {
    return <div className={cn("rounded-full bg-current animate-pulse", sizeClasses[size], className)} />
  }

  return <Loader2 className={cn("animate-spin", sizeClasses[size], className)} />
}
