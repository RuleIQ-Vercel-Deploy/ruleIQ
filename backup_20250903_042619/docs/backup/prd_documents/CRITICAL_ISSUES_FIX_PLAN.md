# Critical Issues Fix Plan - ruleIQ Frontend

## Executive Summary

The testsprite automated testing revealed 4 critical issues blocking 80% of functionality:
1. **Authentication System Failure** (422 errors)
2. **Dashboard Routing Broken** (404 errors)
3. **React Hydration Errors** (SSR inconsistencies)
4. **Assessment Loop Bug** (React key warnings)

This plan provides a systematic approach to resolve these issues in priority order.

---

## 🚨 Priority 1: Authentication System (422 Errors)

### Root Cause Analysis
- Frontend sending malformed/incomplete data to `/api/auth/login`
- Possible field mapping issues between frontend and backend
- JWT token handling may be misconfigured

### Investigation Steps
```bash
# 1. Check backend logs for exact validation errors
docker-compose logs api | grep -A5 "422"

# 2. Verify API endpoint expectations
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 3. Check frontend login payload
# Add console.log in frontend/lib/api/auth.service.ts
```

### Fix Implementation

#### Step 1: Backend Validation Check
```python
# api/routers/auth.py - Add detailed logging
@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt for: {form_data.username}")
    try:
        # Add validation logging
        if not form_data.username or not form_data.password:
            logger.error("Missing username or password")
            raise HTTPException(
                status_code=422,
                detail="Username and password are required"
            )
```

#### Step 2: Frontend Auth Service Fix
```typescript
// frontend/lib/api/auth.service.ts
export const authService = {
  async login(credentials: LoginCredentials) {
    try {
      // Ensure correct field names
      const payload = {
        username: credentials.email, // OAuth2 expects 'username'
        password: credentials.password,
        grant_type: 'password' // Required for OAuth2
      };
      
      // Use FormData for OAuth2 compatibility
      const formData = new URLSearchParams();
      Object.entries(payload).forEach(([key, value]) => {
        formData.append(key, value);
      });
      
      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
```

#### Step 3: Environment Configuration
```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_USE_NEW_THEME=true
```

### Testing Verification
```bash
# Test authentication flow
cd frontend && pnpm test tests/auth/login.test.tsx

# Manual test
1. Start backend: python main.py
2. Start frontend: cd frontend && pnpm dev
3. Navigate to /login
4. Use test credentials: test@example.com / password123
```

---

## 🚨 Priority 2: Dashboard Routing (404 Errors)

### Root Cause Analysis
- Missing route definitions in Next.js App Router
- Incorrect navigation paths from landing page
- Possible middleware redirect issues

### Investigation Steps
```bash
# 1. Check existing routes
find frontend/app -name "page.tsx" | sort

# 2. Verify dashboard route exists
ls -la frontend/app/dashboard/
ls -la frontend/app/\(dashboard\)/dashboard/

# 3. Check middleware redirects
cat frontend/middleware.ts
```

### Fix Implementation

#### Step 1: Fix Dashboard Route Structure
```bash
# Ensure proper route structure
frontend/app/(dashboard)/dashboard/page.tsx  # Group route
# OR
frontend/app/dashboard/page.tsx             # Direct route
```

#### Step 2: Update Navigation Links
```typescript
// frontend/app/page.tsx (landing page)
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div>
      {/* Fix dashboard link */}
      <Link href="/dashboard" className="...">
        Go to Dashboard
      </Link>
      {/* Alternative auth-protected route */}
      <Link href="/auth/login?redirect=/dashboard" className="...">
        Login to Dashboard
      </Link>
    </div>
  );
}
```

#### Step 3: Add Auth Middleware
```typescript
// frontend/middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const isAuthenticated = request.cookies.get('auth-token');
  const isAuthPage = request.nextUrl.pathname.startsWith('/auth');
  
  if (!isAuthenticated && !isAuthPage) {
    // Redirect to login with return URL
    const url = new URL('/auth/login', request.url);
    url.searchParams.set('redirect', request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/assessments/:path*', '/policies/:path*']
};
```

### Testing Verification
```bash
# Test all dashboard routes
cd frontend
pnpm dev

# Visit these URLs:
# http://localhost:3000/dashboard
# http://localhost:3000/auth/login
# http://localhost:3000/ (check navigation links)
```

---

## 🚨 Priority 3: React Hydration Errors

### Root Cause Analysis
- Style mismatches between SSR and client
- Dynamic theme values not consistent
- Browser-only code running during SSR

### Fix Implementation

#### Step 1: Fix Theme Provider
```typescript
// frontend/components/theme-provider.tsx
'use client';

import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { useEffect, useState } from 'react';

export function ThemeProvider({ children, ...props }) {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  // Prevent hydration mismatch by not rendering theme-dependent content until mounted
  if (!mounted) {
    return <div style={{ visibility: 'hidden' }}>{children}</div>;
  }
  
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
```

#### Step 2: Fix Dynamic Styles
```typescript
// frontend/components/ui/input.tsx
import { cn } from '@/lib/utils';

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    // Use CSS variables instead of dynamic styles
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-input",
          "bg-background px-3 py-2 text-sm ring-offset-background",
          "file:border-0 file:bg-transparent file:text-sm file:font-medium",
          "placeholder:text-muted-foreground",
          "focus-visible:outline-none focus-visible:ring-2",
          "focus-visible:ring-ring focus-visible:ring-offset-2",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
```

