'use client';

import React, { useCallback } from 'react';
import Particles from '@tsparticles/react';
import { loadSlim } from 'tsparticles-slim';
import type { Container, Engine } from '@tsparticles/engine';

// PARTICLE SWARM DATA VISUALIZATION
export const ParticleSwarmChart = () => {
  const particlesInit = useCallback(async (engine: Engine) => {
    await loadSlim(engine);
  }, []);

  const particlesLoaded = useCallback(async (container: Container | undefined) => {
    console.log('Particles loaded', container);
  }, []);

  return (
    <div className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20 h-[400px] overflow-hidden">
      <h3 className="text-xl font-semibold text-white mb-4 z-10 relative">Neural Network Activity</h3>
      <Particles
        className="absolute inset-0"
        id="tsparticles"
        init={particlesInit}
        loaded={particlesLoaded}
        options={{
          background: {
            color: {
              value: 'transparent',
            },
          },
          fpsLimit: 120,
          interactivity: {
            events: {
              onHover: {
                enable: true,
                mode: 'grab',
              },
              resize: {
                enable: true,
              },
            },            modes: {
              grab: {
                distance: 140,
                links: {
                  opacity: 0.5,
                  color: '#C0C0C0',
                },
              },
            },
          },
          particles: {
            color: {
              value: ['#8B5CF6', '#A855F7', '#C084FC', '#C0C0C0'],
            },
            links: {
              color: '#8B5CF6',
              distance: 150,
              enable: true,
              opacity: 0.3,
              width: 1,
            },
            move: {
              direction: 'none',
              enable: true,
              outModes: {
                default: 'bounce',
              },
              random: true,
              speed: 2,
              straight: false,
            },
            number: {
              density: {
                enable: true,
                height: 800,
                width: 800,
              },
              value: 80,
            },
            opacity: {
              value: 0.8,
              animation: {
                enable: true,
                speed: 1,
                minimumValue: 0.3,
                sync: false,
              },
            },
            shape: {
              type: 'circle',
            },
            size: {
              value: { min: 1, max: 5 },
              animation: {
                enable: true,
                speed: 3,
                minimumValue: 1,
                sync: false,
              },
            },
          },
          detectRetina: true,
        }}
      />
    </div>
  );
};