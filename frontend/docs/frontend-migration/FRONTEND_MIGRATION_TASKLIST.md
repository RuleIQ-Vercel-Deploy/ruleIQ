# Frontend Migration Task List
## Teal Design System Implementation

### 🎯 **Migration Overview**
Systematic migration from dark purple/cyan theme to professional teal-based light theme across 25+ pages and 200+ components.

---

## **Phase 1: Foundation & Infrastructure Setup** 
*Priority: HIGH | Estimated: 1-2 days*

### 1.1 Design System Integration
- [ ] **1.1.1** Cherry-pick design system CSS file
  ```bash
  git checkout front-end-design-refactor -- frontend/app/styles/design-system.css
  ```
- [ ] **1.1.2** Update `globals.css` to import design system
  ```css
  @import './styles/design-system.css';
  ```
- [ ] **1.1.3** Verify CSS custom properties are accessible
- [ ] **1.1.4** Test design tokens in browser dev tools

### 1.2 Feature Flag Implementation
- [ ] **1.2.1** Create feature flag file `frontend/lib/features/theme-flags.ts`
  ```typescript
  export const USE_NEW_THEME = process.env.NEXT_PUBLIC_USE_NEW_THEME === 'true';
  ```
- [ ] **1.2.2** Add environment variable to `.env.local`
  ```
  NEXT_PUBLIC_USE_NEW_THEME=true
  ```
- [ ] **1.2.3** Test feature flag functionality
- [ ] **1.2.4** Document feature flag usage for team

### 1.3 Tailwind Configuration Update
- [ ] **1.3.1** Cherry-pick updated `tailwind.config.ts`
  ```bash
  git checkout front-end-design-refactor -- frontend/tailwind.config.ts
  ```
- [ ] **1.3.2** Verify teal color scale integration
- [ ] **1.3.3** Test Tailwind classes in browser
- [ ] **1.3.4** Ensure backward compatibility with existing classes

### 1.4 Typography Integration
- [ ] **1.4.1** Verify Inter font loading from Google Fonts
- [ ] **1.4.2** Test typography scale across different screen sizes
- [ ] **1.4.3** Validate font weight variations
- [ ] **1.4.4** Check font rendering across browsers

---

## **Phase 2: Core UI Components Migration**
*Priority: HIGH | Estimated: 2-3 days*

### 2.1 Typography Component
- [ ] **2.1.1** Cherry-pick updated typography component
  ```bash
  git checkout front-end-design-refactor -- frontend/components/ui/typography.tsx
  ```
- [ ] **2.1.2** Test all typography variants (h1-h6, body, caption, etc.)
- [ ] **2.1.3** Verify color mappings (navy → teal)
- [ ] **2.1.4** Update Storybook documentation if exists

### 2.2 Button Component
- [ ] **2.2.1** Update button variants to use teal colors
  - [ ] Primary: `bg-teal-600` → `hover:bg-teal-700`
  - [ ] Secondary: `bg-neutral-100` → `hover:bg-neutral-200`
  - [ ] Ghost: `text-teal-600` → `hover:bg-teal-50`
  - [ ] Destructive: Keep red colors
- [ ] **2.2.2** Update focus states to use teal rings
- [ ] **2.2.3** Test all button sizes (sm, default, lg, icon)
- [ ] **2.2.4** Verify loading states with teal spinner
- [ ] **2.2.5** Test accessibility (contrast, focus, keyboard nav)

### 2.3 Form Components
- [ ] **2.3.1** Update Input component
  - [ ] Border: `border-neutral-200`
  - [ ] Focus: `focus:border-teal-600` + `focus:ring-teal-600`
  - [ ] Placeholder: `placeholder-neutral-400`
- [ ] **2.3.2** Update Select component
- [ ] **2.3.3** Update Textarea component
- [ ] **2.3.4** Update Checkbox component (teal checked state)
- [ ] **2.3.5** Update Radio Group component
- [ ] **2.3.6** Test form validation states (error, success, warning)

### 2.4 Card Component
- [ ] **2.4.1** Update card styling
  - [ ] Background: `bg-white`
  - [ ] Border: `border-neutral-200`
  - [ ] Shadow: `shadow-sm` → `hover:shadow-md`
