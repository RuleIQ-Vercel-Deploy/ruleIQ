'use client';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

import { cn } from '@/lib/utils';

export const SparklesCore = (props: {
  id?: string;
  className?: string;
  background?: string;
  particleSize?: number;
  minSize?: number;
  maxSize?: number;
  particleColor?: string;
  particleDensity?: number;
  speed?: number;
}) => {
  const {
    id: _id = 'tsparticles',
    className,
    background: _background = 'transparent',
    particleSize: _particleSize = 1,
    minSize = 0.4,
    maxSize = 1,
    particleColor = '#FFD700',
    particleDensity = 1200,
    speed: _speed = 1,
  } = props;

  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // This component relies on a library that might not be available in SSR.
    // We simulate its loading here.
    setIsLoaded(true);
  }, []);

  if (!isLoaded) return null;

  // In a real scenario, you would initialize the particles library here.
  // For this example, we'll use a simplified motion-based sparkle effect.

  return (
    <div className={cn('absolute inset-0 h-full w-full', className)}>
      {Array.from({ length: particleDensity / 20 }).map((_, i) => (
        <motion.div
          key={`sparkle-${i}`}
          style={{
            position: 'absolute',
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: `${Math.random() * (maxSize - minSize) + minSize}px`,
            height: `${Math.random() * (maxSize - minSize) + minSize}px`,
            backgroundColor: particleColor,
            borderRadius: '50%',
          }}
          animate={{
            opacity: [0, 1, 0],
            scale: [1, 1.2, 1],
            x: Math.random() * 20 - 10,
            y: Math.random() * 20 - 10,
          }}
          transition={{
            duration: Math.random() * 2 + 1,
            repeat: Number.POSITIVE_INFINITY,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
};
