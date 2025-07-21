# ruleIQ Frontend Production Build Prompts

## Overview

This document contains bite-sized prompts to complete the ruleIQ frontend build for production. Each prompt is self-contained and can be executed independently.

## Phase 1: Component Library Cleanup (Week 1)

### Prompt 1.1: Remove Aceternity Components

```
Task: Remove all aceternity UI components and replace with shadcn/ui equivalents.

Context:
- Project: ruleIQ compliance automation platform
- Location: /home/omar/Documents/ruleIQ/frontend
- Current state: Mixed component libraries causing visual inconsistency

Requirements:
1. Delete /components/ui/aceternity/ directory
2. Find all imports of aceternity components (grep -r "aceternity" .)
3. Replace BeamsBackground with CSS gradient pattern
4. Update all affected files to use shadcn/ui components
5. Ensure no visual regression

Deliverables:
- All aceternity imports removed
- Replacement components implemented
- Visual consistency maintained
```

### Prompt 1.2: Standardize Component Variants

```
Task: Audit and standardize all custom component variants to align with shadcn/ui patterns.

Context:
- Design system: Navy (#17255A) primary, Gold (#CB963E) accent
- Current issues: Duplicate size variants, inconsistent naming

Requirements:
1. Audit all components in /components/ui/
2. Remove duplicate size variants (small/medium/large → sm/default/lg)
3. Standardize variant naming (navy → primary, gold → accent)
4. Update all component usage across the app
5. Document breaking changes

Deliverables:
- Standardized component API
- Migration guide for team
- Zero duplicate variants
```

### Prompt 1.3: Integrate Animated Logo

````
Task: Replace static branding with the new animated hexagon logo throughout the application.

Context:
- New components created: AnimatedLogo and LandingHero
- Current landing page uses inline components and static text
- Logo should spin on first load for premium effect

Requirements:
1. Update /app/page.tsx to use LandingHero component:
   - Import: import { LandingHero } from "@/components/sections/landing-hero"
   - Replace current hero section with <LandingHero />
2. Update navigation components to use NavLogo:
   - Replace static logo in AppSidebar
   - Add to public header if exists
3. Update loading.tsx files to use LoadingLogo component
4. Add favicon and app icons:
   - Generate from hexagon SVG
   - Sizes: 16x16, 32x32, 180x180, 192x192, 512x512
5. Update metadata with new branding

Code example for page.tsx:
```tsx
import { LandingHero } from "@/components/sections/landing-hero"
// ... other imports

export default function HomePage() {
  return (
    <main>
      <LandingHero />
      {/* Keep existing sections below hero */}
    </main>
  )
}
````

Deliverables:

- Animated logo on landing page
- Logo in navigation
- Loading states with spinning logo
- Updated favicons

```

## Phase 2: Design System Enhancement (Week 1-2)

### Prompt 2.1: Migrate Color System to CSS Variables
```

Task: Complete migration from mixed color system to unified CSS variables with OKLCH support.

Context:

- Current: Mix of HSL percentages and named colors
- Target: OKLCH color space for better color management
- File: /app/globals.css and tailwind.config.ts

Requirements:

1. Convert all HSL colors to OKLCH
2. Create semantic color tokens:
   - background, foreground, card, popover
   - primary, secondary, accent, muted
   - success, warning, error, info
3. Update Tailwind config to use CSS variables exclusively
4. Remove all hardcoded color values from components
5. Test in both light and dark themes

Deliverables:

- Unified color system in globals.css
- Updated tailwind.config.ts
- No hardcoded colors in components

```

### Prompt 2.2: Implement Remaining shadcn/ui Components
```

Task: Add missing shadcn/ui components that ruleIQ needs.

Context:

- Current: Basic set of shadcn components
- Needed: Advanced components for compliance workflows

Requirements:

1. Add these shadcn/ui components:
   - npx shadcn-ui@latest add calendar
   - npx shadcn-ui@latest add date-picker
   - npx shadcn-ui@latest add combobox
   - npx shadcn-ui@latest add data-table
   - npx shadcn-ui@latest add timeline
2. Customize each for ruleIQ branding
3. Add TypeScript interfaces for props
4. Create usage examples

Deliverables:

- All components installed and customized
- TypeScript definitions
- Usage documentation

```

## Phase 3: Complete Quick Actions & Productivity Features

### Prompt 3.1: Quick Actions Floating Panel
```

Task: Implement the Quick Actions floating action button panel.

Context:

- User: Alex (power user) and Catherine (bulk operations)
- Design: Floating button in bottom-right, expands to show actions
- Reference: Material Design FAB pattern

Requirements:

1. Create /components/dashboard/quick-actions/quick-actions-panel.tsx
2. Implement floating action button with:
   - Primary action: Create new assessment
   - Secondary actions: Upload evidence, Generate report, Bulk edit
3. Add keyboard shortcuts (Alt+A to open)
4. Animate with Framer Motion (use animation utilities)
5. Persist state in localStorage

Code structure:

- Use Radix UI Popover for accessibility
- Position: fixed bottom-6 right-6
- Gold accent for primary action
- Include tooltips for each action

Deliverables:

- Fully functional quick actions panel
- Keyboard navigation support
- Smooth animations

```

