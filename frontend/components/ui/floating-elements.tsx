'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Shield, FileText, BrainCircuit, CheckCircle, BarChart } from 'lucide-react';

interface FloatingElementsProps {
  className?: string;
  density?: number;
}

export function FloatingElements({ className = '', density = 15 }: FloatingElementsProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const icons = [Shield, FileText, BrainCircuit, CheckCircle, BarChart];
  const elements = Array.from({ length: density }, (_, i) => ({
    id: i,
    Icon: icons[i % icons.length],
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 20 + 16,
    duration: Math.random() * 10 + 15,
    delay: Math.random() * 5,
  }));

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      {elements.map((element) => (
        <motion.div
          key={element.id}
          className="absolute text-teal-600/20"
          style={{
            left: `${element.x}%`,
            top: `${element.y}%`,
            fontSize: `${element.size}px`,
          }}
          animate={{
            y: [0, -50, 0],
            rotate: [0, 180, 360],
            opacity: [0.1, 0.3, 0.1],
          }}
          transition={{
            duration: element.duration,
            delay: element.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          {element.Icon && <element.Icon size={element.size} />}
        </motion.div>
      ))}
    </div>
  );
}