#### Step 3: Add suppressHydrationWarning
```typescript
// frontend/app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

---

## 🚨 Priority 4: Assessment Loop Bug (React Keys)

### Root Cause Analysis
- Duplicate keys in list rendering
- Assessment questions array not properly indexed
- State management causing re-renders with same data

### Fix Implementation

#### Step 1: Fix Question Rendering
```typescript
// frontend/components/assessments/QuestionRenderer.tsx
export function QuestionRenderer({ questions, onAnswer }) {
  return (
    <div className="space-y-4">
      {questions.map((question, index) => (
        <QuestionCard
          key={`${question.id}-${index}`} // Ensure unique keys
          question={question}
          onAnswer={onAnswer}
        />
      ))}
    </div>
  );
}
```

#### Step 2: Fix Assessment State Management
```typescript
// frontend/lib/stores/assessment-store.ts
import { create } from 'zustand';

interface AssessmentStore {
  currentQuestionIndex: number;
  questions: Question[];
  answers: Record<string, any>;
  
  submitAnswer: (questionId: string, answer: any) => void;
  nextQuestion: () => void;
}

export const useAssessmentStore = create<AssessmentStore>((set, get) => ({
  currentQuestionIndex: 0,
  questions: [],
  answers: {},
  
  submitAnswer: (questionId, answer) => {
    set((state) => ({
      answers: { ...state.answers, [questionId]: answer }
    }));
  },
  
  nextQuestion: () => {
    set((state) => ({
      currentQuestionIndex: Math.min(
        state.currentQuestionIndex + 1,
        state.questions.length - 1
      )
    }));
  }
}));
```

#### Step 3: Fix Dynamic Question Loading
```typescript
// frontend/app/(dashboard)/assessments/new/page.tsx
export default function NewAssessment() {
  const { currentQuestionIndex, submitAnswer, nextQuestion } = useAssessmentStore();
  
  const handleSubmit = async (answer: any) => {
    const currentQuestion = questions[currentQuestionIndex];
    
    // Submit answer
    await submitAnswer(currentQuestion.id, answer);
    
    // Check if we need to load more questions
    if (shouldLoadDynamicQuestions(answer)) {
      await loadAdaptiveQuestions(currentQuestion, answer);
    }
    
    // Move to next question
    nextQuestion();
  };
}
```

---

## 📋 Implementation Timeline

### Week 1: Critical Blockers
- **Day 1-2**: Fix authentication (422 errors)
- **Day 3-4**: Fix dashboard routing (404 errors)
- **Day 5**: Deploy fixes to staging

### Week 2: Stability Issues
- **Day 1-2**: Resolve hydration errors
- **Day 3-4**: Fix assessment loop bug
- **Day 5**: Comprehensive testing

### Week 3: Verification & Monitoring
- **Day 1-2**: Re-run testsprite full suite
- **Day 3-4**: Fix any remaining issues
- **Day 5**: Production deployment prep

---

## 🧪 Testing Strategy

### Unit Tests
```bash
# Run after each fix
cd frontend
pnpm test --watch

# Specific test suites
pnpm test tests/auth/
pnpm test tests/navigation/
pnpm test tests/assessments/
```

### Integration Tests
```bash
# Full E2E test suite
cd frontend
pnpm test:e2e

# Specific flows
pnpm test:e2e tests/e2e/auth-flow.test.ts
pnpm test:e2e tests/e2e/dashboard-navigation.test.ts
```

### Manual Testing Checklist
- [ ] Login with valid credentials
- [ ] Login with invalid credentials  
- [ ] Navigate to dashboard from landing
- [ ] Switch assessment modes
- [ ] Complete assessment flow
- [ ] Check browser console for errors
- [ ] Verify no hydration warnings

---

## 🔍 Monitoring & Validation

### Error Tracking
```typescript
// frontend/lib/monitoring/error-tracker.ts
export function trackError(error: Error, context: any) {
  console.error('[ruleIQ Error]', {
    timestamp: new Date().toISOString(),
    message: error.message,
    stack: error.stack,
    context
  });
  
  // Send to monitoring service
  if (process.env.NODE_ENV === 'production') {
    // Sentry, LogRocket, etc.
  }
}
```

### Success Metrics
- Authentication success rate > 95%
- Zero 404 errors on core routes
- Zero hydration warnings in console
- Assessment completion rate > 90%
- All testsprite tests passing

---

## 🚀 Quick Start Commands

```bash
# Backend
source /home/omar/Documents/ruleIQ/.venv/bin/activate
python main.py

# Frontend (separate terminal)
cd frontend
pnpm dev

# Run tests
cd frontend
pnpm test
pnpm test:e2e

# Check for issues
pnpm lint
pnpm typecheck
```

---

## 📞 Escalation Path

1. **Authentication Issues**: Check `api/routers/auth.py` and `services/auth_service.py`
2. **Routing Issues**: Review `frontend/app` structure and `middleware.ts`
3. **Hydration Issues**: Check `ThemeProvider` and dynamic style usage
4. **State Issues**: Review Zustand stores and React Query hooks

Remember: After fixing each issue, run the relevant tests before moving to the next issue.