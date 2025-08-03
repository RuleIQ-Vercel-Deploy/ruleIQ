// Proper HTMLFormElement.prototype.requestSubmit polyfill
if (!HTMLFormElement.prototype.requestSubmit) {
  HTMLFormElement.prototype.requestSubmit = function(submitter) {
    if (submitter && submitter.form !== this) {
      throw new DOMException('The specified element is not a descendant of this form element', 'NotFoundError');
    }
    
    // Create and dispatch submit event
    const submitEvent = new Event('submit', {
      bubbles: true,
      cancelable: true
    });
    
    // Set submitter if provided
    if (submitter) {
      Object.defineProperty(submitEvent, 'submitter', {
        value: submitter,
        configurable: true
      });
    }
    
    this.dispatchEvent(submitEvent);
  };
}
// Proper HTMLFormElement.prototype.requestSubmit polyfill
if (!HTMLFormElement.prototype.requestSubmit) {
  HTMLFormElement.prototype.requestSubmit = function(submitter) {
    if (submitter && submitter.form !== this) {
      throw new DOMException('The specified element is not a descendant of this form element', 'NotFoundError');
    }
    
    // Create and dispatch submit event
    const submitEvent = new Event('submit', {
      bubbles: true,
      cancelable: true
    });
    
    // Set submitter if provided
    if (submitter) {
      Object.defineProperty(submitEvent, 'submitter', {
        value: submitter,
        configurable: true
      });
    }
    
    this.dispatchEvent(submitEvent);
  };
}
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeAll, afterAll, vi } from 'vitest';
import React from 'react';

// Mock environment variables
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api';
process.env.NEXT_PUBLIC_WEBSOCKET_URL = 'ws://localhost:8000/api/chat/ws';
process.env.NEXT_PUBLIC_AUTH_DOMAIN = 'localhost';
process.env.NEXT_PUBLIC_JWT_EXPIRES_IN = '86400';
process.env.NEXT_PUBLIC_ENABLE_ANALYTICS = 'false';
process.env.NEXT_PUBLIC_ENABLE_SENTRY = 'false';
process.env.NEXT_PUBLIC_ENABLE_MOCK_DATA = 'true';
process.env.NEXT_PUBLIC_ENV = 'test';
process.env.NODE_ENV = 'test';
process.env.SKIP_ENV_VALIDATION = 'true';

// Setup MSW server for API mocking
import { server } from './mocks/server';

// Global test setup
beforeAll(() => {
  // Start MSW server
  server.listen({
    onUnhandledRequest: 'warn',
  });
  // Mock window.matchMedia (used by components with responsive behavior)
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });

  // Mock window.ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Mock window.IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Mock window.scrollTo
  Object.defineProperty(window, 'scrollTo', {
    writable: true,
    value: vi.fn(),
  });

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
          array[i] = Math.floor(Math.random() * 256);
        }
        return array;
      }),
    },
  });

  // Mock localStorage with working implementation
  const localStorageStore: Record<string, string> = {};
  const localStorageMock = {
    getItem: vi.fn((key: string) => localStorageStore[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      localStorageStore[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete localStorageStore[key];
    }),
    clear: vi.fn(() => {
      Object.keys(localStorageStore).forEach((key) => delete localStorageStore[key]);
    }),
    get length() {
      return Object.keys(localStorageStore).length;
    },
    key: vi.fn((index: number) => {
      const keys = Object.keys(localStorageStore);
      return keys[index] || null;
    }),
  };
  Object.defineProperty(window, 'localStorage', {
    writable: true,
    value: localStorageMock,
  });

  // Mock sessionStorage
  const sessionStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    length: 0,
    key: vi.fn(),
  };
  Object.defineProperty(window, 'sessionStorage', {
    writable: true,
    value: sessionStorageMock,
  });

  // Mock URL.createObjectURL
  Object.defineProperty(URL, 'createObjectURL', {
    writable: true,
    value: vi.fn().mockReturnValue('mock-object-url'),
  });

  Object.defineProperty(URL, 'revokeObjectURL', {
    writable: true,
    value: vi.fn(),
  });

  // Mock fetch
  global.fetch = vi.fn();

  // Use real timers for better test stability
  vi.useRealTimers();

  // Mock navigator.clipboard
  Object.defineProperty(navigator, 'clipboard', {
    writable: true,
    configurable: true,
    value: {
      writeText: vi.fn().mockResolvedValue(undefined),
      readText: vi.fn().mockResolvedValue(''),
    },
  });

  // Fix user-event clipboard redefinition issue
  const originalDefineProperty = Object.defineProperty;
  Object.defineProperty = function (obj: any, prop: string, descriptor: PropertyDescriptor) {
    if (prop === 'clipboard' && obj === navigator) {
      // Allow redefinition of clipboard property
      return originalDefineProperty.call(this, obj, prop, { ...descriptor, configurable: true });
    }
    return originalDefineProperty.call(this, obj, prop, descriptor);
  };

  // Mock File and FileReader - commented out to avoid conflicts

  // FileReader mock properties removed to fix syntax errors

  // FileReader mock methods removed to fix syntax errors

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
  });

  // Mock HTMLElement.scrollIntoView
  HTMLElement.prototype.scrollIntoView = vi.fn();

  // Mock hasPointerCapture for Radix UI components
  HTMLElement.prototype.hasPointerCapture = vi.fn().mockReturnValue(false);
  HTMLElement.prototype.setPointerCapture = vi.fn();
  HTMLElement.prototype.releasePointerCapture = vi.fn();

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
  });
});

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
}));

