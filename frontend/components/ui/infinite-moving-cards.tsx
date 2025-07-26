'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface MovingCardItem {
  quote: string;
  name: string;
  title: string;
  img?: string;
}

interface InfiniteMovingCardsProps {
  items: MovingCardItem[];
  direction?: 'left' | 'right';
  speed?: 'fast' | 'normal' | 'slow';
  pauseOnHover?: boolean;
  className?: string;
}

export const InfiniteMovingCards = ({
  items,
  direction = 'left',
  speed = 'normal',
  pauseOnHover = true,
  className,
}: InfiniteMovingCardsProps) => {
  const [duplicatedItems, setDuplicatedItems] = useState(items);

  useEffect(() => {
    setDuplicatedItems([...items, ...items]);
  }, [items]);

  const speedClass = {
    fast: 'animate-scroll-fast',
    normal: 'animate-scroll',
    slow: 'animate-scroll-slow',
  }[speed];

  return (
    <div className={cn('overflow-hidden', className)}>
      <div
        className={cn(
          'flex w-max gap-4',
          speedClass,
          direction === 'right' && 'animate-reverse',
          pauseOnHover && 'hover:pause'
        )}
      >
        {duplicatedItems.map((item, idx) => (
          <div
            key={idx}
            className="w-80 flex-shrink-0 rounded-lg border bg-card p-6"
          >
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">"{item.quote}"</p>
              <div className="flex items-center gap-3">
                {item.img && (
                  <img
                    src={item.img}
                    alt={item.name}
                    className="h-10 w-10 rounded-full object-cover"
                  />
                )}
                <div>
                  <p className="font-semibold">{item.name}</p>
                  <p className="text-xs text-muted-foreground">{item.title}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
