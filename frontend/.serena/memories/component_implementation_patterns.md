# Component Implementation Patterns - Updated for Teal Theme

## Component Architecture Patterns

### Button Component Variants (Teal Theme)

```tsx
// Primary - Main actions (Teal)
<Button variant="primary" size="default">Save Changes</Button>

// Secondary - Less emphasis (Neutral)
<Button variant="secondary" size="default">Cancel</Button>

// Accent - Brand highlight (Bright Teal)
<Button variant="accent" size="lg">Start Assessment</Button>

// Destructive - Dangerous operations (Red)
<Button variant="destructive" size="default">Delete Account</Button>

// Ghost - Minimal styling (Transparent with teal text)
<Button variant="ghost">Learn More</Button>
```

### Card Component Structure

```tsx
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';

<Card className="transition-shadow hover:shadow-md">
  <CardHeader>
    <CardTitle>Assessment Progress</CardTitle>
    <CardDescription>Track your compliance journey</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="space-y-4">{/* Content with proper spacing */}</div>
  </CardContent>
  <CardFooter className="justify-between">
    <Button variant="secondary">View Details</Button>
    <Button variant="primary">Continue</Button>
  </CardFooter>
</Card>;
```

### Form Component Patterns

```tsx
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from '@/components/ui/form';

<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
    <FormField
      control={form.control}
      name="companyName"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Company Name</FormLabel>
          <FormControl>
            <Input
              placeholder="Enter your company name"
              className="focus:border-teal-600 focus:ring-teal-600"
              {...field}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  </form>
</Form>;
```

## Layout Patterns

### Page Layout Structure

```tsx
export default function Page() {
  return (
    <div className="container mx-auto px-6 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="mb-2 text-4xl font-bold text-neutral-900">Page Title</h1>
        <p className="text-neutral-600">Descriptive subtitle</p>
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">{/* Primary content */}</div>
        <div>{/* Sidebar content */}</div>
      </div>
    </div>
  );
}
```

### Navigation Patterns

```tsx
// Sidebar Navigation (Teal Theme)
<div className="sidebar bg-white border-r border-neutral-200">
  <nav className="p-4 space-y-2">
    <a className="flex items-center p-3 rounded-lg text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 active:bg-teal-50 active:text-teal-700">
      <DashboardIcon className="w-5 h-5 mr-3" />
      Dashboard
    </a>
  </nav>
</div>

// Top Navigation
<header className="bg-white border-b border-neutral-200 px-6 py-4">
  <div className="flex items-center justify-between">
    <div className="flex items-center space-x-4">
      <h1 className="text-xl font-semibold text-neutral-900">ruleIQ</h1>
    </div>
    <div className="flex items-center space-x-4">
      <Button variant="ghost" size="icon">
        <Bell className="w-5 h-5" />
      </Button>
    </div>
  </div>
</header>
```

## Typography Implementation (Updated)

### Text Hierarchy

```tsx
// Page title - H1
<h1 className="text-4xl font-bold text-neutral-900">Assessment Results</h1>

// Section title - H2
<h2 className="text-2xl font-semibold text-neutral-900 mb-4">Compliance Score</h2>

// Subsection title - H3
<h3 className="text-lg font-medium text-neutral-900 mb-2">GDPR Requirements</h3>

// Body text
<p className="text-base text-neutral-700 leading-relaxed">
  Your organization demonstrates strong compliance practices...
</p>

// Secondary text
<p className="text-sm text-neutral-600">Supporting information</p>

// Muted text (metadata, placeholders)
<span className="text-sm text-neutral-500">Last updated 2 hours ago</span>
```

### Text Colors (Teal Theme)

```tsx
// Primary text
<p className="text-neutral-900">Main content text</p>

// Secondary text
<p className="text-neutral-700">Body content</p>

// Muted text
<span className="text-neutral-500">Helper text, metadata</span>

// Brand accent text
<span className="text-teal-600">Brand highlights</span>

// Success text
<span className="text-emerald-600">Success messages</span>

// Error text
<span className="text-red-600">Error messages</span>
```

## Interactive States (Updated)

### Hover States

