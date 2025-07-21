'use client';

interface ComplianceScoreGaugeProps {
  score: number;
  className?: string;
}

export function ComplianceScoreGauge({ score, className = '' }: ComplianceScoreGaugeProps) {
  const radius = 80;
  const strokeWidth = 16;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getScoreColor = (s: number) => {
    if (s >= 90) return 'hsl(var(--success))'; // success
    if (s >= 70) return 'hsl(var(--warning))'; // warning
    return 'hsl(var(--destructive))'; // error
  };

  const color = getScoreColor(score);

  return (
    <div
      className={`relative flex items-center justify-center ${className}`}
      style={{ width: 200, height: 200 }}
    >
      <svg className="absolute inset-0" width="200" height="200" viewBox="0 0 200 200">
        {/* Background Circle */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          strokeWidth={strokeWidth}
          className="stroke-current text-muted-foreground/20"
          fill="transparent"
        />
        {/* Progress Arc */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          strokeWidth={strokeWidth}
          stroke={color}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 100 100)"
          className="transition-all duration-700 ease-in-out"
        />
      </svg>
      <div className="text-center">
        <span className="text-5xl font-bold">
          {score}
          <span className="text-3xl text-muted-foreground">%</span>
        </span>
        <p className="text-sm font-medium text-muted-foreground">Compliance Score</p>
      </div>
    </div>
  );
}
