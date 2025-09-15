# Neural Purple Theme Implementation Guide

## Quick Start

### 1. Update Tailwind Configuration
```bash
# Backup current config
cp tailwind.config.ts tailwind.config.ts.backup

# Use the neural theme config
cp tailwind.config.neural.ts tailwind.config.ts
```

### 2. Update Global Styles
```bash
# Backup current styles
cp app/globals.css app/globals.css.backup

# Use the neural theme styles
cp styles/globals.neural.css app/globals.css
```

### 3. Update Your Layout
```tsx
// app/layout.tsx
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-black text-white font-sans font-light antialiased">
        {children}
      </body>
    </html>
  )
}
```

## Component Conversion Guide

### Typography Changes

#### Before (Teal Theme):
```tsx
<h1 className="text-4xl font-bold text-teal-500">Title</h1>
<p className="text-gray-600">Description text</p>
```

#### After (Neural Purple Theme):
```tsx
<h1 className="text-5xl font-extralight tracking-tight text-white">Title</h1>
<p className="text-lg font-light text-white/75">Description text</p>
```

### Button Changes

#### Before:
```tsx
<button className="bg-teal-500 hover:bg-teal-600 px-4 py-2 rounded">
  Click Me
</button>
```

#### After:
```tsx
<button className="btn btn-primary">
  Click Me
</button>
```

### Card Changes

#### Before:
```tsx
<div className="bg-white rounded-lg shadow p-6">
  <h3 className="text-xl font-semibold">Card Title</h3>
  <p className="text-gray-600">Card content</p>
</div>
```

#### After:
```tsx
<div className="card">
  <h3 className="text-xl font-light text-white mb-3">Card Title</h3>
  <p className="text-sm font-light text-white/60">Card content</p>
</div>
```

## Color Mapping

| Old (Teal) | New (Neural Purple) |
|------------|-------------------|
| teal-500 | neural-purple-500 |
| teal-600 | neural-purple-600 |
| teal-400 | neural-purple-400 |
| gray-600 | white/60 |
| gray-500 | white/50 |
| gray-400 | white/40 |
| white | black |
| black | white |

## Key Design Rules

### ✅ DO:
- Use `font-extralight` for all headlines
- Use `font-light` for all body text
- Apply `tracking-tight` to headlines
- Use white with opacity for text hierarchy
- Add purple accents sparingly (CTAs, active states)
- Use silver for secondary elements
- Apply glass morphism to overlays
- Keep animations subtle (300ms transitions)

### ❌ DON'T:
- Use emojis anywhere
- Use bold font weights (except for emphasis)
- Use bright/saturated colors
- Add bouncy or playful animations
- Use teal or blue colors
- Mix different design patterns

## Component Classes Reference

### Text Styles
```css
.headline       /* Large headlines */
.body-text      /* Body paragraphs */
.ui-text        /* Interface text */
.text-gradient  /* Purple gradient text */
```

### Buttons
```css
.btn-primary    /* Primary CTA */
.btn-secondary  /* Secondary action */
.btn-ghost      /* Subtle action */
```

### Cards & Containers
```css
.card           /* Standard card */
.card-dark      /* Dark variant */
.glass          /* Glass morphism */
.glass-dark     /* Dark glass */
```

### Utilities
```css
.hover-lift     /* Hover animation */
.glow-purple    /* Purple shadow */
.divider        /* Section divider */
.skeleton       /* Loading state */
```

## Page Template

```tsx
export default function Page() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-neural-purple-900 via-black to-black">
      {/* Navigation */}
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="badge badge-purple mb-6">
            NEW • Feature Update
          </div>
          
          <h1 className="text-hero font-extralight tracking-tight text-white mb-6">
            Your Headline
            <span className="text-neural-purple-400"> Here</span>
          </h1>
          
          <p className="text-lg font-light text-white/75 mb-8 max-w-2xl">
            Description text with elegant typography and proper spacing.
          </p>
          
          <div className="flex gap-4">
            <button className="btn btn-primary">Primary Action</button>
            <button className="btn btn-secondary">Secondary</button>
          </div>
        </div>
      </section>
      
      {/* Content Sections */}
      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid-features">
            {/* Feature cards */}
          </div>
        </div>
      </section>
    </div>
  );
}
```

## Migration Checklist

- [ ] Update Tailwind config
- [ ] Update global CSS
- [ ] Replace teal colors with purple
- [ ] Update font weights (bold → light/extralight)
- [ ] Remove all emojis
- [ ] Update button styles
- [ ] Update card components
- [ ] Apply glass morphism to modals/overlays
- [ ] Update navigation styles
- [ ] Test dark mode consistency
- [ ] Verify accessibility contrast ratios

## Questions?

Refer to:
- `DESIGN_SYSTEM_V2.md` - Complete design system documentation
- `components/examples/neural-components.tsx` - Component examples
- `styles/globals.neural.css` - Global styles
- `tailwind.config.neural.ts` - Tailwind configuration
