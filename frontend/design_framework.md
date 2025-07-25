ruleIQ Design System

## Professional Light Theme with Teal Primary

### 📋 Table of Contents

- [Overview](#overview)
- [Color System](#color-system)
- [Typography](#typography)
- [Spacing & Layout](#spacing--layout)
- [Components](#components)
- [Accessibility](#accessibility)
- [Implementation](#implementation)
- [Migration Guide](#migration-guide)

---

## Overview

The ruleIQ design system establishes a professional, trustworthy visual identity for our compliance automation platform. Built on a foundation of **teal primary colors** and **clean neutrals**, it prioritizes accessibility, consistency, and scalability.

### Design Principles

1. **🛡️ Trustworthy**: Professional appearance that instills confidence in compliance processes
2. **♿ Accessible**: WCAG 2.2 AA compliant with excellent contrast ratios
3. **📐 Consistent**: 8px grid system ensures precise, harmonious spacing
4. **🎨 Modern**: Subtle shadows, rounded corners, and smooth animations
5. **⚡ Scalable**: CSS custom properties enable easy theming and maintenance

---

## Color System

### Primary Brand Colors

#### Teal Primary Palette

Our signature teal creates a professional, calming presence perfect for compliance applications.

| Token      | Hex Code  | Use Case                             | Example                   |
| ---------- | --------- | ------------------------------------ | ------------------------- |
| `teal-50`  | `#E6FFFA` | Light backgrounds, subtle highlights | Success state backgrounds |
| `teal-100` | `#B2F5EA` | Light hover states                   | Sidebar item hover        |
| `teal-200` | `#81E6D9` | Light accents, borders               | Active input borders      |
| `teal-300` | `#4FD1C5` | **Bright accent, highlights**        | Badge backgrounds         |
| `teal-400` | `#38B2AC` | Medium teal, icons                   | Secondary icons           |
| `teal-500` | `#319795` | Standard teal                        | Alternative buttons       |
| `teal-600` | `#2C7A7B` | **PRIMARY BRAND COLOR**              | Main buttons, links       |
| `teal-700` | `#285E61` | **Hover states, emphasis**           | Button hover, active nav  |
| `teal-800` | `#234E52` | Dark text on light backgrounds       | Headers on light cards    |
| `teal-900` | `#1D4044` | Darkest teal                         | High contrast text        |

#### Neutral Gray Palette

Professional grays provide hierarchy and readability throughout the interface.

| Token         | Hex Code  | Use Case                  | Example                   |
| ------------- | --------- | ------------------------- | ------------------------- |
| `neutral-50`  | `#F9FAFB` | **Lightest backgrounds**  | Page backgrounds          |
| `neutral-100` | `#F3F4F6` | **Secondary backgrounds** | Card backgrounds          |
| `neutral-200` | `#E5E7EB` | **Borders, dividers**     | Input borders, separators |
| `neutral-300` | `#D1D5DB` | Disabled borders          | Disabled input states     |
| `neutral-400` | `#9CA3AF` | **Placeholder text**      | Form placeholders         |
| `neutral-500` | `#6B7280` | **Muted text**            | Helper text, captions     |
| `neutral-600` | `#4B5563` | **Secondary text**        | Descriptions, subtitles   |
| `neutral-700` | `#374151` | **Body text**             | Paragraph text            |
| `neutral-800` | `#1F2937` | **Headings**              | Section headers           |
| `neutral-900` | `#111827` | **PRIMARY TEXT**          | Main headings, labels     |

### Semantic Colors

#### Success (Emerald Green)

| Token         | Hex Code  | Use Case                          |
| ------------- | --------- | --------------------------------- |
| `success-500` | `#10B981` | Success states, positive feedback |
| `success-600` | `#059669` | Success button hover states       |

#### Warning (Amber)

| Token         | Hex Code  | Use Case                       |
| ------------- | --------- | ------------------------------ |
| `warning-500` | `#F59E0B` | Warning states, caution alerts |
| `warning-600` | `#D97706` | Warning button hover states    |

#### Error (Red)

| Token       | Hex Code  | Use Case                          |
| ----------- | --------- | --------------------------------- |
| `error-500` | `#EF4444` | Error states, validation failures |
| `error-600` | `#DC2626` | Error button hover states         |

#### Info (Blue)

| Token      | Hex Code  | Use Case                    |
| ---------- | --------- | --------------------------- |
| `info-500` | `#3B82F6` | Informational content, tips |
| `info-600` | `#2563EB` | Info button hover states    |

### Design Tokens

#### Primary Tokens

```css
--primary: #2c7a7b; /* Main brand color */
--primary-foreground: #ffffff; /* Text on primary */
--primary-hover: #285e61; /* Hover state */
--primary-light: #e6fffa; /* Light variant */
--primary-dark: #234e52; /* Dark variant */
```

#### Background Tokens

```css
--background: #ffffff; /* Main background */
--background-secondary: #f9fafb; /* Secondary background */
--background-tertiary: #f3f4f6; /* Tertiary background */
```

#### Text Tokens

```css
--text-primary: #111827; /* Primary text */
--text-secondary: #4b5563; /* Secondary text */
--text-muted: #6b7280; /* Muted text */
--text-placeholder: #9ca3af; /* Placeholder text */
```

#### Border Tokens

```css
--border: #e5e7eb; /* Default borders */
--border-hover: #d1d5db; /* Hover borders */
--border-focus: #2c7a7b; /* Focus borders */
```

---

## Typography

### Font Family

**Primary**: Inter (Google Fonts)

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Type Scale

Professional hierarchy from small captions to large displays.

| Token       | Size | Rem      | Use Case               | Example           |
| ----------- | ---- | -------- | ---------------------- | ----------------- |
| `text-xs`   | 12px | 0.75rem  | Captions, badges       | Status badges     |
| `text-sm`   | 14px | 0.875rem | **Body text, buttons** | Paragraph text    |
| `text-base` | 16px | 1rem     | **Default size**       | Form labels       |
| `text-lg`   | 18px | 1.125rem | Subheadings            | Card titles       |
| `text-xl`   | 20px | 1.25rem  | Section headers        | Widget headers    |
| `text-2xl`  | 24px | 1.5rem   | **Page headings**      | Page titles       |
| `text-3xl`  | 30px | 1.875rem | Large headings         | Dashboard titles  |
| `text-4xl`  | 36px | 2.25rem  | **Display text**       | Hero headings     |
| `text-5xl`  | 48px | 3rem     | Large displays         | Marketing headers |
| `text-6xl`  | 60px | 3.75rem  | Extra large            | Landing page hero |

### Font Weights

| Token           | Weight | Use Case                  |
| --------------- | ------ | ------------------------- |
| `font-normal`   | 400    | Body text, descriptions   |
| `font-medium`   | 500    | **UI text, buttons**      |
| `font-semibold` | 600    | **Subheadings, emphasis** |
| `font-bold`     | 700    | **Headings, titles**      |

### Line Heights

| Token             | Value | Use Case               |
| ----------------- | ----- | ---------------------- |
| `leading-tight`   | 1.25  | Headings, compact text |
| `leading-normal`  | 1.5   | **Body text**          |
| `leading-relaxed` | 1.625 | Long-form content      |

---

## Spacing & Layout

### 8px Grid System

All spacing follows an 8px base unit for visual harmony and consistency.

| Token        | Size | Rem     | Use Case             |
| ------------ | ---- | ------- | -------------------- |
| `spacing-1`  | 4px  | 0.25rem | **Tight spacing**    |
| `spacing-2`  | 8px  | 0.5rem  | **Base unit**        |
| `spacing-3`  | 12px | 0.75rem | Small gaps           |
| `spacing-4`  | 16px | 1rem    | **Standard spacing** |
| `spacing-5`  | 20px | 1.25rem | Medium gaps          |
| `spacing-6`  | 24px | 1.5rem  | **Large spacing**    |
| `spacing-8`  | 32px | 2rem    | Section spacing      |
| `spacing-10` | 40px | 2.5rem  | Component spacing    |
| `spacing-12` | 48px | 3rem    | **Layout spacing**   |
| `spacing-16` | 64px | 4rem    | Large sections       |
| `spacing-20` | 80px | 5rem    | Page sections        |
| `spacing-24` | 96px | 6rem    | Major sections       |

### Border Radius

Consistent rounded corners create a modern, friendly appearance.

| Token         | Size   | Rem      | Use Case              |
| ------------- | ------ | -------- | --------------------- |
| `radius-sm`   | 4px    | 0.25rem  | Small elements        |
| `radius`      | 8px    | 0.5rem   | **Primary radius**    |
| `radius-md`   | 10px   | 0.625rem | Medium elements       |
| `radius-lg`   | 12px   | 0.75rem  | **Cards, containers** |
| `radius-xl`   | 16px   | 1rem     | Large containers      |
| `radius-2xl`  | 20px   | 1.25rem  | Hero elements         |
| `radius-full` | 9999px | -        | **Pills, avatars**    |

### Shadows

Subtle depth creates visual hierarchy without overwhelming content.

| Token       | Value                                                           | Use Case           |
| ----------- | --------------------------------------------------------------- | ------------------ |
| `shadow-sm` | `0 1px 3px 0 rgb(0 0 0 / 0.1)`                                  | **Cards, buttons** |
| `shadow`    | `0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)` | **Default shadow** |
| `shadow-md` | `0 4px 6px -1px rgb(0 0 0 / 0.1)`                               | **Hover states**   |
| `shadow-lg` | `0 10px 15px -3px rgb(0 0 0 / 0.1)`                             | Modals, dropdowns  |
| `shadow-xl` | `0 20px 25px -5px rgb(0 0 0 / 0.1)`                             | Large modals       |

---

## Components

### Buttons

#### Primary Button

```css
.btn-primary {
  background-color: var(--teal-600);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 200ms ease-out;
}

.btn-primary:hover {
  background-color: var(--teal-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

#### Secondary Button

```css
.btn-secondary {
  background-color: var(--neutral-100);
  color: var(--neutral-900);
  border: 1px solid var(--neutral-200);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
}

.btn-secondary:hover {
  background-color: var(--neutral-200);
}
```

#### Ghost Button

```css
.btn-ghost {
  background-color: transparent;
  color: var(--teal-600);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
}

.btn-ghost:hover {
  background-color: var(--teal-50);
}
```

### Form Elements

#### Input Fields

```css
.input {
  background-color: white;
  border: 1px solid var(--neutral-200);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  transition: all 200ms ease-out;
}

.input:focus {
  outline: none;
  border-color: var(--teal-600);
  box-shadow: 0 0 0 3px rgb(44 122 123 / 0.1);
}

.input::placeholder {
  color: var(--neutral-400);
}
```

### Cards

```css
.card {
  background-color: white;
  border: 1px solid var(--neutral-200);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 200ms ease-out;
}

.card:hover {
  box-shadow: var(--shadow-md);
}
```

### Navigation

#### Sidebar

```css
.sidebar {
  background-color: white;
  border-right: 1px solid var(--neutral-200);
  width: 280px;
}

.sidebar-item {
  padding: 12px 16px;
  color: var(--neutral-600);
  border-radius: 8px;
  margin: 4px 8px;
  transition: all 200ms ease-out;
}

.sidebar-item:hover {
  background-color: var(--neutral-50);
  color: var(--neutral-900);
}

.sidebar-item.active {
  background-color: var(--teal-50);
  color: var(--teal-700);
  font-weight: 500;
}
```

#### Top Navigation

```css
.top-nav {
  background-color: white;
  border-bottom: 1px solid var(--neutral-200);
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-search {
  background-color: var(--neutral-50);
  border: 1px solid var(--neutral-200);
  border-radius: 8px;
  padding: 8px 12px;
  width: 320px;
}

.nav-search:focus {
  background-color: white;
  border-color: var(--teal-600);
}
```

---

## Accessibility

### WCAG 2.2 AA Compliance

Our design system meets and exceeds accessibility standards.

#### Contrast Ratios

| Combination            | Ratio   | Standard | Status  |
| ---------------------- | ------- | -------- | ------- |
| `teal-600` on white    | 5.87:1  | AA       | ✅ Pass |
| `neutral-900` on white | 19.30:1 | AAA      | ✅ Pass |
| `neutral-700` on white | 11.89:1 | AAA      | ✅ Pass |
| `neutral-600` on white | 7.69:1  | AAA      | ✅ Pass |

#### Focus States

All interactive elements have visible focus indicators:

```css
.focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--teal-600);
}
```

#### Motion Preferences

Respects user motion preferences:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Implementation

### CSS Custom Properties

The design system uses CSS custom properties for easy theming:

```css
:root {
  /* Primary colors */
  --teal-600: #2c7a7b;
  --teal-700: #285e61;

  /* Semantic tokens */
  --primary: var(--teal-600);
  --primary-hover: var(--teal-700);

  /* Typography */
  --font-sans: 'Inter', sans-serif;
  --text-base: 1rem;

  /* Spacing */
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;

  /* Borders */
  --radius: 0.5rem;
  --border: #e5e7eb;
}
```

### Tailwind Integration

Our design tokens integrate seamlessly with Tailwind CSS:

```javascript
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        teal: {
          50: '#E6FFFA',
          600: '#2C7A7B',
          700: '#285E61',
        },
        neutral: {
          50: '#F9FAFB',
          900: '#111827',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      spacing: {
        // 8px grid system
      },
    },
  },
};
```

### Component Usage

```tsx
// Using design tokens in React components
import { Button } from '@/components/ui/button'

export function ExampleComponent() {
return (
<div className="bg-neutral-50 p-6 rounded-lg">
<h2 className="text-2xl font-bold text-neutral-900 mb-4">
Compliance Dashboard
</h2>
<Button variant="primary">
Start Assessment
</Button>
</div>
)
}
```

---

## Migration Guide

### Phase 1: Foundation (Week 1)

1. **Install Design System**

```bash
# Add design system CSS
git checkout front-end-design-refactor -- frontend/app/styles/design-system.css
```

2. **Update Global Styles**

```css
/* Add to globals.css */
@import './styles/design-system.css';
```

3. **Feature Flag Setup**

```typescript
// lib/features/theme-flags.ts
export const USE_NEW_THEME = process.env.NEXT_PUBLIC_USE_NEW_THEME === 'true';
```

### Phase 2: Core Components (Week 2)

1. **Update Navigation**

- AppSidebar: Apply new teal color scheme
- TopNavigation: Update search and user menu styling

2. **Button Components**

- Replace purple theme with teal variants
- Update hover and focus states

### Phase 3: Page Components (Week 3)

1. **Dashboard Pages**

- Update chart colors to teal palette
- Apply new card styling

2. **Form Components**

- Update input styling with teal focus states
- Apply new validation error styling

### Phase 4: Testing & Rollout (Week 4)

1. **Accessibility Testing**

- Verify contrast ratios
- Test keyboard navigation
- Validate screen reader compatibility

2. **Gradual Rollout**

```bash
# Enable for testing
NEXT_PUBLIC_USE_NEW_THEME=true pnpm dev

# Production rollout (10% → 25% → 100%)
NEXT_PUBLIC_USE_NEW_THEME=true pnpm build
```

---

## Resources

### Files

- **Design System CSS**: `frontend/app/styles/design-system.css`
- **Component Library**: `frontend/components/ui/`
- **Migration Plan**: `FRONTEND_MIGRATION_PLAN.md`

### Tools

- **Color Palette**: [Tailwind CSS Colors](https://tailwindcss.com/docs/customizing-colors)
- **Accessibility**: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- **Typography**: [Inter Font](https://fonts.google.com/specimen/Inter)

### Team

- **Design System Owner**: Frontend Team
- **Accessibility Champion**: QA Team
- **Implementation Lead**: Senior Frontend Developer

---

_Last Updated: 2025-01-18_
_Version: 1.0.0_
_Status: Ready for Implementation_
I understand! You have a comprehensive design system for ruleIQ with a professional teal-based theme. This is a great foundation to work with.

What specific design would you like me to create using this ruleIQ design system? For example:

A dashboard interface
A specific component or widget
A form or data entry screen
A compliance report view
Something else entirely
Just let me know what you'd like to design, and I'll follow the workflow:

Layout design (ASCII wireframe)
Theme design (using your ruleIQ colors and tokens)
Animation design
Generate the HTML implementation
