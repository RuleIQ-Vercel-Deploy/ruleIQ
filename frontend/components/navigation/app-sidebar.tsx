'use client';

import {
  LayoutDashboard,
  FileText,
  BarChart3,
  FolderOpen,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect, useRef, createRef } from 'react';

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
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const menuItems = [
  { href: '/policies', label: 'Policies', icon: FileText },
  { href: '/evidence', label: 'Evidence', icon: FolderOpen },
  { href: '/risks', label: 'Risks', icon: BarChart3 },
  { href: '/debug', label: 'Debug', icon: LayoutDashboard },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function AppSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(0);
  const menuRef = useRef<HTMLUListElement>(null);
  const itemRefs = useRef(menuItems.map(() => createRef<HTMLAnchorElement>()));

  // Focus management for roving tabindex
  useEffect(() => {
    const ref = itemRefs.current[focusedIndex]?.current;
    if (ref) {
      ref.focus();
    }
  }, [focusedIndex]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!menuRef.current) return;

      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault();
          setFocusedIndex((prev) => (prev > 0 ? prev - 1 : menuItems.length - 1));
          break;
        case 'ArrowDown':
          e.preventDefault();
          setFocusedIndex((prev) => (prev < menuItems.length - 1 ? prev + 1 : 0));
          break;
        case 'ArrowLeft':
          if (!isCollapsed) {
            e.preventDefault();
            setIsCollapsed(true);
          }
          break;
        case 'ArrowRight':
          if (isCollapsed) {
            e.preventDefault();
            setIsCollapsed(false);
          }
          break;
        case 'Enter':
        case ' ':
          e.preventDefault();
          const focusedItem = menuItems[focusedIndex];
          if (focusedItem) {
            router.push(focusedItem.href);
            // Re-focus after navigation
            setTimeout(() => {
              const ref = itemRefs.current[focusedIndex]?.current;
              if (ref) {
                ref.focus();
              }
            }, 100);
          }
          break;
        case 'Escape':
          if (isCollapsed) {
            setIsCollapsed(false);
          }
          break;
      }
    };

    const currentMenu = menuRef.current;
    if (currentMenu) {
      currentMenu.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      if (currentMenu) {
        currentMenu.removeEventListener('keydown', handleKeyDown);
      }
    };
  }, [focusedIndex, isCollapsed, router]);

  return (
    <TooltipProvider>
      <aside 
        className={cn(
          "border-r border-purple-200/20 bg-background transition-all duration-300",
          isCollapsed ? "w-20" : "w-64"
        )}
        role="navigation"
        aria-label="Main navigation"
      >
        <Sidebar className="h-full">
          {/* Skip to main content link for accessibility */}
          <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-purple-600 text-white p-2 rounded">
            Skip to main content
          </a>
          
          <SidebarHeader className="p-4 flex items-center justify-between">
            <Link 
              href="/" 
              className={cn(
                "flex items-center gap-2 transition-opacity",
                isCollapsed && "opacity-0 pointer-events-none"
              )}
              aria-label="ruleIQ Home"
            >
              <span className="text-2xl font-extralight text-purple-600">ruleIQ</span>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsCollapsed(!isCollapsed)}
              aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
            >
              {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </Button>
          </SidebarHeader>
          
          <SidebarContent className="p-2">
            <SidebarMenu ref={menuRef}>
              {menuItems.map((item, index) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
                const MenuItem = (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      className={cn(
                        'w-full justify-start font-light text-gray-600 transition-all hover:text-purple-600',
                        isActive && 'bg-purple-600/10 text-purple-600 hover:bg-purple-600/20',
                        focusedIndex === index && 'ring-2 ring-purple-600 ring-offset-2',
                        isCollapsed && "justify-center"
                      )}
                      aria-current={isActive ? 'page' : undefined}
                      aria-label={item.label}
                      tabIndex={focusedIndex === index ? 0 : -1}
                    >
                      <Link href={item.href} ref={itemRefs.current[index]}>
                        <item.icon className={cn("h-5 w-5", !isCollapsed && "mr-2")} aria-hidden="true" />
                        <span className={cn(
                          "transition-opacity",
                          isCollapsed && "sr-only"
                        )}>
                          {item.label}
                        </span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );

                if (isCollapsed) {
                  return (
                    <Tooltip key={item.href} delayDuration={0}>
                      <TooltipTrigger asChild>
                        {MenuItem}
                      </TooltipTrigger>
                      <TooltipContent side="right" className="bg-purple-600 text-white">
                        {item.label}
                      </TooltipContent>
                    </Tooltip>
                  );
                }

                return MenuItem;
              })}
            </SidebarMenu>
          </SidebarContent>
          
          <SidebarFooter className="p-4">
            <div className={cn(
              "transition-opacity",
              isCollapsed && "opacity-0 pointer-events-none"
            )}>
              <ThemeToggle />
            </div>
          </SidebarFooter>
        </Sidebar>
      </aside>
    </TooltipProvider>
  );
}