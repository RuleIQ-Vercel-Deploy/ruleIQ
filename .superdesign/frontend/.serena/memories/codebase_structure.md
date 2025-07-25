# Codebase Structure Overview

## Directory Organization

### Core Application (`/app`)

Next.js 15 App Router structure with route groups:

- `(auth)/` - Authentication pages (login, signup, register)
- `(dashboard)/` - Main application pages (dashboard, policies, assessments)
- `(public)/` - Public marketing/informational pages
- `api/` - API routes and server functions

### Component Library (`/components`)

Organized by feature and reusability:

- `ui/` - Base design system components (buttons, cards, forms)
- `shared/` - Cross-feature reusable components
- `dashboard/` - Dashboard-specific components
- `auth/` - Authentication-related components
- `assessments/` - Compliance assessment components
- `policies/` - Policy management components
- `evidence/` - Evidence tracking components
- `chat/` - AI chat interface components

### Utilities & Configuration (`/lib`, `/hooks`, `/types`)

- `lib/` - Utility functions, API clients, shared logic
- `hooks/` - Custom React hooks
- `types/` - TypeScript type definitions
- `config/` - Application configuration

### Testing (`/tests`)

Comprehensive testing structure:

- `unit/` - Component and utility unit tests
- `e2e/` - End-to-end user journey tests
- `visual/` - Visual regression tests
- `performance/` - Performance benchmarking
- `accessibility/` - Accessibility compliance tests

## Key File Patterns

### Page Structure

```
app/(dashboard)/assessments/
├── page.tsx              # Main assessments listing
├── new/page.tsx         # New assessment creation
├── [id]/page.tsx        # Individual assessment view
└── [id]/results/page.tsx # Assessment results
```

### Component Architecture

```
components/assessments/
├── AssessmentWizard.tsx     # Main wizard component
├── AssessmentCard.tsx       # Individual assessment display
├── QuestionTypes/           # Different question components
└── ResultsDisplay/          # Results visualization
```

## Architecture Patterns

### State Management

- **Server State**: TanStack Query for API data caching
- **Global State**: Zustand stores for cross-component state
- **Local State**: React hooks for component-specific state
- **Form State**: React Hook Form for complex forms

### Data Flow

1. **API Layer**: Server actions and API routes
2. **Query Layer**: TanStack Query for data fetching
3. **State Layer**: Zustand for global state management
4. **Component Layer**: React components with local state
5. **UI Layer**: Radix UI primitives with Tailwind styling

### Feature Organization

Each major feature follows a consistent pattern:

```
components/[feature]/
├── index.ts              # Public exports
├── [Feature]Main.tsx     # Main feature component
├── [Feature]Card.tsx     # List item component
├── [Feature]Form.tsx     # Creation/editing form
├── [Feature]Modal.tsx    # Modal dialogs
└── types.ts              # Feature-specific types
```

## Configuration Files

### Build & Development

- `next.config.mjs` - Next.js configuration with security headers
- `tailwind.config.ts` - Design system tokens and utilities
- `tsconfig.json` - TypeScript compiler options
- `vitest.config.ts` - Testing configuration

### Code Quality

- `eslint.config.mjs` - Linting rules (flat config)
- `.prettierrc.json` - Code formatting rules
- `.editorconfig` - Editor consistency

### CI/CD & Deployment

- `.github/workflows/` - GitHub Actions pipelines
- `Dockerfile` - Container configuration
- `playwright.config.ts` - E2E testing setup
