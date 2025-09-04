# Manual Browser Testing Guide - ruleIQ Frontend

## Quick Start Instructions

### 1. Access the Application

- **URL**: http://localhost:3000
- **Status**: ✅ Running (verified)
- **Browser**: Use Chrome or Firefox for best experience

### 2. Key Testing Routes

#### Homepage Testing

```
URL: http://localhost:3000
FOCUS: Theme consistency, navigation, loading performance
CHECK: Console for hydration warnings
```

#### Authentication Pages

```
Login: http://localhost:3000/login
Signup: http://localhost:3000/signup
FOCUS: Form validation, OAuth integration
```

#### Dashboard (Requires Auth)

```
Main: http://localhost:3000/dashboard
Business Profile: http://localhost:3000/business-profile
FOCUS: Component rendering, data loading
```

## Critical Test Scenarios

### Scenario 1: Theme Switching Test 🎨

**Setup**:

1. Stop current server: `Ctrl+C`
2. Set theme variable: `NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev`
3. Open browser developer tools (F12)
4. Navigate to http://localhost:3000

**What to Check**:

- [ ] No hydration mismatch warnings in console
- [ ] Teal colors (not purple/cyan) throughout UI
- [ ] Consistent design tokens across components
- [ ] Assessment cards show teal status colors

**Expected**: Clean console, consistent teal branding

### Scenario 2: Assessment Components Test 📋

**Steps**:

1. Navigate to `/dashboard` (may require login)
2. Look for assessment-related components
3. Open React DevTools
4. Monitor for React key warnings

**What to Check**:

- [ ] Assessment cards render without warnings
- [ ] Progress bars display correctly
- [ ] Status badges show appropriate colors
- [ ] No "unique key prop" warnings in console

**Components to Verify**:

- AssessmentCard (uses teal colors ✅)
- Assessment wizard/form components
- File upload areas
- Question rendering lists

### Scenario 3: File Upload Testing 📁

**Steps**:

1. Find file upload components in assessments
2. Test drag & drop functionality
3. Try different file types (PDF, DOC, XLS)
4. Monitor upload progress

**What to Check**:

- [ ] Drag & drop visual feedback
- [ ] File type validation
- [ ] Progress tracking works
- [ ] Error handling for invalid files
- [ ] Multiple file selection

### Scenario 4: Business Profile Forms 👤

**Location**: `/business-profile`
**Focus**: Field mapping and validation

**What to Check**:

- [ ] Form fields load correctly
- [ ] Validation messages appear
- [ ] Submit button state management
- [ ] Data persistence
- [ ] Field mappers handle truncated columns

**Critical**: Watch for database column truncation issues

### Scenario 5: Navigation & Routing 🧭

**Test Sequence**:

1. Homepage → Login → Dashboard
2. Dashboard → Business Profile → Settings
3. Use browser back/forward buttons
4. Test direct URL access

**What to Check**:

- [ ] Smooth route transitions
- [ ] Auth guards work properly
- [ ] Loading states display
- [ ] No navigation errors
- [ ] Protected routes redirect correctly

## Console Monitoring Checklist

### React Warnings to Watch For:

```javascript
// BAD - Look for these
"Warning: Each child in a list should have a unique 'key' prop";
'Warning: Expected server HTML to contain a matching';
'Warning: Cannot update a component while rendering';

// ACCEPTABLE - Development only
'[webpack.cache.PackFileCacheStrategy] Serializing big strings';
'Sentry disabled: No valid DSN provided';
```

### Network Tab Monitoring:

- [ ] No failed API requests
- [ ] Reasonable loading times
- [ ] Proper HTTP status codes
- [ ] No CORS errors

## Performance Testing

### Core Web Vitals Check:

1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Run Performance audit
4. Check Core Web Vitals scores

**Target Metrics**:

- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

### Mobile Responsiveness:

1. Toggle device toolbar (Ctrl+Shift+M)
2. Test on different screen sizes
3. Check touch interactions
4. Verify responsive layout

## Issue Documentation Template

When you find issues, document them like this:

```markdown
## Issue: [Brief Description]

- **Component**: [Component name/path]
- **Browser**: [Chrome/Firefox/Safari]
- **Steps to Reproduce**:
  1. Step one
  2. Step two
- **Expected**: [What should happen]
- **Actual**: [What actually happens]
- **Console Errors**: [Copy any error messages]
- **Priority**: [High/Medium/Low]
```

## Testing Priorities

### 🔴 High Priority (Test First)

1. Authentication flows
2. Assessment component rendering
3. React key uniqueness issues
4. Theme switching without hydration errors

### 🟡 Medium Priority

1. Business profile functionality
2. Navigation and routing
3. Form validation
4. Performance optimization

### 🟢 Low Priority (Nice to Have)

1. Cross-browser compatibility
2. Accessibility testing
3. Mobile responsiveness
4. Animation performance

## Quick Commands Reference

```bash
# Start with teal theme
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev

# Check server logs
tail -f dev-server.log

# Quick HTTP test
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

# Kill development server
pkill -f "next dev"
```

## Success Criteria

### ✅ Testing Complete When:

- [ ] No React key warnings in console
- [ ] Theme switching works without hydration errors
- [ ] Assessment components render properly
- [ ] File upload functionality works
- [ ] Forms validate and submit correctly
- [ ] Navigation works smoothly
- [ ] Business profile components load
- [ ] No critical console errors
- [ ] Reasonable performance metrics

---

## Current Status Summary

**Application**: ✅ Running on http://localhost:3000
**Initial Assessment**: ✅ Homepage loads correctly
**Console Status**: 🟡 Development warnings only (acceptable)
**Theme Migration**: 🔄 65% complete (teal colors visible in components)
**Authentication**: 🔄 Required for most functionality testing

**Next Action**: Begin manual testing with authentication setup and theme switching verification.

---

_Guide Created: August 5, 2025_
_Ready for Manual Testing: ✅_
