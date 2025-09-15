# API Integration Implementation Guide - Dark Mode RuleIQ

## Overview
This document describes the API integration pattern used for the new Dark Mode (Purple/Silver theme) pages in the RuleIQ frontend application.

## Implementation Strategy

### 1. REUSE EXISTING INFRASTRUCTURE
- **Principle**: Do NOT create new API connections from scratch
- **Action**: Leverage existing API services and stores from the TEAL implementation
- **Location**: `/lib/api/` and `/lib/stores/`

### 2. AUTHENTICATION STATE MANAGEMENT

#### Store Location
```typescript
// File: /lib/stores/auth.store.ts
import { useAuthStore } from '@/lib/stores/auth.store';
```

#### Usage Pattern
```typescript
const { isAuthenticated } = useAuthStore();

// Dynamic routing based on auth state
href={isAuthenticated ? "/dashboard" : "/auth/sign-up"}
```

### 3. API CLIENT CONFIGURATION

#### Base Configuration
```typescript
// File: /lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Automatic token management
private async getAuthHeaders(): Promise<HeadersInit> {
  const { tokens, refreshTokens } = useAuthStore.getState();
  // Auto-refresh logic included
}
```

### 4. PAGE-SPECIFIC IMPLEMENTATIONS

#### A. Marketing/Hero Page (`/app/page.tsx`)

##### Imports Required
```typescript
import { useAuthStore } from '@/lib/stores/auth.store';
import { useRouter } from 'next/navigation';
```

##### Dynamic CTAs
```typescript
// Hero Section CTAs
ctaButtons={[
  { 
    text: "Start Free Trial", 
    href: isAuthenticated ? "/dashboard" : "/auth/sign-up",
    primary: true 
  },
  { 
    text: "View Demo", 
    href: "#demo" 
  }
]}
```

##### Pricing Integration
```typescript
// Pricing tiers with plan parameters
const pricingPlans = [
  {
    name: "Starter",
    cta: {
      href: "/auth/sign-up?plan=starter"
    }
  },
  {
    name: "Professional",
    cta: {
      href: "/auth/sign-up?plan=professional"
    }
  },
  {
    name: "Enterprise",
    cta: {
      href: "/contact-sales"
    }
  }
];
```

#### B. Header Component (`/components/ui/header.tsx`)

##### Authentication-Based Navigation
```typescript
{isAuthenticated ? (
  <Link href="/dashboard">
    <Button variant="ghost">Dashboard</Button>
  </Link>
) : (
  <>
    <Link href="/auth/sign-in">
      <Button variant="ghost">Sign In</Button>
    </Link>
    <Link href="/auth/sign-up">
      <Button>Get Started</Button>
    </Link>
  </>
)}
```

### 5. ROUTING PATTERNS

#### Static Routes
```yaml
sign_in: /auth/sign-in
sign_up: /auth/sign-up
dashboard: /dashboard
privacy: /privacy
terms: /terms
contact: /contact
contact_sales: /contact-sales
```

#### Dynamic Routes with Parameters
```yaml
sign_up_with_plan: /auth/sign-up?plan={plan_name}
```

#### Programmatic Navigation
```typescript
const router = useRouter();
onClick={() => router.push('/contact')}
```

### 6. ENVIRONMENT CONFIGURATION

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_ENABLE_MOCK_DATA=false
```

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ruleiq
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

### 7. MOCK DATA PATTERN (FOR DEVELOPMENT)

#### Service Structure
```typescript
// File: /lib/api/{service}.service.ts
const useMockData = process.env.NEXT_PUBLIC_ENABLE_MOCK_DATA === 'true';

export const serviceAPI = {
  getData: async () => {
    if (useMockData) {
      return mockData;
    }
    return apiClient.get('/endpoint');
  }
};
```

### 8. COMPONENT HIERARCHY

```
app/
├── page.tsx (HomePage)
│   ├── Header (from /components/ui/header.tsx)
│   │   └── useAuthStore() → Dynamic nav
│   ├── Hero (from /components/ui/neural-network-hero.tsx)
│   │   └── Static content only
│   ├── PricingPreview (from /components/ui/pricing-preview.tsx)
│   │   └── Static plans with dynamic links
│   └── Footer
│       └── Static links
```

### 9. STATE FLOW

```mermaid
graph LR
    A[User Lands] --> B{Check Auth}
    B -->|Authenticated| C[Show Dashboard Links]
    B -->|Not Authenticated| D[Show Sign Up/In Links]
    C --> E[CTA → /dashboard]
    D --> F[CTA → /auth/sign-up]
```

### 10. IMPLEMENTATION CHECKLIST

- [x] Import existing auth store
- [x] Check authentication state in components
- [x] Apply conditional routing to CTAs
- [x] Add plan parameters to pricing links
- [x] Connect navigation links in header
- [x] Wire up footer links
- [x] Setup router for programmatic navigation
- [x] Maintain consistent href patterns

### 11. TESTING VERIFICATION

#### Manual Testing Steps
1. Load page while logged out → CTAs should show `/auth/sign-up`
2. Load page while logged in → CTAs should show `/dashboard`
3. Click pricing plans → Should navigate to `/auth/sign-up?plan={name}`
4. Click header Sign In → Should navigate to `/auth/sign-in`
5. Click footer links → Should navigate to respective pages

### 12. COMMON PATTERNS TO FOLLOW

#### Pattern 1: Conditional Rendering
```typescript
{isAuthenticated ? <AuthenticatedComponent /> : <PublicComponent />}
```

#### Pattern 2: Dynamic Href
```typescript
href={isAuthenticated ? "/protected-route" : "/public-route"}
```

#### Pattern 3: Protected Route Check
```typescript
useEffect(() => {
  if (!isAuthenticated) {
    router.push('/auth/sign-in');
  }
}, [isAuthenticated]);
```

### 13. FILES MODIFIED FOR DARK MODE

```yaml
modified_files:
  - /app/page.tsx
  - /components/ui/header.tsx
  - /components/ui/pricing-preview.tsx
  - /components/ui/neural-network-hero.tsx

unchanged_api_files:
  - /lib/stores/auth.store.ts
  - /lib/api/client.ts
  - /lib/api/*.service.ts
```

### 14. NO BACKEND REQUIRED FOR

- Static marketing content
- Pricing display
- Navigation between pages
- Theme/styling

### 15. BACKEND REQUIRED FOR

- Authentication (sign in/up)
- Dashboard data
- User-specific content
- API calls in service files

---

## IMPLEMENTATION RULE

**GOLDEN RULE**: When converting TEAL pages to Dark Mode, COPY the API connections exactly as they are. Do NOT reinvent the wheel. The API layer remains unchanged - only the UI theme changes.

## COMMANDS TO VERIFY

```bash
# Check if backend is running
curl http://localhost:8000/docs

# Check frontend auth store
grep -r "useAuthStore" frontend/app/
grep -r "useAuthStore" frontend/components/

# Find all API service files
ls -la frontend/lib/api/*.service.ts

# Check all href patterns
grep -r "href=" frontend/app/page.tsx
grep -r "router.push" frontend/app/page.tsx
```

---

**Generated**: 2025-01-13
**Theme**: Dark Mode (Purple/Silver)
**Framework**: Next.js 14+ with App Router
**State Management**: Zustand (auth.store.ts)
**API Client**: Custom fetch wrapper with JWT management