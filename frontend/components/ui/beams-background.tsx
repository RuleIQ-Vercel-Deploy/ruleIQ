'use client';

import { motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

import { cn } from '@/lib/utils';

import type React from 'react';

export interface BeamsBackgroundProps {
  className?: string;
  intensity?: 'strong' | 'medium' | 'light';
}

export const BeamsBackground: React.FC<BeamsBackgroundProps> = ({
  className,
  intensity = 'light',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  const intensityMap = {
    strong: 40,
    medium: 20,
    light: 10,
  };
  const numBeams = intensityMap[intensity];

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);

    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={cn('absolute left-0 top-0 h-full w-full overflow-hidden', className)}
    >
      {Array.from({ length: numBeams }).map((_, i) => (
        <motion.div
          key={`beam-${i}`}
          initial={{
            y: Math.random() * dimensions.height - dimensions.height / 2,
            x: Math.random() * dimensions.width - dimensions.width / 2,
            rotate: Math.random() * 360,
            scale: Math.random() * 0.5 + 0.5,
          }}
          animate={{
            x: [
              Math.random() * dimensions.width - dimensions.width / 2,
              Math.random() * dimensions.width - dimensions.width / 2,
            ],
            y: [
              Math.random() * dimensions.height - dimensions.height / 2,
              Math.random() * dimensions.height - dimensions.height / 2,
            ],
            rotate: [Math.random() * 360, Math.random() * 360],
            scale: [Math.random() * 0.5 + 0.5, Math.random() * 0.5 + 0.5],
          }}
          transition={{
            duration: Math.random() * 20 + 10,
            repeat: Number.POSITIVE_INFINITY,
            repeatType: 'reverse',
            ease: 'easeInOut',
          }}
          style={{
            position: 'absolute',
            width: '2px',
            height: '300px',
            backgroundColor: 'rgba(255, 215, 0, 0.1)',
            boxShadow: '0 0 10px rgba(255, 215, 0, 0.2)',
          }}
        />
      ))}
    </div>
  );
};
