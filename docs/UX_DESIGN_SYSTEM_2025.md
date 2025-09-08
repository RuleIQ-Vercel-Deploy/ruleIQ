# RuleIQ UX Design System
## Version 1.0 - January 2025

---

## EXECUTIVE SUMMARY

This document defines the complete UX design system for RuleIQ, establishing patterns, components, and guidelines that ensure consistent, accessible, and delightful user experiences across all touchpoints.

**Critical Issue**: Current implementation has WCAG violations in color contrast and missing ARIA labels that must be fixed for accessibility compliance.

---

## 1. DESIGN PRINCIPLES

### 1.1 Core Principles

```yaml
Clarity:
  Definition: "Make the complex simple"
  Application:
    - Progressive disclosure
    - Clear visual hierarchy
    - Plain language
    - Contextual help
    
Efficiency:
  Definition: "Respect user's time"
  Application:
    - Smart defaults
    - Bulk actions
    - Keyboard shortcuts
    - Saved preferences
    
Trust:
  Definition: "Build confidence"
  Application:
    - Transparent processes
    - Clear feedback
    - Undo capabilities
    - Data validation
    
Delight:
  Definition: "Exceed expectations"
  Application:
    - Micro-interactions
    - Celebration moments
    - Personalization
    - Thoughtful empty states
```

### 1.2 Design Philosophy
**"Professional doesn't mean boring. Compliance doesn't mean complex."**

---

## 2. BRAND IDENTITY

### 2.1 Visual Identity

```yaml
Logo:
  Primary: RuleIQ wordmark with shield icon
  Secondary: Shield icon standalone
  Clearspace: 2x height minimum
  Min Size: 120px width
  
Personality:
  - Professional yet approachable
  - Modern yet timeless
  - Authoritative yet friendly
  - Innovative yet reliable
  
Voice & Tone:
  - Clear and concise
  - Confident but not condescending
  - Helpful without being pushy
  - Technical when needed, simple when possible
```

### 2.2 Color System

```css
/* Primary Palette - Professional Teal Theme */
:root {
  /* Brand Colors */
  --brand-primary: #2C7A7B;      /* Teal-600 - Main brand */
  --brand-secondary: #0F766E;     /* Teal-700 - Darker variant */
  --brand-tertiary: #14B8A6;      /* Teal-400 - Accent */
  --brand-dark: #285E61;          /* Teal-800 - Hover states */
  --brand-light: #E6FFFA;         /* Teal-50 - Backgrounds */
  
  /* Semantic Colors */
  --success: #10B981;             /* Green - Positive actions */
  --warning: #F59E0B;             /* Amber - Caution */
  --error: #EF4444;               /* Red - Errors */
  --info: #319795;                /* Teal-500 - Information */
  
  /* Neutral Scale */
  --neutral-50: #FAFAFA;
  --neutral-100: #F4F4F5;
  --neutral-200: #E4E4E7;
  --neutral-300: #D4D4D8;
  --neutral-400: #A1A1AA;
  --neutral-500: #71717A;
  --neutral-600: #52525B;
  --neutral-700: #3F3F46;
  --neutral-800: #27272A;
  --neutral-900: #18181B;
}

/* WCAG AA Compliance Requirements */
.contrast-ratios {
  /* Text on white background */
  --min-normal-text: 4.5:1;      /* Use neutral-600 minimum */
  --min-large-text: 3:1;          /* Use neutral-500 minimum */
  
  /* Interactive elements */
  --min-interactive: 3:1;         /* Use brand-secondary minimum */
  --min-focus: 3:1;               /* Use brand-primary minimum */
}
```

### 2.3 Typography

