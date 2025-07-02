"use client"

interface GapAnalysisChartProps {
  data: { name: string; score: number }[]
}

export function GapAnalysisChart({ data }: GapAnalysisChartProps) {
  const getBarColor = (score: number) => {
    if (score >= 90) return "bg-success"
    if (score >= 70) return "bg-warning"
    return "bg-error"
  }

  return (
    <div className="space-y-4">
      {data.map((item) => (
        <div key={item.name} className="grid grid-cols-12 items-center gap-4">
          <div className="col-span-3">
            <p className="text-sm font-medium truncate">{item.name}</p>
          </div>
          <div className="col-span-9">
            <div className="flex items-center gap-4">
              <div className="flex-1 h-4 rounded-full bg-muted/20">
                <div
                  className={`h-4 rounded-full transition-all duration-500 ease-out ${getBarColor(item.score)}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>
              <div className="w-12 text-right">
                <span className="text-sm font-semibold">{item.score}%</span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
