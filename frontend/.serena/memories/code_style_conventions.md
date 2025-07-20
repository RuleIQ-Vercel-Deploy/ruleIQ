# Code Style and Conventions - Updated for Teal Design System

## TypeScript Configuration
- **Strict mode enabled** with comprehensive type checking
- **Path mapping** for clean imports (`@/` for root, `@/components/*`, `@/lib/*`, etc.)
- **Consistent type imports** using `import type { ... }` syntax
- **NoEmit mode** for type checking without compilation

## Code Formatting (Prettier)
- **Semi-colons**: Always required
- **Single quotes**: Preferred for strings
- **Trailing commas**: Always include
- **Print width**: 100 characters
- **Tab width**: 2 spaces (no tabs)
- **Tailwind plugin**: Automatic class sorting

## Linting Rules (ESLint)
- **TypeScript strict rules** with relaxed production settings
- **Import ordering**: Enforced with alphabetical sorting and grouping
- **React hooks**: Exhaustive deps warnings
- **No console logs** except warn/error in production
- **Consistent type imports**: Required for all type-only imports

## File Organization
```
/app                    # Next.js App Router pages
/components            # Reusable UI components
  /ui                  # Base design system components (TEAL THEME)
  /forms              # Form-specific components
  /dashboard          # Dashboard-specific components
  /shared             # Cross-feature shared components
/lib                   # Utility functions and configurations
/hooks                 # Custom React hooks
/types                 # TypeScript type definitions
/styles               # Global styles and CSS
  /design-system.css  # NEW TEAL DESIGN SYSTEM
/tests                # Test files organized by type
  /unit              # Unit tests
  /e2e               # End-to-end tests
  /visual            # Visual regression tests
```

## Component Conventions
- **Functional components only** (no class components)
- **TypeScript interfaces** for all props with descriptive names
- **Default exports** for page components, named exports for utilities
- **Consistent naming**: PascalCase for components, camelCase for functions/variables
- **Props destructuring** preferred over props object access

## NEW DESIGN SYSTEM INTEGRATION (Teal Theme)
- **Tailwind-first approach** with teal design tokens
- **Light mode first** design philosophy (CHANGED from dark-mode first)
- **8px grid system** for consistent spacing
- **NEW Brand colors**: Teal-600 (#2C7A7B), Neutral grays, Emerald success
- **Radix UI components** for accessibility-compliant base components
- **Feature flag**: `NEXT_PUBLIC_USE_NEW_THEME=true` for new design system

## Design Token Usage
```tsx
// NEW TEAL SYSTEM - Use these tokens
- Primary: `teal-600` (#2C7A7B)
- Hover: `teal-700` (#285E61) 
- Light: `teal-50` (#E6FFFA)
- Backgrounds: `neutral-50` (#F9FAFB), `white`
- Text: `neutral-900` (#111827), `neutral-700` (#374151)
- Success: `emerald-600` (#10B981)
- Warning: `amber-600` (#F59E0B)
- Error: `red-600` (#EF4444)

// AVOID OLD TOKENS (being phased out)
❌ navy, gold, turquoise, midnight colors
❌ Dark-mode first assumptions
❌ Purple/cyan theme references
```

## State Management Patterns
- **Server state**: TanStack Query for API data
- **Client state**: Zustand for global state, React state for local
- **Form state**: React Hook Form with Zod validation
- **URL state**: Next.js router for navigation state

## Error Handling
- **Error boundaries** for component-level error catching
- **Sentry integration** for production error tracking
- **Zod validation** for runtime type checking
- **Graceful degradation** for non-critical features

## Accessibility Standards
- **WCAG 2.2 AA compliance** as minimum standard (upgraded from 2.1)
- **Semantic HTML** structure required
- **ARIA labels** for interactive elements
- **Keyboard navigation** support for all interactions
- **Focus management** with visible focus indicators (teal focus rings)

## Migration-Specific Conventions
- **Always check feature flag** when adding new UI components
- **Use new component variants** from `@/components/ui/*`
- **Test with both themes** during transition period
- **Prefer new design tokens** over legacy color references
- **Document migration status** in component comments if needed