### Prompt 3.2: Keyboard Shortcuts System
```

Task: Implement global keyboard shortcuts with visual dialog.

Context:

- User: Alex (power user)
- Current: Only Cmd+K implemented for command palette
- Need: Comprehensive keyboard navigation

Requirements:

1. Create /components/dashboard/keyboard-shortcuts-dialog.tsx
2. Implement shortcuts:
   - Cmd+N: New assessment
   - Cmd+U: Upload evidence
   - Cmd+/: Show shortcuts dialog
   - Cmd+S: Save current form
   - Cmd+Enter: Submit current form
   - Esc: Close modals/dialogs
3. Visual shortcuts dialog (like Slack/Linear)
4. Store user preferences for custom shortcuts
5. Show shortcuts in tooltips throughout app

Deliverables:

- Global keyboard navigation
- Visual shortcuts reference
- Customizable shortcuts

```

## Phase 4: Performance & Error Handling (Week 2)

### Prompt 4.1: Implement Error Boundaries
```

Task: Add error boundaries throughout the application for graceful error handling.

Context:

- Current: No error boundaries, errors crash the app
- Need: Production-ready error handling

Requirements:

1. Create /components/error-boundary/ directory with:
   - RootErrorBoundary (app-level)
   - DashboardErrorBoundary (feature-level)
   - WidgetErrorBoundary (component-level)
2. Implement error logging to console (later: Sentry)
3. Design error UI that matches ruleIQ branding
4. Add reset functionality
5. Include helpful error messages for users

Deliverables:

- Three levels of error boundaries
- Branded error UI
- Error recovery mechanisms

```

### Prompt 4.2: Code Splitting & Lazy Loading
```

Task: Implement code splitting for optimal performance.

Context:

- Current: All routes loaded upfront
- Target: < 2s TTI, < 1.5s LCP

Requirements:

1. Implement React.lazy for all route components
2. Add loading boundaries for each route
3. Prefetch critical routes (dashboard, assessments)
4. Split large components (charts, editors)
5. Analyze bundle with next-bundle-analyzer

Code example:
const AssessmentsPage = lazy(() => import('./assessments/page'))

Deliverables:

- All routes lazy loaded
- Bundle size < 200KB initial
- Performance metrics documented

```

## Phase 5: Testing & Quality Assurance (Week 2-3)

### Prompt 5.1: Component Testing Suite
```

Task: Implement comprehensive testing for all UI components.

Context:

- Current: Basic test setup with Vitest
- Need: Full component coverage

Requirements:

1. Write tests for each component in /components/ui/:
   - Render tests
   - Interaction tests
   - Accessibility tests
   - Visual regression tests
2. Test user personas scenarios:
   - Alex: Keyboard navigation
   - Ben: Tooltip/help visibility
   - Catherine: Bulk selection
3. Achieve 80% coverage minimum

Deliverables:

- Complete test suite
- Coverage report
- CI/CD integration

```

### Prompt 5.2: Accessibility Audit & Fixes
```

Task: Ensure WCAG AA compliance across the application.

Context:

- Target: WCAG AA compliance
- Users: Including those with disabilities

Requirements:

1. Run axe-core accessibility tests
2. Test with screen readers (NVDA, JAWS)
3. Verify keyboard navigation paths
4. Check color contrast ratios (4.5:1 minimum)
5. Add ARIA labels where needed
6. Test with reduced motion preferences

Deliverables:

- Accessibility report
- All issues fixed
- Documentation for maintaining accessibility

```

## Phase 6: Production Preparation (Week 3)

### Prompt 6.1: Performance Optimization
```

Task: Optimize application for production performance.

Context:

- Targets: TTI < 2s, LCP < 1.5s, CLS < 0.1
- Current: Not measured

Requirements:

1. Implement performance monitoring (Web Vitals)
2. Optimize images (next/image, WebP format)
3. Implement service worker for offline support
4. Add resource hints (preconnect, prefetch)
5. Optimize fonts (subset Inter, font-display: swap)
6. Enable gzip/brotli compression

Deliverables:

- Performance metrics dashboard
- All metrics meeting targets
- Lighthouse score > 90

```

### Prompt 6.2: Security Hardening
```

Task: Implement security best practices for production.

Context:

- Application: Compliance platform (sensitive data)
- Requirements: SOC 2 compliance

Requirements:

1. Add Content Security Policy headers
2. Implement CSRF protection
3. Add rate limiting for API calls
4. Sanitize all user inputs
5. Implement secure session management
6. Add security.txt file

Deliverables:

- Security headers configured
- OWASP Top 10 addressed
- Security documentation

```