```css
/* Typography Scale */
:root {
  /* Font Families */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Font Sizes with line heights and weights */
  --text-xs: 12px/16px 400;      /* Small labels */
  --text-sm: 14px/20px 400;      /* Body small */
  --text-base: 16px/24px 400;    /* Body default */
  --text-lg: 18px/28px 500;      /* Body large */
  --text-xl: 20px/28px 500;      /* H3 */
  --text-2xl: 24px/32px 600;     /* H2 */
  --text-3xl: 30px/36px 600;     /* H1 small */
  --text-4xl: 36px/40px 600;     /* H1 default */
  --text-5xl: 48px/48px 700;     /* Display */
  
  /* Letter Spacing */
  --tracking-tight: -0.025em;    /* Headlines */
  --tracking-normal: 0;           /* Body text */
  --tracking-wide: 0.025em;      /* Labels */
}

/* Typography Classes */
.heading-1 {
  font-size: 36px;
  line-height: 40px;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: var(--neutral-900);
}

.body-text {
  font-size: 16px;
  line-height: 24px;
  font-weight: 400;
  color: var(--neutral-700);
}

.label-text {
  font-size: 14px;
  line-height: 20px;
  font-weight: 500;
  letter-spacing: 0.025em;
  text-transform: uppercase;
  color: var(--neutral-600);
}
```

---

## 3. COMPONENT LIBRARY

### 3.1 Component Architecture

```yaml
Foundation:
  - Colors
  - Typography
  - Spacing (8px grid)
  - Shadows
  - Border radius
  
Atoms:
  - Buttons
  - Inputs
  - Labels
  - Icons
  - Badges
  
Molecules:
  - Form fields
  - Cards
  - Alerts
  - Tooltips
  - Dropdowns
  
Organisms:
  - Navigation
  - Headers
  - Footers
  - Modals
  - Tables
  
Templates:
  - Dashboard
  - Form layouts
  - List views
  - Detail pages
  - Wizards
```

### 3.2 Core Components

#### Buttons
```tsx
// Button Variants
<Button variant="primary">   // Brand-primary bg, white text
<Button variant="secondary"> // Neutral bg, dark text
<Button variant="outline">   // Border only
<Button variant="ghost">     // No border, subtle hover
<Button variant="danger">    // Red for destructive actions

// Button Sizes
<Button size="sm">  // 32px height
<Button size="md">  // 40px height (default)
<Button size="lg">  // 48px height

// Button States
- Default: Base appearance
- Hover: Darker shade + shadow
- Active: Pressed appearance
- Focus: Ring outline (brand-primary)
- Disabled: 50% opacity + cursor not-allowed
- Loading: Spinner + disabled state
```

#### Form Inputs
```tsx
// Input Types
<Input type="text">
<Input type="email">
<Input type="password">
<Input type="number">
<Select>
<Textarea>
<Checkbox>
<RadioGroup>
<Switch>
<DatePicker>

// Input States
- Default: Neutral border
- Focus: Brand-primary border + ring
- Error: Red border + error message
- Success: Green border + checkmark
- Disabled: Gray background
- Loading: Skeleton animation
```

#### Cards
```tsx
// Card Variants
<Card>
  <CardHeader>
    <CardTitle>
    <CardDescription>
  </CardHeader>
  <CardContent>
    // Content here
  </CardContent>
  <CardFooter>
    // Actions here
  </CardFooter>
</Card>

// Card Styles
- Default: White bg, subtle shadow
- Elevated: Stronger shadow
- Interactive: Hover state with lift
- Selected: Brand border
- Disabled: Gray overlay
```

---

## 4. LAYOUT SYSTEM

### 4.1 Grid System

```css
/* 8px Grid System */
:root {
  --grid-unit: 8px;
  
  /* Spacing Scale */
  --space-0: 0;
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 40px;
  --space-6: 48px;
  --space-8: 64px;
  --space-10: 80px;
  --space-12: 96px;
  --space-16: 128px;
  --space-20: 160px;
  
  /* Container Widths */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1536px;
}
```

### 4.2 Responsive Breakpoints

```css
/* Mobile First Breakpoints */
@media (min-width: 640px) {  /* sm - Tablet */
@media (min-width: 768px) {  /* md - Small laptop */
@media (min-width: 1024px) { /* lg - Desktop */
@media (min-width: 1280px) { /* xl - Large desktop */
@media (min-width: 1536px) { /* 2xl - Ultra wide */
```

