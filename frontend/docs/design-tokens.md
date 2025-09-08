# Design Tokens Documentation

## Overview
This document outlines the design tokens and component system for the ruleIQ frontend application.

## Design Tokens

### Spacing
The spacing system uses Tailwind's default spacing scale with rem units:
- `spacing-0`: 0
- `spacing-1`: 0.25rem (4px)
- `spacing-2`: 0.5rem (8px)
- `spacing-4`: 1rem (16px)
- `spacing-6`: 1.5rem (24px)
- `spacing-8`: 2rem (32px)
- `spacing-12`: 3rem (48px)
- `spacing-16`: 4rem (64px)

### Typography
Font system configuration:
- **Font Family**: Inter (system font stack fallback)
- **Font Sizes**: Tailwind default scale (text-xs to text-9xl)
- **Font Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)
- **Line Heights**: Tailwind defaults with optimal readability

### Border Radius
Consistent radius tokens for UI elements:
- `radius-none`: 0
- `radius-sm`: 0.125rem (2px)
- `radius-md`: 0.375rem (6px) - default
- `radius-lg`: 0.5rem (8px)
- `radius-xl`: 0.75rem (12px)
- `radius-2xl`: 1rem (16px)
- `radius-full`: 9999px

### Shadows
Elevation system for depth perception:
- `shadow-sm`: Small shadow for subtle elevation
- `shadow-md`: Medium shadow for cards and dropdowns
- `shadow-lg`: Large shadow for modals and overlays
- `shadow-xl`: Extra large shadow for high elevation
- `shadow-2xl`: Maximum elevation

### Colors
The color system is defined in `tailwind.config.ts`:

#### Brand Colors
- **Primary**: `#2C7A7B` (teal-600)
- **Secondary**: `#319795` (teal-500)
- **Tertiary**: `#4FD1C5` (teal-300)

#### Semantic Colors
- **Success**: `#10B981`
- **Warning**: `#F59E0B`
- **Error**: `#EF4444`
- **Info**: `#319795`

#### Surface Colors
- **Base**: `#FFFFFF`
- **Primary**: `#FFFFFF`
- **Secondary**: `#F9FAFB`
- **Tertiary**: `#F3F4F6`

## Base Components

### Button Component
Located at: `components/ui/button.tsx`

Variants:
- `default`: Primary brand color
- `secondary`: Secondary/muted style
- `destructive`: Error/danger actions
- `outline`: Border-only style
- `ghost`: Minimal/text style
- `link`: Link-like appearance

Sizes:
- `sm`: Small size
- `md`: Medium/default size
- `lg`: Large size
- `icon`: Icon-only square button

### Card Component
Located at: `components/ui/card.tsx`

Structure:
- `Card`: Container with padding and border
- `CardHeader`: Header section
- `CardTitle`: Title text
- `CardDescription`: Subtitle/description
- `CardContent`: Main content area
- `CardFooter`: Footer with actions

### Form Component
Located at: `components/ui/form.tsx`

Features:
- React Hook Form integration
- Zod validation support
- Accessible form controls
- Error state handling
- Field-level validation

### DataTable Component
Located at: `components/ui/table.tsx`

Features:
- Responsive design
- Sortable columns
- Pagination support
- Bulk actions
- Export functionality

## Focus Ring Token
All interactive elements include a consistent focus ring for accessibility:
```css
focus-visible:outline-none 
focus-visible:ring-2 
focus-visible:ring-ring 
focus-visible:ring-offset-2
```

## Usage Guidelines

### Applying Tokens
Use Tailwind utility classes to apply design tokens:
```jsx
// Spacing
<div className="p-4 mt-6 mb-8">

// Typography
<h1 className="text-2xl font-bold">

// Colors
<button className="bg-brand-primary text-white">

// Shadows
<div className="shadow-md rounded-lg">
```

### Component Composition
Combine base components for complex UI:
```jsx
<Card>
  <CardHeader>
    <CardTitle>Dashboard</CardTitle>
  </CardHeader>
  <CardContent>
    <Button variant="default">Action</Button>
  </CardContent>
</Card>
```

## Accessibility
- All components support keyboard navigation
- ARIA attributes are properly implemented
- Focus indicators meet WCAG 2.1 AA standards
- Color contrast ratios exceed minimum requirements