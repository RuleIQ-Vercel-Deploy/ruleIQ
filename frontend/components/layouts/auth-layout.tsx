import Link from 'next/link';

import { TrustBadges } from '@/components/ui/trust-badges';

import type * as React from 'react';

interface AuthLayoutProps {
  children: React.ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div
      className="flex min-h-screen w-full flex-col items-center justify-center bg-gradient-to-br from-purple-50 to-white p-4 sm:p-6 md:p-8"
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fillRule='evenodd'%3E%3Cg fill='%238B5CF6' fillOpacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      }}
    >
      <main className="flex w-full flex-1 flex-col items-center justify-center">
        {/* Logo Header */}
        <div className="mb-8">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-3xl font-bold" style={{ color: '#F0EAD6' }}>
              rule
            </span>
            <span className="text-3xl font-bold" style={{ color: '#FFD700' }}>
              IQ
            </span>
          </Link>
        </div>

        {/* Centered Card */}
        <div className="bg-oxford-blue/30 text-eggshell-white w-full max-w-md rounded-2xl border border-gold/20 p-8 shadow-2xl backdrop-blur-xl">
          {children}
        </div>
      </main>

      {/* Trust Badges Footer */}
      <footer className="mt-8 w-full max-w-md">
        <TrustBadges />
      </footer>
    </div>
  );
}
