"use client"

import { Suspense } from "react"
import { BusinessProfileDashboard } from "@/components/business-profile/business-profile-dashboard"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

function BusinessProfileSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-24" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default function BusinessProfilePage() {
  return (
    <div className="container mx-auto py-8">
      <Suspense fallback={<BusinessProfileSkeleton />}>
        <BusinessProfileDashboard />
      </Suspense>
    </div>
  )
}
