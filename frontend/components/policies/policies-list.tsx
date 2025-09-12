'use client';

import { usePolicies } from '@/lib/tanstack-query/hooks/use-policies';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export function PoliciesList() {
  const { data: policies, isLoading, isError, error } = usePolicies();

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-[250px]" />
              <Skeleton className="h-4 w-[350px]" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-4 w-[150px]" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          {error?.message || 'Failed to load policies. Please try again later.'}
        </AlertDescription>
      </Alert>
    );
  }

  if (!policies || !policies.items || policies.items.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <p className="text-muted-foreground">
            No policies found. Create your first policy to get started.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {policies.items.map((policy) => (
        <Card key={policy.id} className="hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle>{policy.policy_name}</CardTitle>
                <CardDescription className="mt-1">
                  Framework: {policy.framework_name || policy.framework_id}
                </CardDescription>
              </div>
              <Badge
                variant={
                  policy.status === 'active'
                    ? 'default'
                    : policy.status === 'draft'
                    ? 'secondary'
                    : 'outline'
                }
              >
                {policy.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>Type: {policy.policy_type}</span>
              {policy.sections && (
                <span>{policy.sections.length} sections</span>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}