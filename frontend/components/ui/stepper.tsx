"use client"

import { Check } from "lucide-react"
import * as React from "react"

import { cn } from "@/lib/utils"

interface StepperProps {
  steps: string[]
  currentStep: number
  className?: string
}

export function Stepper({ steps, currentStep, className }: StepperProps) {
  return (
    <div className={cn("flex items-center justify-between w-full", className)}>
      {steps.map((step, index) => {
        const stepNumber = index + 1
        const isActive = stepNumber === currentStep
        const isCompleted = stepNumber < currentStep

        return (
          <React.Fragment key={step}>
            <div className="flex flex-col items-center text-center">
              <div
                className={cn(
                  "flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all duration-300",
                  isCompleted
                    ? "bg-gold border-gold text-oxford-blue"
                    : isActive
                      ? "border-gold text-gold"
                      : "border-grey-600 text-grey-600",
                )}
              >
                {isCompleted ? <Check className="w-5 h-5" /> : <span className="font-bold">{stepNumber}</span>}
              </div>
              <p
                className={cn(
                  "mt-2 text-xs font-medium transition-colors duration-300",
                  isActive || isCompleted ? "text-eggshell-white" : "text-grey-600",
                )}
              >
                {step}
              </p>
            </div>
            {index < steps.length - 1 && (
              <div
                className={cn(
                  "flex-1 h-0.5 mx-4 transition-colors duration-300",
                  isCompleted ? "bg-gold" : "bg-grey-600",
                )}
              />
            )}
          </React.Fragment>
        )
      })}
    </div>
  )
}
