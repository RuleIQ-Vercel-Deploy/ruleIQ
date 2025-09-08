# Component Transformation Guide - New ruleIQ Design System

## 🔄 Component-by-Component Transformation

This guide provides specific before/after examples for transforming each component to match the new clean, professional aesthetic.

## Button Components

### Before (Dark Theme)

```tsx
// Old primary button
<Button className="bg-brand-primary text-white hover:bg-brand-dark">Save Changes</Button>
```

### After (New Design)

```tsx
// New primary button
<Button className="rounded-lg bg-[#2C7A7B] px-6 py-3 font-medium text-white shadow-sm transition-all duration-200 hover:bg-[#285E61] hover:shadow-md">
  Save Changes
</Button>;

// Button variants
const buttonVariants = {
  primary: 'bg-[#2C7A7B] hover:bg-[#285E61] text-white shadow-sm hover:shadow-md',
  secondary: 'bg-white hover:bg-gray-50 text-[#2C7A7B] border-2 border-[#2C7A7B]',
  ghost: 'text-[#2C7A7B] hover:text-[#285E61] hover:bg-[#E6FFFA]',
  destructive: 'bg-red-500 hover:bg-red-600 text-white shadow-sm hover:shadow-md',
};
```

## Card Components

### Before (Dark Theme)

```tsx
<Card className="border border-neutral-800 bg-surface-primary">
  <CardHeader>
    <CardTitle className="text-text-primary">Dashboard</CardTitle>
  </CardHeader>
  <CardContent>{/* Dark content */}</CardContent>
</Card>
```

### After (New Design)

```tsx
<Card className="rounded-xl border-0 bg-white shadow-sm transition-shadow duration-200 hover:shadow-md">
  <CardHeader className="p-6 pb-4">
    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-[#E6FFFA]">
      <Shield className="h-6 w-6 text-[#2C7A7B]" />
    </div>
    <CardTitle className="text-xl font-semibold text-gray-900">Compliance Dashboard</CardTitle>
    <CardDescription className="mt-1 text-gray-500">All systems operational</CardDescription>
  </CardHeader>
  <CardContent className="px-6 pb-6">
    <div className="space-y-4">{/* Clean, spacious content */}</div>
  </CardContent>
</Card>
```

## Form Components

### Input Fields

#### Before

```tsx
<Input
  className="border-neutral-700 bg-surface-secondary text-text-primary"
  placeholder="Enter email"
/>
```

#### After

```tsx
<div className="space-y-2">
  <Label className="text-sm font-medium text-gray-700">Email Address</Label>
  <Input
    className="w-full rounded-lg border border-gray-200 bg-white px-4 py-3 transition-all duration-200 placeholder:text-gray-400 focus:border-[#2C7A7B] focus:ring-2 focus:ring-[#2C7A7B]/20"
    placeholder="you@company.com"
  />
  <p className="text-sm text-gray-500">We'll use this for important notifications</p>
</div>
```

### Select Components

#### Before

```tsx
<Select>
  <SelectTrigger className="border-neutral-700 bg-surface-secondary">
    <SelectValue />
  </SelectTrigger>
  <SelectContent className="bg-surface-primary">{/* Options */}</SelectContent>
</Select>
```

#### After

```tsx
<Select>
  <SelectTrigger className="w-full rounded-lg border border-gray-200 bg-white px-4 py-3 hover:border-gray-300 focus:border-[#2C7A7B] focus:ring-2 focus:ring-[#2C7A7B]/20">
    <SelectValue placeholder="Select framework" />
  </SelectTrigger>
  <SelectContent className="rounded-lg border border-gray-200 bg-white shadow-lg">
    <SelectItem value="gdpr" className="hover:bg-gray-50">
      <div className="flex items-center gap-3">
        <div className="h-2 w-2 rounded-full bg-[#2C7A7B]" />
        GDPR
      </div>
    </SelectItem>
    <SelectItem value="iso27001" className="hover:bg-gray-50">
      <div className="flex items-center gap-3">
        <div className="h-2 w-2 rounded-full bg-[#2C7A7B]" />
        ISO 27001
      </div>
    </SelectItem>
  </SelectContent>
</Select>
```

## Navigation Components

### Sidebar Navigation

#### Before

```tsx
<nav className="border-r border-neutral-800 bg-surface-primary">
  <Link className="text-text-secondary hover:text-text-primary">Dashboard</Link>
</nav>
```

#### After

