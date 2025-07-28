'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface AnimatedGridProps {
  className?: string;
  gridSize?: number;
  animationDuration?: number;
}

export function AnimatedGrid({ 
  className = '', 
  gridSize = 20, 
  animationDuration = 4 
}: AnimatedGridProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const gridItems = Array.from({ length: gridSize * gridSize }, (_, i) => i);

  return (
    <div className={`absolute inset-0 overflow-hidden ${className}`}>
      <div 
        className="grid gap-1 h-full w-full opacity-10"
        style={{ 
          gridTemplateColumns: `repeat(${gridSize}, 1fr)`,
          gridTemplateRows: `repeat(${gridSize}, 1fr)`
        }}
      >
        {gridItems.map((i) => (
          <motion.div
            key={i}
            className="bg-primary"
            initial={{ opacity: 0 }}
            animate={{ 
              opacity: [0, 0.3, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{
              duration: animationDuration,
              delay: (i % gridSize) * 0.1 + Math.floor(i / gridSize) * 0.05,
              repeat: Infinity,
              repeatType: 'loop',
              ease: 'easeInOut'
            }}
          />
        ))}
      </div>
    </div>
  );
}