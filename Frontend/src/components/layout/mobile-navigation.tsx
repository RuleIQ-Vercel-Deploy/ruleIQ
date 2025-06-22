"use client"

import { useState } from "react"
import { Link, useLocation } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useAuthStore } from "@/store/auth-store"
import { useSwipe } from "@/hooks/use-touch"
import {
  Home,
  Building2,
  FileText,
  Shield,
  MessageSquare,
  BarChart3,
  Zap,
  Users,
  Activity,
  Menu,
  X,
  Settings,
  LogOut,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = (user: any) => [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: Home,
    badge: null,
  },
  {
    name: "Profiles",
    href: "/business-profiles",
    icon: Building2,
    badge: "3",
  },
  {
    name: "Evidence",
    href: "/evidence",
    icon: FileText,
    badge: "127",
  },
  {
    name: "Assessments",
    href: "/assessments",
    icon: Shield,
    badge: null,
  },
  {
    name: "AI Chat",
    href: "/chat",
    icon: MessageSquare,
    badge: "New",
  },
  {
    name: "Reports",
    href: "/reports",
    icon: BarChart3,
    badge: null,
  },
  {
    name: "Integrations",
    href: "/integrations",
    icon: Zap,
    badge: null,
  },
  {
    name: "Team",
    href: "/team",
    icon: Users,
    badge: null,
  },
  ...(user?.role === "admin"
    ? [
        {
          name: "Monitoring",
          href: "/monitoring",
          icon: Activity,
          badge: null,
        },
      ]
    : []),
]

interface MobileNavigationProps {
  className?: string
}

export function MobileNavigation({ className }: MobileNavigationProps) {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)

  const swipeHandlers = useSwipe((swipe) => {
    if (swipe.direction === "left" && isOpen) {
      setIsOpen(false)
    }
  })

  const handleLogout = () => {
    logout()
    setIsOpen(false)
    window.location.href = "/login"
  }

  return (
    <div className={cn("lg:hidden", className)}>
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="sm" className="h-10 w-10 p-0 hover:bg-gray-100 dark:hover:bg-gray-800">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Open navigation menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-80 p-0 bg-white dark:bg-gray-900" {...swipeHandlers}>
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Shield className="h-5 w-5 text-white" />
                </div>
                <span className="text-lg font-bold text-gray-900 dark:text-white">NexCompli</span>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setIsOpen(false)} className="h-8 w-8 p-0">
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* User Info */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <Avatar className="h-10 w-10">
                  <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                    {user?.email?.charAt(0).toUpperCase() || "U"}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{user?.email}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {user?.role === "admin" ? "Administrator" : "User"}
                  </p>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
              {navigation(user).map((item) => {
                const Icon = item.icon
                const isActive =
                  location.pathname === item.href ||
                  (item.href !== "/dashboard" && location.pathname.startsWith(item.href))

                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setIsOpen(false)}
                    className={cn(
                      "group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 touch-manipulation",
                      isActive
                        ? "bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 text-blue-700 dark:text-blue-300"
                        : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white active:bg-gray-100 dark:active:bg-gray-700",
                    )}
                  >
                    <Icon
                      className={cn(
                        "mr-3 h-6 w-6 transition-colors",
                        isActive ? "text-blue-600 dark:text-blue-400" : "text-gray-400",
                      )}
                    />
                    <span className="flex-1">{item.name}</span>
                    {item.badge && (
                      <Badge variant={isActive ? "default" : "secondary"} className="text-xs ml-2">
                        {item.badge}
                      </Badge>
                    )}
                  </Link>
                )
              })}
            </nav>

            {/* Footer Actions */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
              <Link
                to="/settings"
                onClick={() => setIsOpen(false)}
                className="flex items-center px-3 py-3 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white transition-colors touch-manipulation"
              >
                <Settings className="mr-3 h-5 w-5" />
                Settings
              </Link>
              <button
                onClick={handleLogout}
                className="w-full flex items-center px-3 py-3 text-sm font-medium text-red-600 rounded-lg hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-900/20 dark:hover:text-red-300 transition-colors touch-manipulation"
              >
                <LogOut className="mr-3 h-5 w-5" />
                Sign Out
              </button>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  )
}
