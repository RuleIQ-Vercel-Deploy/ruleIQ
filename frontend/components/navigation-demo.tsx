'use client'

import { useState } from 'react'
import { useDesignSystem } from '@/providers/design-system-provider'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AppSidebar } from '@/components/navigation/app-sidebar'
import { TopNavigation } from '@/components/navigation/top-navigation'
import { MobileNav } from '@/components/navigation/mobile-nav'
import { Menu } from 'lucide-react'

export function NavigationDemo() {
  const { designSystem, toggleDesignSystem, isNewTheme } = useDesignSystem()
  const [showMobileNav, setShowMobileNav] = useState(false)

  return (
    <div className="min-h-screen">
      {/* Top Navigation Demo */}
      <TopNavigation />
      
      <div className="flex">
        {/* Sidebar Demo */}
        <div className="hidden md:block w-64 h-[calc(100vh-4rem)]">
          <AppSidebar />
        </div>
        
        {/* Main Content */}
        <div className="flex-1 p-8 space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold">Navigation Demo</h1>
            <div className="flex items-center gap-4">
              <Badge variant={isNewTheme ? 'brand' : 'secondary'}>
                {isNewTheme ? 'Teal Theme' : 'Legacy Theme'}
              </Badge>
              <Button onClick={toggleDesignSystem}>
                Switch to {isNewTheme ? 'Legacy' : 'Teal'} Theme
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="md:hidden"
                onClick={() => setShowMobileNav(true)}
              >
                <Menu className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Navigation Features</CardTitle>
                <CardDescription>Theme-aware navigation components</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-medium">✅ Top Navigation</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Theme-aware header background and text</li>
                    <li>• Search input with proper contrast</li>
                    <li>• Countdown timer with brand colors</li>
                    <li>• Theme toggle with visual feedback</li>
                    <li>• Alerts dropdown with theme styling</li>
                    <li>• User profile menu adaptation</li>
                  </ul>
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-medium">✅ App Sidebar</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Gradient logo with theme colors</li>
                    <li>• Menu items with active states</li>
                    <li>• Hover effects per theme</li>
                    <li>• Collapsible submenu support</li>
                    <li>• Border and background adaptation</li>
                  </ul>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">✅ Mobile Navigation</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Sheet component theme support</li>
                    <li>• Logo with brand colors</li>
                    <li>• Navigation links with active states</li>
                    <li>• Close button hover effects</li>
                    <li>• Responsive design maintained</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Theme Comparison</CardTitle>
                <CardDescription>Visual differences between themes</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-medium">🎨 Teal Theme (Light)</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Clean white backgrounds</li>
                    <li>• Teal brand colors (#2C7A7B)</li>
                    <li>• Neutral gray text hierarchy</li>
                    <li>• Light borders and subtle shadows</li>
                    <li>• High contrast for accessibility</li>
                  </ul>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">🌙 Legacy Theme (Dark)</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Dark surface backgrounds</li>
                    <li>• Purple/cyan brand colors</li>
                    <li>• Light text on dark surfaces</li>
                    <li>• Glowing effects and transparency</li>
                    <li>• Professional dark mode feel</li>
                  </ul>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">🔄 Transition Features</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Smooth color transitions</li>
                    <li>• CSS variable switching</li>
                    <li>• Instant theme updates</li>
                    <li>• Consistent component behavior</li>
                    <li>• Preserved interactive states</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="text-sm text-muted-foreground">
            <strong>Current State:</strong> Design System = {designSystem}, 
            Theme = {isNewTheme ? 'Teal (Light)' : 'Legacy (Dark)'}, 
            Components = Top Nav + App Sidebar + Mobile Nav
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <MobileNav 
        open={showMobileNav} 
        onOpenChange={setShowMobileNav} 
      />
    </div>
  )
}