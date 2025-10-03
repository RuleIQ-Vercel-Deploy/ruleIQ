'use client';

import { useEffect, useRef } from 'react';

interface RadarChartProps {
  data: {
    section: string;
    score: number;
    maxScore: number;
  }[];
  size?: number;
}

export function RadarChart({ data, size = 300 }: RadarChartProps) {
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
    const radius = size / 2 - 50;
    const angleStep = (2 * Math.PI) / data.length;

    // Draw grid circles
    for (let i = 1; i <= 5; i++) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, (radius / 5) * i, 0, 2 * Math.PI);
      ctx.strokeStyle = '#8b5cf65E3';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Draw axis lines
    data.forEach((_, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.strokeStyle = '#8b5cf65E3';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Draw data polygon
    ctx.beginPath();
    data.forEach((item, index) => {
      const percentage = item.score / item.maxScore;
      const angle = index * angleStep - Math.PI / 2;
      const x = centerX + Math.cos(angle) * radius * percentage;
      const y = centerY + Math.sin(angle) * radius * percentage;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.closePath();

    // Fill with gradient
    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius);
    gradient.addColorStop(0, 'rgba(203, 150, 62, 0.3)');
    gradient.addColorStop(1, 'rgba(203, 150, 62, 0.1)');
    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.strokeStyle = '#8b5cf6BFA';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw data points
    data.forEach((item, index) => {
      const percentage = item.score / item.maxScore;
      const angle = index * angleStep - Math.PI / 2;
      const x = centerX + Math.cos(angle) * radius * percentage;
      const y = centerY + Math.sin(angle) * radius * percentage;

      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fillStyle = '#8b5cf6BFA';
      ctx.fill();
      ctx.strokeStyle = '#8b5cf655A';
      ctx.lineWidth = 2;
      ctx.stroke();
    });

    // Draw labels
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#8b5cf655A';

    data.forEach((item, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const labelRadius = radius + 30;
      const x = centerX + Math.cos(angle) * labelRadius;
      const y = centerY + Math.sin(angle) * labelRadius;

      // Adjust text alignment based on position
      if (Math.abs(x - centerX) < 10) {
        ctx.textAlign = 'center';
      } else if (x > centerX) {
        ctx.textAlign = 'left';
      } else {
        ctx.textAlign = 'right';
      }

      // Split long labels
      const words = item.section.split(' ');
      if (words.length > 2) {
        const mid = Math.ceil(words.length / 2);
        const line1 = words.slice(0, mid).join(' ');
        const line2 = words.slice(mid).join(' ');
        ctx.fillText(line1, x, y - 6);
        ctx.fillText(line2, x, y + 6);
      } else {
        ctx.fillText(item.section, x, y);
      }
    });
  }, [data, size]);

  return <canvas ref={canvasRef} width={size} height={size} className="h-auto max-w-full" />;
}
