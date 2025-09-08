'use client';

import {
  LayoutDashboard,
  FileText,
  BarChart3,
  FolderOpen,
  Settings,
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@/components/ui/sidebar';
import { cn } from '@/lib/utils';

import { ThemeToggle } from '../ui/theme-toggle';

const menuItems = [
  { href: '/policies', label: 'Policies', icon: FileText },
  { href: '/evidence', label: 'Evidence', icon: FolderOpen },
  { href: '/risks', label: 'Risks', icon: BarChart3 },
  { href: '/debug', label: 'Debug', icon: LayoutDashboard },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar className="border-glass-border border-r bg-background">
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
                isActive={pathname === item.href || (item.href === '/settings' && pathname?.startsWith('/settings'))}
                className={cn(
                  'w-full justify-start text-muted-foreground transition-colors hover:text-foreground',
                  (pathname === item.href || (item.href === '/settings' && pathname?.startsWith('/settings'))) && 
                  'bg-primary/10 text-primary hover:bg-primary/20',
                )}
              >
                <Link href={item.href}>
                  <item.icon />
                  <span>{item.label}</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter className="p-4">
        <ThemeToggle />
      </SidebarFooter>
    </Sidebar>
  );
}