'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface HeroSpotlightProps {
  className?: string;
  size?: number;
  intensity?: number;
}

export function HeroSpotlight({ 
  className = '', 
  size = 800, 
  intensity = 0.3 
}: HeroSpotlightProps) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  if (!mounted) return null;

  return (
    <div className={`absolute inset-0 overflow-hidden ${className}`}>
      {/* Main spotlight following mouse */}
      <motion.div
        className="absolute pointer-events-none"
        style={{
          background: `radial-gradient(${size}px circle at center, rgba(44, 122, 123, ${intensity}) 0%, transparent 70%)`,
          width: size * 2,
          height: size * 2,
          left: mousePosition.x - size,
          top: mousePosition.y - size,
        }}
        animate={{
          left: mousePosition.x - size,
          top: mousePosition.y - size,
        }}
        transition={{ type: 'spring', damping: 30, stiffness: 200 }}
      />
      
      {/* Static ambient spotlights */}
      <div
        className="absolute top-1/4 left-1/4 w-96 h-96 opacity-20 pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(44, 122, 123, 0.2) 0%, transparent 70%)',
        }}
      />
      <div
        className="absolute bottom-1/4 right-1/4 w-80 h-80 opacity-15 pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(79, 209, 197, 0.2) 0%, transparent 70%)',
        }}
      />
    </div>
  );
}