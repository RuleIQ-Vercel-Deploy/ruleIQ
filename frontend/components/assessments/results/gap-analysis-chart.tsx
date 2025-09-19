'use client';

interface GapAnalysisChartProps {
  data: { name: string; score: number }[];
}

export function GapAnalysisChart({ data }: GapAnalysisChartProps) {
  const getBarColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-4">
      {data.map((item) => (
        <div key={item.name} className="grid grid-cols-12 items-center gap-4">
          <div className="col-span-3">
            <p className="truncate text-sm font-medium">{item.name}</p>
          </div>
          <div className="col-span-9">
            <div className="flex items-center gap-4">
              <div className="h-4 flex-1 rounded-full bg-muted/20">
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
  );
}
