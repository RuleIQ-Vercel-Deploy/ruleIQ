"use client"

import { Link, useLocation } from "react-router-dom"
import { Badge } from "@/components/ui/badge"
import { useAuthStore } from "@/store/auth-store"
import { useResponsive } from "@/hooks/use-responsive"
import { Home, Building2, FileText, MessageSquare, BarChart3 } from "lucide-react"
import { cn } from "@/lib/utils"

const bottomNavItems = [
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
]

export function BottomNavigation() {
  const location = useLocation()
  const { user } = useAuthStore()
  const { isMobile } = useResponsive()

  if (!isMobile) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 safe-area-pb">
      <nav className="flex items-center justify-around px-2 py-2">
        {bottomNavItems.map((item) => {
          const Icon = item.icon
          const isActive =
            location.pathname === item.href || (item.href !== "/dashboard" && location.pathname.startsWith(item.href))

          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex flex-col items-center justify-center px-3 py-2 min-w-0 flex-1 text-xs font-medium transition-colors touch-manipulation relative",
                isActive
                  ? "text-blue-600 dark:text-blue-400"
                  : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300",
              )}
            >
              <div className="relative">
                <Icon className="h-6 w-6 mb-1" />
                {item.badge && (
                  <Badge
                    variant="destructive"
                    className="absolute -top-2 -right-2 h-4 w-4 p-0 text-xs flex items-center justify-center"
                  >
                    {item.badge === "New" ? "!" : item.badge.length > 2 ? "99+" : item.badge}
                  </Badge>
                )}
              </div>
              <span className="truncate max-w-full">{item.name}</span>
              {isActive && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-8 h-0.5 bg-blue-600 dark:bg-blue-400 rounded-full" />
              )}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
