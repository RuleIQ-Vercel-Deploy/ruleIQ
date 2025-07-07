/// <reference types="vitest" />
import path from 'path'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    css: true,
    env: {
      NEXT_PUBLIC_API_URL: 'http://localhost:8000/api',
      NEXT_PUBLIC_WEBSOCKET_URL: 'ws://localhost:8000/api/chat/ws',
      NEXT_PUBLIC_AUTH_DOMAIN: 'localhost',
      NEXT_PUBLIC_JWT_EXPIRES_IN: '86400',
      NEXT_PUBLIC_ENABLE_ANALYTICS: 'false',
      NEXT_PUBLIC_ENABLE_SENTRY: 'false',
      NEXT_PUBLIC_ENABLE_MOCK_DATA: 'true',
      NEXT_PUBLIC_ENV: 'test',
      NODE_ENV: 'test',
      SKIP_ENV_VALIDATION: 'true'
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/coverage/**',
        '**/dist/**',
        '**/.next/**',
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70,
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
})
