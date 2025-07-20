# Task Completion Checklist

## Before Committing Changes

### Code Quality Checks (Required)
```bash
# 1. Type checking (CRITICAL - build ignores TS errors)
pnpm typecheck

# 2. Linting (fix auto-fixable issues)
pnpm lint:fix

# 3. Code formatting
pnpm format

# 4. Unit tests
pnpm test --run
```

### Build Verification
```bash
# 5. Production build test
pnpm build

# 6. Start production server (optional verification)
pnpm start
```

### Feature-Specific Testing
```bash
# For UI components
pnpm test:visual

# For accessibility changes
pnpm test:e2e:accessibility

# For performance-critical changes
pnpm test:performance

# For E2E functionality
pnpm test:e2e:smoke
```

## Security & Best Practices
- [ ] No secrets/API keys in code
- [ ] Proper error boundaries implemented
- [ ] Loading states handled
- [ ] Accessibility requirements met (WCAG 2.1 AA)
- [ ] Mobile responsiveness verified
- [ ] Dark mode compatibility checked

## Documentation Updates
- [ ] Component props documented (if applicable)
- [ ] README updated for new features
- [ ] CHANGELOG entry added
- [ ] Storybook stories updated/added

## Performance Considerations
- [ ] Bundle size impact assessed (`pnpm build:analyze`)
- [ ] Image optimization verified
- [ ] Code splitting appropriate
- [ ] Memory leaks checked (`pnpm test:memory-leaks`)

## Production Readiness
- [ ] Error handling implemented
- [ ] Loading states defined
- [ ] Edge cases considered
- [ ] Cross-browser compatibility verified
- [ ] SEO considerations (meta tags, semantic HTML)

## Git Workflow
```bash
# Pre-commit hooks will run automatically, but manual verification:
git add .
git status
git commit -m "feat: descriptive commit message"
git push origin branch-name
```

## Critical Notes
- **TypeScript errors are ignored in build** - Always run `pnpm typecheck`
- **ESLint errors are ignored in build** - Always run `pnpm lint`
- **Use pnpm** (not npm/yarn) for package management
- **Test in production mode** before deploying critical changes
- **Visual regression tests** for UI changes
- **E2E tests** for user flow changes