// Mock Next.js image
vi.mock('next/image', () => ({
  default: (props: any) => {
    const { src, alt, ...rest } = props;
    return React.createElement('img', { src, alt, ...rest });
  },
}));

// Mock Lucide React icons
vi.mock('lucide-react', () => {
  const createMockIcon = (name: string) => (props: any) => 
    React.createElement('svg', {
      'data-testid': `${name}-icon`,
      ...props,
      children: React.createElement('path', { d: 'M0 0h24v24H0z' })
    });

  return {
    ArrowRight: createMockIcon('arrow-right'),
    Sparkles: createMockIcon('sparkles'),
    Shield: createMockIcon('shield'),
    Zap: createMockIcon('zap'),
    BarChart3: createMockIcon('bar-chart-3'),
    Lock: createMockIcon('lock'),
    Globe: createMockIcon('globe'),
    CheckCircle: createMockIcon('check-circle'),
    Star: createMockIcon('star'),
    TrendingUp: createMockIcon('trending-up'),
    Users: createMockIcon('users'),
    FileCheck: createMockIcon('file-check'),
    ChevronRight: createMockIcon('chevron-right'),
    ChevronDown: createMockIcon('chevron-down'),
    ChevronUp: createMockIcon('chevron-up'),
    ChevronLeft: createMockIcon('chevron-left'),
    Circle: createMockIcon('circle'),
    Loader2: createMockIcon('loader-2'),
    Save: createMockIcon('save'),
    Check: createMockIcon('check'),
    X: createMockIcon('x'),
    Menu: createMockIcon('menu'),
    Plus: createMockIcon('plus'),
    Minus: createMockIcon('minus'),
    Search: createMockIcon('search'),
    Download: createMockIcon('download'),
    Edit: createMockIcon('edit'),
    Trash: createMockIcon('trash'),
    Eye: createMockIcon('eye'),
    EyeOff: createMockIcon('eye-off'),
    Settings: createMockIcon('settings'),
    Calendar: createMockIcon('calendar'),
    Clock: createMockIcon('clock'),
    Mail: createMockIcon('mail'),
    Phone: createMockIcon('phone'),
    MapPin: createMockIcon('map-pin'),
    Home: createMockIcon('home'),
    Building: createMockIcon('building'),
    User: createMockIcon('user'),
    AlertTriangle: createMockIcon('alert-triangle'),
    AlertCircle: createMockIcon('alert-circle'),
    Info: createMockIcon('info'),
    HelpCircle: createMockIcon('help-circle'),
    ExternalLink: createMockIcon('external-link'),
    Bot: createMockIcon('bot'),
    RefreshCw: createMockIcon('refresh-cw'),
    Upload: createMockIcon('upload'),
    Download2: createMockIcon('download-2'),
    FileText: createMockIcon('file-text'),
    Database: createMockIcon('database'),
    Cpu: createMockIcon('cpu'),
    Activity: createMockIcon('activity'),
    TrendingDown: createMockIcon('trending-down'),
    PieChart: createMockIcon('pie-chart'),
    BarChart: createMockIcon('bar-chart'),
    LineChart: createMockIcon('line-chart'),
    Target: createMockIcon('target'),
    Filter: createMockIcon('filter'),
    Sort: createMockIcon('sort'),
    Grid: createMockIcon('grid'),
    List: createMockIcon('list'),
    Card: createMockIcon('card'),
    Table: createMockIcon('table'),
    Copy: createMockIcon('copy'),
    MessageSquare: createMockIcon('message-square'),
    Lightbulb: createMockIcon('lightbulb'),
    BookOpen: createMockIcon('book-open'),
    ThumbsUp: createMockIcon('thumbs-up'),
    ThumbsDown: createMockIcon('thumbs-down'),
    CalendarIcon: createMockIcon('calendar-icon'),
  };
});

