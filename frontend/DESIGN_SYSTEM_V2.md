# RuleIQ Design System v2.0
## Neural Purple Theme - Professional Compliance Platform

---

## Core Design Principles

### Visual Identity
- **Aesthetic**: Sophisticated, serious, cutting-edge
- **Mood**: Professional authority with technological innovation
- **Approach**: Minimalist elegance with purposeful visual interest
- **NO EMOJIS**: Never use emojis anywhere in the application

---

## Color Palette

### Primary Colors
```css
--neural-purple-900: #1a0033    /* Deepest purple - backgrounds */
--neural-purple-800: #2d0052    /* Deep purple - sections */
--neural-purple-700: #4a0080    /* Rich purple - cards */
--neural-purple-600: #6b00b5    /* Vibrant purple - accents */
--neural-purple-500: #8b5cf6    /* Primary purple - buttons/links */
--neural-purple-400: #a78bfa    /* Light purple - hover states */
--neural-purple-300: #c4b5fd    /* Pale purple - subtle backgrounds */
```

### Accent Colors
```css
--silver-900: #1f2937           /* Dark silver - text on light */
--silver-800: #374151           /* Medium dark silver */
--silver-700: #4b5563           /* Medium silver */
--silver-600: #6b7280           /* Neutral silver */
--silver-500: #9ca3af           /* Light silver - secondary text */
--silver-400: #c0c0c0           /* Classic silver - accents */
--silver-300: #d1d5db           /* Pale silver - borders */
--silver-200: #e5e7eb           /* Very light silver - dividers */
--silver-100: #f3f4f6           /* Almost white - backgrounds */
```

### Semantic Colors
```css
--success: #10b981              /* Emerald - success states */
--warning: #f59e0b              /* Amber - warnings */
--error: #ef4444                /* Red - errors */
--info: #8b5cf6                 /* Purple - information */
```

### Background Gradients
```css
/* Neural network background */
--gradient-neural: radial-gradient(ellipse at top, #4a0080 0%, #1a0033 50%, #000000 100%);

/* Section gradients */
--gradient-section: linear-gradient(135deg, #2d0052 0%, #1a0033 100%);

/* Card gradients */
--gradient-card: linear-gradient(180deg, rgba(139, 92, 246, 0.05) 0%, rgba(0, 0, 0, 0) 100%);
```

---

## Typography System

### Font Stack
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
```

### Font Weights
```css
--font-extralight: 200;   /* Hero headlines */
--font-light: 300;        /* Body text, descriptions */
--font-regular: 400;      /* Standard UI text */
--font-medium: 500;       /* Emphasized text */
--font-semibold: 600;     /* Section headers */
```

### Type Scale
```css
/* Headings - Extralight weight for elegance */
--text-hero: 4.5rem;      /* 72px - Hero headlines */
--text-h1: 3.75rem;       /* 60px - Page titles */
--text-h2: 3rem;          /* 48px - Section headers */
--text-h3: 2.25rem;       /* 36px - Subsections */
--text-h4: 1.875rem;      /* 30px - Card titles */
--text-h5: 1.5rem;        /* 24px - Component headers */

/* Body Text - Light weight for readability */
--text-xl: 1.25rem;       /* 20px - Large body */
--text-lg: 1.125rem;      /* 18px - Emphasized body */
--text-base: 1rem;        /* 16px - Standard body */
--text-sm: 0.875rem;      /* 14px - Secondary text */
--text-xs: 0.75rem;       /* 12px - Captions/labels */
```

### Text Styling Rules
```css
/* Headlines */
.headline {
  font-weight: var(--font-extralight);
  letter-spacing: -0.02em;
  line-height: 1.05;
  color: white;
}

/* Body Text */
.body-text {
  font-weight: var(--font-light);
  letter-spacing: -0.01em;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.75);
}

