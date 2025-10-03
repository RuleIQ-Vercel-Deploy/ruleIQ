'use client';

import React from 'react';
import Particles from '@tsparticles/react';

// PARTICLE SWARM DATA VISUALIZATION
export const ParticleSwarmChart = () => {

  return (
    <div className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 border border-purple-800/20 h-[400px] overflow-hidden">
      <h3 className="text-xl font-semibold text-white mb-4 z-10 relative">Neural Network Activity</h3>
      <Particles
        className="absolute inset-0"
        id="tsparticles"
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
            },
            modes: {
              grab: {
                distance: 140,
                links: {
                  opacity: 0.5,
                  color: 'var(--silver-400)',
                },
              },
            },
          },
          particles: {
            color: {
              value: ['var(--purple-500)', 'var(--purple-500)', 'var(--purple-400)', 'var(--silver-400)'],
            },
            links: {
              color: 'var(--purple-500)',
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
            },
            shape: {
              type: 'circle',
            },
            size: {
              value: { min: 1, max: 5 },
            },
          },
          detectRetina: true,
        }}
      />
    </div>
  );
};