// Mock Framer Motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => React.createElement('div', props, children),
    span: ({ children, ...props }: any) => React.createElement('span', props, children),
    button: ({ children, ...props }: any) => React.createElement('button', props, children),
    form: ({ children, ...props }: any) => React.createElement('form', props, children),
  },
  AnimatePresence: ({ children }: any) => children,
  useScroll: () => ({
    scrollY: { current: 0 },
    scrollYProgress: { current: 0 },
  }),
  useTransform: () => ({ current: 0 }),
  useAnimation: () => ({
    start: vi.fn(),
    stop: vi.fn(),
    set: vi.fn(),
  }),
}));

// Cleanup after each test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  // Reset MSW handlers after each test
  server.resetHandlers();
  // Clear localStorage and sessionStorage mocks
  if (window.localStorage) {
    window.localStorage.clear(); // This will actually clear our store
    vi.mocked(window.localStorage.clear).mockClear();
    vi.mocked(window.localStorage.getItem).mockClear();
    vi.mocked(window.localStorage.setItem).mockClear();
    vi.mocked(window.localStorage.removeItem).mockClear();
  }
  if (window.sessionStorage) {
    vi.mocked(window.sessionStorage.clear).mockClear();
    vi.mocked(window.sessionStorage.getItem).mockClear();
    vi.mocked(window.sessionStorage.setItem).mockClear();
    vi.mocked(window.sessionStorage.removeItem).mockClear();
  }
});

// Cleanup after all tests
afterAll(() => {
  vi.resetAllMocks();
  // Close MSW server
  server.close();
});

// MSW Server Setup
import { setupServer } from 'msw/node'
import { handlers } from './mocks/handlers'

export const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// Proper File and FileReader mocks
Object.defineProperty(global, 'File', {
  writable: true,
  value: class MockFile {
    constructor(bits, name, options = {}) {
      this.bits = bits;
      this.name = name;
      this.type = options.type || '';
      this.size = bits.reduce((acc, bit) => acc + (bit.length || 0), 0);
    }
  }
});

Object.defineProperty(global, 'FileReader', {
  writable: true,
  value: class MockFileReader {
    constructor() {
      this.readyState = 0;
      this.result = null;
      this.error = null;
    }
    
    readAsDataURL(file) {
      this.readyState = 2;
      this.result = 'data:text/plain;base64,dGVzdA==';
      if (this.onload) this.onload();
    }
    
    readAsText(file) {
      this.readyState = 2;
      this.result = 'test content';
      if (this.onload) this.onload();
    }
  }
});

// Import API client setup
import './mocks/api-client-setup';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn()
  })),
  usePathname: vi.fn(() => '/'),
  useSearchParams: vi.fn(() => new URLSearchParams())
}));

// Mock auth store with proper implementation
vi.mock('@/lib/stores/auth.store', () => ({
  useAuthStore: vi.fn(() => ({
    user: {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true
    },
    tokens: {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token'
    },
    isAuthenticated: true,
    isLoading: false,
    error: null,
    login: vi.fn().mockResolvedValue({
      user: {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        is_active: true
      },
      tokens: {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token'
      }
    }),
    register: vi.fn().mockResolvedValue({
      user: {
        id: 'user-456',
        email: 'newuser@example.com',
        name: 'New User',
        is_active: true
      },
      tokens: {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      }
    }),
    logout: vi.fn().mockResolvedValue(undefined),
    getCurrentUser: vi.fn().mockResolvedValue({
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true
    }),
    initialize: vi.fn().mockResolvedValue(undefined)
  }))
}));