/* UI Text */
.ui-text {
  font-weight: var(--font-regular);
  letter-spacing: -0.005em;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
}
```

---

## Component Styles

### Buttons

#### Primary Button
```css
.btn-primary {
  background: linear-gradient(135deg, #8b5cf6 0%, #6b00b5 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 1rem;
  font-weight: 300;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
}
```

#### Secondary Button
```css
.btn-secondary {
  background: transparent;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 1rem;
  font-weight: 300;
  letter-spacing: -0.01em;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}
```

#### Ghost Button
```css
.btn-ghost {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  padding: 0.5rem 1rem;
  font-weight: 300;
  transition: all 0.3s ease;
}

.btn-ghost:hover {
  color: #8b5cf6;
  background: rgba(139, 92, 246, 0.1);
}
```

### Cards

```css
.card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(0, 0, 0, 0) 100%);
  border: 1px solid rgba(139, 92, 246, 0.1);
  border-radius: 1.5rem;
  padding: 2rem;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.card:hover {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 20px 40px rgba(139, 92, 246, 0.1);
  transform: translateY(-4px);
}
```

### Forms

#### Input Fields
```css
.input {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  color: white;
  font-weight: 300;
  transition: all 0.3s ease;
}

.input:focus {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
  outline: none;
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}
```

#### Labels
```css
.label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
  font-weight: 300;
  letter-spacing: -0.01em;
  margin-bottom: 0.5rem;
}
```

### Navigation

```css
.nav-link {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 300;
  letter-spacing: -0.01em;
  transition: color 0.3s ease;
  position: relative;
}

.nav-link:hover {
  color: white;
}

.nav-link.active {
  color: #8b5cf6;
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #8b5cf6 0%, #6b00b5 100%);
}
```

### Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 300;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.badge-purple {
  background: rgba(139, 92, 246, 0.1);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.badge-silver {
  background: rgba(192, 192, 192, 0.1);
  color: #c0c0c0;
  border: 1px solid rgba(192, 192, 192, 0.2);
}
```

---

## Layout Patterns

### Container Widths
```css
--container-xs: 20rem;     /* 320px */
--container-sm: 24rem;     /* 384px */
--container-md: 28rem;     /* 448px */
--container-lg: 32rem;     /* 512px */
--container-xl: 36rem;     /* 576px */
--container-2xl: 42rem;    /* 672px */
--container-3xl: 48rem;    /* 768px */
--container-4xl: 56rem;    /* 896px */
--container-5xl: 64rem;    /* 1024px */
--container-6xl: 72rem;    /* 1152px */
--container-7xl: 80rem;    /* 1280px */
```

### Spacing Scale
```css
--spacing-0: 0;
--spacing-1: 0.25rem;      /* 4px */
--spacing-2: 0.5rem;       /* 8px */
--spacing-3: 0.75rem;      /* 12px */
--spacing-4: 1rem;         /* 16px */
--spacing-5: 1.25rem;      /* 20px */
--spacing-6: 1.5rem;       /* 24px */
--spacing-8: 2rem;         /* 32px */
--spacing-10: 2.5rem;      /* 40px */
--spacing-12: 3rem;        /* 48px */
--spacing-16: 4rem;        /* 64px */
--spacing-20: 5rem;        /* 80px */
--spacing-24: 6rem;        /* 96px */
```

---

## Page Templates

