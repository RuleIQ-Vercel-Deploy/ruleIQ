# Source Tree Structure

## Project Layout

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authentication pages
│   ├── (dashboard)/       # Dashboard pages
│   ├── (public)/          # Public pages
│   ├── api/               # API routes
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── ui/                # UI components
│   ├── features/          # Feature components
│   └── shared/            # Shared components
├── lib/                   # Core libraries
│   ├── api/               # API client and services
│   ├── stores/            # Zustand stores
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   └── validations/       # Zod schemas
├── tests/                 # Test files
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── public/                # Static assets
├── styles/                # Global styles
└── types/                 # TypeScript type definitions
```

## Key Directories

### `/app`
Next.js 14 App Router structure with grouped routes for authentication, dashboard, and public pages.

### `/components`
Reusable React components organized by type:
- `ui/` - Base UI components (buttons, cards, etc.)
- `features/` - Feature-specific components
- `shared/` - Components shared across features

### `/lib`
Core application logic:
- `api/` - API client configuration and service methods
- `stores/` - Zustand state management stores
- `hooks/` - Custom React hooks
- `utils/` - Helper functions and utilities

### `/tests`
Comprehensive test coverage:
- Unit tests for individual functions
- Integration tests for feature flows
- E2E tests for critical user journeys