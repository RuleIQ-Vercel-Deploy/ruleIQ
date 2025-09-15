// app/layout.tsx - Updated Font Configuration for Neural Purple Theme
import { Inter } from 'next/font/google';

import { GlobalErrorBoundary } from '@/components/error-boundary-global';
import { ThemeProvider } from '@/hooks/use-theme';
import { QueryProvider } from '@/lib/tanstack-query/provider';
import { cn } from '@/lib/utils';

import type { Metadata } from 'next';
import type React from 'react';
import './globals.css';

// Configure Inter with specific weights for Neural Purple theme
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  weight: ['200', '300', '400', '500'], // ExtraLight, Light, Regular, Medium
});

export const metadata: Metadata = {
  title: {
    default: 'ruleIQ - AI-Powered Compliance Automation',
    template: '%s | ruleIQ',
  },
  description:
    'Streamline compliance for UK SMBs with intelligent automation, real-time monitoring, and AI-powered insights.',
  keywords: [
    'compliance automation',
    'AI compliance',
    'UK SMB',
    'regulatory technology',
    'compliance management',
    'automated compliance',
  ],
  authors: [{ name: 'ruleIQ Team' }],
  creator: 'ruleIQ',
  metadataBase: new URL('https://ruleiq.com'),
  openGraph: {
    type: 'website',
    locale: 'en_GB',
    url: 'https://ruleiq.com',
    title: 'ruleIQ - AI-Powered Compliance Automation',
    description:
      'Streamline compliance for UK SMBs with intelligent automation and real-time monitoring.',
    siteName: 'ruleIQ',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ruleIQ - AI-Powered Compliance Automation',
    description:
      'Streamline compliance for UK SMBs with intelligent automation and real-time monitoring.',
    creator: '@ruleiq',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={cn('h-full', inter.variable)} suppressHydrationWarning>
      <body className="dark h-full antialiased bg-black font-sans" suppressHydrationWarning>
        <ThemeProvider defaultTheme="dark" storageKey="ruleiq-ui-theme">
          <QueryProvider>
            <GlobalErrorBoundary showErrorDetails={process.env.NODE_ENV === 'development'}>
              {children}
            </GlobalErrorBoundary>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
