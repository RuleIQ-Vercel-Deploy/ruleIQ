"use client"

import * as React from "react"

import {
  PageLoader,
  InlineLoader,
  ProgressLoader,
  StepLoader,
  DotsLoader,
} from "@/components/loading/page-loader"
import { Button } from "@/components/ui/button"
import {
  Skeleton,
  CardSkeleton,
  TableRowSkeleton,
  ListItemSkeleton,
  StatCardSkeleton,
  FormSkeleton,
  ChatMessageSkeleton,
  NavigationSkeleton,
  AssessmentCardSkeleton,
  PolicyCardSkeleton,
} from "@/components/ui/skeleton-loader"
import { H1, H2, H3, Body } from "@/components/ui/typography"

export default function LoadingStatesDemo() {
  const [progress, setProgress] = React.useState(0)
  const [currentStep, setCurrentStep] = React.useState(0)
  const [showPageLoader, setShowPageLoader] = React.useState(false)

  // Simulate progress
  React.useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => (prev >= 100 ? 0 : prev + 10))
    }, 500)
    return () => clearInterval(interval)
  }, [])

  // Simulate step progress
  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev >= 3 ? 0 : prev + 1))
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const steps = [
    "Validating data",
    "Processing request",
    "Generating results",
    "Finalizing",
  ]

  return (
    <div className="container mx-auto p-8 space-y-12">
      <div className="space-y-4">
        <H1>Loading States Showcase</H1>
        <Body color="muted">
          Comprehensive collection of loading states and skeleton loaders.
        </Body>
      </div>

      {/* Basic Skeletons */}
      <section className="space-y-6">
        <H2>Basic Skeleton Variants</H2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-2">
            <H3 className="text-sm">Text</H3>
            <Skeleton variant="text" />
            <Skeleton variant="text" width="80%" />
            <Skeleton variant="text" width="60%" />
          </div>
          
          <div className="space-y-2">
            <H3 className="text-sm">Circular</H3>
            <div className="flex gap-2">
              <Skeleton variant="circular" width={40} height={40} />
              <Skeleton variant="circular" width={60} height={60} />
              <Skeleton variant="circular" width={80} height={80} />
            </div>
          </div>
          
          <div className="space-y-2">
            <H3 className="text-sm">Rectangular</H3>
            <Skeleton variant="rectangular" height={100} />
          </div>
          
          <div className="space-y-2">
            <H3 className="text-sm">Rounded</H3>
            <Skeleton variant="rounded" height={100} />
          </div>
        </div>
      </section>

      {/* Component Skeletons */}
      <section className="space-y-6">
        <H2>Component Skeletons</H2>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="space-y-2">
            <H3 className="text-sm">Card Skeleton</H3>
            <CardSkeleton />
          </div>
          
          <div className="space-y-2">
            <H3 className="text-sm">Stat Card Skeleton</H3>
            <StatCardSkeleton />
          </div>
          
          <div className="space-y-2">
            <H3 className="text-sm">Assessment Card Skeleton</H3>
            <AssessmentCardSkeleton />
          </div>
          
          <div className="space-y-2">
            <H3 className="text-sm">Policy Card Skeleton</H3>
            <PolicyCardSkeleton />
          </div>
          
          <div className="space-y-2">
            <H3 className="text-sm">Form Skeleton</H3>
            <FormSkeleton fields={2} />
          </div>
          
          <div className="space-y-2">
            <H3 className="text-sm">List Items</H3>
            <div className="border rounded-lg">
              <ListItemSkeleton />
              <ListItemSkeleton />
              <ListItemSkeleton />
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <H3 className="text-sm">Navigation Skeleton</H3>
          <NavigationSkeleton />
        </div>

        <div className="space-y-2">
          <H3 className="text-sm">Table Skeleton</H3>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <tbody>
                <TableRowSkeleton columns={5} />
                <TableRowSkeleton columns={5} />
                <TableRowSkeleton columns={5} />
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-2">
          <H3 className="text-sm">Chat Message Skeletons</H3>
          <div className="border rounded-lg p-4 space-y-4">
            <ChatMessageSkeleton />
            <ChatMessageSkeleton isUser />
            <ChatMessageSkeleton />
          </div>
        </div>
      </section>

      {/* Animated Loaders */}
      <section className="space-y-6">
        <H2>Animated Loaders</H2>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="space-y-4">
            <H3 className="text-sm">Page Loader</H3>
            <div className="border rounded-lg p-8">
              <PageLoader message="Loading dashboard" submessage="Please wait..." />
            </div>
          </div>
          
          <div className="space-y-4">
            <H3 className="text-sm">Inline Loader</H3>
            <div className="flex items-center gap-4">
              <Button disabled>
                <InlineLoader className="mr-2" />
                Loading
              </Button>
              <InlineLoader />
              <InlineLoader className="h-6 w-6 text-gold" />
            </div>
          </div>
          
          <div className="space-y-4">
            <H3 className="text-sm">Dots Loader</H3>
            <div className="flex items-center justify-center p-8">
              <DotsLoader />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <H3 className="text-sm">Progress Loader</H3>
          <div className="max-w-md">
            <ProgressLoader 
              progress={progress} 
              message="Uploading files..." 
            />
          </div>
        </div>

        <div className="space-y-4">
          <H3 className="text-sm">Step Loader</H3>
          <div className="max-w-md">
            <StepLoader 
              steps={steps} 
              currentStep={currentStep} 
            />
          </div>
        </div>
      </section>


      {/* Full Page Loader Demo */}
      <section className="space-y-4">
        <H2>Full Page Loader</H2>
        <Button 
          variant="accent"
          onClick={() => {
            setShowPageLoader(true)
            setTimeout(() => setShowPageLoader(false), 3000)
          }}
        >
          Show Full Page Loader (3s)
        </Button>
      </section>

      {/* Full page loader overlay */}
      {showPageLoader && (
        <PageLoader 
          fullScreen 
          overlay 
          message="Loading application" 
          submessage="This will take just a moment..."
        />
      )}
    </div>
  )
}