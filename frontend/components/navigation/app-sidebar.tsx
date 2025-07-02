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
    <Sidebar>
      <SidebarHeader className="p-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl font-bold text-navy">rule</span>
          <span className="text-2xl font-bold text-gold">IQ</span>
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
                  "w-full justify-start",
                  pathname === item.href && "bg-gold/10 text-gold hover:bg-gold/20"
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
                className={cn("w-full justify-start group", isSettingsActive && "text-gold")}
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
                        "w-full justify-start h-9",
                        pathname.startsWith(item.href) && "bg-gold/10 text-gold hover:bg-gold/20"
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
