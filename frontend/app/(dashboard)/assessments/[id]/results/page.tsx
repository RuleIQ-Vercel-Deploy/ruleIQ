import { Download, FileText, BarChart2, Lightbulb } from "lucide-react"

import { ComplianceScoreGauge } from "@/components/assessments/results/compliance-score-gauge"
import { GapAnalysisChart } from "@/components/assessments/results/gap-analysis-chart"
import { RecommendationsList } from "@/components/assessments/results/recommendations-list"
import { RequirementCard } from "@/components/assessments/results/requirement-card"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { assessmentResults } from "@/lib/data/results"


export default function AssessmentResultsPage({ params }: { params: { id: string } }) {
  const { title, overallScore, summary, requirements, gapAnalysis, recommendations } = assessmentResults

  return (
    <div
      className="min-h-screen w-full p-6 sm:p-8"
      style={{
        backgroundColor: "#002147",
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fillRule='evenodd'%3E%3Cg fill='%23F0EAD6' fillOpacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      }}
    >
      <main className="max-w-screen-xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-eggshell-white">{title} - Results</h1>
            <p className="text-lg text-grey-600 mt-1">Assessment ID: {params.id}</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary">
              <Download className="mr-2 h-4 w-4" />
              Export PDF
            </Button>
            <Button variant="default">
              <Download className="mr-2 h-4 w-4" />
              Export Excel
            </Button>
          </div>
        </div>

        {/* Overall Score and Summary */}
        <Card className="ruleiq-card border-gold/20 bg-oxford-blue/30 backdrop-blur-sm">
          <CardContent className="p-6 flex flex-col md:flex-row items-center gap-8">
            <ComplianceScoreGauge score={overallScore} />
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-eggshell-white">Overall Assessment Summary</h2>
              <p className="mt-2 text-base text-eggshell-white/80">{summary}</p>
            </div>
          </CardContent>
        </Card>

        {/* Framework Requirements Grid */}
        <div>
          <h2 className="text-2xl font-bold text-eggshell-white mb-4 flex items-center gap-3">
            <FileText />
            Framework Requirements
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {requirements.map((req) => (
              <RequirementCard
                key={req.id}
                title={req.title}
                score={req.score}
                status={req.status as any}
                icon={req.icon}
                color={req.color}
              />
            ))}
          </div>
        </div>

        {/* Gap Analysis */}
        <Card className="ruleiq-card border-gold/20 bg-oxford-blue/30 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl text-eggshell-white flex items-center gap-3">
              <BarChart2 />
              Gap Analysis
            </CardTitle>
            <CardDescription className="text-grey-600">
              Comparison of scores across different compliance areas.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <GapAnalysisChart data={gapAnalysis} />
          </CardContent>
        </Card>

        {/* Recommendations */}
        <Card className="ruleiq-card border-gold/20 bg-oxford-blue/30 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl text-eggshell-white flex items-center gap-3">
              <Lightbulb />
              Actionable Recommendations
            </CardTitle>
            <CardDescription className="text-grey-600">
              Prioritized steps to improve your compliance score.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RecommendationsList recommendations={recommendations} />
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
