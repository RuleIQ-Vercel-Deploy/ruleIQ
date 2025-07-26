'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface TextGenerateEffectProps {
  words: string;
  className?: string;
  filter?: boolean;
  duration?: number;
}

export const TextGenerateEffect = ({
  words,
  className,
  filter = true,
  duration = 1000,
}: TextGenerateEffectProps) => {
  const [scope, setScope] = useState<string[]>([]);
  const wordsArray = words.split(' ');

  useEffect(() => {
    const timer = setTimeout(() => {
      setScope(wordsArray);
    }, 100);

    return () => clearTimeout(timer);
  }, [wordsArray]);

  const renderWords = () => {
    return (
      <span>
        {wordsArray.map((word, idx) => {
          return (
            <span
              key={word + idx}
              className={cn(
                'opacity-0 animate-in fade-in-0 slide-in-from-bottom-2',
                scope.includes(word) && 'opacity-100',
                filter && 'blur-sm',
                scope.includes(word) && filter && 'blur-none'
              )}
              style={{
                animationDelay: `${idx * 0.1}s`,
                animationDuration: `${duration / 1000}s`,
                animationFillMode: 'forwards',
              }}
            >
              {word}{' '}
            </span>
          );
        })}
      </span>
    );
  };

  return (
    <div className={cn('font-bold', className)}>
      <div className="mt-4">
        <div className="text-foreground leading-snug tracking-wide">
          {renderWords()}
        </div>
      </div>
    </div>
  );
};
