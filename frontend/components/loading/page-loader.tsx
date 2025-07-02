"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Loader2 } from "lucide-react"
import * as React from "react"

import { Body, Caption } from "@/components/ui/typography"
import { cn } from "@/lib/utils"


interface PageLoaderProps {
  className?: string
  message?: string
  submessage?: string
  fullScreen?: boolean
  overlay?: boolean
}

export function PageLoader({
  className,
  message = "Loading...",
  submessage,
  fullScreen = false,
  overlay = false,
}: PageLoaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center space-y-4",
        fullScreen && "fixed inset-0 z-50",
        overlay && "bg-background/80 backdrop-blur-sm",
        !fullScreen && "min-h-[400px]",
        className
      )}
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="relative"
      >
        {/* Outer spinning ring */}
        <div className="absolute inset-0 rounded-full border-4 border-gold/20" />
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-gold animate-spin" />
        
        {/* Inner logo or icon */}
        <div className="relative h-16 w-16 flex items-center justify-center">
          <Loader2 className="h-8 w-8 text-navy animate-pulse" />
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.3 }}
        className="text-center space-y-1"
      >
        <Body className="font-medium">{message}</Body>
        {submessage && <Caption color="muted">{submessage}</Caption>}
      </motion.div>
    </div>
  )
}

// Inline loader for buttons and small areas
export function InlineLoader({ className }: { className?: string }) {
  return (
    <Loader2 className={cn("h-4 w-4 animate-spin", className)} />
  )
}

// Progress loader with percentage
interface ProgressLoaderProps {
  progress: number
  message?: string
  className?: string
}

export function ProgressLoader({
  progress,
  message = "Processing...",
  className,
}: ProgressLoaderProps) {
  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center justify-between">
        <Body className="text-sm">{message}</Body>
        <Caption>{Math.round(progress)}%</Caption>
      </div>
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
        <motion.div
          className="absolute inset-y-0 left-0 bg-gold"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
      </div>
    </div>
  )
}

// Step loader for multi-step processes
interface StepLoaderProps {
  steps: string[]
  currentStep: number
  className?: string
}

export function StepLoader({
  steps,
  currentStep,
  className,
}: StepLoaderProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {steps.map((step, index) => {
        const isActive = index === currentStep
        const isCompleted = index < currentStep
        
        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center gap-3"
          >
            <div className="relative">
              <div
                className={cn(
                  "h-8 w-8 rounded-full border-2 flex items-center justify-center",
                  isCompleted && "bg-success border-success",
                  isActive && "bg-gold border-gold",
                  !isCompleted && !isActive && "border-muted-foreground/30"
                )}
              >
                {isCompleted ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="h-4 w-4 rounded-full bg-white"
                  />
                ) : isActive ? (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                    className="h-3 w-3 rounded-full bg-white"
                  />
                ) : (
                  <div className="h-3 w-3 rounded-full bg-muted-foreground/30" />
                )}
              </div>
              
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    "absolute top-8 left-4 w-0.5 h-8 -translate-x-1/2",
                    isCompleted ? "bg-success" : "bg-muted-foreground/30"
                  )}
                />
              )}
            </div>
            
            <Body
              className={cn(
                "transition-colors",
                isActive && "text-gold font-medium",
                isCompleted && "text-success",
                !isCompleted && !isActive && "text-muted-foreground"
              )}
            >
              {step}
            </Body>
          </motion.div>
        )
      })}
    </div>
  )
}

// Dots loader animation
export function DotsLoader({ className }: { className?: string }) {
  return (
    <div className={cn("flex space-x-1", className)}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className="h-2 w-2 rounded-full bg-gold"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: index * 0.2,
          }}
        />
      ))}
    </div>
  )
}

// Suspense wrapper with loading fallback
interface SuspenseWrapperProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  className?: string
}

export function SuspenseWrapper({
  children,
  fallback,
  className,
}: SuspenseWrapperProps) {
  return (
    <React.Suspense 
      fallback={
        fallback || (
          <div className={cn("min-h-[200px] flex items-center justify-center", className)}>
            <PageLoader />
          </div>
        )
      }
    >
      {children}
    </React.Suspense>
  )
}