- [ ] **2.4.2** Test card variants (default, outlined, elevated)
- [ ] **2.4.3** Verify card hover effects
- [ ] **2.4.4** Test responsive behavior

### 2.5 Alert Component
- [ ] **2.5.1** Update alert variants
  - [ ] Info: Use `info-500` blue
  - [ ] Success: Use `success-500` green
  - [ ] Warning: Use `warning-500` amber
  - [ ] Error: Use `error-500` red
- [ ] **2.5.2** Test alert icons and colors
- [ ] **2.5.3** Verify accessibility (ARIA labels, contrast)

### 2.6 Badge Component
- [ ] **2.6.1** Update badge colors to use teal variants
- [ ] **2.6.2** Test badge sizes and variants
- [ ] **2.6.3** Verify text contrast on colored backgrounds

---

## **Phase 3: Navigation Components Migration**
*Priority: HIGH | Estimated: 2-3 days*

### 3.1 App Sidebar
- [ ] **3.1.1** Cherry-pick updated sidebar component
  ```bash
  git checkout front-end-design-refactor -- frontend/components/navigation/app-sidebar.tsx
  ```
- [ ] **3.1.2** Update sidebar styling
  - [ ] Background: `bg-white`
  - [ ] Border: `border-r border-neutral-200`
  - [ ] Menu items: `text-neutral-600` → `hover:text-neutral-900`
  - [ ] Active item: `bg-teal-50 text-teal-700`
- [ ] **3.1.3** Test collapsible menu functionality
- [ ] **3.1.4** Verify mobile responsive behavior
- [ ] **3.1.5** Test keyboard navigation

### 3.2 Top Navigation
- [ ] **3.2.1** Cherry-pick updated top navigation
  ```bash
  git checkout front-end-design-refactor -- frontend/components/navigation/top-navigation.tsx
  ```
- [ ] **3.2.2** Update navigation styling
  - [ ] Background: `bg-white`
  - [ ] Border: `border-b border-neutral-200`
  - [ ] Search: `focus:border-teal-600`
  - [ ] User menu: Teal accent colors
- [ ] **3.2.3** Test search functionality
- [ ] **3.2.4** Verify notification dropdown
- [ ] **3.2.5** Test user profile menu

### 3.3 Breadcrumb Navigation
- [ ] **3.3.1** Update breadcrumb colors to teal
- [ ] **3.3.2** Test breadcrumb separators and links
- [ ] **3.3.3** Verify truncation for long paths

### 3.4 Mobile Navigation
- [ ] **3.4.1** Update mobile menu styling
- [ ] **3.4.2** Test hamburger menu animation
- [ ] **3.4.3** Verify mobile overlay and backdrop

---

## **Phase 4: Page-by-Page Migration**
*Priority: MEDIUM | Estimated: 4-5 days*

### 4.1 Authentication Pages (4 pages)
- [ ] **4.1.1** Login page (`/login`)
  - [ ] Update SecurityBadges component colors
  - [ ] Test form styling with teal focus states
  - [ ] Verify trust signals and branding
- [ ] **4.1.2** Signup page (`/signup`)
- [ ] **4.1.3** Register page (`/register`)
- [ ] **4.1.4** Signup Traditional page (`/signup-traditional`)

### 4.2 Dashboard Pages (3 pages)
- [ ] **4.2.1** Main Dashboard (`/dashboard`)
  - [ ] Update chart colors to teal palette
  - [ ] Test ComplianceScoreWidget with teal gauge
  - [ ] Update EnhancedStatsCard styling
  - [ ] Verify AIInsightsWidget colors
  - [ ] Test PendingTasksWidget
  - [ ] Update QuickActionsWidget
- [ ] **4.2.2** Custom Dashboard (`/dashboard-custom`)
- [ ] **4.2.3** Analytics page (`/analytics`)

### 4.3 Assessment Pages (4 pages)
- [ ] **4.3.1** Assessments List (`/assessments`)
  - [ ] Update DataTable styling
  - [ ] Test assessment status badges
  - [ ] Verify filter dropdowns
