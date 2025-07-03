import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return '/'
  },
}))

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    span: ({ children, ...props }) => <span {...props}>{children}</span>,
    button: ({ children, ...props }) => <button {...props}>{children}</button>,
    form: ({ children, ...props }) => <form {...props}>{children}</form>,
    section: ({ children, ...props }) => <section {...props}>{children}</section>,
    article: ({ children, ...props }) => <article {...props}>{children}</article>,
    header: ({ children, ...props }) => <header {...props}>{children}</header>,
    main: ({ children, ...props }) => <main {...props}>{children}</main>,
    nav: ({ children, ...props }) => <nav {...props}>{children}</nav>,
    aside: ({ children, ...props }) => <aside {...props}>{children}</aside>,
    footer: ({ children, ...props }) => <footer {...props}>{children}</footer>,
    h1: ({ children, ...props }) => <h1 {...props}>{children}</h1>,
    h2: ({ children, ...props }) => <h2 {...props}>{children}</h2>,
    h3: ({ children, ...props }) => <h3 {...props}>{children}</h3>,
    p: ({ children, ...props }) => <p {...props}>{children}</p>,
    ul: ({ children, ...props }) => <ul {...props}>{children}</ul>,
    li: ({ children, ...props }) => <li {...props}>{children}</li>,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
  useAnimation: () => ({
    start: jest.fn(),
    stop: jest.fn(),
    set: jest.fn(),
  }),
  useMotionValue: () => ({
    get: jest.fn(),
    set: jest.fn(),
  }),
}))

// Mock Lucide React icons
jest.mock('lucide-react', () => {
  const icons = [
    'AlertTriangle', 'ArrowLeft', 'ArrowRight', 'Check', 'ChevronDown', 'ChevronLeft', 
    'ChevronRight', 'ChevronUp', 'Copy', 'Download', 'Edit', 'Eye', 'EyeOff', 
    'FileText', 'Filter', 'Home', 'Info', 'Loader2', 'Lock', 'Mail', 'Menu', 
    'MoreHorizontal', 'Plus', 'Search', 'Settings', 'Shield', 'Star', 'Trash2', 
    'Upload', 'User', 'X', 'Calendar', 'Clock', 'Database', 'Globe', 'Heart',
    'Image', 'Link', 'MessageSquare', 'Phone', 'Play', 'Save', 'Share', 'Tag',
    'Target', 'Zap', 'BarChart3', 'PieChart', 'TrendingUp', 'Activity',
    'AlertCircle', 'CheckCircle2', 'XCircle', 'HelpCircle', 'RefreshCw',
    'ExternalLink', 'MapPin', 'MousePointerClick', 'WandSparkles', 'Gauge',
    'FileCheck', 'Users', 'CreditCard', 'Bot', 'Send', 'Paperclip'
  ]
  
  const mockIcons = {}
  icons.forEach(iconName => {
    mockIcons[iconName] = ({ children, ...props }) => (
      <svg data-testid={`${iconName}-icon`} {...props}>
        {children}
      </svg>
    )
  })
  
  return mockIcons
})

// Global test utilities
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})
