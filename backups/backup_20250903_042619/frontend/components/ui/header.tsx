import Link from 'next/link';

import { Button } from '@/components/ui/button';

export function Header() {
  return (
    <header className="bg-oxford-blue/95 supports-[backdrop-filter]:bg-oxford-blue/60 sticky top-0 z-50 w-full border-b border-border/40 backdrop-blur">
      <div className="container flex h-16 max-w-screen-2xl items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <span className="text-eggshell-white text-2xl font-bold">rule</span>
              <span className="text-2xl font-bold text-gold">IQ</span>
            </div>
          </Link>
          <nav className="hidden items-center space-x-6 text-sm font-medium md:flex">
            <Link
              href="/dashboard"
              className="text-eggshell-white transition-colors hover:text-gold"
            >
              Dashboard
            </Link>
            <Link
              href="/compliance"
              className="text-grey-600 hover:text-eggshell-white transition-colors"
            >
              Compliance
            </Link>
            <Link
              href="/reports"
              className="text-grey-600 hover:text-eggshell-white transition-colors"
            >
              Reports
            </Link>
            <Link
              href="/settings"
              className="text-grey-600 hover:text-eggshell-white transition-colors"
            >
              Settings
            </Link>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="w-full flex-1 md:w-auto md:flex-none">
            {/* Search component will go here */}
          </div>
          <nav className="flex items-center space-x-2">
            <Button variant="ghost" size="sm" className="text-eggshell-white hover:text-gold">
              Sign In
            </Button>
            <Button size="sm" className="ruleiq-button-primary">
              Get Started
            </Button>
          </nav>
        </div>
      </div>
    </header>
  );
}
