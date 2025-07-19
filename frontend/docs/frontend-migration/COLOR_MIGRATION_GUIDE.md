# ruleIQ Color Migration Guide

This guide documents the color system migration from the old navy/gold theme to the new modern purple/cyan gradient theme.

## Color Palette Overview

### Old Colors → New Colors Mapping

| Old Color | Old Hex | New Color | New Hex | Usage |
|-----------|---------|-----------|---------|--------|
| navy | #17255A | brand-primary | #7C3AED | Primary brand color |
| gold | #CB963E | warning / brand-secondary | #F59E0B / #06B6D4 | Warnings or secondary accents |
| turquoise | #00BCD4 | brand-secondary | #06B6D4 | Secondary brand color |
| midnight | #0F172A | surface-base | #0A0A0B | Base background |

### New Color System

```scss
// Brand Colors
brand: {
  primary: "#7C3AED",     // Vibrant purple
  secondary: "#06B6D4",   // Cyan
  tertiary: "#10B981",    // Emerald
  dark: "#5B21B6",        // Dark purple
  light: "#A78BFA",       // Light purple
}

// Surface Colors (Dark Theme)
surface: {
  base: "#0A0A0B",        // Near black
  primary: "#111113",     // Primary surface
  secondary: "#18181B",   // Secondary surface
  tertiary: "#27272A",    // Tertiary surface
  elevated: "#2D2D30",    // Elevated components
}

// Text Colors
text: {
  primary: "#FAFAFA",     // High contrast white
  secondary: "#A1A1AA",   // Muted gray
  tertiary: "#71717A",    // Even more muted
  inverse: "#0A0A0B",     // For light backgrounds
  brand: "#A78BFA",       // Brand purple text
  accent: "#67E8F9",      // Cyan accent text
}

// Semantic Colors
success: "#10B981",       // Emerald
warning: "#F59E0B",       // Amber
error: "#EF4444",         // Red
info: "#06B6D4",          // Cyan
```

## Component Migration Patterns

### 1. Backgrounds

```tsx
// Old
<div className="bg-background"> // or bg-midnight
<div className="bg-card">

// New
<div className="bg-surface-base">
<div className="bg-surface-primary">
```

### 2. Text Colors

```tsx
// Old
<p className="text-foreground">
<p className="text-muted-foreground">

// New
<p className="text-text-primary">
<p className="text-text-secondary">
```

### 3. Brand Colors

```tsx
// Old
<span className="text-navy">rule</span>
<span className="text-gold">IQ</span>

// New
<span className="gradient-text">ruleIQ</span>
// or
<span className="text-brand-primary">text</span>
```

### 4. Buttons

```tsx
// Old
<Button className="bg-gold hover:bg-gold-dark text-navy">

// New
<Button className="btn-gradient">
// or
<Button className="glass-card hover:bg-glass-white-hover">
```

### 5. Cards

```tsx
// Old
<Card className="bg-card border-border">

// New
<Card className="glass-card">
```

## Utility Classes

### Gradient Effects

```tsx
// Gradient Text
<h1 className="gradient-text">Title</h1>

// Gradient Background (animated)
<div className="gradient-bg">Content</div>

// Mesh Gradient Background
<div className="mesh-gradient">Content</div>
```

### Glass Morphism

```tsx
// Glass Card
<div className="glass-card">Content</div>

// Glass properties
glass: {
  white: "rgba(255, 255, 255, 0.05)",
  "white-hover": "rgba(255, 255, 255, 0.08)",
  border: "rgba(255, 255, 255, 0.1)",
  "border-hover": "rgba(255, 255, 255, 0.2)",
}
```

### Glow Effects

```tsx
// Purple Glow
<div className="glow-purple">Content</div>

// Cyan Glow
<div className="glow-cyan">Content</div>
```

## Migration Checklist

- [ ] Update Tailwind config with new color values
- [ ] Update global CSS variables in `globals.css`
- [ ] Replace all instances of old color classes
- [ ] Apply glass morphism to cards and modals
- [ ] Update buttons to use gradient or glass styles
- [ ] Apply gradient text to headings and brand elements
- [ ] Update backgrounds to use new surface colors
- [ ] Test both light and dark themes (if applicable)
- [ ] Update any hardcoded color values in component styles
- [ ] Review and update hover/focus states
- [ ] Check accessibility contrast ratios

## Common Patterns

### Hero Sections
```tsx
<section className="bg-surface-base">
  <div className="mesh-gradient" />
  <h1 className="gradient-text">Title</h1>
  <Button className="btn-gradient">CTA</Button>
</section>
```

### Dashboard Cards
```tsx
<Card className="glass-card">
  <CardHeader>
    <CardTitle className="gradient-text">Title</CardTitle>
  </CardHeader>
  <CardContent className="text-text-secondary">
    Content
  </CardContent>
</Card>
```

### Forms
```tsx
<form className="glass-card p-8">
  <Input className="bg-surface-secondary/50 border-glass-border" />
  <Button className="btn-gradient">Submit</Button>
</form>
```

## Notes

1. The new color system is designed for dark mode first
2. Glass morphism effects require backdrop-blur support
3. Gradient animations may impact performance on low-end devices
4. Always test color contrast for accessibility (WCAG AA minimum)
5. The legacy color mappings in Tailwind config allow gradual migration

## Resources

- Tailwind Config: `/tailwind.config.ts`
- Global Styles: `/app/globals.css`
- Component Examples: `/app/page.tsx` (Hero), `/app/(auth)/login/page.tsx` (Forms)