/// <reference types="vitest" />
import path from 'path';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    css: true,
    testTimeout: 30000, // 30 seconds per test
    hookTimeout: 30000, // 30 seconds for hooks
    pool: 'forks', // Use forks instead of threads for better isolation
    poolOptions: {
      forks: {
        singleFork: true, // Run tests sequentially in a single fork
        isolate: true, // Isolate each test file
      },
    },
    maxConcurrency: 1, // Run tests one at a time
    isolate: true, // Isolate tests to prevent memory leaks,
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**',
      '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build,playwright}.config.*',
      '**/tests/e2e/**', // Exclude Playwright e2e tests
      '**/tests/visual/**', // Exclude visual regression tests
      '**/tests/performance/**', // Exclude performance tests
      '**/tests/css/**', // Exclude CSS tests that need special setup
      '**/tests/accessibility/**', // Exclude all accessibility tests (they need jest-axe or Playwright)
      '**/tests/components/ai/ai-components-memory-leak.test.tsx', // Exclude memory leak tests
      '**/tests/components/memory-leak-detection.test.tsx', // Exclude memory leak tests
      '**/tests/components/assessments/auto-save-indicator-memory-leak.test.tsx', // Exclude memory leak tests
      '**/*memory-leak*.test.tsx', // Exclude all memory leak tests
      '**/*memory-leak*.test.ts', // Exclude all memory leak tests
    ],
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
      SKIP_ENV_VALIDATION: 'true',
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
});
