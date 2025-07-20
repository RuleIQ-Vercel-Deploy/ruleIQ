# Suggested Development Commands

## Package Management (Required: pnpm)
```bash
# Install dependencies
pnpm install

# Add new dependency
pnpm add <package-name>

# Add dev dependency
pnpm add -D <package-name>
```

## Development Server
```bash
# Start development server (http://localhost:3000)
pnpm dev

# Start production build locally
pnpm build && pnpm start
```

## Code Quality & Validation
```bash
# Type checking (run manually - build ignores TS errors)
pnpm typecheck
# or
pnpm tsc --noEmit

# Linting
pnpm lint
pnpm lint:fix

# Code formatting
pnpm format
pnpm format:check
```

## Testing Commands
```bash
# Unit tests (Vitest)
pnpm test
pnpm test:watch
pnpm test:coverage
pnpm test:ui

# End-to-end tests (Playwright)
pnpm test:e2e
pnpm test:e2e:ui
pnpm test:e2e:headed
pnpm test:e2e:debug

# Specific test suites
pnpm test:e2e:smoke
pnpm test:e2e:accessibility
pnpm test:performance
pnpm test:visual
pnpm test:visual:update

# Memory leak testing
pnpm test:memory-leaks
pnpm test:memory-leaks:watch
```

## Build & Production
```bash
# Production build
pnpm build

# Build with bundle analysis
pnpm build:analyze

# Staging build
pnpm build:staging

# Production build
pnpm build:production
```

## Storybook (Component Development)
```bash
# Start Storybook dev server
pnpm storybook

# Build Storybook for production
pnpm build-storybook

# Run Storybook tests
pnpm test:storybook
```

## CI/CD Pipeline
```bash
# Run full CI pipeline locally
pnpm ci

# Preview build
pnpm preview
```

## System Commands (Linux)
```bash
# File operations
ls -la                 # List files with details
find . -name "*.tsx"   # Find TypeScript React files
grep -r "searchterm"   # Search in files
cd /path/to/directory  # Change directory

# Git operations
git status
git add .
git commit -m "message"
git push origin main
git pull origin main

# Process management
ps aux | grep node     # Find Node processes
kill -9 <pid>         # Force kill process
netstat -tlnp | grep :3000  # Check port 3000
```

## Debugging & Analysis
```bash
# Bundle analysis
pnpm analyze:bundle
pnpm analyze:bundle:ci

# Memory leak analysis
pnpm test:memory-leaks:report

# Performance testing
pnpm test:performance
```

## Essential Development Workflow
1. `pnpm dev` - Start development
2. `pnpm typecheck` - Verify types before committing
3. `pnpm lint` - Check code style
4. `pnpm test --run` - Run unit tests
5. `pnpm build` - Verify production build works