```tsx
<aside className="min-h-screen w-64 bg-white shadow-sm">
  <div className="border-b border-gray-100 p-6">
    <img src="/logo.svg" alt="ruleIQ" className="h-8" />
  </div>

  <nav className="space-y-1 p-4">
    <Link
      href="/dashboard"
      className="group flex items-center gap-3 rounded-lg px-4 py-3 text-gray-700 transition-colors hover:bg-[#E6FFFA] hover:text-[#2C7A7B]"
    >
      <Home className="h-5 w-5 text-gray-400 group-hover:text-[#2C7A7B]" />
      <span className="font-medium">Dashboard</span>
    </Link>

    <Link
      href="/assessments"
      className="flex items-center gap-3 rounded-lg bg-[#E6FFFA] px-4 py-3 text-[#2C7A7B]"
    >
      <FileCheck className="h-5 w-5" />
      <span className="font-medium">Assessments</span>
      <Badge className="ml-auto rounded-full bg-[#2C7A7B] px-2 py-0.5 text-xs text-white">3</Badge>
    </Link>
  </nav>
</aside>
```

## Data Display Components

### Stats Cards

#### Before

```tsx
<div className="rounded-lg border border-neutral-800 bg-surface-primary p-6">
  <p className="text-text-secondary">Total Users</p>
  <p className="text-3xl text-text-primary">1,234</p>
</div>
```

#### After

```tsx
<div className="rounded-xl bg-white p-6 shadow-sm">
  <div className="flex items-center justify-between">
    <div>
      <p className="text-sm font-medium text-gray-500">Compliance Score</p>
      <p className="mt-1 text-3xl font-bold text-gray-900">94%</p>
      <p className="mt-2 flex items-center gap-1 text-sm text-green-600">
        <TrendingUp className="h-4 w-4" />
        +12% from last month
      </p>
    </div>
    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#E6FFFA]">
      <Shield className="h-8 w-8 text-[#2C7A7B]" />
    </div>
  </div>
</div>
```

### Progress Indicators

#### Before

```tsx
<Progress value={75} className="bg-neutral-800 [&>div]:bg-brand-primary" />
```

#### After

```tsx
<div className="space-y-3">
  <div className="flex items-center justify-between">
    <span className="text-sm font-medium text-gray-700">GDPR Compliance</span>
    <span className="text-sm font-semibold text-[#2C7A7B]">75%</span>
  </div>
  <div className="h-2.5 overflow-hidden rounded-full bg-gray-100">
    <div
      className="h-full rounded-full bg-gradient-to-r from-[#2C7A7B] to-[#38A169] transition-all duration-500 ease-out"
      style={{ width: '75%' }}
    />
  </div>
  <p className="text-xs text-gray-500">3 of 4 requirements completed</p>
</div>
```

## Alert & Notification Components

### Alert Messages

#### Before

```tsx
<Alert className="border-success bg-surface-secondary">
  <AlertDescription className="text-text-primary">Assessment completed</AlertDescription>
</Alert>
```

#### After

```tsx
// Success Alert
<Alert className="bg-green-50 border border-green-200 rounded-lg">
  <CheckCircle className="w-5 h-5 text-green-600" />
  <AlertDescription className="text-green-800 ml-3">
    <strong>Success!</strong> Your assessment has been saved and compliance score updated.
  </AlertDescription>
</Alert>

// Info Alert
<Alert className="bg-blue-50 border border-blue-200 rounded-lg">
  <Info className="w-5 h-5 text-blue-600" />
  <AlertDescription className="text-blue-800 ml-3">
    <strong>Tip:</strong> Complete your profile to unlock advanced features.
  </AlertDescription>
</Alert>

// Warning Alert
<Alert className="bg-amber-50 border border-amber-200 rounded-lg">
  <AlertTriangle className="w-5 h-5 text-amber-600" />
  <AlertDescription className="text-amber-800 ml-3">
    <strong>Action required:</strong> Your ISO 27001 certification expires in 30 days.
  </AlertDescription>
</Alert>
```

## Modal & Dialog Components

### Before

```tsx
<Dialog>
  <DialogContent className="border-neutral-800 bg-surface-primary">
    <DialogHeader>
      <DialogTitle className="text-text-primary">Delete Item</DialogTitle>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

### After

```tsx
<Dialog>
  <DialogContent className="max-w-md rounded-xl border-0 bg-white p-0 shadow-xl">
    <DialogHeader className="p-6 pb-0">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
        <AlertTriangle className="h-6 w-6 text-red-600" />
      </div>
      <DialogTitle className="text-xl font-semibold text-gray-900">Delete Assessment?</DialogTitle>
      <DialogDescription className="mt-2 text-gray-500">
        This action cannot be undone. This will permanently delete your assessment and remove all
        associated data.
      </DialogDescription>
    </DialogHeader>

    <DialogFooter className="rounded-b-xl bg-gray-50 p-6 pt-4">
      <Button variant="ghost" className="text-gray-700 hover:bg-gray-100">
        Cancel
      </Button>
      <Button className="bg-red-500 text-white hover:bg-red-600">Delete Assessment</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

