'use client'

import { useDesignSystem } from '@/providers/design-system-provider'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { InfoIcon } from 'lucide-react'

export function ThemeDemo() {
  const { designSystem, toggleDesignSystem, isNewTheme } = useDesignSystem()

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Theme Demo</h1>
        <div className="flex items-center gap-4">
          <Badge variant={isNewTheme ? 'brand' : 'secondary'}>
            {isNewTheme ? 'Teal Theme' : 'Legacy Theme'}
          </Badge>
          <Button onClick={toggleDesignSystem}>
            Switch to {isNewTheme ? 'Legacy' : 'Teal'} Theme
          </Button>
        </div>
      </div>

      <Alert>
        <InfoIcon className="h-4 w-4" />
        <AlertTitle>Theme System Active</AlertTitle>
        <AlertDescription>
          Currently using the <strong>{designSystem}</strong> design system. 
          Toggle between themes to see the visual differences.
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Button Variants</CardTitle>
            <CardDescription>All button styles with theme support</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Button variant="default">Default</Button>
              <Button variant="brand">Brand</Button>
              <Button variant="brand-secondary">Brand Secondary</Button>
              <Button variant="brand-outline">Brand Outline</Button>
              <Button variant="brand-ghost">Brand Ghost</Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="destructive">Destructive</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Form Components</CardTitle>
            <CardDescription>Form elements with theme-aware styling</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="demo-input">Theme-aware Input</Label>
              <Input id="demo-input" placeholder="Type something..." />
            </div>
            <div className="space-y-2">
              <Label htmlFor="demo-input-error">Input with Error</Label>
              <Input id="demo-input-error" placeholder="Error state" error />
            </div>
            <div className="space-y-2">
              <Label htmlFor="demo-input-success">Input with Success</Label>
              <Input id="demo-input-success" placeholder="Success state" success />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Badge Variants</CardTitle>
            <CardDescription>Status and tag badges</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Badge variant="default">Default</Badge>
              <Badge variant="brand">Brand</Badge>
              <Badge variant="brand-subtle">Brand Subtle</Badge>
              <Badge variant="success">Success</Badge>
              <Badge variant="pending">Pending</Badge>
              <Badge variant="rejected">Rejected</Badge>
              <Badge variant="tag">Tag</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alert Variants</CardTitle>
            <CardDescription>Notification components</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="success">
              <InfoIcon className="h-4 w-4" />
              <AlertTitle>Success</AlertTitle>
              <AlertDescription>Operation completed successfully.</AlertDescription>
            </Alert>
            <Alert variant="warning">
              <InfoIcon className="h-4 w-4" />
              <AlertTitle>Warning</AlertTitle>
              <AlertDescription>Please review this information.</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>

      <div className="text-sm text-muted-foreground">
        <strong>Debug Info:</strong> Design System = {designSystem}, Is New Theme = {isNewTheme.toString()}
      </div>
    </div>
  )
}