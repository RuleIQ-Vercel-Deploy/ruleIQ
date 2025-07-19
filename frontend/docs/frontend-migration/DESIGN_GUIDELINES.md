# ruleIQ Design Guidelines for Developers

## Overview

This guide provides practical design implementation guidelines for developers working on the ruleIQ compliance automation platform. Follow these patterns to maintain consistency, accessibility, and brand alignment.

## Component Design Principles

### 1. Consistency First
- Always use design tokens instead of arbitrary values
- Follow established component patterns
- Maintain consistent spacing throughout the application
- Use standardized variant naming across all components

### 2. Accessibility by Default
- Ensure WCAG 2.2 AA compliance for all components
- Implement proper focus management
- Provide meaningful ARIA labels and descriptions
- Support keyboard navigation patterns

### 3. Performance Optimization
- Use CSS-in-JS efficiently with design tokens
- Implement proper loading states and skeleton screens
- Optimize animations for reduced motion preferences
- Lazy load non-critical components

## Component Implementation Patterns

### Button Components

#### ✅ Recommended Pattern
```tsx
import { Button } from "@/components/ui/button"

// Primary action - most important
<Button variant="primary" size="default">
  Save Changes
</Button>

// Secondary action - less emphasis
<Button variant="secondary" size="default">
  Cancel
</Button>

// Accent action - brand highlight
<Button variant="accent" size="lg">
  Start Assessment
</Button>

// Destructive action - dangerous operations
<Button variant="destructive" size="default">
  Delete Account
</Button>
```

#### ❌ Avoid
```tsx
// Don't use arbitrary values
<button className="bg-[#17255A] px-[16px] py-[8px]">

// Don't mix different sizing systems
<Button className="h-[42px] px-5 text-[14px]">

// Don't ignore semantic variants
<Button className="bg-red-500 text-white">Delete</Button>
```

### Card Components

#### ✅ Recommended Pattern
```tsx
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"

<Card className="hover:shadow-md transition-shadow">
  <CardHeader>
    <CardTitle>Assessment Progress</CardTitle>
    <CardDescription>Track your compliance journey</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="space-y-4">
      {/* Content with proper spacing */}
    </div>
  </CardContent>
  <CardFooter className="justify-between">
    <Button variant="secondary">View Details</Button>
    <Button variant="primary">Continue</Button>
  </CardFooter>
</Card>
```

### Form Components

#### ✅ Recommended Pattern
```tsx
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"

<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
    <FormField
      control={form.control}
      name="companyName"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Company Name</FormLabel>
          <FormControl>
            <Input placeholder="Enter your company name" {...field} />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
    
    <div className="flex gap-4">
      <Button type="button" variant="secondary" className="flex-1">
        Cancel
      </Button>
      <Button type="submit" variant="primary" className="flex-1">
        Save
      </Button>
    </div>
  </form>
</Form>
```

## Layout Guidelines

### Page Layout Structure
```tsx
export default function Page() {
  return (
    <div className="container mx-auto px-6 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-navy mb-2">Page Title</h1>
        <p className="text-text-secondary">Descriptive subtitle</p>
      </div>
      
      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          {/* Primary content */}
        </div>
        <div>
          {/* Sidebar content */}
        </div>
      </div>
    </div>
  )
}
```

### Grid Systems
```tsx
// Dashboard grid - responsive
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
  {/* Cards */}
</div>

// Content grid - asymmetric
<div className="grid gap-8 lg:grid-cols-3">
  <div className="lg:col-span-2">{/* Main */}</div>
  <div>{/* Sidebar */}</div>
</div>

// Form grid - consistent
<div className="grid gap-4 sm:grid-cols-2">
  {/* Form fields */}
</div>
```

## Typography Implementation

