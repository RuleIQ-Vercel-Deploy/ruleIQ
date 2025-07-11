import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, beforeAll, afterAll, vi } from 'vitest'
import React from 'react'

// Mock environment variables
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

// Setup MSW server for API mocking
import { server } from './mocks/server'

// Global test setup
beforeAll(() => {
  // Start MSW server
  server.listen({
    onUnhandledRequest: 'warn',
  })
  // Mock window.matchMedia (used by components with responsive behavior)
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

  // Mock window.ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }))

  // Mock window.IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }))

  // Mock window.scrollTo
  Object.defineProperty(window, 'scrollTo', {
    writable: true,
    value: vi.fn(),
  })

  // Mock crypto API for secure storage tests
  Object.defineProperty(window, 'crypto', {
    writable: true,
    value: {
      subtle: {
        generateKey: vi.fn().mockResolvedValue({}),
        encrypt: vi.fn().mockResolvedValue(new ArrayBuffer(8)),
        decrypt: vi.fn().mockResolvedValue(new ArrayBuffer(8)),
        importKey: vi.fn().mockResolvedValue({}),
        exportKey: vi.fn().mockResolvedValue(new ArrayBuffer(8)),
      },
      getRandomValues: vi.fn().mockImplementation((array) => {
        for (let i = 0; i < array.length; i++) {
          array[i] = Math.floor(Math.random() * 256)
        }
        return array
      }),
    },
  })

  // Mock localStorage with working implementation
  const localStorageStore: Record<string, string> = {}
  const localStorageMock = {
    getItem: vi.fn((key: string) => localStorageStore[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      localStorageStore[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete localStorageStore[key]
    }),
    clear: vi.fn(() => {
      Object.keys(localStorageStore).forEach(key => delete localStorageStore[key])
    }),
    get length() {
      return Object.keys(localStorageStore).length
    },
    key: vi.fn((index: number) => {
      const keys = Object.keys(localStorageStore)
      return keys[index] || null
    }),
  }
  Object.defineProperty(window, 'localStorage', {
    writable: true,
    value: localStorageMock,
  })

  // Mock sessionStorage
  const sessionStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    length: 0,
    key: vi.fn(),
  }
  Object.defineProperty(window, 'sessionStorage', {
    writable: true,
    value: sessionStorageMock,
  })

  // Mock URL.createObjectURL
  Object.defineProperty(URL, 'createObjectURL', {
    writable: true,
    value: vi.fn().mockReturnValue('mock-object-url'),
  })

  Object.defineProperty(URL, 'revokeObjectURL', {
    writable: true,
    value: vi.fn(),
  })

  // Mock fetch
  global.fetch = vi.fn()

  // Mock navigator.clipboard
  Object.defineProperty(navigator, 'clipboard', {
    writable: true,
    value: {
      writeText: vi.fn().mockResolvedValue(undefined),
      readText: vi.fn().mockResolvedValue(''),
    },
  })

  // Mock File and FileReader
  global.File = class MockFile {
    constructor(public bits: any[], public name: string, public options: any = {}) {
      this.type = options.type || ''
      this.size = bits.reduce((acc, bit) => acc + (bit.length || 0), 0)
      this.lastModified = options.lastModified || Date.now()
    }
    type: string
    size: number
    lastModified: number
    stream = vi.fn()
    text = vi.fn().mockResolvedValue('')
    arrayBuffer = vi.fn().mockResolvedValue(new ArrayBuffer(0))
    slice = vi.fn()
  }

  global.FileReader = class MockFileReader {
    result: string | ArrayBuffer | null = null
    error: any = null
    readyState: number = 0
    onload: ((event: any) => void) | null = null
    onerror: ((event: any) => void) | null = null
    onprogress: ((event: any) => void) | null = null
    onabort: ((event: any) => void) | null = null
    onloadstart: ((event: any) => void) | null = null
    onloadend: ((event: any) => void) | null = null

    readAsText = vi.fn().mockImplementation(() => {
      this.readyState = 2
      this.result = 'mock file content'
      if (this.onload) this.onload({ target: this })
    })

    readAsDataURL = vi.fn().mockImplementation(() => {
      this.readyState = 2
      this.result = 'data:text/plain;base64,bW9jayBmaWxlIGNvbnRlbnQ='
      if (this.onload) this.onload({ target: this })
    })

    readAsArrayBuffer = vi.fn().mockImplementation(() => {
      this.readyState = 2
      this.result = new ArrayBuffer(8)
      if (this.onload) this.onload({ target: this })
    })

    abort = vi.fn()
  }

  // Mock HTMLCanvasElement.getContext (for chart components)
  HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
    fillRect: vi.fn(),
    clearRect: vi.fn(),
    getImageData: vi.fn().mockReturnValue({ data: new Uint8ClampedArray(4) }),
    putImageData: vi.fn(),
    createImageData: vi.fn().mockReturnValue({ data: new Uint8ClampedArray(4) }),
    setTransform: vi.fn(),
    drawImage: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    closePath: vi.fn(),
    stroke: vi.fn(),
    fill: vi.fn(),
  })

  // Mock HTMLElement.scrollIntoView
  HTMLElement.prototype.scrollIntoView = vi.fn()

  // Mock WebSocket
  Object.defineProperty(global, 'WebSocket', {
    writable: true,
    value: vi.fn().mockImplementation(() => ({
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      send: vi.fn(),
      close: vi.fn(),
      readyState: 1,
      CONNECTING: 0,
      OPEN: 1,
      CLOSING: 2,
      CLOSED: 3,
    })),
  })
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

// Cleanup after each test
afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  // Reset MSW handlers after each test
  server.resetHandlers()
  // Clear localStorage and sessionStorage mocks
  if (window.localStorage) {
    window.localStorage.clear() // This will actually clear our store
    vi.mocked(window.localStorage.clear).mockClear()
    vi.mocked(window.localStorage.getItem).mockClear()
    vi.mocked(window.localStorage.setItem).mockClear()
    vi.mocked(window.localStorage.removeItem).mockClear()
  }
  if (window.sessionStorage) {
    vi.mocked(window.sessionStorage.clear).mockClear()
    vi.mocked(window.sessionStorage.getItem).mockClear()
    vi.mocked(window.sessionStorage.setItem).mockClear()
    vi.mocked(window.sessionStorage.removeItem).mockClear()
  }
})

// Cleanup after all tests
afterAll(() => {
  vi.resetAllMocks()
  // Close MSW server
  server.close()
})
