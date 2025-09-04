# Animated Logo Implementation

## Overview

The spinning hexagon logo animation creates a premium, dynamic first impression for ruleIQ. The implementation uses Framer Motion for smooth, performant animations with accessibility considerations.

## Files Created

1. `/components/ui/animated-logo.tsx` - Core animated logo component
2. `/components/sections/landing-hero.tsx` - Hero section with spinning logo

## Usage Examples

### 1. Landing Page Hero (One-time spin on load)

```tsx
import { LandingHero } from '@/components/sections/landing-hero';

export default function HomePage() {
  return <LandingHero />;
}
```

### 2. Loading State (Continuous spin)

```tsx
import { LoadingLogo } from '@/components/sections/landing-hero';

// Use during data fetching or page transitions
{
  isLoading && <LoadingLogo />;
}
```

### 3. Navigation Logo (Spin on hover)

```tsx
import { NavLogo } from '@/components/sections/landing-hero';

<header>
  <NavLogo />
</header>;
```

### 4. Custom Implementation

```tsx
import { AnimatedLogo } from "@/components/ui/animated-logo"

// One-time spin
<AnimatedLogo size="xl" animationType="once" duration={3} />

// Continuous spin
<AnimatedLogo size="lg" animationType="continuous" duration={5} />

// Hover to spin
<AnimatedLogo size="default" animationType="hover" />

// Loading spinner
<AnimatedLogo size="sm" animationType="loading" />
```

## Animation Types

| Type         | Behavior                                  | Use Case                  |
| ------------ | ----------------------------------------- | ------------------------- |
| `once`       | Spins 360° on mount with scale/fade in    | Hero sections, first load |
| `continuous` | Infinite rotation after initial animation | Background elements       |
| `hover`      | Spins 360° when hovered                   | Interactive elements      |
| `loading`    | Continuous spin without intro animation   | Loading states            |

## Performance Features

1. **Reduced Motion Support**: Automatically disables spin for users who prefer reduced motion
2. **GPU Acceleration**: Uses `transform` for smooth 60fps animation
3. **Scroll-linked Animation**: Logo responds to scroll for parallax effect
4. **Lazy Loading**: Component can be dynamically imported

## Customization

### Sizes

- `sm`: 64x64px (navigation)
- `default`: 96x96px (cards)
- `lg`: 128x128px (sections)
- `xl`: 192x192px (hero)

### Duration

- Default: 2 seconds for one rotation
- Adjustable via `duration` prop

### Additional Effects

- Glow pulse animation
- Scale on hover
- Scroll-based rotation

## Integration with Landing Page

Update your `/app/page.tsx`:

```tsx
import { LandingHero } from '@/components/sections/landing-hero';

export default function HomePage() {
  return (
    <main>
      <LandingHero />
      {/* Rest of your landing page */}
    </main>
  );
}
```

## Accessibility

- Respects `prefers-reduced-motion`
- Maintains visual hierarchy without animation
- Provides ARIA labels for screen readers
- Non-blocking animation (doesn't prevent interaction)

## Browser Support

- All modern browsers
- Falls back gracefully in older browsers
- CSS transforms for wide compatibility

---

The spinning hexagon creates a memorable brand moment while maintaining performance and accessibility standards.
