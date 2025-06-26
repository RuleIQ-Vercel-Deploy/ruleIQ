import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'

export const metadata: Metadata = {
  title: 'ruleIQ - AI-Driven Compliance Automation',
  description: 'Streamline your compliance management with AI-powered automation',
  icons: {
    icon: '/favicon.png',
    shortcut: '/favicon.png',
    apple: '/ruleiq-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
