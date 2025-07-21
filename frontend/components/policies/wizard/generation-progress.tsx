'use client';

import { Loader2 } from 'lucide-react';
import * as React from 'react';

export function GenerationProgress() {
  const [progress, setProgress] = React.useState(0);
  const [estimatedTime, setEstimatedTime] = React.useState(45);

  React.useEffect(() => {
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 1;
      });
    }, 400);

    const timeInterval = setInterval(() => {
      setEstimatedTime((prev) => {
        if (prev <= 0) {
          clearInterval(timeInterval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      clearInterval(progressInterval);
      clearInterval(timeInterval);
    };
  }, []);

  return (
    <div className="bg-oxford-blue-light flex h-full flex-col items-center justify-center space-y-6 rounded-lg border border-white/10 p-8 text-center">
      <div className="relative">
        <svg className="h-32 w-32 -rotate-90 transform">
          <circle
            className="text-gray-700"
            strokeWidth="8"
            stroke="currentColor"
            fill="transparent"
            r="58"
            cx="64"
            cy="64"
          />
          <circle
            className="text-gold"
            strokeWidth="8"
            strokeDasharray={2 * Math.PI * 58}
            strokeDashoffset={2 * Math.PI * 58 - (progress / 100) * (2 * Math.PI * 58)}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r="58"
            cx="64"
            cy="64"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <Loader2 className="h-12 w-12 animate-spin text-gold" />
        </div>
      </div>
      <h2 className="text-eggshell-white text-2xl font-bold">AI is generating your policy...</h2>
      <p className="text-grey-600">This may take a moment. Please don't close this window.</p>
      <div className="h-2.5 w-full rounded-full bg-gray-700">
        <div className="h-2.5 rounded-full bg-gold" style={{ width: `${progress}%` }}></div>
      </div>
      <p className="text-grey-600 text-sm">
        Estimated time remaining:{' '}
        <span className="text-eggshell-white font-semibold">{estimatedTime} seconds</span>
      </p>
    </div>
  );
}