### Heading Hierarchy
```tsx
// Page title - H1
<h1 className="text-4xl font-bold text-navy">Assessment Results</h1>

// Section title - H2  
<h2 className="text-2xl font-semibold text-navy mb-4">Compliance Score</h2>

// Subsection title - H3
<h3 className="text-lg font-medium text-navy mb-2">GDPR Requirements</h3>

// Body text
<p className="text-base text-text-secondary leading-relaxed">
  Your organization demonstrates strong compliance practices...
</p>

// Metadata / captions
<span className="text-sm text-text-muted">Updated 2 hours ago</span>
```

### Text Color Usage
```tsx
// Primary text on light backgrounds
<p className="text-text-on-light">Main content text</p>

// Secondary information
<p className="text-text-secondary">Supporting information</p>

// Muted text (metadata, placeholders)
<span className="text-text-muted">Last updated...</span>

// Text on colored backgrounds
<div className="bg-gold p-4">
  <p className="text-text-on-gold">Text on gold background</p>
</div>
```

## Interactive States

### Hover States
```tsx
// Cards
<Card className="hover:shadow-md hover:shadow-navy/10 transition-all duration-200">

// Buttons (built into variants)
<Button variant="primary"> // Already includes hover states

// Custom interactive elements
<div className="hover:bg-navy/5 hover:scale-[1.02] transition-all duration-200">
```

### Focus States
```tsx
// Automatic focus management (built into components)
<Button> // Focus states automatically applied

// Custom focusable elements
<div 
  tabIndex={0}
  className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-outline-primary focus-visible:ring-offset-2"
>
```

### Loading States
```tsx
// Button loading
<Button loading disabled>
  {loading ? "Saving..." : "Save Changes"}
</Button>

// Skeleton loading
import { Skeleton } from "@/components/ui/skeleton"

{isLoading ? (
  <Skeleton className="h-[200px] w-full" />
) : (
  <div>{content}</div>
)}
```

## Animation Guidelines

### Micro-interactions
```tsx
import { motion } from "framer-motion"

// Fade in animation
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
>

// Slide up animation  
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, ease: "easeOut" }}
>

// Staggered list animation
<motion.div
  variants={{
    container: {
      initial: { opacity: 0 },
      animate: { 
        opacity: 1,
        transition: { staggerChildren: 0.1 }
      }
    },
    item: {
      initial: { opacity: 0, y: 20 },
      animate: { opacity: 1, y: 0 }
    }
  }}
  initial="initial"
  animate="animate"
>
```

### Reduced Motion Support
```tsx
import { shouldReduceMotion } from "@/lib/styles/animations"

// Conditional animations
<motion.div
  animate={shouldReduceMotion() ? {} : { x: 100 }}
  transition={{ duration: shouldReduceMotion() ? 0 : 0.3 }}
>

// CSS approach
<div className={`transition-all ${shouldReduceMotion() ? 'duration-0' : 'duration-300'}`}>
```

## Error Handling & Validation

### Form Validation
```tsx
// Error states
<FormItem>
  <FormLabel className={error ? "text-error" : ""}>
    Email Address
  </FormLabel>
  <FormControl>
    <Input 
      className={error ? "border-error focus:border-error" : ""}
      {...field} 
    />
  </FormControl>
  {error && (
    <FormMessage className="text-error">
      {error.message}
    </FormMessage>
  )}
</FormItem>
```

### Alert Components
```tsx
import { Alert, AlertDescription } from "@/components/ui/alert"

// Success alert
<Alert variant="success">
  <CheckCircle className="h-4 w-4" />
  <AlertDescription>
    Your assessment has been saved successfully.
  </AlertDescription>
</Alert>

// Error alert
<Alert variant="destructive">
  <AlertCircle className="h-4 w-4" />
  <AlertDescription>
    Unable to save assessment. Please try again.
  </AlertDescription>
</Alert>
```

## Responsive Design

### Breakpoint Usage
```tsx
// Mobile-first responsive grid
<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">

// Responsive text sizing
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">

// Responsive spacing
<div className="p-4 md:p-6 lg:p-8">

// Responsive visibility
<div className="hidden md:block lg:hidden xl:block">
```

