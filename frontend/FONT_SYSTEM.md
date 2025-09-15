# Neural Purple Theme - Font System Guide

## Primary Font: Inter

**Inter** is the sole font family used throughout the RuleIQ platform for absolute consistency.

### Why Inter?
- Modern, geometric sans-serif design
- Exceptional readability at all sizes
- Wide weight range (100-900)
- Optimized for screens
- Professional and sophisticated appearance
- Perfect for both UI elements and body text

---

## Font Weights & Usage

### 200 - Extra Light
**Usage:** Hero headlines, large display text
```css
font-weight: 200;
/* Tailwind: font-extralight */
```
**Where to use:**
- Hero section headlines (72px/4.5rem)
- Page titles (60px/3.75rem)
- Large feature headlines
- Metric values in dashboards

### 300 - Light  
**Usage:** Primary body text, descriptions
```css
font-weight: 300;
/* Tailwind: font-light */
```
**Where to use:**
- Body paragraphs
- Card descriptions
- Button text
- Form labels
- Navigation links
- Badge text

### 400 - Regular
**Usage:** UI elements, emphasis
```css
font-weight: 400;
/* Tailwind: font-normal */
```
**Where to use:**
- Data tables
- Form inputs (user-entered text)
- Code/technical content
- Bold emphasis within light text

### 500 - Medium
**Usage:** Section headers, important UI
```css
font-weight: 500;
/* Tailwind: font-medium */
```
**Where to use:**
- Section subheadings
- Important buttons (CTAs)
- Active navigation states
- Alert titles

---

## Typography Scale

### Headlines
```css
/* Hero - 72px */
.text-hero {
  font-size: 4.5rem;
  font-weight: 200;
  line-height: 1.05;
  letter-spacing: -0.02em;
}

/* Display Large - 60px */
.text-display-lg {
  font-size: 3.75rem;
  font-weight: 200;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

/* Display - 48px */
.text-display {
  font-size: 3rem;
  font-weight: 200;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

/* Display Small - 36px */
.text-display-sm {
  font-size: 2.25rem;
  font-weight: 200;
  line-height: 1.2;
  letter-spacing: -0.01em;
}
```

### Body Text
```css
/* Large Body - 20px */
.text-xl {
  font-size: 1.25rem;
  font-weight: 300;
  line-height: 1.75;
  letter-spacing: -0.01em;
}

/* Emphasized Body - 18px */
.text-lg {
  font-size: 1.125rem;
  font-weight: 300;
  line-height: 1.75;
  letter-spacing: -0.01em;
}

/* Standard Body - 16px */
.text-base {
  font-size: 1rem;
  font-weight: 300;
  line-height: 1.625;
  letter-spacing: -0.005em;
}

/* Small Text - 14px */
.text-sm {
  font-size: 0.875rem;
  font-weight: 300;
  line-height: 1.5;
  letter-spacing: -0.005em;
}

/* Caption/Label - 12px */
.text-xs {
  font-size: 0.75rem;
  font-weight: 300;
  line-height: 1.5;
  letter-spacing: 0;
}
```

---

## Implementation in Tailwind

### Configure in tailwind.config.ts:
```javascript
module.exports = {
  theme: {
    fontFamily: {
      'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
    },
    fontWeight: {
      'extralight': '200',
      'light': '300',
      'normal': '400',
      'medium': '500',
    }
  }
}
```

### Usage in Components:
```jsx
// Hero Headline
<h1 className="text-7xl font-extralight tracking-tight">
  Automate Compliance
</h1>

// Body Text
<p className="text-lg font-light text-white/75">
  Transform your regulatory processes...
</p>

// Button
<button className="font-light tracking-tight">
  Get Started
</button>

// Navigation
<a className="font-light text-white/70 hover:text-white">
  Features
</a>
```

---

## Letter Spacing Rules

### Headlines (font-extralight)
- **-0.02em** for hero text (72px+)
- **-0.01em** for large headlines (36-60px)
- **-0.005em** for smaller headlines (24-36px)

### Body Text (font-light)
- **-0.01em** for large body text (18-20px)
- **-0.005em** for standard body (14-16px)
- **0** for small text (12px and below)

### Tailwind Classes:
```css
tracking-tighter  /* -0.05em */
tracking-tight    /* -0.025em */
tracking-normal   /* 0 */
```

---

## Text Color Hierarchy

### On Dark Backgrounds:
```css
text-white           /* Primary text - 100% white */
text-white/90        /* Slightly muted - 90% opacity */
text-white/75        /* Body text - 75% opacity */
text-white/60        /* Secondary text - 60% opacity */
text-white/40        /* Tertiary/disabled - 40% opacity */
```

### Accent Colors:
```css
text-neural-purple-400  /* Purple accents */
text-neural-purple-500  /* Purple CTAs */
text-silver-400         /* Silver accents */
text-silver-500         /* Silver secondary */
```

---

## Common Patterns

### Hero Section:
```jsx
<div className="badge badge-purple mb-6">
  <span className="text-xs font-light uppercase tracking-wider">
    NEW
  </span>
  <span className="text-sm font-light">
    Next-Gen Platform
  </span>
</div>

<h1 className="text-7xl font-extralight tracking-tight text-white mb-6">
  Your Headline Here
</h1>

<p className="text-lg font-light text-white/75 leading-relaxed max-w-2xl">
  Description text with elegant typography
</p>
```

### Dashboard Card:
```jsx
<div className="card">
  <h3 className="text-xl font-light text-white mb-2">
    Card Title
  </h3>
  <p className="text-3xl font-extralight text-white mb-4">
    1,234
  </p>
  <p className="text-sm font-light text-white/60">
    Additional information
  </p>
</div>
```

### Form Elements:
```jsx
<label className="text-sm font-light text-white/60 mb-2">
  Email Address
</label>
<input 
  className="font-light text-white placeholder:text-white/30"
  placeholder="you@example.com"
/>
```

---

## DO's and DON'Ts

### ✅ DO:
- Use Inter exclusively for all text
- Use font-extralight (200) for headlines
- Use font-light (300) for body text
- Apply tight letter-spacing to headlines
- Use opacity for text hierarchy
- Keep consistent weight usage

### ❌ DON'T:
- Mix different font families
- Use bold (600+) weights except rarely
- Use default system fonts
- Apply loose letter-spacing
- Use pure gray colors (use white with opacity)
- Add decorative or script fonts

---

## Loading Fonts in Next.js

```javascript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  weight: ['200', '300', '400', '500'],
});

// Apply to html element
<html className={inter.variable}>
```

---

## CSS Custom Properties

```css
:root {
  --font-family-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-weight-extralight: 200;
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
}
```

---

This font system ensures complete consistency across the entire RuleIQ platform, maintaining the elegant, sophisticated aesthetic established by the neural network hero.
