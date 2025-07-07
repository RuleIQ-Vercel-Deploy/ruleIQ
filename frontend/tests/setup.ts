import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach, beforeAll, vi } from 'vitest'
import React from 'react'

// Cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup()
})

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
  }),
  useSearchParams: () => ({
    get: vi.fn(),
  }),
  usePathname: () => '/',
}))

// Mock Next.js image
vi.mock('next/image', () => ({
  default: (props: any) => {
    const { src, alt, ...rest } = props
    return React.createElement('img', { src, alt, ...rest })
  },
}))

// Mock Framer Motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => React.createElement('div', props, children),
    span: ({ children, ...props }: any) => React.createElement('span', props, children),
    button: ({ children, ...props }: any) => React.createElement('button', props, children),
    form: ({ children, ...props }: any) => React.createElement('form', props, children),
  },
  AnimatePresence: ({ children }: any) => children,
}))

// Mock environment variables
beforeAll(() => {
  // Set up environment variables for testing
  process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api'
  process.env.NEXT_PUBLIC_WEBSOCKET_URL = 'ws://localhost:8000/api/chat/ws'
  process.env.NEXT_PUBLIC_AUTH_DOMAIN = 'localhost'
  process.env.NEXT_PUBLIC_JWT_EXPIRES_IN = '86400'
  process.env.NEXT_PUBLIC_ENABLE_ANALYTICS = 'false'
  process.env.NEXT_PUBLIC_ENABLE_SENTRY = 'false'
  process.env.NEXT_PUBLIC_ENABLE_MOCK_DATA = 'true'
  process.env.NEXT_PUBLIC_ENV = 'test'
  process.env.NODE_ENV = 'test'
  process.env.SKIP_ENV_VALIDATION = 'true'

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })

  // Mock ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }))

  // Mock IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }))
})
