import { Metadata } from 'next';
import AssessmentResultsClient from './client';
import { assessmentResultsService } from '@/lib/services/assessment-results.service';

interface PageProps {
  params: {
    token: string;
  };
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  try {
    const results = await assessmentResultsService.getResults(params.token);
    const score = Math.round(results.compliance_score);
    const riskLevel = results.risk_level;

    return {
      title: `Compliance Assessment Results - ${score}% Score | ruleIQ`,
      description: `Your compliance assessment shows a ${score}% score with ${riskLevel} risk level. Get detailed insights and recommendations to improve your compliance posture.`,
      openGraph: {
        title: `My Compliance Assessment Results - ${score}% Score`,
        description: `I scored ${score}% on my compliance assessment with ruleIQ. Check out the detailed analysis and recommendations.`,
        type: 'website',
        url: `${process.env.NEXT_PUBLIC_BASE_URL || ''}/assessment/results/${params.token}`,
      },
      twitter: {
        card: 'summary_large_image',
        title: `Compliance Assessment Results - ${score}% Score`,
        description: `Detailed compliance assessment results with ${riskLevel} risk level and actionable recommendations.`,
      }
    };
  } catch (error) {
    // Default metadata if results cannot be loaded
    return {
      title: 'Assessment Results | ruleIQ',
      description: 'View your compliance assessment results and get personalized recommendations.',
    };
  }
}

export default function AssessmentResultsPage({ params }: PageProps) {
  return <AssessmentResultsClient token={params.token} />;
}