## Table Components

### Before

```tsx
<Table>
  <TableHeader className="bg-surface-secondary">
    <TableRow className="border-neutral-800">
      <TableHead className="text-text-secondary">Name</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow className="border-neutral-800">
      <TableCell className="text-text-primary">Item</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### After

```tsx
<div className="overflow-hidden rounded-xl bg-white shadow-sm">
  <Table>
    <TableHeader>
      <TableRow className="border-b border-gray-200 bg-gray-50">
        <TableHead className="px-6 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
          Framework
        </TableHead>
        <TableHead className="px-6 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
          Status
        </TableHead>
        <TableHead className="px-6 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
          Progress
        </TableHead>
        <TableHead className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-600">
          Actions
        </TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow className="border-b border-gray-100 transition-colors hover:bg-gray-50">
        <TableCell className="px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#E6FFFA]">
              <Shield className="h-5 w-5 text-[#2C7A7B]" />
            </div>
            <div>
              <p className="font-medium text-gray-900">GDPR</p>
              <p className="text-sm text-gray-500">Last updated 2 days ago</p>
            </div>
          </div>
        </TableCell>
        <TableCell className="px-6 py-4">
          <Badge className="border-0 bg-green-100 text-green-700">Active</Badge>
        </TableCell>
        <TableCell className="px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-gray-200">
              <div className="h-full rounded-full bg-[#2C7A7B]" style={{ width: '75%' }} />
            </div>
            <span className="text-sm font-medium text-gray-600">75%</span>
          </div>
        </TableCell>
        <TableCell className="px-6 py-4 text-right">
          <Button variant="ghost" size="sm" className="text-[#2C7A7B] hover:text-[#285E61]">
            View Details
          </Button>
        </TableCell>
      </TableRow>
    </TableBody>
  </Table>
</div>
```

## Loading States

### Skeleton Loaders

```tsx
// Card skeleton
<div className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
  <div className="w-12 h-12 bg-gray-200 rounded-lg mb-4" />
  <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
  <div className="h-4 bg-gray-200 rounded w-1/2" />
</div>

// Table row skeleton
<TableRow className="animate-pulse">
  <TableCell className="px-6 py-4">
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 bg-gray-200 rounded-lg" />
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded w-24" />
        <div className="h-3 bg-gray-200 rounded w-32" />
      </div>
    </div>
  </TableCell>
  <TableCell className="px-6 py-4">
    <div className="h-6 bg-gray-200 rounded-full w-16" />
  </TableCell>
</TableRow>
```

### Spinner

```tsx
// Clean spinner component
<div className="flex items-center justify-center p-8">
  <div className="relative h-10 w-10">
    <div className="border-3 absolute inset-0 rounded-full border-gray-200" />
    <div className="border-3 absolute inset-0 animate-spin rounded-full border-[#2C7A7B] border-t-transparent" />
  </div>
</div>
```

## Empty States

### Before

```tsx
<div className="text-center text-text-secondary">
  <p>No data available</p>
</div>
```

### After

```tsx
<div className="flex flex-col items-center justify-center px-4 py-12">
  <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-gray-100">
    <FileX className="h-10 w-10 text-gray-400" />
  </div>
  <h3 className="mb-2 text-lg font-semibold text-gray-900">No assessments yet</h3>
  <p className="mb-6 max-w-sm text-center text-gray-500">
    Start your compliance journey by creating your first assessment.
  </p>
  <Button className="bg-[#2C7A7B] text-white hover:bg-[#285E61]">
    <Plus className="mr-2 h-4 w-4" />
    Create Assessment
  </Button>
</div>
```

## Implementation Tips

### 1. Color Usage

- Use teal (`#2C7A7B`) as primary action color
- Use white backgrounds with subtle gray (`#F7FAFC`) for page backgrounds
- Use shadows instead of borders for elevation
- Maintain high contrast for accessibility

### 2. Spacing

- Use consistent padding: 24px (p-6) for cards, 16px (p-4) for compact areas
- Maintain 8px grid system
- Add generous whitespace between sections

### 3. Typography

- Use Inter font family
- Clear hierarchy with size and weight
- Gray-900 for primary text, gray-500 for secondary

### 4. Interactions

- Subtle hover effects (shadow increase, slight color change)
- Smooth transitions (200ms duration)
- Clear focus states with teal ring

### 5. Icons

- Use rounded backgrounds for feature icons
- Consistent 2px stroke width
- Teal color for brand consistency

This transformation guide ensures all components align with the new clean, professional aesthetic while maintaining usability and accessibility standards.
