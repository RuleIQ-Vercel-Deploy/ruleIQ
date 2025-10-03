'use client';

import { Search, Bell, Menu, User, Settings, LogOut } from 'lucide-react';
import Link from 'next/link';
import * as React from 'react';

import { Badge } from '@/components/ui/badge';
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

interface TopHeaderProps {
  onMobileMenuToggle?: () => void;
}

export function TopHeader({ onMobileMenuToggle }: TopHeaderProps) {
  const { toggleSidebar, isMobile } = useSidebar();
  const [searchValue, setSearchValue] = React.useState('');

  const handleMobileMenuClick = () => {
    if (isMobile) {
      toggleSidebar();
    }
    onMobileMenuToggle?.();
  };

  return (
    <header
      className="supports-[backdrop-filter]:bg-oxford-blue/95 sticky top-0 z-50 w-full border-b backdrop-blur"
      style={{
        backgroundColor: 'var(--black)',
        borderBottomColor: 'rgba(233, 236, 239, 0.2)',
      }}
    >
      <div className="container flex h-16 max-w-screen-2xl items-center px-4">
        {/* Mobile Hamburger Menu */}
        <Button
          variant="ghost"
          size="icon"
          className="mr-2 hover:bg-white/10 md:hidden"
          onClick={handleMobileMenuClick}
          style={{ color: 'var(--purple-50)' }}
        >
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle navigation menu</span>
        </Button>

        {/* Logo Area */}
        <div className="mr-6 flex items-center space-x-2">
          <Link href="/" className="flex items-center space-x-1">
            <div className="flex items-center space-x-1">
              <span className="text-xl font-bold" style={{ color: 'var(--purple-50)' }}>
                rule
              </span>
              <span className="text-xl font-bold" style={{ color: 'var(--purple-400)' }}>
                IQ
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation Links - Hidden on mobile */}
        <nav className="mr-6 hidden items-center space-x-6 text-sm font-medium md:flex">
          <Link
            href="/"
            className="transition-colors hover:text-white"
            style={{ color: 'var(--purple-50)' }}
          >
            Dashboard
          </Link>
          <Link
            href="/assessments"
            className="transition-colors hover:text-white"
            style={{ color: 'var(--silver-500)' }}
          >
            Assessments
          </Link>
          <Link
            href="/evidence"
            className="transition-colors hover:text-white"
            style={{ color: 'var(--silver-500)' }}
          >
            Evidence
          </Link>
          <Link
            href="/policies"
            className="transition-colors hover:text-white"
            style={{ color: 'var(--silver-500)' }}
          >
            Policies
          </Link>
          <Link
            href="/reports"
            className="transition-colors hover:text-white"
            style={{ color: 'var(--silver-500)' }}
          >
            Reports
          </Link>
        </nav>

        {/* Search Input */}
        <div className="flex flex-1 items-center justify-center px-2 lg:ml-6 lg:justify-start">
          <div className="w-full max-w-lg lg:max-w-xs">
            <div className="relative">
              <Search
                className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2"
                style={{ color: 'var(--silver-500)' }}
              />
              <Input
                type="search"
                placeholder="Search compliance data..."
                className="w-full border-0 py-2 pl-10 pr-4 text-sm focus-visible:ring-1 focus-visible:ring-offset-0"
                style={{
                  backgroundColor: 'rgba(240, 234, 214, 0.1)',
                  color: 'var(--purple-50)',
                  borderColor: 'rgba(233, 236, 239, 0.2)',
                }}
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Right Side - Notifications and User Menu */}
        <div className="flex items-center space-x-2">
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="relative hover:bg-white/10"
                style={{ color: 'var(--purple-50)' }}
              >
                <Bell className="h-5 w-5" />
                {/* Notification Badge */}
                <Badge
                  className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full p-0 text-xs"
                  style={{
                    backgroundColor: 'var(--purple-500)',
                    color: 'var(--white)',
                  }}
                >
                  3
                </Badge>
                <span className="sr-only">View notifications</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-80"
              style={{
                backgroundColor: 'var(--purple-50)',
                borderColor: 'rgba(233, 236, 239, 0.2)',
              }}
            >
              <DropdownMenuLabel style={{ color: 'var(--black)' }}>Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <div className="space-y-1">
                <div className="p-3 text-sm" style={{ color: 'var(--black)' }}>
                  <div className="font-medium">GDPR Assessment Due</div>
                  <div className="text-xs" style={{ color: 'var(--silver-500)' }}>
                    Complete by March 15, 2024
                  </div>
                </div>
                <div className="p-3 text-sm" style={{ color: 'var(--black)' }}>
                  <div className="font-medium">New Policy Update</div>
                  <div className="text-xs" style={{ color: 'var(--silver-500)' }}>
                    Financial reporting policy updated
                  </div>
                </div>
                <div className="p-3 text-sm" style={{ color: 'var(--black)' }}>
                  <div className="font-medium">Compliance Score Improved</div>
                  <div className="text-xs" style={{ color: 'var(--silver-500)' }}>
                    Your score increased to 98%
                  </div>
                </div>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Avatar and Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-8 w-8 rounded-full hover:bg-white/10"
                style={{
                  backgroundColor: 'rgba(255, 215, 0, 0.2)',
                }}
              >
                <User className="h-4 w-4" style={{ color: 'var(--purple-400)' }} />
                <span className="sr-only">Open user menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className="w-56"
              align="end"
              forceMount
              style={{
                backgroundColor: 'var(--purple-50)',
                borderColor: 'rgba(233, 236, 239, 0.2)',
              }}
            >
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none" style={{ color: 'var(--black)' }}>
                    John Doe
                  </p>
                  <p className="text-xs leading-none" style={{ color: 'var(--silver-500)' }}>
                    john.doe@company.com
                  </p>
                  <p className="text-xs leading-none" style={{ color: 'var(--silver-500)' }}>
                    Compliance Manager
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem style={{ color: 'var(--black)' }}>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem style={{ color: 'var(--black)' }}>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem style={{ color: 'var(--black)' }}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
