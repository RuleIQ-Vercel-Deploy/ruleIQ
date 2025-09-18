'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { WidgetContainer, type WidgetConfig } from '@/components/dashboard/widget-container';
import { UndoRedoControls } from '@/components/dashboard/layout/UndoRedoControls';
import { RuleList } from '@/components/dashboard/rules/RuleList';
import { useLayoutPersistence } from '@/lib/hooks/use-layout-persistence';
import { useLayoutStore } from '@/lib/stores/layout.store';
import { useAuth } from '@/lib/auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LayoutGrid,
  ListOrdered,
  Settings,
  Download,
  Upload,
  Share2,
  AlertCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Mock data for widgets (replace with actual data fetching)
const mockWidgets: WidgetConfig[] = [
  {
    id: 'compliance-overview',
    type: 'stats',
    title: 'Compliance Overview',
    content: (
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-sm text-muted-foreground">Total Rules</span>
          <span className="text-2xl font-bold">247</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-muted-foreground">Active</span>
          <span className="text-lg font-medium text-emerald-600">189</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-muted-foreground">Violations</span>
          <span className="text-lg font-medium text-red-600">12</span>
        </div>
      </div>
    ),
    canRemove: false,
  },
  {
    id: 'recent-activity',
    type: 'list',
    title: 'Recent Activity',
    content: (
      <ul className="space-y-2 text-sm">
        <li className="flex items-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full" />
          <span>GDPR compliance check passed</span>
        </li>
        <li className="flex items-center gap-2">
          <span className="w-2 h-2 bg-yellow-500 rounded-full" />
          <span>SOX audit pending review</span>
        </li>
        <li className="flex items-center gap-2">
          <span className="w-2 h-2 bg-blue-500 rounded-full" />
          <span>New ISO 27001 rule added</span>
        </li>
      </ul>
    ),
  },
  {
    id: 'compliance-score',
    type: 'chart',
    title: 'Compliance Score',
    content: (
      <div className="flex items-center justify-center h-32">
        <div className="text-center">
          <div className="text-4xl font-light text-purple-600">92%</div>
          <p className="text-sm text-muted-foreground mt-1">Overall Compliance</p>
        </div>
      </div>
    ),
  },
  {
    id: 'upcoming-deadlines',
    type: 'list',
    title: 'Upcoming Deadlines',
    content: (
      <ul className="space-y-2 text-sm">
        <li className="flex justify-between">
          <span>GDPR Annual Review</span>
          <span className="text-muted-foreground">3 days</span>
        </li>
        <li className="flex justify-between">
          <span>SOX Q4 Report</span>
          <span className="text-muted-foreground">7 days</span>
        </li>
        <li className="flex justify-between">
          <span>ISO 27001 Audit</span>
          <span className="text-muted-foreground">14 days</span>
        </li>
      </ul>
    ),
  },
];

