'use client';

import { Loader2, RefreshCw } from 'lucide-react';
import * as React from 'react';

import { DataTableSkeleton } from '@/components/dashboard/data-table-skeleton';
import { StatsCardSkeleton } from '@/components/dashboard/stats-card-skeleton';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export function LoadingShowcase() {
  const [isLoading, setIsLoading] = React.useState(false);

  const handleButtonClick = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 2000);
  };

  return (
    <div className="space-y-8">
      {/* Stat Card Skeleton */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle className="text-foreground">Stat Card Skeleton</CardTitle>
          <CardDescription className="text-muted-foreground">
            Provides a visual placeholder while stat card data is loading.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <StatsCardSkeleton />
            <StatsCardSkeleton />
            <StatsCardSkeleton />
            <StatsCardSkeleton />
          </div>
        </CardContent>
      </Card>

      {/* Table Loading Skeleton */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle className="text-foreground">Table Loading Skeleton</CardTitle>
          <CardDescription className="text-muted-foreground">
            Replicates the table structure to indicate that data is being fetched.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTableSkeleton />
        </CardContent>
      </Card>

      {/* Button Loading Spinner */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle className="text-foreground">Button Loading Spinner</CardTitle>
          <CardDescription className="text-muted-foreground">
            Indicates an action is in progress within a button. Click to see the loading state.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-4">
            <Button
              variant="default"
              size="default"
              loading={isLoading}
              onClick={handleButtonClick}
            >
              <RefreshCw className="h-4 w-4" />
              Click to Load
            </Button>
            <Button
              variant="secondary"
              size="default"
              loading={isLoading}
              onClick={handleButtonClick}
            >
              <RefreshCw className="h-4 w-4" />
              Click to Load
            </Button>
            <Button
              variant="destructive"
              size="default"
              loading={isLoading}
              onClick={handleButtonClick}
            >
              <RefreshCw className="h-4 w-4" />
              Click to Load
            </Button>
            <Button variant="ghost" size="default" loading={isLoading} onClick={handleButtonClick}>
              <RefreshCw className="h-4 w-4" />
              Click to Load
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Page-Level Loading Indicator */}
      <Card className="ruleiq-card">
        <CardHeader>
          <CardTitle className="text-neutral-900">Page-Level Loading Indicator</CardTitle>
          <CardDescription className="text-neutral-600">
            Displayed during initial page loads and navigation. This is handled by
            `app/loading.tsx`.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center gap-4 rounded-lg bg-white p-8 shadow-sm border border-neutral-200">
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-neutral-700">
                rule
              </span>
              <span className="text-2xl font-bold text-teal-600">
                IQ
              </span>
            </div>
            <Loader2 className="h-6 w-6 animate-spin text-teal-600" />
            <p className="text-neutral-600">Simulating page load...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
