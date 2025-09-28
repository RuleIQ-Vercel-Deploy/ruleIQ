import { Metadata } from 'next';

export async function generateMetadata({ params }: { params: { token: string } }): Promise<Metadata> {
  // For freemium assessments, we can't fetch dynamic data server-side without an API endpoint
  // Use minimal, stable metadata
  return {
    title: 'Compliance Assessment Results | ruleIQ',
    description: 'View your comprehensive AI-powered compliance assessment results with detailed insights and recommendations to improve your compliance posture.',
    openGraph: {
      title: 'Compliance Assessment Results | ruleIQ',
      description: 'Get detailed insights and recommendations from your compliance assessment.',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: 'Compliance Assessment Results',
      description: 'Detailed compliance assessment results with actionable recommendations.',
    }
  };
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}