// Enhanced Lucide React mock with all required icons
vi.mock('lucide-react', () => ({
  // Common icons used in components
  Shield: vi.fn(() => 'div'),
  Filter: vi.fn(() => 'div'),
  Check: vi.fn(() => 'div'),
  X: vi.fn(() => 'div'),
  Upload: vi.fn(() => 'div'),
  Download: vi.fn(() => 'div'),
  Eye: vi.fn(() => 'div'),
  Edit: vi.fn(() => 'div'),
  Trash: vi.fn(() => 'div'),
  Plus: vi.fn(() => 'div'),
  Minus: vi.fn(() => 'div'),
  Search: vi.fn(() => 'div'),
  Settings: vi.fn(() => 'div'),
  User: vi.fn(() => 'div'),
  Home: vi.fn(() => 'div'),
  FileText: vi.fn(() => 'div'),
  BarChart: vi.fn(() => 'div'),
  PieChart: vi.fn(() => 'div'),
  TrendingUp: vi.fn(() => 'div'),
  TrendingDown: vi.fn(() => 'div'),
  AlertTriangle: vi.fn(() => 'div'),
  Info: vi.fn(() => 'div'),
  CheckCircle: vi.fn(() => 'div'),
  XCircle: vi.fn(() => 'div'),
  Clock: vi.fn(() => 'div'),
  Calendar: vi.fn(() => 'div'),
  Mail: vi.fn(() => 'div'),
  Phone: vi.fn(() => 'div'),
  MapPin: vi.fn(() => 'div'),
  Globe: vi.fn(() => 'div'),
  Lock: vi.fn(() => 'div'),
  Unlock: vi.fn(() => 'div'),
  Key: vi.fn(() => 'div'),
  Database: vi.fn(() => 'div'),
  Server: vi.fn(() => 'div'),
  Cloud: vi.fn(() => 'div'),
  Wifi: vi.fn(() => 'div'),
  Activity: vi.fn(() => 'div'),
  Zap: vi.fn(() => 'div'),
  Star: vi.fn(() => 'div'),
  Heart: vi.fn(() => 'div'),
  Bookmark: vi.fn(() => 'div'),
  Flag: vi.fn(() => 'div'),
  Tag: vi.fn(() => 'div'),
  Folder: vi.fn(() => 'div'),
  File: vi.fn(() => 'div'),
  Image: vi.fn(() => 'div'),
  Video: vi.fn(() => 'div'),
  Music: vi.fn(() => 'div'),
  Headphones: vi.fn(() => 'div'),
  Camera: vi.fn(() => 'div'),
  Printer: vi.fn(() => 'div'),
  Monitor: vi.fn(() => 'div'),
  Smartphone: vi.fn(() => 'div'),
  Tablet: vi.fn(() => 'div'),
  Laptop: vi.fn(() => 'div'),
  HardDrive: vi.fn(() => 'div'),
  Cpu: vi.fn(() => 'div'),
  MemoryStick: vi.fn(() => 'div'),
  Battery: vi.fn(() => 'div'),
  Power: vi.fn(() => 'div'),
  Plug: vi.fn(() => 'div'),
  Bluetooth: vi.fn(() => 'div'),
  Usb: vi.fn(() => 'div'),
  // Add any other icons that might be used
  ChevronDown: vi.fn(() => 'div'),
  ChevronUp: vi.fn(() => 'div'),
  ChevronLeft: vi.fn(() => 'div'),
  ChevronRight: vi.fn(() => 'div'),
  ArrowUp: vi.fn(() => 'div'),
  ArrowDown: vi.fn(() => 'div'),
  ArrowLeft: vi.fn(() => 'div'),
  ArrowRight: vi.fn(() => 'div'),
  MoreHorizontal: vi.fn(() => 'div'),
  MoreVertical: vi.fn(() => 'div'),
  Menu: vi.fn(() => 'div'),
  Grid: vi.fn(() => 'div'),
  List: vi.fn(() => 'div'),
  Layout: vi.fn(() => 'div'),
  Sidebar: vi.fn(() => 'div'),
  Maximize: vi.fn(() => 'div'),
  Minimize: vi.fn(() => 'div'),
  Copy: vi.fn(() => 'div'),
  Clipboard: vi.fn(() => 'div'),
  Share: vi.fn(() => 'div'),
  ExternalLink: vi.fn(() => 'div'),
  Link: vi.fn(() => 'div'),
  Unlink: vi.fn(() => 'div'),
  Refresh: vi.fn(() => 'div'),
  RotateCw: vi.fn(() => 'div'),
  RotateCcw: vi.fn(() => 'div'),
  Repeat: vi.fn(() => 'div'),
  Shuffle: vi.fn(() => 'div'),
  Play: vi.fn(() => 'div'),
  Pause: vi.fn(() => 'div'),
  Stop: vi.fn(() => 'div'),
  SkipBack: vi.fn(() => 'div'),
  SkipForward: vi.fn(() => 'div'),
  FastForward: vi.fn(() => 'div'),
  Rewind: vi.fn(() => 'div'),
  Volume: vi.fn(() => 'div'),
  Volume1: vi.fn(() => 'div'),
  Volume2: vi.fn(() => 'div'),
  VolumeX: vi.fn(() => 'div'),
  Mic: vi.fn(() => 'div'),
  MicOff: vi.fn(() => 'div'),
  // Default export for any missing icons
  default: vi.fn(() => 'div')
}));

