'use client';

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
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  useSidebar,
} from '@/components/ui/sidebar';
import { cn } from '@/lib/utils';

import { ThemeToggle } from '../ui/theme-toggle';

const menuItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/analytics', label: 'Analytics', icon: TrendingUp },
  { href: '/assessments', label: 'Assessments', icon: BookCheck },
  { href: '/evidence', label: 'Evidence', icon: FolderOpen },
  { href: '/policies', label: 'Policies', icon: FileText },
  { href: '/reports', label: 'Reports', icon: BarChart3 },
  { href: '/chat', label: 'IQ Chat', icon: MessageSquare },
];

const settingsSubMenu = [
  { href: '/settings/team', label: 'Team Management', icon: Users },
  { href: '/settings/integrations', label: 'Integrations', icon: Plug },
];

export function AppSidebar() {
  const pathname = usePathname();
  const {} = useSidebar();

  const isSettingsActive = settingsSubMenu.some((item) => pathname?.startsWith(item.href) ?? false);

  return (
    <Sidebar className="border-r border-glass-border bg-background">
      <SidebarHeader className="p-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="gradient-text text-2xl font-bold">ruleIQ</span>
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
                  'w-full justify-start text-muted-foreground transition-colors hover:text-foreground',
                  pathname === item.href && 'bg-primary/10 text-primary hover:bg-primary/20',
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
                  'group w-full justify-start text-muted-foreground hover:text-foreground',
                  isSettingsActive && 'text-primary',
                )}
              >
                <Settings />
                <span>Settings</span>
                <ChevronDown className="ml-auto h-4 w-4 transition-transform group-data-[state=open]:rotate-180" />
              </SidebarMenuButton>
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-1 pl-8 pt-1">
              <SidebarMenu>
                {settingsSubMenu.map((item) => (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      asChild
                      isActive={pathname?.startsWith(item.href) ?? false}
                      className={cn(
                        'h-9 w-full justify-start text-muted-foreground hover:text-foreground',
                        pathname?.startsWith(item.href) &&
                          'bg-primary/10 text-primary hover:bg-primary/20',
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
  );
}