### Mobile Considerations
```tsx
// Touch-friendly sizing
<Button size="lg" className="min-h-[44px]"> // 44px minimum touch target

// Mobile navigation
<Sheet> // Use sheet for mobile menus
  <SheetTrigger asChild>
    <Button variant="ghost" size="icon" className="md:hidden">
      <Menu className="h-6 w-6" />
    </Button>
  </SheetTrigger>
</Sheet>
```

## Performance Best Practices

### Component Optimization
```tsx
import { memo, useCallback, useMemo } from "react"

// Memoize expensive components
const ExpensiveComponent = memo(({ data }) => {
  const processedData = useMemo(() => 
    data.map(item => processItem(item)), [data]
  )
  
  const handleClick = useCallback((id) => {
    onItemClick(id)
  }, [onItemClick])
  
  return <div>{/* Render */}</div>
})

// Lazy load heavy components
const HeavyChart = lazy(() => import("@/components/charts/heavy-chart"))

<Suspense fallback={<Skeleton className="h-[400px]" />}>
  <HeavyChart />
</Suspense>
```

### Bundle Optimization
```tsx
// Dynamic imports for routes
const AssessmentPage = lazy(() => import("@/app/assessments/page"))

// Tree-shake libraries
import { format } from "date-fns/format" // Specific import
// not: import { format } from "date-fns" // Full library
```

## Testing Considerations

### Component Testing
```tsx
// Test component variants
test("renders all button variants", () => {
  const variants = ["primary", "secondary", "accent", "outline"]
  
  variants.forEach(variant => {
    render(<Button variant={variant}>Test</Button>)
    // Assert styles and accessibility
  })
})

// Test responsive behavior
test("adapts to mobile viewport", () => {
  global.innerWidth = 375
  render(<ResponsiveComponent />)
  // Assert mobile-specific behavior
})
```

### Accessibility Testing
```tsx
import { axe, toHaveNoViolations } from "jest-axe"

test("has no accessibility violations", async () => {
  const { container } = render(<Component />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

## Code Review Checklist

### ✅ Design Implementation
- [ ] Uses design tokens instead of arbitrary values
- [ ] Follows established component patterns
- [ ] Implements proper spacing using 8px grid
- [ ] Uses standardized variant naming
- [ ] Maintains brand color consistency

### ✅ Accessibility
- [ ] Proper ARIA labels and descriptions
- [ ] Keyboard navigation support
- [ ] Focus management implementation
- [ ] Color contrast compliance
- [ ] Reduced motion support

### ✅ Performance
- [ ] Proper component memoization
- [ ] Efficient re-rendering patterns
- [ ] Optimized bundle imports
- [ ] Skeleton loading states
- [ ] Responsive image optimization

### ✅ Responsiveness
- [ ] Mobile-first implementation
- [ ] Touch-friendly interactions
- [ ] Proper breakpoint usage
- [ ] Content reflow validation
- [ ] Cross-device testing

## Common Patterns Library

### Data Display
```tsx
// Stat cards
<Card>
  <CardContent className="flex items-center justify-between p-6">
    <div>
      <p className="text-sm text-text-muted">Compliance Score</p>
      <p className="text-3xl font-bold text-navy">94%</p>
    </div>
    <div className="rounded-full bg-success/10 p-3">
      <Shield className="h-6 w-6 text-success" />
    </div>
  </CardContent>
</Card>

// Progress indicators
<div className="space-y-2">
  <div className="flex justify-between text-sm">
    <span>GDPR Compliance</span>
    <span>78%</span>
  </div>
  <Progress value={78} className="h-2" />
</div>
```

### Navigation Patterns
```tsx
// Breadcrumb navigation
<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbPage>Assessments</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>

// Tab navigation
<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Overview</TabsTrigger>
    <TabsTrigger value="details">Details</TabsTrigger>
    <TabsTrigger value="history">History</TabsTrigger>
  </TabsList>
  <TabsContent value="overview">
    {/* Content */}
  </TabsContent>
</Tabs>
```

This comprehensive guide ensures consistent, accessible, and performant component implementation across the ruleIQ platform. Always refer to these patterns when building new features or updating existing components.