// Fix HTMLFormElement.prototype.requestSubmit not implemented in JSDOM
Object.defineProperty(HTMLFormElement.prototype, 'requestSubmit', {
  writable: true,
  value: function(submitter) {
    if (submitter && submitter.form !== this) {
      throw new DOMException('The specified element is not a descendant of this form element', 'NotFoundError');
    }
    
    // Create and dispatch submit event
    const submitEvent = new Event('submit', {
      bubbles: true,
      cancelable: true
    });
    
    // Set submitter if provided
    if (submitter) {
      Object.defineProperty(submitEvent, 'submitter', {
        value: submitter,
        configurable: true
      });
    }
    
    this.dispatchEvent(submitEvent);
  }
});

// Import and use complete Lucide React mock
import { LucideIconMocks } from './mocks/lucide-react-complete';

vi.mock('lucide-react', () => LucideIconMocks);

// Import all enhanced mocks
import './mocks/api-client-setup';
import './mocks/business-profile-service';

// Mock AI services to prevent timeout errors
vi.mock('@/lib/services/ai-service', () => ({
  AIService: {
    generateFollowUpQuestions: vi.fn().mockResolvedValue([
      'What is your data retention policy?',
      'How do you handle data breaches?',
      'Do you have employee training programs?'
    ]),
    getEnhancedResponse: vi.fn().mockResolvedValue({
      response: 'This is a mock AI response',
      confidence: 0.85,
      suggestions: ['Consider implementing automated data deletion']
    }),
    analyzeCompliance: vi.fn().mockResolvedValue({
      score: 85,
      recommendations: ['Improve data retention policies'],
      risks: ['Missing employee training records']
    })
  }
}));

// Mock network requests to prevent actual API calls
global.fetch = vi.fn().mockImplementation((url, options = {}) => {
  console.log('Mock fetch:', url, options);

  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ success: true }),
    text: () => Promise.resolve('Mock response'),
    headers: new Headers(),
    redirected: false,
    statusText: 'OK',
    type: 'basic',
    url: url as string
  } as Response);
});

// Import and use comprehensive Lucide React mock with proxy
import { LucideProxy } from './mocks/lucide-react-complete';

vi.mock('lucide-react', () => LucideProxy);

// Import AI service mock
import './mocks/ai-service-mock';

// Fix HTMLFormElement.prototype.requestSubmit not implemented in JSDOM
Object.defineProperty(HTMLFormElement.prototype, 'requestSubmit', {
  writable: true,
  value: function(submitter) {
    if (submitter && submitter.form !== this) {
      throw new DOMException('The specified element is not a descendant of this form element', 'NotFoundError');
    }
    
    // Create and dispatch submit event
    const submitEvent = new Event('submit', {
      bubbles: true,
      cancelable: true
    });
    
    // Set submitter if provided
    if (submitter) {
      Object.defineProperty(submitEvent, 'submitter', {
        value: submitter,
        configurable: true
      });
    }
    
    this.dispatchEvent(submitEvent);
  }
});

// Import and use complete Lucide React mock
import { LucideIconMocks } from './mocks/lucide-react-complete';

vi.mock('lucide-react', () => LucideIconMocks);

// Import all enhanced mocks
import './mocks/api-client-setup';
import './mocks/business-profile-service';

