# Frontend Design Migration Plan

## Migrating `front-end-design-refactor` → `main`

### 🎯 Objective

Safely merge the new teal-based light theme design system from the refactor branch into the main branch while maintaining stability and allowing for gradual adoption.

---

## 📅 Migration Timeline

### **Week 1: Foundation & Core Components**

**Goal**: Establish design system infrastructure without breaking existing functionality

#### Day 1-2: Design System Setup

```bash
# 1. Create design system CSS file
git checkout main
git checkout front-end-design-refactor -- frontend/app/styles/design-system.css

# 2. Update globals.css to import design system
# Add at top of globals.css:
@import './styles/design-system.css';

# 3. Create feature flag for theme switching
# In frontend/lib/features/theme-flags.ts:
export const USE_NEW_THEME = process.env.NEXT_PUBLIC_USE_NEW_THEME === 'true';
```

#### Day 3-4: Tailwind Configuration

```javascript
// Update tailwind.config.ts to support both themes:
const config = {
  theme: {
    extend: {
      colors: {
        // New teal theme colors
        teal: {
          50: '#E6FFFA',
          100: '#B2F5EA',
          // ... rest of teal scale
          600: '#2C7A7B', // Primary
          700: '#285E61',
        },

        // Keep existing colors for backward compatibility
        brand: {
          primary: process.env.NEXT_PUBLIC_USE_NEW_THEME ? '#2C7A7B' : '#7C3AED',
          // ... map other colors conditionally
        },
      },
    },
  },
};
```

#### Day 5: Core Components Migration

1. **Typography Component**:

   ```bash
   git checkout front-end-design-refactor -- frontend/components/ui/typography.tsx
   ```

2. **Button Component** (with theme support):
   ```typescript
   // Modify button.tsx to support both themes:
   const buttonVariants = cva('...', {
     variants: {
       variant: {
         default: USE_NEW_THEME
           ? 'bg-teal-600 text-white hover:bg-teal-700'
           : 'bg-primary text-primary-foreground hover:bg-primary/90',
         // ... other variants
       },
     },
   });
   ```

---

### **Week 2: Navigation & Layout Components**

#### Day 1-2: Navigation Components

1. **Top Navigation Migration**:
   - Create `top-navigation-new.tsx` alongside existing
   - Use feature flag to conditionally render
   - Test both versions in parallel

2. **App Sidebar Migration**:
   - Follow same pattern as top navigation
   - Ensure menu items work with both themes

#### Day 3-5: Page-by-Page Migration

Priority order:

1. Dashboard page
2. Assessments pages
3. Evidence management
4. Policies section
5. Reports and analytics

---

### **Week 3: Forms & Interactive Components**

#### Components to Migrate:

- Input fields
- Select dropdowns
- Checkboxes and radios
- Form validation states
- Modal dialogs
- Toast notifications

#### Migration Strategy:

```typescript
// Create theme-aware component wrappers:
export const ThemedInput = (props) => {
  const className = USE_NEW_THEME
    ? "border-neutral-200 focus:border-teal-600"
    : "border-input focus:border-primary";

  return <Input className={className} {...props} />;
};
```

---

### **Week 4: Testing & Cleanup**

#### Day 1-2: Comprehensive Testing

- [ ] Visual regression testing
- [ ] Accessibility audit (WCAG 2.2 AA)
- [ ] Cross-browser testing
- [ ] Mobile responsiveness
- [ ] Performance metrics

#### Day 3-4: Gradual Rollout

1. Enable new theme for internal team (10%)
2. A/B test with 25% of users
3. Monitor feedback and metrics
4. Full rollout if metrics are positive

#### Day 5: Cleanup

- Remove feature flags
- Delete old theme code
- Update documentation
- Archive dark theme assets

---

## 🛠️ Implementation Commands

### 1. Cherry-pick Specific Files

```bash
# Switch to main branch
git checkout main

# Cherry-pick design system file
git checkout front-end-design-refactor -- frontend/app/styles/design-system.css

# Cherry-pick specific components
git checkout front-end-design-refactor -- frontend/components/ui/typography.tsx
git checkout front-end-design-refactor -- frontend/components/ui/button.tsx
```

### 2. Create Migration Branch

```bash
# Create a new branch for migration
git checkout -b feature/teal-theme-migration

# Apply changes incrementally
git add frontend/app/styles/design-system.css
git commit -m "feat: add new teal-based design system"

# Continue with other components...
```

### 3. Testing Commands

```bash
# Run with new theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev

# Run with old theme (default)
pnpm dev

# Run tests with both themes
NEXT_PUBLIC_USE_NEW_THEME=true pnpm test
NEXT_PUBLIC_USE_NEW_THEME=false pnpm test
```

---

## ⚠️ Risk Mitigation

### 1. **Feature Flags**

- Use environment variables for easy rollback
- Test both themes in parallel
- Gradual user rollout

### 2. **Backward Compatibility**

- Keep old color mappings temporarily
- Support both theme systems during migration
- No breaking changes to component APIs

### 3. **Monitoring**

- Track user engagement metrics
- Monitor error rates
- Collect user feedback
- A/B test performance

### 4. **Rollback Plan**

```bash
# If issues arise, quickly rollback:
NEXT_PUBLIC_USE_NEW_THEME=false pnpm build
# Deploy with old theme active
```

---

## 📋 Pre-Migration Checklist

- [ ] Backup current main branch
- [ ] Document all custom CSS overrides
- [ ] Identify hardcoded color values
- [ ] Review component dependencies
- [ ] Set up feature flags
- [ ] Prepare rollback procedures
- [ ] Brief the team on changes
- [ ] Set up monitoring dashboards

---

## 🎯 Success Criteria

1. **No Breaking Changes**: Existing functionality remains intact
2. **Performance**: No degradation in load times or runtime
3. **Accessibility**: Maintain or improve WCAG compliance
4. **User Satisfaction**: Positive feedback from A/B testing
5. **Developer Experience**: Clear migration path for team

---

## 📚 Resources

- [Design System Documentation](./frontend/app/styles/design-system.css)
- [Typography Guidelines](./frontend/components/ui/typography.tsx)
- [Color Migration Guide](./FRONTEND_REFACTOR_ANALYSIS.md)
- [Component Library](./frontend/components/ui/)

---

## 🚀 Next Steps

1. Review and approve migration plan
2. Set up feature flags infrastructure
3. Begin Week 1 implementation
4. Schedule daily standup for migration progress
5. Prepare user communication about upcoming changes
