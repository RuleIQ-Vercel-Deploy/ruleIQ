'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

// LIQUID DATA VISUALIZATION - Data as flowing liquid
export const LiquidDataVisualization = ({ data = [] }: { data?: number[] }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [particles, setParticles] = useState<any[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Create liquid particles
    const liquidParticles: any[] = [];
    const particleCount = 500;
    
    for (let i = 0; i < particleCount; i++) {
      liquidParticles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        radius: Math.random() * 3 + 1,
        color: `hsla(${263 + Math.random() * 30}, 72%, ${50 + Math.random() * 20}%, ${0.3 + Math.random() * 0.5})`,
        life: Math.random(),
      });
    }