// Mock AI services to prevent timeout errors
vi.mock('@/lib/services/ai-service', () => ({
  AIService: {
    generateFollowUpQuestions: vi.fn().mockResolvedValue([
      'What is your data retention policy?',
      'How do you handle data breaches?',
      'Do you have employee training programs?'
    ]),
    getEnhancedResponse: vi.fn().mockResolvedValue({
      response: 'This is a mock AI response',
      confidence: 0.85,
      suggestions: ['Consider implementing automated data deletion']
    }),
    analyzeCompliance: vi.fn().mockResolvedValue({
      score: 85,
      recommendations: ['Improve data retention policies'],
      risks: ['Missing employee training records']
    })
  }
}));

// Mock network requests to prevent actual API calls
global.fetch = vi.fn().mockImplementation((url, options = {}) => {
  console.log('Mock fetch:', url, options);

  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ success: true }),
    text: () => Promise.resolve('Mock response'),
    headers: new Headers(),
    redirected: false,
    statusText: 'OK',
    type: 'basic',
    url: url as string
  } as Response);
});

// Import and use comprehensive Lucide React mock with proxy
import { LucideProxy } from './mocks/lucide-react-complete';

vi.mock('lucide-react', () => LucideProxy);

// Import AI service mock
import './mocks/ai-service-mock';

// Import API client setup
import './mocks/api-client-setup';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn()
  })),
  usePathname: vi.fn(() => '/'),
  useSearchParams: vi.fn(() => new URLSearchParams())
}));

// Mock auth store with proper implementation
vi.mock('@/lib/stores/auth.store', () => ({
  useAuthStore: vi.fn(() => ({
    user: {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true
    },
    tokens: {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token'
    },
    isAuthenticated: true,
    isLoading: false,
    error: null,
    login: vi.fn().mockResolvedValue({
      user: {
        id: 'user-123',
        email: 'test@example.com',
        name: 'Test User',
        is_active: true
      },
      tokens: {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token'
      }
    }),
    register: vi.fn().mockResolvedValue({
      user: {
        id: 'user-456',
        email: 'newuser@example.com',
        name: 'New User',
        is_active: true
      },
      tokens: {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      }
    }),
    logout: vi.fn().mockResolvedValue(undefined),
    getCurrentUser: vi.fn().mockResolvedValue({
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true
    }),
    initialize: vi.fn().mockResolvedValue(undefined)
  }))
}));

