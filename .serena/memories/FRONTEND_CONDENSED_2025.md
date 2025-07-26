# Frontend Development - Condensed Reference (July 2025)

## Current Status: Teal Design System Migration
- **Progress**: 65% complete - Foundation established, implementation gaps remain
- **Timeline**: 4 weeks to completion
- **Key Document**: `frontend/FRONTEND_DESIGN_COMPLIANCE_PLAN.md`

## Design System Quick Reference

### Teal Color Palette
```css
--teal-600: #2C7A7B;   /* PRIMARY BRAND */
--teal-700: #285E61;   /* Hover states */
--teal-50: #E6FFFA;    /* Light backgrounds */
--teal-300: #4FD1C5;   /* Bright accents */
```

### Core Design Tokens
- **Font**: Inter (Google Fonts)
- **Spacing**: 8px grid system
- **Radius**: 8px primary, 12px large
- **Shadows**: --shadow-sm through --shadow-lg
- **Animation**: 200ms ease-out (base)

## Critical Implementation Tasks

### Phase 1: Foundation (CRITICAL - Week 1)
1. **Tailwind Config**: Replace purple (#7C3AED) and cyan (#06B6D4) with teal
2. **Aceternity Removal**: Delete `frontend/components/ui/aceternity/` directory
3. **Feature Flags**: Implement `NEXT_PUBLIC_USE_NEW_THEME` for gradual rollout

### Phase 2: Components (HIGH - Week 2)
1. **Buttons**: Remove turquoise variant, use teal system
2. **Navigation**: Fix surface-primary and gradient-text classes
3. **Forms**: Implement teal focus states
4. **Cards**: 12px radius with teal accents

### Phase 3: Color Migration (HIGH - Week 2-3)
- Replace all hardcoded #7C3AED and #06B6D4
- Update chart color palettes to teal variants
- Component-by-component migration

### Phase 4: Advanced UI (MEDIUM - Week 3-4)
- Loading states with teal shimmer
- Modal patterns with teal headers
- Enhanced tooltips and popovers

### Phase 5: Testing (HIGH - Week 4)
- Visual regression testing
- Maintain 98% WCAG 2.2 AA compliance
- Performance optimization (<5% bundle increase)

## Key Files
- Design System: `frontend/app/styles/design-system.css`
- Tailwind Config: `frontend/tailwind.config.ts`
- Global Styles: `frontend/app/globals.css`

## Migration Commands
```bash
# Test with new theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev

# Run frontend tests
cd frontend && pnpm test
cd frontend && pnpm typecheck
cd frontend && pnpm lint
```

## Success Metrics
- 100% design token usage (no hardcoded colors)
- 98% WCAG 2.2 AA compliance maintained
- <5% bundle size increase
- All visual regression tests passing

## References
- Full plan: `frontend/FRONTEND_DESIGN_COMPLIANCE_PLAN.md`
- Design framework: `frontend/design_framework.md`
- Original memories: new_design_system, FRONTEND_DESIGN_COMPLIANCE_WORKFLOW, frontend_migration_plan