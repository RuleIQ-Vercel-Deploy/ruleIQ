# Design Patterns and Guidelines - Teal Design System

## Component Design Patterns

### Composition Pattern
Components are built using composition over inheritance:
```tsx
// Preferred: Composable components with NEW TEAL STYLING
<Card className="bg-white border-neutral-200">
  <CardHeader>
    <CardTitle className="text-neutral-900">Assessment Results</CardTitle>
  </CardHeader>
  <CardContent>
    <AssessmentMetrics data={results} />
  </CardContent>
</Card>
```

### Render Props Pattern
For flexible component behavior:
```tsx
<DataProvider>
  {({ data, loading, error }) => (
    loading ? <Skeleton className="bg-neutral-200" /> : <Content data={data} />
  )}
</DataProvider>
```

### Compound Components
Related components work together:
```tsx
<Assessment>
  <Assessment.Header />
  <Assessment.Questions />
  <Assessment.Progress className="bg-teal-600" />
  <Assessment.Actions />
</Assessment>
```

## NEW TEAL DESIGN SYSTEM PATTERNS

### Button Patterns (Updated)
```tsx
// Primary - Teal brand color
<Button variant="primary" className="bg-teal-600 hover:bg-teal-700">
  Save Changes
</Button>

// Secondary - Neutral styling
<Button variant="secondary" className="bg-neutral-100 text-neutral-900">
  Cancel
</Button>

// Accent - Bright teal highlight
<Button variant="accent" className="bg-teal-300 text-teal-900">
  Start Assessment
</Button>

// Destructive - Red for dangerous actions
<Button variant="destructive" className="bg-red-600 hover:bg-red-700">
  Delete
</Button>
```

### Card Patterns (Updated)
```tsx
// Standard card with new styling
<Card className="bg-white border-neutral-200 hover:shadow-md">
  <CardContent className="p-6">
    <h3 className="text-lg font-semibold text-neutral-900 mb-2">
      Compliance Score
    </h3>
    <p className="text-3xl font-bold text-teal-600">94%</p>
    <p className="text-sm text-neutral-600">Above industry average</p>
  </CardContent>
</Card>
```

### Form Patterns (Updated)
```tsx
// Form with teal focus states
<FormField
  control={form.control}
  name="email"
  render={({ field }) => (
    <FormItem>
      <FormLabel className="text-neutral-900">Email Address</FormLabel>
      <FormControl>
        <Input 
          placeholder="Enter email" 
          className="border-neutral-200 focus:border-teal-600 focus:ring-teal-600"
          {...field} 
        />
      </FormControl>
      <FormMessage className="text-red-600" />
    </FormItem>
  )}
/>
```

## State Management Patterns

### Server State (TanStack Query)
```tsx
// Consistent query patterns
const { data: assessments, isLoading, error } = useQuery({
  queryKey: ['assessments'],
  queryFn: fetchAssessments,
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

### Global State (Zustand)
```tsx
// Simple, focused stores
interface AuthStore {
  user: User | null;
  login: (credentials: LoginData) => Promise<void>;
  logout: () => void;
}

const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  login: async (credentials) => {
    const user = await authApi.login(credentials);
    set({ user });
  },
  logout: () => set({ user: null }),
}));
```

## Error Handling Patterns

### Alert Components (Updated Colors)
```tsx
// Success alert - Emerald
<Alert className="border-emerald-200 bg-emerald-50">
  <CheckCircle className="h-4 w-4 text-emerald-600" />
  <AlertDescription className="text-emerald-700">
    Assessment saved successfully.
  </AlertDescription>
</Alert>

// Error alert - Red  
<Alert variant="destructive" className="border-red-200 bg-red-50">
  <AlertCircle className="h-4 w-4 text-red-600" />
  <AlertDescription className="text-red-700">
    Unable to save assessment.
  </AlertDescription>
</Alert>

// Warning alert - Amber
<Alert className="border-amber-200 bg-amber-50">
  <AlertTriangle className="h-4 w-4 text-amber-600" />
  <AlertDescription className="text-amber-700">
    Some requirements need attention.
  </AlertDescription>
</Alert>

// Info alert - Teal
<Alert className="border-teal-200 bg-teal-50">
  <Info className="h-4 w-4 text-teal-600" />
  <AlertDescription className="text-teal-700">
    New compliance updates available.
  </AlertDescription>
