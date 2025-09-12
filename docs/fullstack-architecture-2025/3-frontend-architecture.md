# 3. FRONTEND ARCHITECTURE

## 3.1 Component Structure

```typescript
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth pages (public)
│   │   ├── login/
│   │   ├── register/
│   │   ├── reset-password/
│   │   └── onboarding/
│   ├── (dashboard)/              # Protected pages
│   │   ├── layout.tsx           # Auth wrapper
│   │   ├── page.tsx             # Dashboard
│   │   ├── policies/
│   │   ├── assessments/
│   │   ├── evidence/
│   │   ├── risks/
│   │   ├── profile/             # User management
│   │   └── settings/
│   └── api/                      # API routes
├── components/
│   ├── ui/                       # shadcn/ui components
│   ├── features/                 # Feature components
│   │   ├── auth/
│   │   ├── policies/
│   │   ├── assessments/
│   │   └── evidence/
│   ├── layouts/
│   └── shared/
├── lib/
│   ├── api/                      # API client services
│   ├── auth/                     # Auth utilities
│   ├── hooks/                    # Custom React hooks
│   ├── stores/                   # Zustand stores
│   └── utils/
└── types/
```

## 3.2 State Management

```typescript
// stores/auth.store.ts
interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginDto) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

// stores/compliance.store.ts
interface ComplianceStore {
  policies: Policy[];
  assessments: Assessment[];
  currentFramework: Framework | null;
  complianceScore: number;
  fetchDashboardData: () => Promise<void>;
}
```

## 3.3 Performance Optimizations

```typescript
// Dynamic imports for code splitting
const PolicyEditor = dynamic(() => import('@/components/features/policies/PolicyEditor'), {
  loading: () => <PolicyEditorSkeleton />,
  ssr: false,
});

// Image optimization
const OptimizedImage = ({ src, alt, ...props }) => (
  <Image
    src={src}
    alt={alt}
    placeholder="blur"
    blurDataURL={generateBlurDataURL(src)}
    loading="lazy"
    {...props}
  />
);

// Virtual scrolling for large lists
const VirtualPolicyList = ({ policies }) => (
  <VirtualList
    height={600}
    itemCount={policies.length}
    itemSize={120}
    width="100%"
  >
    {({ index, style }) => (
      <div style={style}>
        <PolicyCard policy={policies[index]} />
      </div>
    )}
  </VirtualList>
);
```

## 3.4 Accessibility Compliance

```yaml
WCAG 2.1 AA Requirements:
  Color Contrast:
    Text: 4.5:1 minimum
    Large Text: 3:1 minimum
    Interactive: 3:1 minimum
    Fix: Update teal-300 to #14B8A6

  Keyboard Navigation:
    Skip Links: Add to layout
    Focus Trap: Modal implementation
    Tab Order: Logical flow
    Shortcuts: Document all

  ARIA Implementation:
    Landmarks: Proper regions
    Labels: All interactive elements
    Live Regions: Status updates
    Descriptions: Complex interactions

  Screen Reader:
    Alt Text: All images
    Headings: Proper hierarchy
    Tables: Headers and captions
    Forms: Associated labels
```

---