## Phase 7: Documentation & Deployment (Week 3-4)

### Prompt 7.1: Complete Documentation
```

Task: Create comprehensive documentation for the platform.

Context:

- Audiences: Developers, designers, end users
- Current: Minimal documentation

Requirements:

1. Create /docs directory with:
   - Getting Started guide
   - Component library docs
   - API documentation
   - Design system guide
   - Deployment guide
2. Add JSDoc comments to all components
3. Create Storybook stories for components
4. Write user guides for each persona

Deliverables:

- Complete documentation site
- Storybook deployed
- User guides published

```

### Prompt 7.2: Production Deployment Setup
```

Task: Configure production deployment pipeline.

Context:

- Platform: Vercel (Next.js optimized)
- Environments: Dev, Staging, Production

Requirements:

1. Configure Vercel project settings
2. Set up environment variables
3. Configure custom domain
4. Implement preview deployments
5. Set up monitoring (Vercel Analytics)
6. Configure error tracking (Sentry)
7. Set up automated backups

Deliverables:

- Production deployed
- Monitoring active
- Rollback procedures documented

```

## Phase 8: Post-Launch Optimization (Week 4+)

### Prompt 8.1: User Analytics Implementation
```

Task: Implement privacy-conscious analytics.

Context:

- Need: Understand user behavior
- Constraint: GDPR compliance

Requirements:

1. Implement Plausible or Fathom analytics
2. Track key user journeys:
   - Onboarding completion
   - Assessment creation
   - Report generation
3. Create analytics dashboard
4. Set up conversion tracking
5. Implement A/B testing framework

Deliverables:

- Analytics implemented
- Dashboard configured
- Privacy policy updated

```

### Prompt 8.2: Progressive Enhancement
```

Task: Add progressive web app features.

Context:

- Users: Often work offline or on slow connections
- Goal: Native app-like experience

Requirements:

1. Implement PWA manifest
2. Add offline support for critical features
3. Enable push notifications for compliance deadlines
4. Implement background sync
5. Add install prompts

Deliverables:

- PWA features active
- Offline functionality
- Push notifications working

```

## Phase 9: Bug Fixing & Error Resolution (Week 4-5)

### Prompt 9.1: Comprehensive Bug Audit
```

Task: Identify and fix all critical bugs before production launch.

Context:

- Platform: Compliance software (zero tolerance for errors)
- Users: SMBs rely on accuracy for compliance

Requirements:

1. Run full test suite and document all failures
2. Check browser console for any errors/warnings
3. Test all user journeys for three personas:
   - Alex: All keyboard shortcuts work
   - Ben: All tooltips and help text display
   - Catherine: Bulk operations handle edge cases
4. Fix critical bugs (P0-P1):
   - Data loss scenarios
   - Security vulnerabilities
   - Accessibility failures
   - Performance bottlenecks
5. Fix major bugs (P2):
   - UI inconsistencies
   - Animation glitches
   - Form validation errors
6. Create bug tracking spreadsheet

Bug Priority Matrix:

- P0: Data loss, security, crashes
- P1: Feature broken, major UX issue
- P2: Visual bugs, minor UX issues
- P3: Nice-to-have improvements

Deliverables:

- Zero P0-P1 bugs
- < 5 P2 bugs documented
- Bug tracking system active

```

### Prompt 9.2: Error Monitoring & Logging
```

Task: Implement comprehensive error tracking for production.

Context:

- Need: Real-time error monitoring
- Goal: < 0.1% error rate

Requirements:

1. Set up Sentry error tracking:
   - Frontend exceptions
   - API errors
   - Performance monitoring
2. Implement custom error logging:
   - User actions before error
   - Browser/device info
   - Session replay for errors
3. Create error dashboard:
   - Real-time error feed
   - Error grouping by type
   - User impact metrics
4. Set up alerts:
   - P0: Immediate Slack/email
   - P1: Within 1 hour
   - P2: Daily digest
5. Error recovery flows:
   - Graceful degradation
   - Retry mechanisms
   - User-friendly error messages

Code example:

```typescript
// lib/error-monitoring.ts
export function logError(error: Error, context?: any) {
  console.error(error);

  if (typeof window !== 'undefined') {
    Sentry.captureException(error, {
      contexts: {
        custom: context,
        userData: getUserContext(),
      },
    });
  }
}
```

Deliverables:

- Sentry configured and active
- Custom error logging implemented
- Alert system configured
- Error dashboard live

```

## Phase 10: Final Polish & Refinement (Week 5)

