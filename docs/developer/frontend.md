# Frontend Development Guide

## Overview

The ruleIQ frontend is built with Next.js 15, TypeScript, and follows a component-based architecture using shadcn/ui components with Tailwind CSS. This guide covers the current teal design system implementation and development workflows.

## Current Status: Teal Design System Migration

- **Progress**: Foundation established, implementation ongoing
- **Design System**: Migrating from purple/cyan to teal color palette
- **Key Document**: `frontend/FRONTEND_DESIGN_COMPLIANCE_PLAN.md`

## Quick Start

```bash
cd frontend
pnpm install
pnpm dev  # Starts on http://localhost:3000
```

## Design System

### Color Palette
```css
/* Primary teal colors */
--teal-600: #2C7A7B;   /* PRIMARY BRAND */
--teal-700: #285E61;   /* Hover states */
--teal-50: #E6FFFA;    /* Light backgrounds */
--teal-300: #4FD1C5;   /* Bright accents */
```

### Core Tokens
- **Font**: Inter (Google Fonts)
- **Spacing**: 8px grid system
- **Border Radius**: 8px primary, 12px large
- **Shadows**: CSS custom properties
- **Animation**: 200ms ease-out transitions

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (dashboard)/       # Dashboard pages
│   ├── (auth)/           # Authentication pages
│   ├── marketing/        # Marketing pages
│   └── globals.css       # Global styles
├── components/           # React components
│   ├── ui/              # shadcn/ui components
│   └── custom/          # Custom components
├── lib/                 # Utilities and configurations
│   ├── api/            # API client functions
│   ├── stores/         # Zustand state stores
│   └── utils/          # Utility functions
└── public/             # Static assets
```

## State Management

- **Client State**: Zustand stores
- **Server State**: TanStack Query
- **Form State**: React Hook Form

## Testing

```bash
# Unit tests
pnpm test

# Type checking
pnpm typecheck

# Linting
pnpm lint

# Build verification
pnpm build
```

## Development Workflow

1. **Feature Development**: Create feature branch
2. **Component Creation**: Use shadcn/ui patterns
3. **State Management**: Implement Zustand stores
4. **API Integration**: Use TanStack Query hooks
5. **Testing**: Write component tests
6. **Code Quality**: Run lint and typecheck

## Migration Tasks

### Active Migration: Purple/Cyan → Teal
- Replace hardcoded color values
- Update component variants
- Migrate Aceternity components
- Implement design tokens

### Commands
```bash
# Test with new theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev

# Run all checks
pnpm test && pnpm typecheck && pnpm lint
```

## Best Practices

1. **Components**: Use shadcn/ui as base, customize with Tailwind
2. **State**: Keep client and server state separate
3. **Types**: Use TypeScript strictly, avoid `any`
4. **Performance**: Optimize images and bundle size
5. **Accessibility**: Maintain WCAG 2.2 AA compliance

## Troubleshooting

### Common Issues
- **Build Errors**: Check TypeScript errors with `pnpm typecheck`
- **Style Issues**: Verify Tailwind class usage
- **API Errors**: Check network tab and API client configuration

For detailed frontend migration documentation, see the files in `frontend/docs/`.