'use client';

import {
  Shield,
  Plus,
  Edit,
  Eye,
  FileText,
  Download,
  Clock,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { policyService } from '@/lib/api/policies.service';

import type { Policy } from '@/types/api';

export default function PoliciesPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [policies, setPolicies] = useState<Policy[]>([]);

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await policyService.getPolicies({
        page: 1,
        page_size: 50,
      });
      setPolicies(response.policies);
    } catch {} {
      // TODO: Replace with proper logging

      // // TODO: Replace with proper logging
      setError(err instanceof Error ? err.message : 'Failed to load policies');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'approved':
        return <CheckCircle className="h-4 w-4" />;
      case 'under_review':
      case 'draft':
        return <Clock className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'approved':
        return 'bg-success/20 text-success border-success/40';
      case 'under_review':
        return 'bg-warning/20 text-warning border-warning/40';
      case 'draft':
        return 'bg-muted text-muted-foreground border-border';
      case 'archived':
        return 'bg-muted/50 text-muted-foreground border-border';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  const formatStatus = (status: string) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const handleNewPolicy = () => {
    router.push('/policies/new');
  };

  const handleExportPolicy = async (policyId: string, format: 'pdf' | 'word') => {
    try {
      if (format === 'pdf') {
        await policyService.exportPolicyAsPDF(policyId);
      } else {
        await policyService.exportPolicyAsWord(policyId);
      }
    } catch {} {
      // TODO: Replace with proper logging
      // // TODO: Replace with proper logging
    }
  };

  return (
    <div className="flex-1 space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-navy">Policy Management</h2>
          <p className="text-muted-foreground">
            Create and manage compliance policies for your organization
          </p>
        </div>
        <Button className="bg-gold text-navy hover:bg-gold-dark" onClick={handleNewPolicy}>
          <Plus className="mr-2 h-4 w-4" />
          Generate Policy
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Policies Grid */}
      {loading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : policies.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {policies.map((policy) => (
            <Card key={policy.id} className="transition-shadow hover:shadow-lg">
              <CardHeader>
                <div className="mb-2 flex items-center justify-between">
                  <Shield className="h-5 w-5 text-gold" />
                  <Badge variant="outline" className={getStatusColor(policy.status)}>
                    {getStatusIcon(policy.status)}
                    {formatStatus(policy.status)}
                  </Badge>
                </div>
                <CardTitle className="text-navy">{policy.policy_name}</CardTitle>
                <CardDescription>
                  {`${policy.policy_type} policy for ${policy.framework_name || policy.framework_id}`}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Framework</span>
                  <span className="font-medium">
                    {policy.framework_name || policy.framework_id}
                  </span>
                </div>
                {policy.version && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Version</span>
                    <span className="font-medium">v{policy.version}</span>
                  </div>
                )}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Last Updated</span>
                  <span className="font-medium">
                    {new Date(policy.updated_at).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex gap-2 pt-4">
                  <Button size="sm" variant="outline" className="flex-1" asChild>
                    <Link href={`/policies/${policy.id}`}>
                      <Eye className="mr-2 h-4 w-4" />
                      View
                    </Link>
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1" asChild>
                    <Link href={`/policies/${policy.id}/edit`}>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit
                    </Link>
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleExportPolicy(policy.id, 'pdf')}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="mb-4 h-12 w-12 text-muted-foreground" />
            <h3 className="mb-2 text-lg font-semibold">No Policies Found</h3>
            <p className="mb-4 max-w-md text-center text-sm text-muted-foreground">
              Get started by generating your first compliance policy.
            </p>
            <Button className="bg-gold text-navy hover:bg-gold-dark" onClick={handleNewPolicy}>
              <Plus className="mr-2 h-4 w-4" />
              Generate Your First Policy
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
