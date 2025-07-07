import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export const StatsCardSkeleton = () => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <Skeleton className="h-4 w-[100px]" />
      <Skeleton className="h-4 w-4" />
    </CardHeader>
    <CardContent>
      <Skeleton className="h-8 w-[120px] mb-1" />
      <Skeleton className="h-3 w-[80px]" />
    </CardContent>
  </Card>
)

export const ChartSkeleton = () => (
  <div className="w-full">
    <div className="flex items-center justify-between mb-4">
      <Skeleton className="h-6 w-[150px]" />
      <Skeleton className="h-8 w-[100px]" />
    </div>
    <Skeleton className="h-[300px] w-full" />
  </div>
)

export const InsightsSkeleton = () => (
  <div className="space-y-4">
    <Skeleton className="h-6 w-[200px]" />
    <div className="space-y-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="flex items-start space-x-3">
          <Skeleton className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-[90%]" />
          </div>
        </div>
      ))}
    </div>
  </div>
)

export const DashboardSkeleton = () => (
  <div className="space-y-6">
    {/* Stats cards */}
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <StatsCardSkeleton key={i} />
      ))}
    </div>
    
    {/* Charts section */}
    <div className="grid gap-6 lg:grid-cols-7">
      <Card className="lg:col-span-4">
        <CardHeader>
          <Skeleton className="h-6 w-[180px]" />
        </CardHeader>
        <CardContent>
          <ChartSkeleton />
        </CardContent>
      </Card>
      
      <Card className="lg:col-span-3">
        <CardHeader>
          <Skeleton className="h-6 w-[150px]" />
        </CardHeader>
        <CardContent>
          <InsightsSkeleton />
        </CardContent>
      </Card>
    </div>
  </div>
)

export const TableRowSkeleton = () => (
  <div className="flex items-center space-x-4 py-4">
    <Skeleton className="h-4 w-4" />
    <Skeleton className="h-4 w-[200px]" />
    <Skeleton className="h-4 w-[100px]" />
    <Skeleton className="h-4 w-[80px]" />
    <Skeleton className="h-8 w-[60px]" />
  </div>
)

export const TableSkeleton = ({ rows = 5 }: { rows?: number }) => (
  <div className="w-full">
    <div className="border-b">
      <div className="flex items-center space-x-4 py-4 font-medium">
        <Skeleton className="h-4 w-4" />
        <Skeleton className="h-4 w-[150px]" />
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 w-[80px]" />
        <Skeleton className="h-4 w-[60px]" />
      </div>
    </div>
    <div className="divide-y">
      {Array.from({ length: rows }).map((_, i) => (
        <TableRowSkeleton key={i} />
      ))}
    </div>
  </div>
)