```tsx
// Cards
<Card className="hover:shadow-md hover:shadow-neutral-200 transition-all duration-200">

// Interactive elements
<div className="hover:bg-neutral-50 hover:scale-[1.02] transition-all duration-200">

// Links
<a className="text-teal-600 hover:text-teal-700 hover:underline">
```

### Focus States (Teal Theme)

```tsx
// Input focus
<Input className="focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20" />

// Button focus (built into variants)
<Button variant="primary"> // Automatic teal focus ring

// Custom focusable elements
<div
  tabIndex={0}
  className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-600 focus-visible:ring-offset-2"
>
```

### Loading States

```tsx
// Button loading with teal spinner
<Button loading disabled variant="primary">
  {loading ? 'Saving...' : 'Save Changes'}
</Button>;

// Skeleton loading (neutral colors)
import { Skeleton } from '@/components/ui/skeleton';

{
  isLoading ? <Skeleton className="h-[200px] w-full bg-neutral-200" /> : <div>{content}</div>;
}
```

## Alert and Status Components

### Alert Variants (Updated Colors)

```tsx
import { Alert, AlertDescription } from "@/components/ui/alert"

// Success alert (Emerald)
<Alert variant="success" className="border-emerald-200 bg-emerald-50">
  <CheckCircle className="h-4 w-4 text-emerald-600" />
  <AlertDescription className="text-emerald-700">
    Assessment saved successfully.
  </AlertDescription>
</Alert>

// Warning alert (Amber)
<Alert variant="warning" className="border-amber-200 bg-amber-50">
  <AlertTriangle className="h-4 w-4 text-amber-600" />
  <AlertDescription className="text-amber-700">
    Some requirements need attention.
  </AlertDescription>
</Alert>

// Error alert (Red)
<Alert variant="destructive" className="border-red-200 bg-red-50">
  <AlertCircle className="h-4 w-4 text-red-600" />
  <AlertDescription className="text-red-700">
    Unable to save assessment.
  </AlertDescription>
</Alert>

// Info alert (Teal)
<Alert variant="info" className="border-teal-200 bg-teal-50">
  <Info className="h-4 w-4 text-teal-600" />
  <AlertDescription className="text-teal-700">
    New compliance updates available.
  </AlertDescription>
</Alert>
```

## Data Display Patterns

### Status Indicators

```tsx
// Compliance score card
<Card>
  <CardContent className="flex items-center justify-between p-6">
    <div>
      <p className="text-sm text-neutral-500">Compliance Score</p>
      <p className="text-3xl font-bold text-neutral-900">94%</p>
      <p className="text-sm text-emerald-600">↗ +2% from last month</p>
    </div>
    <div className="rounded-full bg-teal-50 p-3">
      <Shield className="h-6 w-6 text-teal-600" />
    </div>
  </CardContent>
</Card>

// Progress indicators
<div className="space-y-2">
  <div className="flex justify-between text-sm">
    <span className="text-neutral-700">GDPR Compliance</span>
    <span className="text-neutral-900 font-medium">78%</span>
  </div>
  <Progress value={78} className="h-2 bg-neutral-200">
    <div className="h-full bg-teal-600 rounded-full transition-all" />
  </Progress>
</div>
```

## Migration-Specific Patterns

### Feature Flag Usage

```tsx
// Check if new theme is enabled
import { useFeatureFlag } from '@/lib/feature-flags';

export function ThemedComponent() {
  const useNewTheme = useFeatureFlag('USE_NEW_THEME');

  return (
    <div className={useNewTheme ? 'border-neutral-200 bg-white' : 'border-navy-light bg-navy'}>
      {/* Component content */}
    </div>
  );
}
```

### Conditional Styling During Migration

```tsx
// Support both old and new themes during transition
<Button
  className={cn(
    'transition-all duration-200',
    useNewTheme
      ? ['bg-teal-600 text-white', 'hover:bg-teal-700', 'focus:ring-teal-600']
      : ['bg-navy text-white', 'hover:bg-navy-dark', 'focus:ring-navy'],
  )}
>
  Action Button
</Button>
```

This updated pattern library ensures consistent implementation of the new teal design system while supporting the ongoing migration process.