### Dashboard Layout
```
┌─────────────────────────────────────────┐
│  Neural Network Background (subtle)     │
├─────────────────────────────────────────┤
│  Header (glass morphism)                │
├─────────────────────────────────────────┤
│  ┌───────┐ ┌──────────────────────────┐ │
│  │       │ │                          │ │
│  │  Nav  │ │     Main Content         │ │
│  │       │ │                          │ │
│  │       │ │  Cards with purple       │ │
│  │       │ │  gradient borders        │ │
│  │       │ │                          │ │
│  └───────┘ └──────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Content Pages
```
┌─────────────────────────────────────────┐
│  Subtle gradient background             │
├─────────────────────────────────────────┤
│  Header                                 │
├─────────────────────────────────────────┤
│  Hero Section                           │
│  - Extralight headline                  │
│  - Light description                    │
│  - Purple CTA buttons                   │
├─────────────────────────────────────────┤
│  Content Sections                       │
│  - Cards with hover effects             │
│  - Silver accents                       │
│  - Minimal dividers                     │
└─────────────────────────────────────────┘
```

---

## Animation Guidelines

### Transitions
```css
--transition-fast: 150ms ease;
--transition-base: 300ms ease;
--transition-slow: 500ms ease;
--transition-slower: 700ms ease;
```

### Hover Effects
- Subtle transform: translateY(-2px to -4px)
- Soft shadows with purple tint
- Border color intensity increase
- Background opacity changes

### Page Transitions
- Fade in with subtle scale (0.98 to 1)
- Stagger animations for lists
- Smooth scroll behavior
- No bouncy or playful animations

---

## Component Examples

### Hero Section
```jsx
<section className="relative min-h-screen">
  {/* Neural network background */}
  <div className="absolute inset-0 bg-gradient-neural" />
  
  <div className="relative z-10 max-w-7xl mx-auto px-6 py-24">
    <div className="max-w-3xl">
      {/* Badge */}
      <div className="badge badge-purple mb-6">
        <span className="w-1 h-1 bg-purple-400 rounded-full" />
        NEW • Next-Gen Platform
      </div>
      
      {/* Headline */}
      <h1 className="text-hero font-extralight tracking-tight text-white mb-6">
        Your Headline
        <span className="text-purple-400"> Here</span>
      </h1>
      
      {/* Description */}
      <p className="text-lg font-light text-white/75 mb-8 max-w-xl">
        Professional description text with elegant typography.
      </p>
      
      {/* CTAs */}
      <div className="flex gap-4">
        <button className="btn-primary">Get Started</button>
        <button className="btn-secondary">Learn More</button>
      </div>
    </div>
  </div>
</section>
```

### Dashboard Card
```jsx
<div className="card">
  <div className="flex items-center justify-between mb-4">
    <h3 className="text-xl font-light text-white">
      Metric Title
    </h3>
    <span className="text-sm text-silver-400">
      Last 30 days
    </span>
  </div>
  
  <div className="text-3xl font-extralight text-white mb-2">
    1,234<span className="text-purple-400">+</span>
  </div>
  
  <div className="text-sm font-light text-silver-500">
    <span className="text-success">↑ 12%</span> from last period
  </div>
</div>
```

---

## Implementation Notes

1. **Dark Mode Only**: The design system is optimized for dark mode exclusively
2. **No Emojis**: Never use emojis in any context
3. **Consistent Spacing**: Use the spacing scale for all margins/padding
4. **Purple Accents**: Use purple sparingly for emphasis and CTAs
5. **Silver Secondary**: Silver for secondary text and subtle borders
6. **Glass Morphism**: Apply backdrop-filter: blur() on overlays
7. **Gradient Borders**: Use gradient borders on hover for premium feel
8. **Typography Hierarchy**: Maintain clear visual hierarchy with font weights
9. **Professional Tone**: All copy should be serious and authoritative
10. **Performance**: Keep animations smooth and non-blocking

---

## Accessibility

- Maintain WCAG AA contrast ratios
- Focus states with purple outline
- Keyboard navigation support
- Screen reader friendly markup
- Reduced motion respects user preferences

---

## File Structure for Styles

```
/styles
  /base
    - reset.css
    - variables.css
    - typography.css
  /components
    - buttons.css
    - cards.css
    - forms.css
    - navigation.css
  /layouts
    - dashboard.css
    - content.css
  /utilities
    - animations.css
    - gradients.css
```

---

This design system ensures consistency across the entire RuleIQ platform while maintaining the sophisticated, professional aesthetic established by the neural network hero.
