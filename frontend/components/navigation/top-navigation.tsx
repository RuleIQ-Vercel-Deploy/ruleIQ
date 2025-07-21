'use client';

import {
  Search,
  Bell,
  Sun,
  Moon,
  User,
  Settings,
  LogOut,
  Clock,
  AlertTriangle,
} from 'lucide-react';
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
import { Switch } from '@/components/ui/switch';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface TopNavigationProps {
  isDarkMode?: boolean;
  onThemeToggle?: (isDark: boolean) => void;
}

export function TopNavigation({ isDarkMode = false, onThemeToggle }: TopNavigationProps) {
  const [searchValue, setSearchValue] = React.useState('');
  const [timeUntilAudit, setTimeUntilAudit] = React.useState({
    days: 15,
    hours: 8,
    minutes: 42,
    seconds: 30,
  });

  // Countdown timer effect
  React.useEffect(() => {
    const timer = setInterval(() => {
      setTimeUntilAudit((prev) => {
        let { days, hours, minutes, seconds } = prev;

        if (seconds > 0) {
          seconds--;
        } else if (minutes > 0) {
          minutes--;
          seconds = 59;
        } else if (hours > 0) {
          hours--;
          minutes = 59;
          seconds = 59;
        } else if (days > 0) {
          days--;
          hours = 23;
          minutes = 59;
          seconds = 59;
        }

        return { days, hours, minutes, seconds };
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleThemeToggle = (checked: boolean) => {
    onThemeToggle?.(checked);
  };

  const formatTime = (value: number) => value.toString().padStart(2, '0');

  return (
    <TooltipProvider>
      <header
        className="supports-[backdrop-filter]:bg-oxford-blue/95 sticky top-0 z-50 w-full border-b backdrop-blur"
        style={{
          backgroundColor: '#161e3a',
          borderBottomColor: 'rgba(233, 236, 239, 0.2)',
        }}
      >
        <div className="flex h-16 items-center gap-4 px-4">
          {/* Logo Section */}
          <div className="flex min-w-fit items-center space-x-2">
            <Link href="/" className="flex items-center space-x-1">
              <div className="flex items-center space-x-1">
                <span className="text-xl font-bold" style={{ color: '#F0EAD6' }}>
                  rule
                </span>
                <span className="text-xl font-bold" style={{ color: '#FFD700' }}>
                  IQ
                </span>
              </div>
            </Link>
          </div>

          {/* Search Bar */}
          <div className="max-w-md flex-1">
            <div className="relative">
              <Search
                className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2"
                style={{ color: '#6C757D' }}
              />
              <Input
                type="search"
                placeholder="Search compliance data, policies, reports..."
                className="w-full border-0 py-2 pl-10 pr-4 text-sm focus-visible:ring-1 focus-visible:ring-offset-0"
                style={{
                  backgroundColor: 'rgba(240, 234, 214, 0.1)',
                  color: '#F0EAD6',
                  borderColor: 'rgba(233, 236, 239, 0.2)',
                }}
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
              />
            </div>
          </div>

          {/* Countdown Clock */}
          <div
            className="hidden items-center space-x-2 rounded-lg px-3 py-1 lg:flex"
            style={{ backgroundColor: 'rgba(240, 234, 214, 0.1)' }}
          >
            <Clock className="h-4 w-4" style={{ color: '#FFD700' }} />
            <div
              className="flex items-center space-x-1 font-mono text-sm"
              style={{ color: '#F0EAD6' }}
            >
              <span className="text-xs" style={{ color: '#6C757D' }}>
                Next Audit:
              </span>
              <span className="font-semibold">{formatTime(timeUntilAudit.days)}d</span>
              <span style={{ color: '#6C757D' }}>:</span>
              <span className="font-semibold">{formatTime(timeUntilAudit.hours)}h</span>
              <span style={{ color: '#6C757D' }}>:</span>
              <span className="font-semibold">{formatTime(timeUntilAudit.minutes)}m</span>
              <span style={{ color: '#6C757D' }}>:</span>
              <span className="font-semibold">{formatTime(timeUntilAudit.seconds)}s</span>
            </div>
          </div>

          {/* Mobile Countdown (Compact) */}
          <div className="flex items-center space-x-1 lg:hidden">
            <Tooltip>
              <TooltipTrigger asChild>
                <div
                  className="flex items-center space-x-1 font-mono text-xs"
                  style={{ color: '#F0EAD6' }}
                >
                  <Clock className="h-3 w-3" style={{ color: '#FFD700' }} />
                  <span>
                    {timeUntilAudit.days}d {formatTime(timeUntilAudit.hours)}h
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>
                  Next audit in {timeUntilAudit.days} days, {timeUntilAudit.hours} hours,{' '}
                  {timeUntilAudit.minutes} minutes
                </p>
              </TooltipContent>
            </Tooltip>
          </div>

          {/* Theme Toggle */}
          <div className="flex items-center space-x-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex items-center space-x-2">
                  <Sun className="h-4 w-4" style={{ color: isDarkMode ? '#6C757D' : '#FFD700' }} />
                  <Switch
                    checked={isDarkMode}
                    onCheckedChange={handleThemeToggle}
                    className="data-[state=checked]:bg-oxford-blue data-[state=unchecked]:bg-grey-300"
                  />
                  <Moon className="h-4 w-4" style={{ color: isDarkMode ? '#F0EAD6' : '#6C757D' }} />
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>Toggle {isDarkMode ? 'light' : 'dark'} mode</p>
              </TooltipContent>
            </Tooltip>
          </div>

          {/* Alerts Indicator */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="relative hover:bg-white/10"
                style={{ color: '#F0EAD6' }}
              >
                <Bell className="h-5 w-5" />
                <Badge
                  className="absolute -right-1 -top-1 flex h-5 w-5 animate-pulse items-center justify-center rounded-full p-0 text-xs"
                  style={{
                    backgroundColor: '#FF6F61',
                    color: '#FFFFFF',
                  }}
                >
                  5
                </Badge>
                <span className="sr-only">View alerts (5 new)</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="w-96"
              style={{
                backgroundColor: '#F0EAD6',
                borderColor: 'rgba(233, 236, 239, 0.2)',
              }}
            >
              <DropdownMenuLabel
                className="flex items-center justify-between"
                style={{ color: '#002147' }}
              >
                <span>Alerts & Notifications</span>
                <Badge variant="secondary" className="text-xs">
                  5 new
                </Badge>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <div className="max-h-80 overflow-y-auto">
                <div className="space-y-1">
                  <div className="hover:bg-grey-300/20 rounded-sm p-3">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="mt-0.5 h-4 w-4" style={{ color: '#FFC107' }} />
                      <div className="flex-1 space-y-1">
                        <div className="text-sm font-medium" style={{ color: '#002147' }}>
                          GDPR Assessment Overdue
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          The quarterly GDPR assessment was due 2 days ago. Please complete
                          immediately.
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          2 hours ago
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="hover:bg-grey-300/20 rounded-sm p-3">
                    <div className="flex items-start space-x-3">
                      <Bell className="mt-0.5 h-4 w-4" style={{ color: '#28A745' }} />
                      <div className="flex-1 space-y-1">
                        <div className="text-sm font-medium" style={{ color: '#002147' }}>
                          Compliance Score Improved
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          Your overall compliance score has increased to 98% (+2.5% from last
                          month).
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          4 hours ago
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="hover:bg-grey-300/20 rounded-sm p-3">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="mt-0.5 h-4 w-4" style={{ color: '#DC3545' }} />
                      <div className="flex-1 space-y-1">
                        <div className="text-sm font-medium" style={{ color: '#002147' }}>
                          Critical Policy Update Required
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          New financial regulations require immediate policy updates. Review
                          required by March 20.
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          6 hours ago
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="hover:bg-grey-300/20 rounded-sm p-3">
                    <div className="flex items-start space-x-3">
                      <Bell className="mt-0.5 h-4 w-4" style={{ color: '#002147' }} />
                      <div className="flex-1 space-y-1">
                        <div className="text-sm font-medium" style={{ color: '#002147' }}>
                          Monthly Report Generated
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          Your February compliance report is ready for review and download.
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          1 day ago
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="hover:bg-grey-300/20 rounded-sm p-3">
                    <div className="flex items-start space-x-3">
                      <Bell className="mt-0.5 h-4 w-4" style={{ color: '#002147' }} />
                      <div className="flex-1 space-y-1">
                        <div className="text-sm font-medium" style={{ color: '#002147' }}>
                          Team Member Added
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          Sarah Johnson has been added to your compliance team as a Risk Analyst.
                        </div>
                        <div className="text-xs" style={{ color: '#6C757D' }}>
                          2 days ago
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <DropdownMenuSeparator />
              <div className="p-2">
                <Button variant="ghost" className="w-full text-sm" style={{ color: '#002147' }}>
                  View All Alerts
                </Button>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Profile Section */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-8 w-8 rounded-full hover:bg-white/10"
                style={{
                  backgroundColor: 'rgba(255, 215, 0, 0.2)',
                }}
              >
                <User className="h-4 w-4" style={{ color: '#FFD700' }} />
                <span className="sr-only">Open user menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className="w-64"
              align="end"
              forceMount
              style={{
                backgroundColor: '#F0EAD6',
                borderColor: 'rgba(233, 236, 239, 0.2)',
              }}
            >
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-2">
                  <div className="flex items-center space-x-3">
                    <div
                      className="flex h-10 w-10 items-center justify-center rounded-full"
                      style={{ backgroundColor: 'rgba(255, 215, 0, 0.2)' }}
                    >
                      <User className="h-5 w-5" style={{ color: '#FFD700' }} />
                    </div>
                    <div className="flex flex-col">
                      <p className="text-sm font-medium leading-none" style={{ color: '#002147' }}>
                        John Doe
                      </p>
                      <p className="mt-1 text-xs leading-none" style={{ color: '#6C757D' }}>
                        Compliance Manager
                      </p>
                    </div>
                  </div>
                  <div className="text-xs" style={{ color: '#6C757D' }}>
                    john.doe@company.com
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span style={{ color: '#6C757D' }}>Last login:</span>
                    <span style={{ color: '#002147' }}>Today, 9:15 AM</span>
                  </div>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem style={{ color: '#002147' }}>
                <User className="mr-2 h-4 w-4" />
                <span>View Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem style={{ color: '#002147' }}>
                <Settings className="mr-2 h-4 w-4" />
                <span>Account Settings</span>
              </DropdownMenuItem>
              <DropdownMenuItem style={{ color: '#002147' }}>
                <Bell className="mr-2 h-4 w-4" />
                <span>Notification Preferences</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem style={{ color: '#DC3545' }}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Sign Out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
    </TooltipProvider>
  );
}
