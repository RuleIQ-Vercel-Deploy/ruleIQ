# RuleIQ Design System
## Based on Neural Network Hero Typography & Styling

### Core Design Philosophy
**"Elegant Minimalism with Technical Sophistication"**

Our design language is inspired by the hero section's light, airy typography and subtle animations. We prioritize readability, breathing room, and sophisticated simplicity.

---

## Logo Usage

### Logo Variants
- **Light Version** (`ruleiq-logo-light.png`): For use on dark backgrounds
- **Dark Version** (`ruleiq-logo-dark.png`): For use on light backgrounds

### Logo Implementation
```tsx
<Image 
  src="/ruleiq-logo-dark.png" 
  alt="RuleIQ" 
  width={128}
  height={40}
  className="object-contain"
  priority
/>
```

### Logo Guidelines
- Minimum clear space: 16px on all sides
- Minimum width: 100px for legibility
- The circuit board pattern in "IQ" should remain clearly visible
- Logo should have subtle hover effects (scale: 1.05) on interactive elements
- Always maintain aspect ratio

---

## 🎨 Color Palette

### Primary Colors
```css
--purple-primary: #8B5CF6;     /* Main brand purple */
--purple-dark: #7C3AED;        /* Hover states */
--purple-light: #A78BFA;       /* Accents */
--purple-subtle: #EDE9FE;      /* Backgrounds */
```

### Accent Colors
```css
--silver-primary: #C0C0C0;     /* Silver accents */
--silver-light: #E5E5E5;       /* Light silver */
--silver-dark: #9CA3AF;        /* Dark silver */
```

### Neutral Colors
```css
--black: #000000;              /* Pure black backgrounds */
--gray-950: #030712;           /* Near black */
--gray-900: #111827;           /* Dark sections */
--gray-800: #1F2937;           /* Borders */
--gray-600: #4B5563;           /* Muted text */
--gray-400: #9CA3AF;           /* Subtle text */
--white: #FFFFFF;              /* Primary text */
```

---

## 📝 Typography System

### Font Family
```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Type Scale (Based on Hero)

#### Display (Hero Titles)
```css
.text-display {
  font-size: clamp(3rem, 5vw, 4.5rem);  /* 48-72px */
  font-weight: 200;                      /* Extra light */
  line-height: 1.05;                     /* Tight */
  letter-spacing: -0.02em;               /* Tight tracking */
  color: var(--white);
}
```

#### Heading 1
```css
.text-h1 {
  font-size: clamp(2.5rem, 4vw, 3.75rem); /* 40-60px */
  font-weight: 200;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--white);
}
```

#### Heading 2
```css
.text-h2 {
  font-size: clamp(2rem, 3vw, 3rem);     /* 32-48px */
  font-weight: 300;
  line-height: 1.2;
  letter-spacing: -0.01em;
  color: var(--white);
}
```

#### Heading 3
```css
.text-h3 {
  font-size: clamp(1.5rem, 2vw, 2rem);   /* 24-32px */
  font-weight: 300;
  line-height: 1.3;
  letter-spacing: -0.01em;
  color: var(--white);
}
```

#### Body Large (Descriptions)
```css
.text-body-lg {
  font-size: 1.125rem;                   /* 18px */
  font-weight: 300;
  line-height: 1.75;                     /* Relaxed */
  letter-spacing: -0.01em;
  color: var(--gray-400);
}
```

#### Body Regular
```css
.text-body {
  font-size: 1rem;                       /* 16px */
  font-weight: 300;
  line-height: 1.625;
  letter-spacing: normal;
  color: var(--gray-400);
}
```

#### Small Text
```css
.text-sm {
  font-size: 0.875rem;                   /* 14px */
  font-weight: 300;
  line-height: 1.5;
  letter-spacing: 0;
  color: var(--gray-600);
}
```

#### Micro Text (Badges/Labels)
```css
.text-micro {
  font-size: 0.625rem;                   /* 10px */
  font-weight: 300;
  text-transform: uppercase;
  letter-spacing: 0.08em;                /* Wide tracking */
  color: var(--gray-600);
}
```

---

## 🎯 Component Patterns

### Badges (Like "NEW • Next-Gen Compliance Platform")
```tsx
<div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 backdrop-blur-sm">
  <span className="text-[10px] font-light uppercase tracking-[0.08em] text-white/70">
    {label}
  </span>
  <span className="h-1 w-1 rounded-full bg-white/40" />
  <span className="text-xs font-light tracking-tight text-white/80">
    {text}
  </span>