// Enhanced Lucide React mock with all required icons
vi.mock('lucide-react', () => ({
  // Common icons used in components
  Shield: vi.fn(() => 'div'),
  Filter: vi.fn(() => 'div'),
  Check: vi.fn(() => 'div'),
  X: vi.fn(() => 'div'),
  Upload: vi.fn(() => 'div'),
  Download: vi.fn(() => 'div'),
  Eye: vi.fn(() => 'div'),
  Edit: vi.fn(() => 'div'),
  Trash: vi.fn(() => 'div'),
  Plus: vi.fn(() => 'div'),
  Minus: vi.fn(() => 'div'),
  Search: vi.fn(() => 'div'),
  Settings: vi.fn(() => 'div'),
  User: vi.fn(() => 'div'),
  Home: vi.fn(() => 'div'),
  FileText: vi.fn(() => 'div'),
  BarChart: vi.fn(() => 'div'),
  PieChart: vi.fn(() => 'div'),
  TrendingUp: vi.fn(() => 'div'),
  TrendingDown: vi.fn(() => 'div'),
  AlertTriangle: vi.fn(() => 'div'),
  Info: vi.fn(() => 'div'),
  CheckCircle: vi.fn(() => 'div'),
  XCircle: vi.fn(() => 'div'),
  Clock: vi.fn(() => 'div'),
  Calendar: vi.fn(() => 'div'),
  Mail: vi.fn(() => 'div'),
  Phone: vi.fn(() => 'div'),
  MapPin: vi.fn(() => 'div'),
  Globe: vi.fn(() => 'div'),
  Lock: vi.fn(() => 'div'),
  Unlock: vi.fn(() => 'div'),
  Key: vi.fn(() => 'div'),
  Database: vi.fn(() => 'div'),
  Server: vi.fn(() => 'div'),
  Cloud: vi.fn(() => 'div'),
  Wifi: vi.fn(() => 'div'),
  Activity: vi.fn(() => 'div'),
  Zap: vi.fn(() => 'div'),
  Star: vi.fn(() => 'div'),
  Heart: vi.fn(() => 'div'),
  Bookmark: vi.fn(() => 'div'),
  Flag: vi.fn(() => 'div'),
  Tag: vi.fn(() => 'div'),
  Folder: vi.fn(() => 'div'),
  File: vi.fn(() => 'div'),
  Image: vi.fn(() => 'div'),
  Video: vi.fn(() => 'div'),
  Music: vi.fn(() => 'div'),
  Headphones: vi.fn(() => 'div'),
  Camera: vi.fn(() => 'div'),
  Printer: vi.fn(() => 'div'),
  Monitor: vi.fn(() => 'div'),
  Smartphone: vi.fn(() => 'div'),
  Tablet: vi.fn(() => 'div'),
  Laptop: vi.fn(() => 'div'),
  HardDrive: vi.fn(() => 'div'),
  Cpu: vi.fn(() => 'div'),
  MemoryStick: vi.fn(() => 'div'),
  Battery: vi.fn(() => 'div'),
  Power: vi.fn(() => 'div'),
  Plug: vi.fn(() => 'div'),
  Bluetooth: vi.fn(() => 'div'),
  Usb: vi.fn(() => 'div'),
  // Add any other icons that might be used
  ChevronDown: vi.fn(() => 'div'),
  ChevronUp: vi.fn(() => 'div'),
  ChevronLeft: vi.fn(() => 'div'),
  ChevronRight: vi.fn(() => 'div'),
  ArrowUp: vi.fn(() => 'div'),
  ArrowDown: vi.fn(() => 'div'),
  ArrowLeft: vi.fn(() => 'div'),
  ArrowRight: vi.fn(() => 'div'),
  MoreHorizontal: vi.fn(() => 'div'),
  MoreVertical: vi.fn(() => 'div'),
  Menu: vi.fn(() => 'div'),
  Grid: vi.fn(() => 'div'),
  List: vi.fn(() => 'div'),
  Layout: vi.fn(() => 'div'),
  Sidebar: vi.fn(() => 'div'),
  Maximize: vi.fn(() => 'div'),
  Minimize: vi.fn(() => 'div'),
  Copy: vi.fn(() => 'div'),
  Clipboard: vi.fn(() => 'div'),
  Share: vi.fn(() => 'div'),
  ExternalLink: vi.fn(() => 'div'),
  Link: vi.fn(() => 'div'),
  Unlink: vi.fn(() => 'div'),
  Refresh: vi.fn(() => 'div'),
  RotateCw: vi.fn(() => 'div'),
  RotateCcw: vi.fn(() => 'div'),
  Repeat: vi.fn(() => 'div'),
  Shuffle: vi.fn(() => 'div'),
  Play: vi.fn(() => 'div'),
  Pause: vi.fn(() => 'div'),
  Stop: vi.fn(() => 'div'),
  SkipBack: vi.fn(() => 'div'),
  SkipForward: vi.fn(() => 'div'),
  FastForward: vi.fn(() => 'div'),
  Rewind: vi.fn(() => 'div'),
  Volume: vi.fn(() => 'div'),
  Volume1: vi.fn(() => 'div'),
  Volume2: vi.fn(() => 'div'),
  VolumeX: vi.fn(() => 'div'),
  Mic: vi.fn(() => 'div'),
  MicOff: vi.fn(() => 'div'),
  // Default export for any missing icons
  default: vi.fn(() => 'div')
}));

// Proper File and FileReader mocks
Object.defineProperty(global, 'File', {
  writable: true,
  value: class MockFile {
    constructor(bits, name, options = {}) {
      this.bits = bits;
      this.name = name;
      this.type = options.type || '';
      this.size = bits.reduce((acc, bit) => acc + (bit.length || 0), 0);
    }
  }
});

Object.defineProperty(global, 'FileReader', {
  writable: true,
  value: class MockFileReader {
    constructor() {
      this.readyState = 0;
      this.result = null;
      this.error = null;
    }
    
    readAsDataURL(file) {
      this.readyState = 2;
      this.result = 'data:text/plain;base64,dGVzdA==';
      if (this.onload) this.onload();
    }
    
    readAsText(file) {
      this.readyState = 2;
      this.result = 'test content';
      if (this.onload) this.onload();
    }
  }
});