</Alert>
```

## Loading State Patterns

### Skeleton Loading (Updated)
```tsx
// Consistent skeleton patterns with neutral colors
{isLoading ? (
  <div className="space-y-4">
    <Skeleton className="h-8 w-[250px] bg-neutral-200" />
    <Skeleton className="h-4 w-[200px] bg-neutral-200" />
  </div>
) : (
  <Content data={data} />
)}
```

### Button Loading States
```tsx
// Loading button with teal spinner
<Button loading disabled variant="primary">
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  {loading ? "Saving..." : "Save Changes"}
</Button>
```

## Navigation Patterns (Updated)

### Sidebar Navigation
```tsx
// Sidebar with new teal styling
<nav className="bg-white border-r border-neutral-200 p-4">
  <div className="space-y-2">
    <a className={cn(
      "flex items-center p-3 rounded-lg transition-colors",
      "text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900",
      "data-[active=true]:bg-teal-50 data-[active=true]:text-teal-700"
    )}>
      <DashboardIcon className="w-5 h-5 mr-3" />
      Dashboard
    </a>
  </div>
</nav>
```

### Top Navigation
```tsx
// Header with new styling
<header className="bg-white border-b border-neutral-200 px-6 py-4">
  <div className="flex items-center justify-between">
    <h1 className="text-xl font-semibold text-neutral-900">ruleIQ</h1>
    <div className="flex items-center space-x-4">
      <Button variant="ghost" size="icon" className="text-neutral-600">
        <Bell className="w-5 h-5" />
      </Button>
    </div>
  </div>
</header>
```

## Accessibility Patterns (Updated)

### Focus Management (Teal Focus)
```tsx
// Focus states with teal colors
<div 
  tabIndex={0}
  className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-600 focus-visible:ring-offset-2"
>
  Focusable content
</div>
```

### ARIA Patterns
```tsx
// Consistent ARIA usage
<button
  aria-expanded={isExpanded}
  aria-controls="content-id"
  className="text-teal-600 hover:text-teal-700"
  onClick={toggle}
>
  {isExpanded ? 'Collapse' : 'Expand'}
</button>
```

## Performance Patterns

### Memoization
```tsx
// Strategic memoization
const ExpensiveComponent = memo(({ data }: Props) => {
  const processedData = useMemo(
    () => expensiveCalculation(data),
    [data]
  );
  
  return <div className="bg-white border-neutral-200">{processedData}</div>;
});
```

### Code Splitting
```tsx
// Route-level code splitting
const AssessmentWizard = lazy(() => import('./AssessmentWizard'));

// Component-level splitting for large features
const AdvancedAnalytics = lazy(() => import('./AdvancedAnalytics'));
```

## API Integration Patterns

### Consistent API Client
```tsx
// Standardized API calls
export const assessmentApi = {
  list: () => api.get<Assessment[]>('/assessments'),
  get: (id: string) => api.get<Assessment>(`/assessments/${id}`),
  create: (data: CreateAssessmentData) => api.post<Assessment>('/assessments', data),
  update: (id: string, data: UpdateAssessmentData) => 
    api.patch<Assessment>(`/assessments/${id}`, data),
  delete: (id: string) => api.delete(`/assessments/${id}`),
};
```

## Security Patterns

### Input Sanitization
```tsx
// Consistent input validation
const sanitizedContent = DOMPurify.sanitize(userInput);
```

### CSRF Protection
```tsx
// CSRF token handling
const csrfToken = await fetch('/api/csrf-token').then(r => r.json());
```

## Testing Patterns

### Component Testing (Updated)
```tsx
// Test with new design system
describe('AssessmentCard', () => {
  it('displays assessment information correctly', () => {
    render(<AssessmentCard assessment={mockAssessment} />);
    expect(screen.getByText(mockAssessment.title)).toBeInTheDocument();
    
    // Test teal styling is applied
    const card = screen.getByRole('article');
    expect(card).toHaveClass('bg-white', 'border-neutral-200');
  });
  
  it('handles click events', async () => {
    const onSelect = vi.fn();
    render(<AssessmentCard assessment={mockAssessment} onSelect={onSelect} />);
    
    await user.click(screen.getByRole('button'));
    expect(onSelect).toHaveBeenCalledWith(mockAssessment.id);
  });
});
```

## Migration-Specific Patterns

### Feature Flag Usage
```tsx
// Use new theme conditionally during migration
import { useFeatureFlag } from "@/lib/feature-flags"

export function ThemedComponent() {
  const useNewTheme = useFeatureFlag('USE_NEW_THEME')
  
  return (
    <div className={useNewTheme ? 
      "bg-white border-neutral-200 text-neutral-900" : 
      "bg-navy border-navy-light text-white"
    }>
      {/* Component content */}
    </div>
  )
}
```

### Conditional Styling
```tsx
// Support both themes during transition
<Button 
  className={cn(
    "transition-all duration-200",
    useNewTheme ? [
      "bg-teal-600 text-white",
      "hover:bg-teal-700",
      "focus:ring-teal-600"
    ] : [
      "bg-navy text-white", 
      "hover:bg-navy-dark",
      "focus:ring-navy"
    ]
  )}
>
  Action Button
</Button>
```

This updated pattern library ensures consistent implementation of the new teal design system throughout the ruleIQ platform.