- [ ] **4.3.2** New Assessment (`/assessments/new`)
  - [ ] Update AssessmentWizard styling
  - [ ] Test FrameworkSelector cards
  - [ ] Verify stepper component
- [ ] **4.3.3** Assessment Detail (`/assessments/[id]`)
  - [ ] Update QuestionRenderer styling
  - [ ] Test ProgressTracker
  - [ ] Verify conditional question logic
- [ ] **4.3.4** Assessment Results (`/assessments/[id]/results`)
  - [ ] Update ComplianceGauge colors
  - [ ] Test RadarChart with teal palette
  - [ ] Update GapAnalysisCard styling
  - [ ] Verify RecommendationCard
  - [ ] Test ActionItemsList

### 4.4 Evidence Pages (2 pages)
- [ ] **4.4.1** Evidence List (`/evidence`)
  - [ ] Update EvidenceCard styling
  - [ ] Test FilterSidebar
  - [ ] Verify BulkActionsBar
  - [ ] Update status badges
- [ ] **4.4.2** Evidence Upload (`/evidence/upload`)
  - [ ] Update FileUploader styling
  - [ ] Test FilePreviewCard
  - [ ] Verify upload progress indicators

### 4.5 Policy Pages (2 pages)
- [ ] **4.5.1** Policies List (`/policies`)
  - [ ] Update policy cards
  - [ ] Test status indicators
  - [ ] Verify action buttons
- [ ] **4.5.2** New Policy (`/policies/new`)
  - [ ] Update policy wizard
  - [ ] Test SelectionCard styling
  - [ ] Verify GenerationProgress

### 4.6 Settings Pages (3 pages)
- [ ] **4.6.1** Team Management (`/settings/team`)
  - [ ] Update TeamMembersTable
  - [ ] Test InviteMemberDialog
  - [ ] Verify PermissionMatrixCard
- [ ] **4.6.2** Integrations (`/settings/integrations`)
  - [ ] Update IntegrationCard styling
  - [ ] Test connection dialogs
- [ ] **4.6.3** Billing (`/settings/billing`)
  - [ ] Update PricingCard
  - [ ] Test CheckoutForm

### 4.7 Other Pages
- [ ] **4.7.1** Chat page (`/chat`)
  - [ ] Update chat message styling
  - [ ] Test conversation sidebar
  - [ ] Verify typing indicators
- [ ] **4.7.2** Reports page (`/reports`)
  - [ ] Update report cards
  - [ ] Test data tables

---

## **Phase 5: Testing & Quality Assurance**
*Priority: MEDIUM | Estimated: 2-3 days*

### 5.1 Visual Regression Testing
- [ ] **5.1.1** Screenshot comparison tests
  - [ ] Desktop screenshots (1920x1080)
  - [ ] Tablet screenshots (768x1024)
  - [ ] Mobile screenshots (375x667)
- [ ] **5.1.2** Component state testing
  - [ ] Default states
  - [ ] Hover states
  - [ ] Focus states
  - [ ] Active states
  - [ ] Disabled states

### 5.2 Accessibility Testing
- [ ] **5.2.1** WCAG 2.2 AA compliance audit
  - [ ] Color contrast verification (all combinations)
  - [ ] Keyboard navigation testing
  - [ ] Screen reader testing (NVDA/JAWS)
  - [ ] Focus indicator visibility
- [ ] **5.2.2** Accessibility automation tests
  - [ ] axe-core integration tests
  - [ ] Lighthouse accessibility scores
- [ ] **5.2.3** Manual accessibility testing
  - [ ] Tab order verification
  - [ ] ARIA label accuracy
  - [ ] Semantic HTML validation

### 5.3 Cross-Browser Testing
- [ ] **5.3.1** Desktop browsers
  - [ ] Chrome (latest)
  - [ ] Firefox (latest)
  - [ ] Safari (latest)
  - [ ] Edge (latest)
- [ ] **5.3.2** Mobile browsers
  - [ ] iOS Safari
  - [ ] Android Chrome
  - [ ] Samsung Internet

