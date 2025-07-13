# Component Transformation Guide - New ruleIQ Design System

## 🔄 Component-by-Component Transformation

This guide provides specific before/after examples for transforming each component to match the new clean, professional aesthetic.

## Button Components

### Before (Dark Theme)
```tsx
// Old primary button
<Button className="bg-brand-primary hover:bg-brand-dark text-white">
  Save Changes
</Button>
```

### After (New Design)
```tsx
// New primary button
<Button className="bg-[#2C7A7B] hover:bg-[#285E61] text-white px-6 py-3 rounded-lg font-medium shadow-sm hover:shadow-md transition-all duration-200">
  Save Changes
</Button>

// Button variants
const buttonVariants = {
  primary: "bg-[#2C7A7B] hover:bg-[#285E61] text-white shadow-sm hover:shadow-md",
  secondary: "bg-white hover:bg-gray-50 text-[#2C7A7B] border-2 border-[#2C7A7B]",
  ghost: "text-[#2C7A7B] hover:text-[#285E61] hover:bg-[#E6FFFA]",
  destructive: "bg-red-500 hover:bg-red-600 text-white shadow-sm hover:shadow-md",
}
```

## Card Components

### Before (Dark Theme)
```tsx
<Card className="bg-surface-primary border border-neutral-800">
  <CardHeader>
    <CardTitle className="text-text-primary">Dashboard</CardTitle>
  </CardHeader>
  <CardContent>
    {/* Dark content */}
  </CardContent>
</Card>
```

### After (New Design)
```tsx
<Card className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border-0">
  <CardHeader className="p-6 pb-4">
    <div className="w-12 h-12 bg-[#E6FFFA] rounded-lg flex items-center justify-center mb-4">
      <Shield className="w-6 h-6 text-[#2C7A7B]" />
    </div>
    <CardTitle className="text-xl font-semibold text-gray-900">
      Compliance Dashboard
    </CardTitle>
    <CardDescription className="text-gray-500 mt-1">
      All systems operational
    </CardDescription>
  </CardHeader>
  <CardContent className="px-6 pb-6">
    <div className="space-y-4">
      {/* Clean, spacious content */}
    </div>
  </CardContent>
</Card>
```

## Form Components

### Input Fields

#### Before
```tsx
<Input 
  className="bg-surface-secondary border-neutral-700 text-text-primary" 
  placeholder="Enter email"
/>
```

#### After
```tsx
<div className="space-y-2">
  <Label className="text-sm font-medium text-gray-700">
    Email Address
  </Label>
  <Input 
    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg 
               focus:border-[#2C7A7B] focus:ring-2 focus:ring-[#2C7A7B]/20 
               placeholder:text-gray-400 transition-all duration-200"
    placeholder="you@company.com"
  />
  <p className="text-sm text-gray-500">
    We'll use this for important notifications
  </p>
</div>
```

### Select Components

#### Before
```tsx
<Select>
  <SelectTrigger className="bg-surface-secondary border-neutral-700">
    <SelectValue />
  </SelectTrigger>
  <SelectContent className="bg-surface-primary">
    {/* Options */}
  </SelectContent>
</Select>
```

#### After
```tsx
<Select>
  <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-200 
                           rounded-lg hover:border-gray-300 focus:border-[#2C7A7B] 
                           focus:ring-2 focus:ring-[#2C7A7B]/20">
    <SelectValue placeholder="Select framework" />
  </SelectTrigger>
  <SelectContent className="bg-white border border-gray-200 shadow-lg rounded-lg">
    <SelectItem value="gdpr" className="hover:bg-gray-50">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 bg-[#2C7A7B] rounded-full" />
        GDPR
      </div>
    </SelectItem>
    <SelectItem value="iso27001" className="hover:bg-gray-50">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 bg-[#2C7A7B] rounded-full" />
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
<nav className="bg-surface-primary border-r border-neutral-800">
  <Link className="text-text-secondary hover:text-text-primary">
    Dashboard
  </Link>
</nav>
```

#### After
```tsx
<aside className="w-64 bg-white shadow-sm min-h-screen">
  <div className="p-6 border-b border-gray-100">
    <img src="/logo.svg" alt="ruleIQ" className="h-8" />
  </div>
  
  <nav className="p-4 space-y-1">
    <Link 
      href="/dashboard"
      className="flex items-center gap-3 px-4 py-3 rounded-lg 
                 hover:bg-[#E6FFFA] text-gray-700 hover:text-[#2C7A7B] 
                 transition-colors group"
    >
      <Home className="w-5 h-5 text-gray-400 group-hover:text-[#2C7A7B]" />
      <span className="font-medium">Dashboard</span>
    </Link>
    
    <Link 
      href="/assessments"
      className="flex items-center gap-3 px-4 py-3 rounded-lg 
                 bg-[#E6FFFA] text-[#2C7A7B]"
    >
      <FileCheck className="w-5 h-5" />
      <span className="font-medium">Assessments</span>
      <Badge className="ml-auto bg-[#2C7A7B] text-white text-xs px-2 py-0.5 rounded-full">
        3
      </Badge>
    </Link>
  </nav>
</aside>
```

