"use client"

import type React from "react"

import { Outlet, Link, useLocation, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Sheet, SheetContent } from "@/components/ui/sheet"
import { useAuthStore } from "@/store/auth-store"
import {
  Building2,
  FileText,
  MessageSquare,
  BarChart3,
  Settings,
  LogOut,
  Bell,
  Search,
  Home,
  Users,
  Shield,
  HelpCircle,
  ChevronDown,
  Plus,
  Zap,
  Activity,
} from "lucide-react"
import { useState, useEffect } from "react"
import { Meteors } from "@/components/aceternity/meteors"
import { AnimatedTooltip } from "@/components/aceternity/animated-tooltip"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import { MobileNavigation } from "./mobile-navigation"
import { BottomNavigation } from "./bottom-navigation"
import { useResponsive } from "@/hooks/use-responsive"
import { SkipLinks } from "@/components/ui/skip-links"
import { useAccessibility } from "@/hooks/use-accessibility"

const navigation = (user: any) => [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: Home,
    description: "Overview and key metrics",
  },
  {
    name: "Business Profiles",
    href: "/business-profiles",
    icon: Building2,
    description: "Manage organization profiles",
    badge: "3",
  },
  {
    name: "Evidence",
    href: "/evidence",
    icon: FileText,
    description: "Compliance documentation",
    badge: "127",
  },
  {
    name: "Assessments",
    href: "/assessments",
    icon: Shield,
    description: "Compliance assessments",
  },
  {
    name: "AI Assistant",
    href: "/chat",
    icon: MessageSquare,
    description: "Get compliance guidance",
    badge: "New",
  },
  {
    name: "Reports",
    href: "/reports",
    icon: BarChart3,
    description: "Generate compliance reports",
  },
  {
    name: "Integrations",
    href: "/integrations",
    icon: Zap,
    description: "Third-party integrations",
  },
  {
    name: "Team",
    href: "/team",
    icon: Users,
    description: "Manage team members",
  },
  // Add monitoring for admin users
  ...(user?.role === "admin"
    ? [
        {
          name: "Monitoring",
          href: "/monitoring",
          icon: Activity,
          description: "System monitoring",
        },
      ]
    : []),
]

const quickActions = [
  { name: "New Business Profile", href: "/business-profiles/new", icon: Building2 },
  { name: "Upload Evidence", href: "/evidence/new", icon: FileText },
  { name: "Start Assessment", href: "/assessments/new", icon: Shield },
  { name: "Generate Report", href: "/reports/new", icon: BarChart3 },
]

const teamMembers = [
  {
    id: 1,
    name: "John Doe",
    designation: "Compliance Officer",
    image: "/placeholder.svg?height=40&width=40&text=JD",
  },
  {
    id: 2,
    name: "Jane Smith",
    designation: "Legal Counsel",
    image: "/placeholder.svg?height=40&width=40&text=JS",
  },
  {
    id: 3,
    name: "Mike Johnson",
    designation: "IT Security",
    image: "/placeholder.svg?height=40&width=40&text=MJ",
  },
  {
    id: 4,
    name: "Sarah Wilson",
    designation: "Risk Manager",
    image: "/placeholder.svg?height=40&width=40&text=SW",
  },
]

interface MainAppLayoutProps {
  children?: React.ReactNode
}

