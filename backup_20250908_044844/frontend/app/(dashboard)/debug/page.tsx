'use client';

import { ExternalLink, FileCode2, Bug, TestTube } from 'lucide-react';
import Link from 'next/link';

export default function DebugPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Debug Suite</h1>
        <p className="text-muted-foreground mt-2">
          Development tools and API documentation
        </p>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        {/* API Documentation Card */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <FileCode2 className="h-6 w-6 text-primary" />
            <h2 className="text-xl font-semibold">API Documentation</h2>
          </div>
          <p className="text-muted-foreground mb-4">
            Interactive API documentation with OpenAPI/Swagger interface
          </p>
          <Link 
            href="/docs" 
            target="_blank"
            className="inline-flex items-center gap-2 text-primary hover:underline"
          >
            Open API Docs
            <ExternalLink className="h-4 w-4" />
          </Link>
        </div>

        {/* Debug Suite HTML Card */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Bug className="h-6 w-6 text-primary" />
            <h2 className="text-xl font-semibold">API Debug Suite</h2>
          </div>
          <p className="text-muted-foreground mb-4">
            HTML-based API testing and debugging interface
          </p>
          <Link 
            href="/api-debug-suite.html" 
            target="_blank"
            className="inline-flex items-center gap-2 text-primary hover:underline"
          >
            Open Debug Suite
            <ExternalLink className="h-4 w-4" />
          </Link>
        </div>

        {/* Test Status Card */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <TestTube className="h-6 w-6 text-primary" />
            <h2 className="text-xl font-semibold">Test Status</h2>
          </div>
          <p className="text-muted-foreground">
            View test coverage and CI/CD pipeline status
          </p>
        </div>
      </div>
    </div>
  );
}