### Prompt 10.1: UI/UX Polish Pass
```

Task: Final visual and interaction polish before launch.

Context:

- Goal: Premium, professional feel
- Brand: Navy/gold enterprise aesthetic

Requirements:

1. Animation Polish:
   - Ensure all animations are smooth (60fps)
   - Add micro-interactions to buttons/links
   - Polish loading state transitions
   - Verify reduced motion works everywhere
2. Visual Consistency:
   - Audit all spacing (8px grid)
   - Check color usage (navy/gold only as defined)
   - Ensure consistent border radius
   - Verify shadow depths match
3. Typography Refinement:
   - Check line heights for readability
   - Ensure consistent font weights
   - Verify text hierarchy
   - Fix any orphaned words
4. Interactive Feedback:
   - All buttons have hover/active states
   - Form fields show focus clearly
   - Loading states for all async actions
   - Success/error states are clear
5. Edge Case UI:
   - Empty states designed
   - Error states polished
   - Long text doesn't break layouts
   - Tables handle many columns gracefully

Polish Checklist:

- [ ] Every interactive element has feedback
- [ ] Animations feel natural, not jarring
- [ ] Colors are exactly as specified
- [ ] Spacing is consistent throughout
- [ ] Loading states never feel "stuck"
- [ ] Error messages are helpful, not technical

Deliverables:

- Polished UI throughout
- Consistent interactions
- Zero visual bugs

```

### Prompt 10.2: Performance & Final Optimization
```

Task: Final performance optimization and launch readiness check.

Context:

- Target: Sub-2s load time
- Users: May have slower connections

Requirements:

1. Final bundle optimization:
   - Remove all console.logs
   - Tree-shake unused code
   - Optimize all images (WebP format)
   - Minify CSS/JS
   - Enable compression
2. Performance audit:
   - Run Lighthouse on all key pages
   - Check Core Web Vitals
   - Test on slow 3G connection
   - Verify lazy loading works
3. Launch readiness checklist:
   - [ ] All environment variables set
   - [ ] API endpoints pointing to production
   - [ ] Analytics tracking verified
   - [ ] SEO meta tags complete
   - [ ] Sitemap generated
   - [ ] Robots.txt configured
   - [ ] Security headers active
   - [ ] HTTPS enforced
   - [ ] Error pages designed (404, 500)
   - [ ] Legal pages linked (privacy, terms)
4. Final testing matrix:
   - Chrome, Firefox, Safari, Edge
   - Desktop, tablet, mobile
   - Fast and slow connections
   - With and without JS
5. Rollback plan:
   - Document deployment process
   - Create rollback procedure
   - Test rollback in staging

Deliverables:

- All scores > 90 in Lighthouse
- Zero blocking issues
- Launch checklist complete
- Rollback plan documented

```

## Phase 11: Post-Launch Support (Week 5-6)

### Prompt 11.1: Launch Day Monitoring
```

Task: Monitor and respond to launch day issues.

Context:

- Critical: First 48 hours post-launch
- Goal: < 1 hour response time to issues

Requirements:

1. Set up war room:
   - Team available for quick fixes
   - Communication channel active
   - Decision makers on standby
2. Monitor key metrics:
   - Error rates
   - Page load times
   - User signups
   - Feature usage
   - Support tickets
3. Quick fix process:
   - Triage incoming issues
   - Fix critical bugs immediately
   - Document all changes
   - Communicate with users
4. User feedback collection:
   - Monitor support channels
   - Track social media mentions
   - Collect NPS scores
   - Document feature requests

Deliverables:

- Zero downtime
- < 1 hour fix time for P0 bugs
- Daily status reports
- User feedback documented

```

## Success Checklist

Before marking complete, verify:

- [ ] All aceternity components removed
- [ ] Animated logo integrated and working
- [ ] Color system fully migrated to CSS variables
- [ ] All three personas have dedicated features
- [ ] Performance metrics meet targets (TTI < 2s, LCP < 1.5s)
- [ ] WCAG AA compliance achieved
- [ ] 80%+ test coverage
- [ ] Zero P0-P1 bugs remaining
- [ ] Error monitoring active (Sentry)
- [ ] All UI polished and consistent
- [ ] Final performance audit passed (Lighthouse > 90)
- [ ] Documentation complete
- [ ] Security hardened
- [ ] Error boundaries implemented
- [ ] Production deployed and monitored
- [ ] Launch day war room ready
- [ ] Rollback plan documented and tested

## Notes

- Each prompt can be assigned to different team members
- Prompts are ordered by priority but can be parallelized
- Use the existing design system: Navy (#17255A), Gold (#CB963E)
- Maintain the 8px grid system throughout
- Test with all three personas after each phase
- Animated logo components already created in:
  - `/components/ui/animated-logo.tsx`
  - `/components/sections/landing-hero.tsx`
  - Documentation: `/components/ui/animated-logo-docs.md`

---
Generated: January 7, 2025
Platform: ruleIQ Compliance Automation
```