### 5.4 Performance Testing
- [ ] **5.4.1** Core Web Vitals
  - [ ] Largest Contentful Paint (LCP)
  - [ ] First Input Delay (FID)
  - [ ] Cumulative Layout Shift (CLS)
- [ ] **5.4.2** Bundle size analysis
  - [ ] CSS bundle impact
  - [ ] JavaScript bundle impact
  - [ ] Font loading optimization

### 5.5 Functional Testing
- [ ] **5.5.1** Feature flag testing
  - [ ] New theme enabled
  - [ ] New theme disabled
  - [ ] Toggle functionality
- [ ] **5.5.2** Interactive component testing
  - [ ] Form submissions
  - [ ] Modal interactions
  - [ ] Navigation functionality
  - [ ] Data table operations

---

## **Phase 6: Gradual Rollout & Cleanup**
*Priority: LOW | Estimated: 1-2 days*

### 6.1 Staged Rollout
- [ ] **6.1.1** Internal team testing (10%)
  - [ ] Enable for development team
  - [ ] Gather feedback
  - [ ] Fix critical issues
- [ ] **6.1.2** Beta user testing (25%)
  - [ ] A/B test setup
  - [ ] User feedback collection
  - [ ] Analytics monitoring
- [ ] **6.1.3** Gradual expansion (50% → 100%)
  - [ ] Monitor error rates
  - [ ] Track user engagement
  - [ ] Performance monitoring

### 6.2 Monitoring & Metrics
- [ ] **6.2.1** Set up monitoring dashboards
  - [ ] Error rate tracking
  - [ ] User engagement metrics
  - [ ] Performance metrics
- [ ] **6.2.2** User feedback collection
  - [ ] In-app feedback widget
  - [ ] User satisfaction surveys
  - [ ] Support ticket analysis

### 6.3 Final Cleanup
- [ ] **6.3.1** Remove feature flags
  - [ ] Delete theme flag code
  - [ ] Remove conditional styling
  - [ ] Update environment variables
- [ ] **6.3.2** Remove old theme code
  - [ ] Delete unused CSS variables
  - [ ] Remove old color mappings
  - [ ] Clean up component variants
- [ ] **6.3.3** Documentation updates
  - [ ] Update component documentation
  - [ ] Update style guide
  - [ ] Team training materials

### 6.4 Archive & Documentation
- [ ] **6.4.1** Archive old design assets
  - [ ] Move old theme files to archive
  - [ ] Document migration process
  - [ ] Create rollback procedures
- [ ] **6.4.2** Update project documentation
  - [ ] Design system documentation
  - [ ] Component usage guidelines
  - [ ] Migration lessons learned

---

## **🚨 Critical Success Criteria**

### Must-Have Requirements
- [ ] Zero breaking changes to existing functionality
- [ ] WCAG 2.2 AA accessibility compliance maintained
- [ ] No performance degradation (Core Web Vitals)
- [ ] All 25+ pages render correctly
- [ ] Feature flag rollback works properly

### Quality Gates
- [ ] 100% visual regression tests pass
- [ ] 95%+ accessibility score maintained
- [ ] Core Web Vitals remain in "Good" range
- [ ] Zero critical bugs in production
- [ ] User satisfaction >= 4.0/5.0

---

## **⚡ Quick Commands Reference**

```bash
# Enable new theme for testing
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev

# Run tests with new theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm test

# Build with new theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm build

# Cherry-pick specific components
git checkout front-end-design-refactor -- frontend/components/ui/button.tsx

# Start migration branch
git checkout -b feature/teal-theme-migration
```

---

## **📋 Daily Checklist Template**

### Before Starting Work
- [ ] Pull latest changes from main
- [ ] Verify feature flag is set correctly
- [ ] Check design system CSS is loaded
- [ ] Test basic functionality works

### During Development
- [ ] Test component in isolation
- [ ] Verify accessibility (contrast, focus)
- [ ] Test responsive behavior
- [ ] Check cross-browser compatibility

### Before Committing
- [ ] Run linting and type checking
- [ ] Test with both themes (flag on/off)
- [ ] Verify no console errors
- [ ] Update task list progress

---

*Migration Task List v1.0 | Total Estimated Time: 12-16 days*  
*Last Updated: 2025-01-18*