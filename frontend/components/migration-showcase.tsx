'use client'

import { useState } from 'react'
import { useDesignSystem } from '@/providers/design-system-provider'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import { TopNavigation } from '@/components/navigation/top-navigation'
import { AppSidebar } from '@/components/navigation/app-sidebar'
import { ThemeDemo } from '@/components/theme-demo'
import { NavigationDemo } from '@/components/navigation-demo'
import { 
  Check, 
  AlertTriangle, 
  Info, 
  Sparkles, 
  Palette, 
  Monitor,
  Smartphone,
  Eye
} from 'lucide-react'

export function MigrationShowcase() {
  const { designSystem, toggleDesignSystem, isNewTheme } = useDesignSystem()
  const [activeDemo, setActiveDemo] = useState<'overview' | 'components' | 'navigation' | 'pages'>('overview')

  const phases = [
    {
      phase: 1,
      title: "Foundation & Infrastructure",
      status: "completed",
      description: "Feature flags, theme provider, CSS variables, Tailwind config",
      items: ["✅ Environment configuration", "✅ Design system provider", "✅ CSS variable system", "✅ Tailwind theme support"]
    },
    {
      phase: 2,
      title: "Core UI Components",
      status: "completed",
      description: "Button, Input, Card, Label, Badge, Alert components",
      items: ["✅ Button variants", "✅ Form components", "✅ Card layouts", "✅ Badge system", "✅ Alert notifications"]
    },
    {
      phase: 3,
      title: "Navigation Components",
      status: "completed",
      description: "Top navigation, sidebar, mobile navigation",
      items: ["✅ Top navigation bar", "✅ App sidebar", "✅ Mobile navigation", "✅ Theme switching"]
    },
    {
      phase: 4,
      title: "Page-by-Page Migration",
      status: "in_progress",
      description: "Dashboard, authentication, assessment pages",
      items: ["🔄 Dashboard page", "🔄 Login page", "⏳ Assessment pages", "⏳ Settings pages"]
    },
    {
      phase: 5,
      title: "Testing & QA",
      status: "pending",
      description: "Visual regression, accessibility, performance testing",
      items: ["⏳ Visual testing", "⏳ Accessibility audit", "⏳ Performance checks", "⏳ Cross-browser testing"]
    },
    {
      phase: 6,
      title: "Gradual Rollout",
      status: "pending",
      description: "Feature flags, A/B testing, production deployment",
      items: ["⏳ Feature flag rollout", "⏳ User feedback", "⏳ Production deployment", "⏳ Legacy cleanup"]
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'in_progress': return 'pending'
      case 'pending': return 'tag'
      default: return 'secondary'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <Check className="h-4 w-4" />
      case 'in_progress': return <AlertTriangle className="h-4 w-4" />
      case 'pending': return <Eye className="h-4 w-4" />
      default: return <Info className="h-4 w-4" />
    }
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Sparkles className="h-8 w-8 text-brand-primary" />
              <div>
                <h1 className="text-2xl font-bold">Design System Migration</h1>
                <p className="text-sm text-muted-foreground">
                  Complete showcase of the teal theme migration progress
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant={isNewTheme ? 'brand' : 'secondary'}>
                {isNewTheme ? 'Teal Theme' : 'Legacy Theme'}
              </Badge>
              <Button onClick={toggleDesignSystem} variant="brand-outline">
                <Palette className="h-4 w-4 mr-2" />
                Switch to {isNewTheme ? 'Legacy' : 'Teal'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b">
        <div className="container mx-auto px-6">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Migration Overview', icon: Monitor },
              { id: 'components', label: 'UI Components', icon: Sparkles },
              { id: 'navigation', label: 'Navigation', icon: Smartphone },
              { id: 'pages', label: 'Page Examples', icon: Eye }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveDemo(id as any)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 transition-colors ${
                  activeDemo === id
                    ? 'border-brand-primary text-brand-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 py-8">
        {activeDemo === 'overview' && (
          <div className="space-y-8">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>Migration Status</AlertTitle>
              <AlertDescription>
                We're migrating from a dark purple/cyan theme to a clean teal/light theme. 
                Phases 1-3 are complete, Phase 4 is in progress.
              </AlertDescription>
            </Alert>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {phases.map((phase) => (
                <Card key={phase.phase} className="relative overflow-hidden">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Badge variant={getStatusColor(phase.status) as any}>
                        {getStatusIcon(phase.status)}
                        Phase {phase.phase}
                      </Badge>
                      <Badge variant="outline">{phase.status}</Badge>
                    </div>
                    <CardTitle className="text-lg">{phase.title}</CardTitle>
                    <CardDescription>{phase.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {phase.items.map((item, index) => (
                        <li key={index} className="text-sm flex items-center gap-2">
                          <span className="text-xs">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Theme Comparison</CardTitle>
                <CardDescription>Visual differences between the legacy and new themes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-semibold text-brand-primary">🌙 Legacy Theme (Dark)</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Dark purple/cyan color scheme</li>
                      <li>• Dark backgrounds with light text</li>
                      <li>• Gradient effects and glowing elements</li>
                      <li>• Glass morphism styling</li>
                      <li>• High-tech aesthetic</li>
                    </ul>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-semibold text-brand-primary">🎨 Teal Theme (Light)</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Professional teal color scheme</li>
                      <li>• Clean white backgrounds</li>
                      <li>• Subtle shadows and borders</li>
                      <li>• High contrast accessibility</li>
                      <li>• Modern business aesthetic</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeDemo === 'components' && <ThemeDemo />}
        
        {activeDemo === 'navigation' && <NavigationDemo />}

        {activeDemo === 'pages' && (
          <div className="space-y-6">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>Page Migration Examples</AlertTitle>
              <AlertDescription>
                Examples of how pages look in both themes. Dashboard and login pages have been migrated.
              </AlertDescription>
            </Alert>

            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Dashboard Page</CardTitle>
                  <CardDescription>Main dashboard with charts, widgets, and data</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Badge variant="success">✅ Migrated</Badge>
                      <span className="text-sm">Background, gradients, and component styling updated</span>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Dynamic background colors</li>
                      <li>• Theme-aware gradient text</li>
                      <li>• Proper button and card styling</li>
                      <li>• Chart color adaptation</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Authentication Pages</CardTitle>
                  <CardDescription>Login and signup forms with security features</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Badge variant="pending">🔄 In Progress</Badge>
                      <span className="text-sm">Login page migrated, signup pages pending</span>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Form input styling</li>
                      <li>• Card background adaptation</li>
                      <li>• Brand logo colors</li>
                      <li>• Button and link theming</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Assessment Pages</CardTitle>
                  <CardDescription>Compliance assessment workflows and results</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Badge variant="tag">⏳ Pending</Badge>
                      <span className="text-sm">Assessment pages need migration</span>
                    </div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Wizard component styling</li>
                      <li>• Progress indicator theming</li>
                      <li>• Question renderer updates</li>
                      <li>• Results page charts</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>

      <div className="border-t mt-12">
        <div className="container mx-auto px-6 py-4">
          <div className="text-sm text-muted-foreground text-center">
            <strong>Migration Progress:</strong> Phase {phases.filter(p => p.status === 'completed').length}/6 Complete • 
            Current Theme: {designSystem} • 
            Components: {['Button', 'Input', 'Card', 'Label', 'Badge', 'Alert', 'Navigation'].length} Migrated
          </div>
        </div>
      </div>
    </div>
  )
}