### 4.3 Page Layouts

```yaml
Dashboard Layout:
  - Collapsible sidebar (240px)
  - Fixed header (64px)
  - Main content area
  - Optional right panel (320px)
  
Form Layout:
  - Centered container (max 640px)
  - Progress indicator
  - Step navigation
  - Action buttons sticky bottom
  
List Layout:
  - Filters sidebar (280px)
  - Search bar
  - Data table/cards
  - Pagination
  
Detail Layout:
  - Breadcrumbs
  - Header with actions
  - Tab navigation
  - Content sections
```

---

## 5. INTERACTION PATTERNS

### 5.1 Micro-interactions

```yaml
Button Click:
  Duration: 150ms
  Effect: Scale(0.95) + ripple
  
Input Focus:
  Duration: 200ms
  Effect: Border color + shadow
  
Card Hover:
  Duration: 200ms
  Effect: Translate Y(-2px) + shadow
  
Loading:
  Skeleton: Shimmer animation
  Spinner: Rotate 360° loop
  Progress: Smooth fill
  
Success:
  Duration: 400ms
  Effect: Check mark draw + fade
  
Error:
  Duration: 300ms
  Effect: Shake X-axis + red flash
```

### 5.2 Navigation Patterns

```yaml
Primary Navigation:
  - Persistent sidebar
  - Icon + label
  - Collapse to icons only
  - Active state highlighting
  
Secondary Navigation:
  - Horizontal tabs
  - Breadcrumbs
  - Step indicators
  - Quick actions menu
  
Mobile Navigation:
  - Bottom tab bar
  - Hamburger menu
  - Swipe gestures
  - Pull to refresh
```

### 5.3 Feedback Patterns

```tsx
// Toast Notifications
toast.success("Policy created successfully");
toast.error("Failed to save changes");
toast.info("New compliance update available");
toast.warning("Your session will expire in 5 minutes");

// Loading States
<Button loading>Saving...</Button>
<Skeleton className="h-4 w-[250px]" />
<Spinner size="lg" />
<ProgressBar value={75} />

// Empty States
<EmptyState
  icon={<FileText />}
  title="No policies yet"
  description="Create your first policy to get started"
  action={<Button>Create Policy</Button>}
/>

// Error States
<ErrorBoundary
  fallback={<ErrorFallback />}
  onError={logToSentry}
/>
```

---

## 6. ACCESSIBILITY STANDARDS

### 6.1 WCAG 2.1 AA Compliance

```yaml
Visual:
  - Color contrast: 4.5:1 minimum
  - Focus indicators: Visible always
  - Text sizing: Zoomable to 200%
  - Color independence: Not sole indicator
  
Keyboard:
  - Tab navigation: Logical order
  - Focus trap: In modals only
  - Skip links: To main content
  - Shortcuts: With visual hints
  
Screen Readers:
  - ARIA labels: All interactive elements
  - Semantic HTML: Proper heading hierarchy
  - Alt text: All informative images
  - Live regions: For dynamic content
  
Interaction:
  - Click targets: 44x44px minimum
  - Time limits: User adjustable
  - Error identification: Clear messages
  - Form labels: Always visible
```

### 6.2 ARIA Implementation

```html
<!-- Navigation -->
<nav aria-label="Main navigation">
  <ul role="list">
    <li>
      <a href="/dashboard" aria-current="page">Dashboard</a>
    </li>
  </ul>
</nav>

<!-- Forms -->
<form aria-labelledby="form-title">
  <div role="group" aria-labelledby="section-title">
    <label for="email">
      Email
      <span aria-label="required">*</span>
    </label>
    <input 
      type="email" 
      id="email"
      aria-describedby="email-error"
      aria-invalid="true"
    />
    <span id="email-error" role="alert">
      Please enter a valid email
    </span>
  </div>
</form>

<!-- Modals -->
<dialog
  role="dialog"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
  aria-modal="true"
>
  <h2 id="modal-title">Confirm Action</h2>
  <p id="modal-description">Are you sure?</p>
</dialog>

<!-- Loading -->
<div aria-live="polite" aria-busy="true">
  <span class="sr-only">Loading...</span>
</div>
```

