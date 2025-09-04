'use client';

import { motion } from 'framer-motion';
import { useEffect, useRef } from 'react';

interface ComplianceGaugeProps {
  score: number;
  size?: number;
}

export function ComplianceGauge({ score, size = 200 }: ComplianceGaugeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, size, size);

    const centerX = size / 2;
    const centerY = size / 2;
    const radius = size / 2 - 20;
    const startAngle = Math.PI * 0.75;
    const endAngle = Math.PI * 2.25;
    const currentAngle = startAngle + (score / 100) * (endAngle - startAngle);

    // Draw background arc
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
    ctx.strokeStyle = '#D0D5E3';
    ctx.lineWidth = 20;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Draw score arc
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, startAngle, currentAngle);

    // Gradient based on score
    const gradient = ctx.createLinearGradient(0, 0, size, 0);
    if (score >= 80) {
      gradient.addColorStop(0, '#28A745');
      gradient.addColorStop(1, '#1F8C3B');
    } else if (score >= 60) {
      gradient.addColorStop(0, '#CB963E');
      gradient.addColorStop(1, '#A67A2E');
    } else {
      gradient.addColorStop(0, '#DC3545');
      gradient.addColorStop(1, '#B42D3B');
    }

    ctx.strokeStyle = gradient;
    ctx.lineWidth = 20;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Draw inner shadow
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius - 10, startAngle, currentAngle);
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.lineWidth = 2;
    ctx.stroke();
  }, [score, size]);

  return (
    <div className="relative">
      <canvas ref={canvasRef} width={size} height={size} className="-rotate-90 transform" />
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-center"
        >
          <div className="text-4xl font-bold text-primary">{score}%</div>
          <div className="text-sm text-muted-foreground">Compliance</div>
        </motion.div>
      </div>
    </div>
  );
}
