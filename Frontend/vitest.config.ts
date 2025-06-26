import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./test-setup.ts'],
    globals: true,
    css: true,
    include: ['**/__tests__/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'test-setup.ts',
        '**/*.d.ts',
        '**/*.config.*',
        'coverage/**',
        '.next/**',
        'out/**'
      ]
    }
  },
  resolve: {
    alias: [
      { find: '@/components', replacement: path.resolve(__dirname, './components') },
      { find: '@/lib', replacement: path.resolve(__dirname, './app/lib') },
      { find: '@/types', replacement: path.resolve(__dirname, './app/types') },
      { find: '@/api', replacement: path.resolve(__dirname, './app/api') },
      { find: '@/store', replacement: path.resolve(__dirname, './app/store') },
      { find: '@/hooks', replacement: path.resolve(__dirname, './hooks') },
      { find: '@', replacement: path.resolve(__dirname, './app') }
    ]
  }
})