---

## 7. MOTION & ANIMATION

### 7.1 Animation Principles

```css
/* Timing Functions */
:root {
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  
  /* Durations */
  --duration-instant: 50ms;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 350ms;
  --duration-slower: 500ms;
}

/* Respect User Preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 7.2 Page Transitions

```yaml
Route Change:
  Enter: Fade in + slide up (300ms)
  Exit: Fade out (200ms)
  
Modal Open:
  Backdrop: Fade in (200ms)
  Content: Scale + fade (250ms)
  
Accordion:
  Expand: Height auto (200ms)
  Collapse: Height 0 (200ms)
  
Tab Switch:
  Exit: Fade out (150ms)
  Enter: Fade in (150ms)
```

---

## 8. RESPONSIVE DESIGN

### 8.1 Mobile-First Approach

```css
/* Base (Mobile) Styles */
.container {
  padding: 16px;
  width: 100%;
}

/* Tablet Enhancement */
@media (min-width: 768px) {
  .container {
    padding: 24px;
    max-width: 768px;
  }
}

/* Desktop Enhancement */
@media (min-width: 1024px) {
  .container {
    padding: 32px;
    max-width: 1280px;
  }
}
```

### 8.2 Adaptive Components

```yaml
Navigation:
  Mobile: Bottom tabs
  Tablet: Collapsed sidebar
  Desktop: Expanded sidebar
  
Data Tables:
  Mobile: Cards view
  Tablet: Condensed table
  Desktop: Full table
  
Forms:
  Mobile: Single column
  Tablet: Two columns
  Desktop: Multi-column
  
Modals:
  Mobile: Full screen
  Tablet: 90% screen
  Desktop: Fixed width
```

---

## 9. DARK MODE

### 9.1 Dark Theme Colors

```css
:root[data-theme="dark"] {
  /* Backgrounds */
  --bg-primary: #0A0A0B;
  --bg-secondary: #18181B;
  --bg-tertiary: #27272A;
  
  /* Text */
  --text-primary: #FAFAFA;
  --text-secondary: #A1A1AA;
  --text-tertiary: #71717A;
  
  /* Borders */
  --border-primary: #3F3F46;
  --border-secondary: #52525B;
  
  /* Brand colors stay same */
  --brand-primary: #2C7A7B;
  --brand-light: #285E61;
}
```

### 9.2 Theme Switching

```tsx
// Theme Toggle Component
<Switch
  checked={theme === 'dark'}
  onCheckedChange={(checked) => 
    setTheme(checked ? 'dark' : 'light')
  }
  aria-label="Toggle dark mode"
>
  <SunIcon className="light-icon" />
  <MoonIcon className="dark-icon" />
</Switch>

// System Preference Detection
const getSystemTheme = () => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
};
```

---

## 10. DESIGN TOKENS

### 10.1 Token Structure

```json
{
  "color": {
    "brand": {
      "primary": {
        "value": "#2C7A7B",
        "type": "color"
      }
    }
  },
  "spacing": {
    "1": {
      "value": "8px",
      "type": "spacing"
    }
  },
  "typography": {
    "heading": {
      "1": {
        "value": {
          "fontFamily": "Inter",
          "fontSize": "36px",
          "lineHeight": "40px",
          "fontWeight": 600
        },
        "type": "typography"
      }
    }
  },
  "shadow": {
    "sm": {
      "value": "0 1px 2px rgba(0,0,0,0.05)",
      "type": "boxShadow"
    }
  }
}
```

---

## APPENDICES

### A. Component Documentation
Full Storybook available at `/storybook`

### B. Icon Library
Using Lucide React - 1000+ icons

### C. Accessibility Checklist
WCAG 2.1 AA compliance checklist

### D. Design Files
Figma designs at `figma.com/ruleiq-design-system`

---

**Document Status**: READY FOR IMPLEMENTATION
**Author**: UX Design Team
**Last Updated**: January 2025
**Next Review**: Monthly