'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/stores/ui.store';
import {
  LayoutDashboard,
  FileText,
  Settings,
  Users,
  BarChart3,
  Shield,
  Bell,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/lib/stores/auth.store';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Compliance', href: '/compliance', icon: Shield },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Reports', href: '/reports', icon: BarChart3 },
  { name: 'Team', href: '/team', icon: Users },
  { name: 'Notifications', href: '/notifications', icon: Bell },
];

const bottomNavigation = [
  { name: 'Help & Support', href: '/help', icon: HelpCircle },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebar, toggleSidebarCollapse } = useUIStore();
  const { logout, user } = useAuthStore();

  return (
    <TooltipProvider>
      <aside
        className={cn(
          'fixed left-0 top-0 z-40 h-screen bg-brand-navy transition-all duration-300',
          sidebar.isOpen && !sidebar.isCollapsed ? 'w-64' : 'w-20',
          !sidebar.isOpen && '-translate-x-full',
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-4">
            <Link
              href="/dashboard"
              className={cn(
                'flex items-center',
                sidebar.isCollapsed && 'justify-center',
              )}
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-teal">
                <span className="text-lg font-bold text-white">R</span>
              </div>
              {!sidebar.isCollapsed && (
                <span className="ml-3 text-xl font-semibold text-white">
                  ruleIQ
                </span>
              )}
            </Link>
            {!sidebar.isCollapsed && (
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleSidebarCollapse}
                className="text-white hover:bg-brand-teal/20"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* User Info */}
          {user && !sidebar.isCollapsed && (
            <div className="border-b border-white/10 px-4 py-4">
              <p className="truncate text-sm font-medium text-white">
                {user.fullName || user.email}
              </p>
              <p className="truncate text-xs text-white/60">{user.email}</p>
            </div>
          )}

          {/* Main Navigation */}
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <Tooltip key={item.name} delayDuration={0}>
                  <TooltipTrigger asChild>
                    <Link
                      href={item.href}
                      className={cn(
                        'group flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-brand-teal text-white'
                          : 'text-white/80 hover:bg-white/10 hover:text-white',
                        sidebar.isCollapsed && 'justify-center px-2',
                      )}
                    >
                      <Icon
                        className={cn(
                          'h-5 w-5 flex-shrink-0',
                          !sidebar.isCollapsed && 'mr-3',
                        )}
                      />
                      {!sidebar.isCollapsed && item.name}
                    </Link>
                  </TooltipTrigger>
                  {sidebar.isCollapsed && (
                    <TooltipContent side="right">
                      <p>{item.name}</p>
                    </TooltipContent>
                  )}
                </Tooltip>
              );
            })}
          </nav>

          {/* Bottom Navigation */}
          <div className="border-t border-white/10 px-2 py-4">
            {bottomNavigation.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <Tooltip key={item.name} delayDuration={0}>
                  <TooltipTrigger asChild>
                    <Link
                      href={item.href}
                      className={cn(
                        'group flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-brand-teal text-white'
                          : 'text-white/80 hover:bg-white/10 hover:text-white',
                        sidebar.isCollapsed && 'justify-center px-2',
                      )}
                    >
                      <Icon
                        className={cn(
                          'h-5 w-5 flex-shrink-0',
                          !sidebar.isCollapsed && 'mr-3',
                        )}
                      />
                      {!sidebar.isCollapsed && item.name}
                    </Link>
                  </TooltipTrigger>
                  {sidebar.isCollapsed && (
                    <TooltipContent side="right">
                      <p>{item.name}</p>
                    </TooltipContent>
                  )}
                </Tooltip>
              );
            })}

            {/* Logout Button */}
            <Tooltip delayDuration={0}>
              <TooltipTrigger asChild>
                <button
                  onClick={logout}
                  className={cn(
                    'group flex w-full items-center rounded-lg px-3 py-2.5 text-sm font-medium text-white/80 transition-colors hover:bg-red-600/20 hover:text-red-400',
                    sidebar.isCollapsed && 'justify-center px-2',
                  )}
                >
                  <LogOut
                    className={cn(
                      'h-5 w-5 flex-shrink-0',
                      !sidebar.isCollapsed && 'mr-3',
                    )}
                  />
                  {!sidebar.isCollapsed && 'Logout'}
                </button>
              </TooltipTrigger>
              {sidebar.isCollapsed && (
                <TooltipContent side="right">
                  <p>Logout</p>
                </TooltipContent>
              )}
            </Tooltip>
          </div>

          {/* Collapse Toggle (when collapsed) */}
          {sidebar.isCollapsed && (
            <div className="border-t border-white/10 p-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleSidebarCollapse}
                className="w-full text-white hover:bg-brand-teal/20"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </aside>
    </TooltipProvider>
  );
}