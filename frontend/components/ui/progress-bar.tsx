import { cn } from '@/lib/utils';
interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  color?: 'success' | 'warning' | 'error' | 'info' | 'gold' | string;
}

const colorMap = {
  success: '#28A745',
  warning: '#FFC107',
  error: '#DC3545',
  info: '#17A2B8',
  gold: '#FFD700',
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
