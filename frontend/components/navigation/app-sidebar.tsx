"use client"

import {
  LayoutDashboard,
  BookCheck,
  FileText,
  BarChart3,
  FolderOpen,
  MessageSquare,
  Settings,
  Users,
  Plug,
  ChevronDown,
  TrendingUp,
} from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  useSidebar,
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"

import { ThemeToggle } from "../ui/theme-toggle"

const menuItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/analytics", label: "Analytics", icon: TrendingUp },
  { href: "/assessments", label: "Assessments", icon: BookCheck },
  { href: "/evidence", label: "Evidence", icon: FolderOpen },
  { href: "/policies", label: "Policies", icon: FileText },
  { href: "/reports", label: "Reports", icon: BarChart3 },
  { href: "/chat", label: "IQ Chat", icon: MessageSquare },
]

const settingsSubMenu = [
  { href: "/settings/team", label: "Team Management", icon: Users },
  { href: "/settings/integrations", label: "Integrations", icon: Plug },
]

export function AppSidebar() {
  const pathname = usePathname()
  const { open } = useSidebar()

  const isSettingsActive = settingsSubMenu.some((item) => pathname.startsWith(item.href))

  return (
    <Sidebar className="bg-white border-r border-neutral-100">
      <SidebarHeader className="p-4 border-b border-neutral-100">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl font-bold text-teal-600">ruleIQ</span>
        </Link>
      </SidebarHeader>
      <SidebarContent className="p-2">
        <SidebarMenu>
          {menuItems.map((item) => (
            <SidebarMenuItem key={item.href}>
              <SidebarMenuButton
                asChild
                isActive={pathname === item.href}
                className={cn(
                  "w-full justify-start text-neutral-600 hover:text-teal-600 hover:bg-teal-50 transition-colors rounded-lg",
                  pathname === item.href && "bg-teal-50 text-teal-600 font-medium"
                )}
              >
                <Link href={item.href}>
                  <item.icon />
                  <span>{item.label}</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
          <Collapsible defaultOpen={isSettingsActive}>
            <CollapsibleTrigger asChild>
              <SidebarMenuButton
                className={cn(
                  "w-full justify-start group text-neutral-600 hover:text-teal-600 hover:bg-teal-50 rounded-lg",
                  isSettingsActive && "text-teal-600"
                )}
              >
                <Settings />
                <span>Settings</span>
                <ChevronDown className="ml-auto h-4 w-4 transition-transform group-data-[state=open]:rotate-180" />
              </SidebarMenuButton>
            </CollapsibleTrigger>
            <CollapsibleContent className="pl-8 pt-1 space-y-1">
              <SidebarMenu>
                {settingsSubMenu.map((item) => (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      asChild
                      isActive={pathname.startsWith(item.href)}
                      className={cn(
                        "w-full justify-start h-9 text-neutral-500 hover:text-teal-600 hover:bg-teal-50 rounded-lg",
                        pathname.startsWith(item.href) && "bg-teal-50 text-teal-600 font-medium"
                      )}
                      size="sm"
                    >
                      <Link href={item.href}>
                        <item.icon />
                        <span>{item.label}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </CollapsibleContent>
          </Collapsible>
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter className="p-4">
        <ThemeToggle />
      </SidebarFooter>
    </Sidebar>
  )
}
