'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

type InfiniteSliderProps = {
  items: Array<{
    quote: string;
    name: string;
    title: string;
    img?: string;
  }>;
  direction?: 'left' | 'right';
  speed?: 'slow' | 'normal' | 'fast';
  className?: string;
};

export function InfiniteSlider({
  items,
  direction = 'left',
  speed = 'normal',
  className,
}: InfiniteSliderProps) {
  const speedMap = {
    slow: 40,
    normal: 20,
    fast: 10,
  };

  const duplicatedItems = [...items, ...items];

  return (
    <div className={cn('flex overflow-hidden', className)}>
      <motion.div
        className="flex gap-4"
        animate={{
          x: direction === 'left' ? '-50%' : '50%',
        }}
        transition={{
          duration: speedMap[speed],
          repeat: Infinity,
          ease: 'linear',
        }}
      >
        {duplicatedItems.map((item, index) => (
          <div key={index} className="w-64 flex-shrink-0 rounded-lg border bg-card p-4">
            <p className="mb-2 text-sm text-muted-foreground">"{item.quote}"</p>
            <div className="flex items-center gap-2">
              {item.img && <img src={item.img} alt={item.name} className="h-8 w-8 rounded-full" />}
              <div>
                <p className="text-sm font-medium">{item.name}</p>
                <p className="text-xs text-muted-foreground">{item.title}</p>
              </div>
            </div>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