</div>
```

### Primary Buttons
```tsx
<button className="rounded-2xl border border-white/10 bg-white/10 px-5 py-3 text-sm font-light tracking-tight text-white backdrop-blur-sm transition-all duration-300 hover:bg-white/20">
  {text}
</button>
```

### Secondary Buttons
```tsx
<button className="rounded-2xl border border-white/10 px-5 py-3 text-sm font-light tracking-tight text-white/80 transition-all duration-300 hover:bg-white/5">
  {text}
</button>
```

### Cards
```tsx
<div className="relative bg-gray-900/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-800 hover:border-purple-500/50 transition-all duration-300">
  {/* Content */}
  <div className="absolute inset-0 rounded-2xl bg-purple-600/0 group-hover:bg-purple-600/5 transition-colors duration-300" />
</div>
```

### Micro Details List
```tsx
<ul className="flex flex-wrap gap-6 text-xs font-extralight tracking-tight text-white/60">
  {details.map(detail => (
    <li className="flex items-center gap-2">
      <span className="h-1 w-1 rounded-full bg-white/40" />
      {detail}
    </li>
  ))}
</ul>
```

---

## ✨ Animation Patterns

### Text Reveal (GSAP SplitText)
```javascript
const split = SplitText.create(element, {
  type: 'lines',
  linesClass: 'split-line',
});

gsap.from(split.lines, {
  filter: 'blur(16px)',
  yPercent: 30,
  autoAlpha: 0,
  scale: 1.06,
  duration: 0.9,
  stagger: 0.15,
  ease: 'power3.out'
});
```

### Fade Up Animation
```javascript
gsap.from(element, {
  autoAlpha: 0,
  y: 8,
  duration: 0.5,
  ease: 'power3.out'
});
```

### Hover Transitions
```css
transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
```

---

## 📐 Spacing System

Based on 4px grid:
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

---

## 🌟 Key Design Principles

### 1. **Generous White Space**
- Let elements breathe
- Use large padding and margins
- Create visual hierarchy through spacing

### 2. **Light Font Weights**
- Primary: 200-300 weight
- Never exceed 600 weight
- Use weight variations for hierarchy

### 3. **Tight Letter Spacing**
- Headlines: -0.02em
- Body: -0.01em to normal
- Micro text: 0.08em (wide for uppercase)

### 4. **Subtle Animations**
- Smooth, elegant transitions
- Blur effects for reveals
- Gentle scaling and opacity changes

### 5. **Layered Transparency**
- Use white/10, white/20 for glass effects
- Layer multiple transparent elements
- Backdrop blur for depth

### 6. **Minimal Color Usage**
- Primarily black/white/gray
- Purple for primary actions
- Silver for premium accents

---

## 🎭 Page Section Templates

### Hero Section
```tsx
<section className="relative h-screen w-screen overflow-hidden">
  {/* Background animation */}
  <div className="absolute inset-0 -z-10" />
  
  {/* Content */}
  <div className="relative mx-auto flex max-w-7xl flex-col items-start gap-6 px-6 pb-24 pt-36">
    {/* Badge */}
    {/* Title with SplitText animation */}
    {/* Description */}
    {/* CTAs */}
    {/* Micro details */}
  </div>
  
  {/* Gradient overlay */}
  <div className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/40 to-transparent" />
</section>
```

### Content Section
```tsx
<section className="relative bg-black py-24">
  <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div className="text-center mb-16">
      <h2 className="text-4xl font-light text-white mb-4">
        {title}
      </h2>
      <p className="text-xl font-light text-gray-400 max-w-3xl mx-auto">
        {description}
      </p>
    </div>
    {/* Content grid/layout */}
  </div>
</section>
```

---

## 🚀 Implementation Guidelines

1. **Always start with the lightest font weight** and only increase if necessary
2. **Use tight letter-spacing** on all headlines
3. **Implement smooth transitions** on all interactive elements
4. **Layer transparencies** for depth without heavy shadows
5. **Maintain high contrast** for accessibility (WCAG AA minimum)
6. **Use the micro details pattern** for supporting information
7. **Apply the badge pattern** for status indicators
8. **Keep animations subtle** but meaningful

---

## 📱 Responsive Considerations

- Use `clamp()` for fluid typography
- Maintain proportional spacing across breakpoints
- Simplify animations on mobile devices
- Ensure touch targets are minimum 44x44px
- Test on actual devices, not just browser DevTools

---

This design system captures the essence of the neural network hero's elegant typography and creates a cohesive visual language for the entire RuleIQ application.
