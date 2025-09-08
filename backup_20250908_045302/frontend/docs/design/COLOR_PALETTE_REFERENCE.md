# ruleIQ New Color Palette - Quick Reference

## 🎨 Primary Brand Colors

### Teal (Primary Brand Color)

```css
/* Main Teal Shades */
--teal-50: #e6fffa /* Lightest - backgrounds */ --teal-100: #b2f5ea /* Light backgrounds */
  --teal-200: #81e6d9 /* Light accents */ --teal-300: #4fd1c5 /* Bright accent */
  --teal-400: #38b2ac /* Medium teal */ --teal-500: #319795 /* Standard teal */ --teal-600: #2c7a7b
  /* PRIMARY - Main brand color */ --teal-700: #285e61 /* Dark - hover states */ --teal-800: #234e52
  /* Darker */ --teal-900: #1d4044 /* Darkest */;
```

### Usage Examples

```tsx
// Primary button
bg-[#2C7A7B] hover:bg-[#285E61]

// Light background
bg-[#E6FFFA]

// Icon backgrounds
bg-[#E6FFFA] with text-[#2C7A7B]

// Accent elements
border-[#4FD1C5] or text-[#4FD1C5]
```

## 🌫️ Neutral Colors (Grays)

```css
/* Gray Scale */
--gray-50: #f9fafb /* Lightest backgrounds */ --gray-100: #f3f4f6 /* Light backgrounds */
  --gray-200: #e5e7eb /* Borders, dividers */ --gray-300: #d1d5db /* Disabled borders */
  --gray-400: #9ca3af /* Placeholder text */ --gray-500: #6b7280 /* Muted text */
  --gray-600: #4b5563 /* Secondary text */ --gray-700: #374151 /* Body text */ --gray-800: #1f2937
  /* Headings */ --gray-900: #111827 /* Primary text */;
```

## ✅ Semantic Colors

### Success (Green)

```css
--success-50: #f0fdf4 --success-100: #dcfce7 --success-200: #bbf7d0 --success-500: #10b981
  /* Main success color */ --success-600: #059669 --success-700: #047857;
```

### Warning (Amber)

```css
--warning-50: #fffbeb --warning-100: #fef3c7 --warning-200: #fde68a --warning-500: #f59e0b
  /* Main warning color */ --warning-600: #d97706 --warning-700: #b45309;
```

### Error (Red)

```css
--error-50: #fef2f2 --error-100: #fee2e2 --error-200: #fecaca --error-500: #ef4444
  /* Main error color */ --error-600: #dc2626 --error-700: #b91c1c;
```

### Info (Blue)

```css
--info-50: #eff6ff --info-100: #dbeafe --info-200: #bfdbfe --info-500: #3b82f6 /* Main info color */
  --info-600: #2563eb --info-700: #1d4ed8;
```

## 🎯 Component Color Mapping

### Buttons

```tsx
// Primary
className = 'bg-[#2C7A7B] hover:bg-[#285E61] text-white';

// Secondary
className = 'bg-white hover:bg-gray-50 text-[#2C7A7B] border-2 border-[#2C7A7B]';

// Ghost
className = 'text-[#2C7A7B] hover:text-[#285E61] hover:bg-[#E6FFFA]';

// Destructive
className = 'bg-red-500 hover:bg-red-600 text-white';
```

### Backgrounds

```tsx
// Page background
className = 'bg-gray-50';

// Card background
className = 'bg-white';

// Hover state
className = 'hover:bg-gray-50';

// Active/Selected
className = 'bg-[#E6FFFA]';
```

### Text

```tsx
// Primary text
className = 'text-gray-900';

// Secondary text
className = 'text-gray-600';

// Muted text
className = 'text-gray-500';

// Link text
className = 'text-[#2C7A7B] hover:text-[#285E61]';
```

### Borders

```tsx
// Default border
className = 'border-gray-200';

// Focus border
className = 'focus:border-[#2C7A7B]';

// Hover border
className = 'hover:border-gray-300';
```

## 🌈 Gradients

```css
/* Brand gradient */
bg-gradient-to-r from-[#2C7A7B] to-[#38B2AC]

/* Success gradient */
bg-gradient-to-r from-[#10B981] to-[#34D399]

/* Subtle gradient for backgrounds */
bg-gradient-to-br from-white to-gray-50
```

## 🎭 Shadows

```css
/* Elevation levels */
--shadow-sm:
  0 1px 2px 0 rgb(0 0 0 / 0.05) --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1),
  0 1px 2px -1px rgb(0 0 0 / 0.1) --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1),
  0 2px 4px -2px rgb(0 0 0 / 0.1) --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1),
  0 4px 6px -4px rgb(0 0 0 / 0.1) --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1),
  0 8px 10px -6px rgb(0 0 0 / 0.1);
```

## 🔍 Focus States

```css
/* Focus ring */
focus:ring-2 focus:ring-[#2C7A7B]/20 focus:border-[#2C7A7B]

/* Focus visible (keyboard navigation) */
focus-visible:ring-2 focus-visible:ring-[#2C7A7B] focus-visible:ring-offset-2
```

## ♿ Accessibility Contrast

### WCAG AA Compliant Combinations

- `#2C7A7B` on white: **5.87:1** ✅
- `#285E61` on white: **7.54:1** ✅
- Gray-900 on white: **19.30:1** ✅
- Gray-600 on white: **7.46:1** ✅
- White on `#2C7A7B`: **5.87:1** ✅

### WCAG AAA Compliant Combinations

- Gray-900 on white: **19.30:1** ✅
- Gray-800 on white: **12.63:1** ✅
- Gray-700 on white: **9.03:1** ✅

## 🚀 Quick Implementation

### Tailwind Config Update

```js
// tailwind.config.ts
colors: {
  teal: {
    50: '#E6FFFA',
    100: '#B2F5EA',
    200: '#81E6D9',
    300: '#4FD1C5',
    400: '#38B2AC',
    500: '#319795',
    600: '#2C7A7B',
    700: '#285E61',
    800: '#234E52',
    900: '#1D4044',
  },
  // ... rest of colors
}
```

### CSS Variables

```css
:root {
  --color-primary: #2c7a7b;
  --color-primary-hover: #285e61;
  --color-primary-light: #e6fffa;
  --color-text-primary: #111827;
  --color-text-secondary: #4b5563;
  --color-text-muted: #6b7280;
  --color-border: #e5e7eb;
  --color-background: #ffffff;
  --color-background-secondary: #f9fafb;
}
```

This color palette creates a clean, professional, and modern appearance that conveys trust and reliability - perfect for a compliance automation platform.
