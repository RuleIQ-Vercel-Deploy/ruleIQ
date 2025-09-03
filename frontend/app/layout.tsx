import { Inter, Roboto } from 'next/font/google';

import { GlobalErrorBoundary } from '@/components/error-boundary-global';
import { ThemeProvider } from '@/hooks/use-theme';
import { QueryProvider } from '@/lib/tanstack-query/provider';
import { cn } from '@/lib/utils';

import type { Metadata } from 'next';
import type React from 'react';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const roboto = Roboto({
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto',
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
    'GDPR compliance',
    'UK compliance software',
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
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'ruleIQ - Compliance Made Simple',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ruleIQ - AI-Powered Compliance Automation',
    description:
      'Streamline compliance for UK SMBs with intelligent automation and real-time monitoring.',
    creator: '@ruleiq',
    images: ['/twitter-image.png'],
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
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  generator: 'Next.js',
  applicationName: 'ruleIQ',
  referrer: 'origin-when-cross-origin',
  colorScheme: 'light',
  themeColor: '#0B4F6C',
  manifest: '/manifest.json',
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [{ url: '/apple-touch-icon.png' }],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html 
      lang="en" 
      className={cn('h-full', inter.variable, roboto.variable)} 
      suppressHydrationWarning
    >
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="h-full antialiased font-sans" suppressHydrationWarning>
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <ThemeProvider defaultTheme="light" storageKey="ruleiq-ui-theme">
          <QueryProvider>
            <GlobalErrorBoundary showErrorDetails={process.env.NODE_ENV === 'development'}>
              <main id="main-content" className="h-full">
                {children}
              </main>
            </GlobalErrorBoundary>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}