## Data Display Components

### Stats Cards

#### Before
```tsx
<div className="bg-surface-primary p-6 rounded-lg border border-neutral-800">
  <p className="text-text-secondary">Total Users</p>
  <p className="text-3xl text-text-primary">1,234</p>
</div>
```

#### After
```tsx
<div className="bg-white p-6 rounded-xl shadow-sm">
  <div className="flex items-center justify-between">
    <div>
      <p className="text-sm font-medium text-gray-500">
        Compliance Score
      </p>
      <p className="text-3xl font-bold text-gray-900 mt-1">
        94%
      </p>
      <p className="text-sm text-green-600 mt-2 flex items-center gap-1">
        <TrendingUp className="w-4 h-4" />
        +12% from last month
      </p>
    </div>
    <div className="w-16 h-16 bg-[#E6FFFA] rounded-full flex items-center justify-center">
      <Shield className="w-8 h-8 text-[#2C7A7B]" />
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
    <span className="text-sm font-medium text-gray-700">
      GDPR Compliance
    </span>
    <span className="text-sm font-semibold text-[#2C7A7B]">
      75%
    </span>
  </div>
  <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
    <div 
      className="h-full bg-gradient-to-r from-[#2C7A7B] to-[#38A169] 
                 rounded-full transition-all duration-500 ease-out"
      style={{ width: '75%' }}
    />
  </div>
  <p className="text-xs text-gray-500">
    3 of 4 requirements completed
  </p>
</div>
```

## Alert & Notification Components

### Alert Messages

#### Before
```tsx
<Alert className="bg-surface-secondary border-success">
  <AlertDescription className="text-text-primary">
    Assessment completed
  </AlertDescription>
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
  <DialogContent className="bg-surface-primary border-neutral-800">
    <DialogHeader>
      <DialogTitle className="text-text-primary">Delete Item</DialogTitle>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

### After
```tsx
<Dialog>
  <DialogContent className="bg-white rounded-xl shadow-xl border-0 p-0 max-w-md">
    <DialogHeader className="p-6 pb-0">
      <div className="w-12 h-12 bg-red-100 rounded-full flex items-center 
                      justify-center mb-4">
        <AlertTriangle className="w-6 h-6 text-red-600" />
      </div>
      <DialogTitle className="text-xl font-semibold text-gray-900">
        Delete Assessment?
      </DialogTitle>
      <DialogDescription className="text-gray-500 mt-2">
        This action cannot be undone. This will permanently delete your 
        assessment and remove all associated data.
      </DialogDescription>
    </DialogHeader>
    
    <DialogFooter className="p-6 pt-4 bg-gray-50 rounded-b-xl">
      <Button 
        variant="ghost" 
        className="text-gray-700 hover:bg-gray-100"
      >
        Cancel
      </Button>
      <Button 
        className="bg-red-500 hover:bg-red-600 text-white"
      >
        Delete Assessment
      </Button>
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
<div className="bg-white rounded-xl shadow-sm overflow-hidden">
  <Table>
    <TableHeader>
      <TableRow className="bg-gray-50 border-b border-gray-200">
        <TableHead className="text-xs font-semibold text-gray-600 uppercase tracking-wider px-6 py-3">
          Framework
        </TableHead>
        <TableHead className="text-xs font-semibold text-gray-600 uppercase tracking-wider px-6 py-3">
          Status
        </TableHead>
        <TableHead className="text-xs font-semibold text-gray-600 uppercase tracking-wider px-6 py-3">
          Progress
        </TableHead>
        <TableHead className="text-xs font-semibold text-gray-600 uppercase tracking-wider px-6 py-3 text-right">
          Actions
        </TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
        <TableCell className="px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#E6FFFA] rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-[#2C7A7B]" />
            </div>
            <div>
              <p className="font-medium text-gray-900">GDPR</p>
              <p className="text-sm text-gray-500">Last updated 2 days ago</p>
            </div>
          </div>
        </TableCell>
        <TableCell className="px-6 py-4">
          <Badge className="bg-green-100 text-green-700 border-0">
            Active
          </Badge>
        </TableCell>
        <TableCell className="px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-[#2C7A7B] rounded-full" style={{ width: '75%' }} />
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
  <div className="relative w-10 h-10">
    <div className="absolute inset-0 border-3 border-gray-200 rounded-full" />
    <div className="absolute inset-0 border-3 border-[#2C7A7B] border-t-transparent rounded-full animate-spin" />
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
<div className="flex flex-col items-center justify-center py-12 px-4">
  <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-6">
    <FileX className="w-10 h-10 text-gray-400" />
  </div>
  <h3 className="text-lg font-semibold text-gray-900 mb-2">
    No assessments yet
  </h3>
  <p className="text-gray-500 text-center max-w-sm mb-6">
    Start your compliance journey by creating your first assessment.
  </p>
  <Button className="bg-[#2C7A7B] hover:bg-[#285E61] text-white">
    <Plus className="w-4 h-4 mr-2" />
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