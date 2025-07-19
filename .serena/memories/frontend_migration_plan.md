# Frontend Design Migration Plan

## Overview
This memory contains the comprehensive plan for migrating the teal-based light theme design system from the `front-end-design-refactor` branch to the `main` branch.

## Key Components

### Migration Timeline (4 weeks)
1. **Week 1**: Foundation & Core Components
   - Design system CSS setup
   - Tailwind configuration updates  
   - Typography and Button component migration
   - Feature flag implementation

2. **Week 2**: Navigation & Layout Components
   - Top navigation migration
   - App sidebar updates
   - Page-by-page migration (Dashboard → Assessments → Evidence → Policies → Reports)

3. **Week 3**: Forms & Interactive Components
   - Input fields, selects, checkboxes
   - Modal dialogs, toast notifications
   - Theme-aware component wrappers

4. **Week 4**: Testing & Cleanup
   - Visual regression and accessibility testing
   - Gradual rollout (10% → 25% → 100%)
   - Remove feature flags and cleanup

### Key Technical Details

#### Feature Flag System
- Environment variable: `NEXT_PUBLIC_USE_NEW_THEME`
- Allows parallel theme testing
- Easy rollback mechanism

#### Design System Changes
- **Colors**: Dark purple/cyan → Light teal (#2C7A7B) theme
- **File**: `frontend/app/styles/design-system.css` (13.82 KB)
- **Typography**: Inter font with comprehensive scale
- **Spacing**: 8px grid system

#### Implementation Commands
```bash
# Cherry-pick design system
git checkout front-end-design-refactor -- frontend/app/styles/design-system.css

# Create migration branch
git checkout -b feature/teal-theme-migration

# Test with new theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev
```

### Risk Mitigation
- Backward compatibility maintained
- Feature flags for safe rollback
- A/B testing approach
- Performance monitoring

### Success Criteria
- No breaking changes
- WCAG 2.2 AA compliance maintained
- Positive user feedback
- No performance degradation

## Related Files
- `FRONTEND_REFACTOR_ANALYSIS.md` - Detailed change analysis
- `frontend/app/styles/design-system.css` - New design system
- `frontend/components/ui/` - Updated components