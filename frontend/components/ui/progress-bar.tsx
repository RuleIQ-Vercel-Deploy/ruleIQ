import { cn } from '@/lib/utils';
interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  color?: 'success' | 'warning' | 'error' | 'info' | 'gold' | string;
}

const colorMap = {
  success: 'var(--purple-400)', // emerald-600
  warning: 'var(--purple-600)', // amber-600
  error: 'var(--purple-500)', // red-600
  info: 'var(--purple-500)', // purple-500
  gold: 'var(--purple-600)', // amber-600 (replacing gold with warning)
};

export function ProgressBar({
  value,
  max = 100,
  className = '',
  color = 'success',
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100);
  const barColor = color in colorMap ? colorMap[color as keyof typeof colorMap] : color;

  return (
    <div className={cn('bg-oxford-blue/50 h-1.5 w-full rounded-full', className)}>
      <div
        className="h-1.5 rounded-full transition-all duration-300 ease-in-out"
        style={{
          width: `${percentage}%`,
          backgroundColor: barColor,
        }}
      />
    </div>
  );
}
