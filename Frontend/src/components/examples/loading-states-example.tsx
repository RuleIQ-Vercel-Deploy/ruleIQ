"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LoadingStateManager } from "@/components/ui/loading-state-manager"
import { ProgressBar, StepIndicator, CircularProgress, LoadingSpinner } from "@/components/ui/progress-indicators"
import { useLoadingState, useAsyncOperation } from "@/hooks/use-loading-state"
import { StaggeredTransition } from "@/components/ui/transitions"

export function LoadingStatesExample() {
  const loadingState = useLoadingState({ minLoadingTime: 1000 })
  const asyncOp = useAsyncOperation()

  const [steps, setSteps] = React.useState([
    { id: "1", title: "Initialize", status: "completed" as const },
    { id: "2", title: "Processing", status: "current" as const },
    { id: "3", title: "Finalizing", status: "pending" as const },
  ])

  const simulateLoading = async () => {
    loadingState.startLoading("Starting process...")

    // Simulate progress updates
    for (let i = 0; i <= 100; i += 10) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      loadingState.updateProgress(i, `Processing... ${i}%`)
    }

    loadingState.stopLoading()
  }

  const simulateAsyncOperation = async () => {
    await asyncOp.execute(async () => {
      await new Promise((resolve) => setTimeout(resolve, 2000))
      return { message: "Operation completed successfully!" }
    })
  }

  const items = ["Dashboard Overview", "Recent Activity", "Performance Metrics", "User Analytics", "System Status"]

  return (
    <div className="space-y-8 p-6">
      <div>
        <h2 className="text-2xl font-bold mb-4">Loading States Examples</h2>
        <p className="text-gray-600 mb-6">
          Comprehensive examples of loading states, progress indicators, and smooth transitions.
        </p>
      </div>

      {/* Progress Indicators */}
      <Card>
        <CardHeader>
          <CardTitle>Progress Indicators</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <ProgressBar value={loadingState.progress} label="Overall Progress" animated />

            <ProgressBar value={75} label="Success Progress" variant="success" animated />

            <ProgressBar value={45} label="Warning Progress" variant="warning" animated />
          </div>

          <div className="flex items-center space-x-8">
            <CircularProgress value={65} label="CPU Usage" />
            <CircularProgress value={80} variant="warning" label="Memory" />
            <CircularProgress value={95} variant="error" label="Storage" />
          </div>

          <div className="flex items-center space-x-4">
            <LoadingSpinner size="sm" />
            <LoadingSpinner size="md" variant="dots" />
            <LoadingSpinner size="lg" variant="pulse" />
          </div>
        </CardContent>
      </Card>

      {/* Step Indicator */}
      <Card>
        <CardHeader>
          <CardTitle>Step Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <StepIndicator steps={steps} />

          <div className="mt-6">
            <StepIndicator steps={steps} orientation="vertical" />
          </div>
        </CardContent>
      </Card>

      {/* Loading State Manager */}
      <Card>
        <CardHeader>
          <CardTitle>Loading State Manager</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex space-x-4">
              <Button onClick={simulateLoading} disabled={loadingState.isLoading}>
                {loadingState.isLoading ? "Loading..." : "Start Loading"}
              </Button>
              <Button onClick={simulateAsyncOperation} disabled={asyncOp.isLoading}>
                {asyncOp.isLoading ? "Processing..." : "Async Operation"}
              </Button>
            </div>

            <LoadingStateManager loading={asyncOp.isLoading} error={asyncOp.error} skeleton="cards">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Card key={i}>
                    <CardContent className="p-4">
                      <h3 className="font-semibold mb-2">Card {i + 1}</h3>
                      <p className="text-sm text-gray-600">This is example content that appears after loading.</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </LoadingStateManager>
          </div>
        </CardContent>
      </Card>

      {/* Staggered Transitions */}
      <Card>
        <CardHeader>
          <CardTitle>Staggered Transitions</CardTitle>
        </CardHeader>
        <CardContent>
          <StaggeredTransition show={!loadingState.isLoading} staggerDelay={150}>
            {items.map((item, index) => (
              <Card key={index} className="mb-3">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full" />
                    <span>{item}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </StaggeredTransition>
        </CardContent>
      </Card>
    </div>
  )
}
