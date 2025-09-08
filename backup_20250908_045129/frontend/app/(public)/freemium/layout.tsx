import React from 'react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    template: '%s | RuleIQ Freemium Assessment',
    default: 'Free AI Compliance Assessment | RuleIQ',
  },
  description:
    'Get a personalized compliance assessment in under 5 minutes. AI-powered analysis identifies your critical compliance gaps and provides actionable recommendations.',
  keywords: [
    'compliance assessment',
    'GDPR compliance',
    'ISO 27001',
    'SOC 2',
    'free assessment',
    'AI compliance',
    'risk assessment',
    'compliance gaps',
    'data protection',
    'cybersecurity compliance',
  ],
  authors: [{ name: 'RuleIQ' }],
  creator: 'RuleIQ',
  publisher: 'RuleIQ',
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
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://ruleiq.com/freemium',
    siteName: 'RuleIQ',
    title: 'Free AI Compliance Assessment | RuleIQ',
    description:
      'Discover your compliance gaps in under 5 minutes with our AI-powered assessment tool.',
    images: [
      {
        url: '/og-freemium-assessment.png', // This would need to be created
        width: 1200,
        height: 630,
        alt: 'RuleIQ Free Compliance Assessment',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Free AI Compliance Assessment | RuleIQ',
    description:
      'Discover your compliance gaps in under 5 minutes with our AI-powered assessment tool.',
    images: ['/og-freemium-assessment.png'],
    creator: '@RuleIQApp',
  },
  alternates: {
    canonical: 'https://ruleiq.com/freemium',
  },
};

export default function FreemiumLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      {/* Structured Data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Service',
            name: 'RuleIQ Compliance Assessment',
            description:
              'AI-powered compliance assessment tool that identifies gaps and provides recommendations',
            provider: {
              '@type': 'Organization',
              name: 'RuleIQ',
              url: 'https://ruleiq.com',
            },
            serviceType: 'Compliance Assessment',
            audience: {
              '@type': 'BusinessAudience',
              audienceType: 'Small and Medium Businesses',
            },
            offers: {
              '@type': 'Offer',
              price: '0',
              priceCurrency: 'GBP',
              availability: 'https://schema.org/InStock',
              validFrom: new Date().toISOString(),
            },
            aggregateRating: {
              '@type': 'AggregateRating',
              ratingValue: '4.8',
              reviewCount: '2300',
              bestRating: '5',
              worstRating: '1',
            },
          }),
        }}
      />

      {/* Analytics and tracking scripts would go here */}

      {children}
    </>
  );
}