export function MainAppLayout({ children }: MainAppLayoutProps = {}) {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const { isMobile, isTablet, isDesktop } = useResponsive()
  const { announceToScreenReader, setFocusToMain } = useAccessibility()
  const [notifications] = useState([
    {
      id: 1,
      title: "New evidence required",
      message: "GDPR Article 30 documentation needed",
      time: "2h ago",
      unread: true,
    },
    { id: 2, title: "Assessment completed", message: "ISO 27001 assessment finished", time: "1d ago", unread: true },
    { id: 3, title: "Report generated", message: "Monthly compliance report ready", time: "2d ago", unread: false },
  ])

  const unreadCount = notifications.filter((n) => n.unread).length

  const handleLogout = async () => {
    try {
      logout()
      announceToScreenReader("You have been logged out successfully")
      navigate("/login")
    } catch (error) {
      console.error("Logout failed:", error)
      announceToScreenReader("Logout failed. Please try again.")
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      announceToScreenReader(`Searching for ${searchQuery}`)
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`)
    }
  }

  // Close mobile sidebar when route changes
  useEffect(() => {
    setSidebarOpen(false)
  }, [location.pathname])

  // Announce route changes to screen readers
  useEffect(() => {
    const currentPage = navigation(user).find((item) => location.pathname.startsWith(item.href))
    if (currentPage) {
      announceToScreenReader(`Navigated to ${currentPage.name} page`)
    }
  }, [location.pathname, user, announceToScreenReader])

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex h-16 items-center px-4 border-b border-gray-200 dark:border-gray-700">
        <Link
          to="/dashboard"
          className="flex items-center space-x-2 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md p-1"
          aria-label="NexCompli Dashboard Home"
        >
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <Shield className="h-5 w-5 text-white" aria-hidden="true" />
          </div>
          <span className="text-xl font-bold text-gray-900 dark:text-white">NexCompli</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto" role="navigation" aria-label="Main navigation">
        {navigation(user).map((item) => {
          const Icon = item.icon
          const isActive =
            location.pathname === item.href || (item.href !== "/dashboard" && location.pathname.startsWith(item.href))

          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200",
                "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
                isActive
                  ? "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-300 border-r-2 border-blue-500"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white",
              )}
              aria-current={isActive ? "page" : undefined}
              aria-describedby={`nav-desc-${item.name.replace(/\s+/g, "-").toLowerCase()}`}
            >
              <Icon
                className={cn(
                  "mr-3 h-5 w-5 transition-colors",
                  isActive ? "text-blue-600 dark:text-blue-400" : "text-gray-400 group-hover:text-gray-600",
                )}
                aria-hidden="true"
              />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span>{item.name}</span>
                  {item.badge && (
                    <Badge
                      variant={isActive ? "default" : "secondary"}
                      className="text-xs"
                      aria-label={`${item.badge} items`}
                    >
                      {item.badge}
                    </Badge>
                  )}
                </div>
                <p
                  id={`nav-desc-${item.name.replace(/\s+/g, "-").toLowerCase()}`}
                  className="text-xs text-gray-500 dark:text-gray-400 mt-0.5"
                >
                  {item.description}
                </p>
              </div>
            </Link>
          )
        })}
      </nav>

      <Separator />

      {/* Quick Actions */}
      <div className="p-4">
        <div className="mb-3">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Quick Actions
          </h3>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              className="w-full justify-between focus:ring-2 focus:ring-blue-500"
              size="sm"
              aria-label="Create new item menu"
            >
              <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
              Create New
              <ChevronDown className="h-4 w-4 ml-2" aria-hidden="true" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56">
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <DropdownMenuItem key={action.name} asChild>
                  <Link to={action.href} className="flex items-center">
                    <Icon className="h-4 w-4 mr-2" aria-hidden="true" />
                    {action.name}
                  </Link>
                </DropdownMenuItem>
              )
            })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <Separator />

      {/* Team Members */}
      <div className="p-4">
        <div className="mb-3">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Team Members
          </h3>
        </div>
        <div className="flex items-center space-x-1" role="group" aria-label="Team member avatars">
          <AnimatedTooltip items={teamMembers} />
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 rounded-full focus:ring-2 focus:ring-blue-500"
            asChild
            aria-label="View all team members"
          >
            <Link to="/team">
              <Plus className="h-4 w-4" aria-hidden="true" />
            </Link>
          </Button>
        </div>
      </div>

      {/* Settings */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <Link
          to="/settings"
          className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          aria-label="Application settings"
        >
          <Settings className="mr-3 h-5 w-5" aria-hidden="true" />
          Settings
        </Link>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Skip Links */}
      <SkipLinks />

      {/* Mobile sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 w-80" aria-label="Navigation menu">
          <SidebarContent />
        </SheetContent>
      </Sheet>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-80 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 relative overflow-hidden">
          <Meteors number={15} />
          <div className="relative z-10 flex-1">
            <SidebarContent />
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className={cn("lg:pl-80", isMobile && "pb-16")}>
        {/* Top bar */}
        <header
          className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-2 sm:gap-x-4 border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm px-2 sm:px-4 shadow-sm lg:px-8"
          role="banner"
        >
          {/* Mobile menu button */}
          <MobileNavigation />

          {/* Search */}
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <form onSubmit={handleSearch} className="relative flex flex-1 max-w-md" role="search">
              <label htmlFor="global-search" className="sr-only">
                Search compliance items
              </label>
              <Search
                className="pointer-events-none absolute inset-y-0 left-0 h-full w-5 text-gray-400 pl-3"
                aria-hidden="true"
              />
              <Input
                id="global-search"
                type="search"
                placeholder="Search compliance items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 focus:ring-2 focus:ring-blue-500"
                aria-describedby="search-description"
              />
              <div id="search-description" className="sr-only">
                Search across all compliance items including evidence, assessments, and reports
              </div>
            </form>
          </div>

          {/* Right side actions */}
          <div className="flex items-center gap-x-4 lg:gap-x-6">
            {/* Help */}
            <Button
              variant="ghost"
              size="sm"
              asChild
              className="focus:ring-2 focus:ring-blue-500"
              aria-label="Get help and support"
            >
              <Link to="/help">
                <HelpCircle className="h-5 w-5" aria-hidden="true" />
              </Link>
            </Button>

            {/* Notifications */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="relative focus:ring-2 focus:ring-blue-500"
                  aria-label={`Notifications ${unreadCount > 0 ? `(${unreadCount} unread)` : ""}`}
                >
                  <Bell className="h-5 w-5" aria-hidden="true" />
                  {unreadCount > 0 && (
                    <Badge
                      variant="destructive"
                      className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center text-xs p-0"
                      aria-hidden="true"
                    >
                      {unreadCount}
                    </Badge>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80" aria-label="Notifications menu">
                <DropdownMenuLabel>Notifications</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {notifications.map((notification) => (
                  <DropdownMenuItem
                    key={notification.id}
                    className="flex flex-col items-start p-4 focus:bg-gray-50 dark:focus:bg-gray-800"
                    role="menuitem"
                  >
                    <div className="flex items-start justify-between w-full">
                      <div className="flex-1">
                        <p className="text-sm font-medium">{notification.title}</p>
                        <p className="text-xs text-gray-500 mt-1">{notification.message}</p>
                        <p className="text-xs text-gray-400 mt-1">{notification.time}</p>
                      </div>
                      {notification.unread && (
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-1" aria-label="Unread notification" />
                      )}
                    </div>
                  </DropdownMenuItem>
                ))}
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/notifications" className="text-center w-full">
                    View all notifications
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* User menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="relative h-8 w-8 rounded-full focus:ring-2 focus:ring-blue-500"
                  aria-label={`User menu for ${user?.email}`}
                >
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user?.avatar || "/placeholder.svg"} alt={`${user?.email} avatar`} />
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                      {user?.email?.charAt(0).toUpperCase() || "U"}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" aria-label="User account menu">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user?.email}</p>
                    <p className="text-xs leading-none text-muted-foreground">Compliance Manager</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/profile">Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/settings">Settings</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/billing">Billing</Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" aria-hidden="true" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page content */}
        <main
          id="main-content"
          className="flex-1 focus:outline-none"
          role="main"
          aria-label="Main content"
          tabIndex={-1}
        >
          <div className="px-4 py-8 sm:px-6 lg:px-8">{children || <Outlet />}</div>
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800" role="contentinfo">
          <div className="px-4 py-6 sm:px-6 lg:px-8">
            <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
              <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                <span>© 2024 NexCompli. All rights reserved.</span>
                <Separator orientation="vertical" className="h-4" />
                <Link
                  to="/privacy"
                  className="hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                >
                  Privacy Policy
                </Link>
                <Link
                  to="/terms"
                  className="hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                >
                  Terms of Service
                </Link>
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                <span>Status: All systems operational</span>
                <div className="w-2 h-2 bg-green-500 rounded-full" aria-label="System status: operational" />
              </div>
            </div>
          </div>
        </footer>
      </div>
      {/* Bottom Navigation for Mobile */}
      <BottomNavigation />

      {/* Screen reader announcements */}
      <div id="screen-reader-announcements" className="sr-only" aria-live="polite" aria-atomic="true" role="status" />
    </div>
  )
}
