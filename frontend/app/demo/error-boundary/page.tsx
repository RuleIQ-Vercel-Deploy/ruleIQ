"use client"

import { AlertCircle } from "lucide-react"
import * as React from "react"

import { FeatureErrorBoundary, useAsyncError } from "@/components/error-boundary"
import { Button } from "@/components/ui/button"
import { H1, H2, Body } from "@/components/ui/typography"

// Component that throws an error
function BrokenComponent() {
  const [shouldError, setShouldError] = React.useState(false)

  if (shouldError) {
    throw new Error("This is a test error from BrokenComponent!")
  }

  return (
    <div className="space-y-4 p-6 border rounded-lg">
      <H2>Component with Error</H2>
      <Body>Click the button to trigger an error in this component.</Body>
      <Button 
        variant="error" 
        onClick={() => setShouldError(true)}
        className="gap-2"
      >
        <AlertCircle className="h-4 w-4" />
        Trigger Error
      </Button>
    </div>
  )
}

// Component that throws async error
function AsyncBrokenComponent() {
  const throwAsyncError = useAsyncError()
  
  const handleAsyncError = async () => {
    try {
      // Simulate async operation that fails
      await new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error("This is an async error!"))
        }, 1000)
      })
    } catch (error) {
      throwAsyncError(error as Error)
    }
  }

  return (
    <div className="space-y-4 p-6 border rounded-lg">
      <H2>Component with Async Error</H2>
      <Body>Click the button to trigger an async error.</Body>
      <Button 
        variant="error" 
        onClick={handleAsyncError}
        className="gap-2"
      >
        <AlertCircle className="h-4 w-4" />
        Trigger Async Error
      </Button>
    </div>
  )
}

// Component that works normally
function WorkingComponent() {
  const [count, setCount] = React.useState(0)

  return (
    <div className="space-y-4 p-6 border rounded-lg">
      <H2>Working Component</H2>
      <Body>This component works normally. Count: {count}</Body>
      <Button 
        variant="accent" 
        onClick={() => setCount(count + 1)}
      >
        Increment Count
      </Button>
    </div>
  )
}

export default function ErrorBoundaryDemoPage() {
  return (
    <div className="container mx-auto p-8 space-y-8">
      <div className="space-y-4">
        <H1>Error Boundary Demo</H1>
        <Body color="muted">
          This page demonstrates how error boundaries catch and handle errors in React components.
        </Body>
      </div>

      <div className="grid gap-6">
        {/* Feature Error Boundary - catches errors in this section only */}
        <FeatureErrorBoundary>
          <BrokenComponent />
        </FeatureErrorBoundary>

        {/* Another Feature Error Boundary - isolated from the first one */}
        <FeatureErrorBoundary>
          <AsyncBrokenComponent />
        </FeatureErrorBoundary>

        {/* This component is not affected by errors in the components above */}
        <WorkingComponent />
      </div>

      <div className="space-y-4 p-6 bg-muted/20 rounded-lg">
        <H2>How Error Boundaries Work</H2>
        <ul className="space-y-2 list-disc list-inside">
          <Body as="li">
            Click "Trigger Error" in the first component to see a synchronous error being caught
          </Body>
          <Body as="li">
            Click "Trigger Async Error" in the second component to see an async error being caught
          </Body>
          <Body as="li">
            Notice how the working component continues to function even when others error
          </Body>
          <Body as="li">
            Each FeatureErrorBoundary isolates errors to its own section
          </Body>
          <Body as="li">
            The global ErrorBoundary in the layout catches any uncaught errors
          </Body>
        </ul>
      </div>
    </div>
  )
}