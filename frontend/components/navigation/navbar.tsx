'use client';

import React from 'react';
import Link from 'next/link';
import { Menu, Search, Bell } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import { useSidebar } from '@/components/ui/sidebar';
import { cn } from '@/lib/utils';

interface NavbarProps {
  className?: string;
}

export function Navbar({ className }: NavbarProps) {
  const { toggleSidebar } = useSidebar();
  const [notifications] = React.useState([
    { id: 1, title: 'New assessment available', time: '5 minutes ago', unread: true },
    { id: 2, title: 'Compliance report ready', time: '1 hour ago', unread: true },
    { id: 3, title: 'Policy update required', time: '2 hours ago', unread: false },
  ]);

  const unreadCount = notifications.filter((n) => n.unread).length;

  return (
    <nav className={cn('sticky top-0 z-40 border-b border-neutral-100 bg-white', className)}>
      <div className="flex h-16 items-center justify-between px-4 lg:px-6">
        {/* Left Side */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="text-neutral-600 hover:text-purple-600 lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>

          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl font-extralight text-purple-600">ruleIQ</span>
          </Link>
        </div>

        {/* Center - Search */}
        <div className="mx-8 hidden max-w-md flex-1 md:flex">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
            <Input
              type="search"
              placeholder="Search assessments, policies, evidence..."
              className="border-neutral-200 bg-neutral-50 pl-10 focus:bg-white"
            />
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-2">
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="relative text-neutral-600 hover:text-purple-600"
              >
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-purple-600 text-xs text-white">
                    {unreadCount}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 bg-white">
              <DropdownMenuLabel>Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {notifications.map((notification) => (
                <DropdownMenuItem
                  key={notification.id}
                  className="flex flex-col items-start gap-1 p-3"
                >
                  <div className="flex w-full items-center gap-2">
                    <span
                      className={cn(
                        'text-sm font-medium',
                        notification.unread && 'text-neutral-900',
                      )}
                    >
                      {notification.title}
                    </span>
                    {notification.unread && (
                      <div className="ml-auto h-2 w-2 rounded-full bg-purple-600" />
                    )}
                  </div>
                  <span className="text-xs text-neutral-500">{notification.time}</span>
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-center text-purple-600 hover:text-purple-700">
                View all notifications
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                <Avatar className="h-9 w-9">
                  <AvatarImage src="/placeholder-avatar.jpg" alt="User" />
                  <AvatarFallback className="bg-purple-100 text-purple-700">JD</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-white">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium text-neutral-900">John Doe</p>
                  <p className="text-xs text-neutral-500">john.doe@company.com</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-neutral-700 hover:text-purple-600">
                Profile Settings
              </DropdownMenuItem>
              <DropdownMenuItem className="text-neutral-700 hover:text-purple-600">
                Billing
              </DropdownMenuItem>
              <DropdownMenuItem className="text-neutral-700 hover:text-purple-600">
                Team Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-neutral-700 hover:text-purple-600">
                Help & Support
              </DropdownMenuItem>
              <DropdownMenuItem className="text-red-600 hover:text-red-700">
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </nav>
  );
}