// Mock rules data
const mockRules = [
  {
    id: 'rule-1',
    name: 'Data Retention Policy',
    description: 'Ensure personal data is not retained beyond specified periods',
    priority: 'P0' as const,
    framework: 'GDPR',
    status: 'active' as const,
    category: 'Data Protection',
    lastModified: '2 hours ago',
    violations: 0,
    compliance: 100,
  },
  {
    id: 'rule-2',
    name: 'Access Control Verification',
    description: 'Verify user access controls are properly configured',
    priority: 'P1' as const,
    framework: 'SOX',
    status: 'active' as const,
    category: 'Security',
    lastModified: '1 day ago',
    violations: 2,
    compliance: 95,
  },
  {
    id: 'rule-3',
    name: 'Encryption Standards',
    description: 'Validate encryption methods meet ISO requirements',
    priority: 'P2' as const,
    framework: 'ISO 27001',
    status: 'pending' as const,
    category: 'Security',
    lastModified: '3 days ago',
    violations: 0,
    compliance: 88,
  },
];

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4].map(i => (
          <Skeleton key={i} className="h-48" />
        ))}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [widgets, setWidgets] = useState(mockWidgets);
  const [rules, setRules] = useState(mockRules);
  const [activeTab, setActiveTab] = useState('widgets');

  const { currentLayout, loadLayout } = useLayoutStore();

  const {
    isLoading,
    hasUnsavedChanges,
    saveNow,
    resetToServer,
    createSnapshot,
    exportLayout,
    importLayout,
  } = useLayoutPersistence({
    autoSave: true,
    loadOnMount: true,
  });

  // Initialize layout on mount
  useEffect(() => {
    if (!currentLayout && user?.id) {
      // Create initial layout
      loadLayout({
        id: `layout-${user.id}`,
        userId: user.id,
        name: 'My Dashboard',
        widgets: widgets.map((w, index) => ({
          id: w.id,
          gridX: index % 3,
          gridY: Math.floor(index / 3),
          width: 1,
          height: 1,
        })),
        ruleOrder: rules.map(r => r.id),
        metadata: {
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          version: 1,
          isDefault: true,
        },
      });
    }
  }, [currentLayout, user, widgets, rules, loadLayout]);

  const handleWidgetOrderChange = (newWidgets: WidgetConfig[]) => {
    setWidgets(newWidgets);
  };

  const handleWidgetRemove = (widgetId: string) => {
    setWidgets(prev => prev.filter(w => w.id !== widgetId));
  };

  const handleWidgetSettings = (widgetId: string) => {
    // Open settings modal for widget
    console.log('Opening settings for widget:', widgetId);
  };

  const handleRuleOrderChange = (newRules: typeof rules) => {
    setRules(newRules);
  };

  const handleExportLayout = async () => {
    await exportLayout('json');
  };

  const handleImportLayout = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        await importLayout(file);
      }
    };
    input.click();
  };

  const handleCreateSnapshot = async () => {
    const name = prompt('Enter a name for this snapshot:');
    if (name) {
      await createSnapshot(name, 'Manual snapshot created by user');
    }
  };

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extralight tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground font-light mt-1">
            Manage your compliance rules and monitor violations
          </p>
        </div>

        <div className="flex items-center gap-2">
          <UndoRedoControls
            onSave={saveNow}
            onReset={resetToServer}
            compact={false}
          />

          <div className="flex items-center gap-1 border-l pl-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleExportLayout}
              title="Export layout"
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleImportLayout}
              title="Import layout"
            >
              <Upload className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleCreateSnapshot}
              title="Create snapshot"
            >
              <Share2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Unsaved changes alert */}
      {hasUnsavedChanges && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            You have unsaved changes. Your layout will be automatically saved, or you can{' '}
            <Button
              variant="link"
              className="p-0 h-auto font-semibold"
              onClick={saveNow}
            >
              save now
            </Button>
            .
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-2 bg-gray-100 border border-purple-100">
          <TabsTrigger value="widgets" className="gap-2">
            <LayoutGrid className="h-4 w-4" />
            Widgets
          </TabsTrigger>
          <TabsTrigger value="rules" className="gap-2">
            <ListOrdered className="h-4 w-4" />
            Rules
          </TabsTrigger>
        </TabsList>

        <TabsContent value="widgets" className="mt-6">
          <WidgetContainer
            widgets={widgets}
            onWidgetOrderChange={handleWidgetOrderChange}
            onWidgetRemove={handleWidgetRemove}
            onWidgetSettings={handleWidgetSettings}
            columns={3}
            gap={6}
            enablePersistence={true}
            enableUndoRedo={true}
            dragContextType="widgets"
          />
        </TabsContent>

        <TabsContent value="rules" className="mt-6">
          <Card className="bg-gray-50 border-purple-100 hover:border-purple-200 transition-colors">
            <CardHeader>
              <CardTitle>Compliance Rules</CardTitle>
            </CardHeader>
            <CardContent>
              <RuleList
                rules={rules}
                onOrderChange={handleRuleOrderChange}
                onRuleClick={(rule) => console.log('Clicked rule:', rule)}
                onRuleEdit={(rule) => console.log('Edit rule:', rule)}
                onRuleDelete={(rule) => console.log('Delete rule:', rule)}
                onRuleDuplicate={(rule) => console.log('Duplicate rule:', rule)}
                enableReordering={true}
                enableBulkOperations={true}
                showMetadata={true}
                filterOptions={{
                  priorities: ['P0', 'P1', 'P2', 'P3'],
                  frameworks: ['GDPR', 'SOX', 'ISO 27001'],
                  statuses: ['active', 'inactive', 'pending', 'draft'],
                }}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Layout Settings */}
      <Card className="bg-gray-50 border-purple-100 hover:border-purple-200 transition-colors">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Layout Settings</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Auto-save:</span>
              <span className="font-medium">Enabled</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Grid columns:</span>
              <span className="font-medium">3</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Animations:</span>
              <span className="font-medium">Enabled</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Keyboard shortcuts:</span>
              <span className="font-medium">Enabled</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}