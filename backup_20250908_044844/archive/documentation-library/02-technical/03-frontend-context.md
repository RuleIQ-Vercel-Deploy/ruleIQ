# Frontend Context

## Purpose & Responsibility

The frontend layer provides the user interface for the ruleIQ compliance automation platform. It delivers a modern, responsive web application for UK SMBs to manage compliance assessments, evidence collection, AI-powered guidance, and compliance reporting.

## Architecture Overview

### **Frontend Design Pattern**
- **Pattern**: Component-based architecture with feature-driven organization
- **Approach**: Modern React patterns with Next.js App Router and TypeScript
- **State Management**: Zustand for client state, TanStack Query for server state

### **Technology Stack**
```
Framework: Next.js 15 with App Router
Language: TypeScript (strict mode)
Styling: Tailwind CSS + shadcn/ui component library
State: Zustand (client) + TanStack Query (server)
Forms: React Hook Form + Zod validation
Animation: Framer Motion
Real-time: Native WebSocket API
Testing: Vitest + Testing Library + Playwright E2E
```

## Dependencies

### **Incoming Dependencies**
- **Web Browsers**: Chrome, Firefox, Safari, Edge (modern versions)
- **User Personas**: Alex (Analytical), Ben (Cautious), Catherine (Principled)
- **Business Requirements**: UK SMB compliance automation workflows
- **Design System**: Brand guidelines and accessibility requirements

### **Outgoing Dependencies**
- **Backend API**: REST API at `/api/v1/*` for all data operations
- **WebSocket Services**: Real-time chat and streaming responses
- **File Storage**: Document upload and evidence management
- **Authentication Services**: JWT-based authentication with refresh
- **External Services**: Stripe for payments, analytics tracking

## Key Interfaces

### **Public User Interfaces**

#### **Authentication Pages** (`/app/(auth)/`)
```typescript
/login           - User authentication with email/password
/register        - New user registration and onboarding
/signup          - Alternative signup flow for different user types
/signup-traditional - Traditional form-based registration
```

#### **Dashboard Application** (`/app/(dashboard)/`)
```typescript
/dashboard       - Main compliance dashboard with widgets
/business-profile - Company profile setup and management
/assessments/*   - Compliance assessment workflows
/evidence        - Evidence collection and management
/policies/*      - AI-powered policy generation
/chat           - Real-time AI compliance assistant
/reports        - Compliance reporting and analytics
/settings/*     - User, billing, and integration settings
```

#### **Public Pages** (`/app/(public)/`)
```typescript
/               - Marketing landing page
/marketing      - Product marketing pages
/design-system  - Component showcase and documentation
```

### **Component Architecture**

#### **UI Foundation** (`/components/ui/`)
```typescript
// Base shadcn/ui components (90+ components)
Button, Input, Card, Dialog, Form, Table, Select, etc.

// Enhanced UI components
DataTable           - Advanced data tables with sorting, filtering
Chart              - Data visualization components
ProgressBar        - Loading and progress indicators
Skeleton           - Loading state placeholders
Toast              - Notification system
Theme-toggle       - Dark/light mode switching
```

#### **Feature Components** (`/components/`)
```typescript
// Assessment workflow components
AssessmentWizard           - Multi-step assessment interface
QuestionRenderer          - Dynamic question display logic
ProgressTracker           - Assessment progress visualization
ComplianceGauge          - Compliance score visualization
AIGuidancePanel          - Real-time AI assistance integration
StreamingAnalysisDialog  - Real-time AI analysis streaming

// Dashboard components  
DashboardHeader          - Navigation and user controls
StatsCard               - Key metrics display
QuickActionsWidget      - Common action shortcuts
AIInsightsWidget        - AI-powered compliance insights
ComplianceScoreWidget   - Overall compliance status
PendingTasksWidget      - Outstanding action items

// Evidence management
FileUploader            - Drag-and-drop file upload
EvidenceCard           - Evidence item display
BulkActionsBar         - Multi-item operations
FilterSidebar          - Evidence filtering and search

// Chat interface
ChatHeader             - Chat session controls
ChatMessage            - Message display with AI formatting
ConversationSidebar    - Chat history and management
TypingIndicator        - Real-time typing status
```

### **State Management Architecture**

#### **Zustand Stores** (`/lib/stores/`)
```typescript
// Authentication state
AuthStore {
  user: User | null
  tokens: TokenPair | null
  isAuthenticated: boolean
  login(credentials): Promise<void>
  logout(): Promise<void>
  refreshToken(): Promise<void>
}

// Business profile management  
BusinessProfileStore {
  profile: BusinessProfile | null
  formData: Partial<BusinessProfile>
  isLoading: boolean
  errors: Record<string, string>
  
  loadProfile(): Promise<void>
  updateProfile(data): Promise<void>
  validateStep(step): boolean
  isFormValid(): boolean
}

// Assessment workflow
AssessmentStore {
  currentAssessment: Assessment | null
  responses: Record<string, any>
  progress: number
  aiRecommendations: Recommendation[]
  
  startAssessment(frameworkId): Promise<void>
  saveResponse(questionId, response): Promise<void>
  generateRecommendations(): Promise<void>
}

// Evidence collection
EvidenceStore {
  items: EvidenceItem[]
  filters: EvidenceFilters
  uploadProgress: Record<string, number>
  
  loadEvidence(): Promise<void>
  uploadFile(file): Promise<void>
  updateItem(id, updates): Promise<void>
  deleteItems(ids): Promise<void>
}

// Chat interface
ChatStore {
  conversations: Conversation[]
  activeConversation: string | null
  messages: Message[]
  isTyping: boolean
  
  createConversation(): Promise<string>
  sendMessage(content): Promise<void>
  connectWebSocket(): void
}
```

#### **TanStack Query Integration** (`/lib/tanstack-query/`)
```typescript
// API query hooks
useAuth()             - Authentication state and operations
useBusinessProfile()  - Business profile CRUD operations
useAssessments()      - Assessment data and operations
useEvidence()         - Evidence management
usePolicies()         - Policy generation and management
useDashboard()        - Dashboard widget data

// Advanced query patterns
useInfiniteScroll()   - Infinite scrolling for large datasets
useMutationWithToast() - Mutations with success/error notifications
useOptimistic()       - Optimistic updates for better UX
```

## Implementation Context

### **Critical Security Issues** ⚠️

#### **URGENT: Authentication Token Storage**
**Impact**: XSS vulnerability allowing token theft
**Priority**: Critical - Security risk requiring immediate fix

```typescript
// CURRENT (VULNERABLE) IMPLEMENTATION:
// lib/stores/auth.store.ts:130
localStorage.setItem("ruleiq_auth_token", tokens.access_token);
localStorage.setItem("ruleiq_refresh_token", tokens.refresh_token);

// REQUIRED FIX:
// 1. Use HTTP-only secure cookies for refresh tokens
// 2. Keep access tokens in memory only  
// 3. Add token encryption for localStorage fallback
// 4. Implement proper token rotation
```

#### **Missing CSRF Protection**
```typescript
// MISSING: CSRF token implementation
// Required for all state-changing operations
// Add SameSite cookie attributes
// Validate origin headers
```

#### **Client-side Data Exposure**
```typescript
// VULNERABLE: Sensitive data in localStorage
// app/(dashboard)/compliance-wizard/page.tsx:235
localStorage.setItem('compliance_assessment', JSON.stringify({
  answers, report, timestamp: Date.now()
}));

// FIX: Encrypt sensitive data before storage
// Implement data expiration
// Use secure session storage for temporary data
```

### **Build Configuration Issues** ⚠️

#### **TypeScript Errors Ignored**
```typescript
// next.config.mjs - PROBLEMATIC:
typescript: {
  ignoreBuildErrors: true,    // 26+ TypeScript errors ignored
},
eslint: {
  ignoreDuringBuilds: true,   // ESLint errors ignored
}

// IMPACT: Type safety compromised, potential runtime errors
// REQUIRED: Fix all TypeScript errors before production
```

#### **Bundle Size Concerns**
```json
// package.json - Large dependency footprint
"dependencies": {
  // 170+ packages including heavy libraries
  "@radix-ui/*": "^1.0.0",      // Multiple Radix components
  "framer-motion": "^10.0.0",   // Animation library (large)
  "recharts": "^2.8.0",         // Chart library (large)
  "react-hook-form": "^7.45.0", // Form handling
  // ... many more
}

// OPTIMIZATION NEEDED:
// - Dynamic imports for heavy components
// - Code splitting for routes
// - Tree shaking optimization
```

### **Component Architecture Strengths**

#### **Modern React Patterns**
```typescript
// Excellent use of modern React patterns
export function Component({ className, ...props }: ComponentProps) {
  return (
    <div className={cn("default-styles", className)} {...props}>
      {/* Clean component implementation */}
    </div>
  );
}

// Proper TypeScript integration
interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
  variant?: 'default' | 'secondary' | 'destructive';
}
```

#### **Form Handling Excellence**
```typescript
// React Hook Form + Zod validation pattern
const schema = z.object({
  field: z.string().min(1, "Required"),
  email: z.string().email("Invalid email"),
});

const form = useForm<z.infer<typeof schema>>({
  resolver: zodResolver(schema),
});
```

#### **UI Consistency**
```typescript
// shadcn/ui provides excellent component consistency
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Form } from "@/components/ui/form";

// Consistent styling with Tailwind CSS
// Accessibility built-in with proper ARIA attributes
// Theme support with CSS custom properties
```

### **Performance Considerations**

#### **Current Performance Issues**
```typescript
// Heavy component imports without lazy loading
import { AssessmentWizard } from '@/components/assessments/AssessmentWizard';
import { StreamingAnalysisDialog } from '@/components/assessments/StreamingAnalysisDialog';

// OPTIMIZATION: Use dynamic imports
const AssessmentWizard = lazy(() => import('@/components/assessments/AssessmentWizard'));
const StreamingAnalysisDialog = lazy(() => import('@/components/assessments/StreamingAnalysisDialog'));
```

#### **Memory Management**
```typescript
// WebSocket connections need proper cleanup
useEffect(() => {
  const ws = new WebSocket(wsUrl);
  return () => {
    ws.close(); // Ensure cleanup
  };
}, []);

// Event listeners need cleanup
useEffect(() => {
  const handler = (event) => { /* ... */ };
  window.addEventListener('resize', handler);
  return () => window.removeEventListener('resize', handler);
}, []);
```

### **Testing Infrastructure**

#### **Test Coverage Status**
```bash
Frontend Tests: 159 total
├── Component Tests: 45 tests (UI components)
├── Integration Tests: 38 tests (user flows)  
├── E2E Tests: 28 tests (complete journeys)
├── Accessibility Tests: 15 tests (WCAG compliance)
├── Performance Tests: 12 tests (Core Web Vitals)
├── AI Integration Tests: 21 tests (AI component testing)
└── Store Tests: 22 tests (state management) - 100% passing
```

#### **Testing Strategy**
```typescript
// Component testing with Testing Library
test('renders assessment wizard correctly', () => {
  render(<AssessmentWizard framework="gdpr" />);
  expect(screen.getByRole('progressbar')).toBeInTheDocument();
});

// E2E testing with Playwright
test('complete assessment workflow', async ({ page }) => {
  await page.goto('/assessments/new');
  await page.selectOption('[data-testid=framework-select]', 'gdpr');
  await page.click('[data-testid=start-assessment]');
  // ... complete workflow testing
});

// Store testing with comprehensive coverage
describe('BusinessProfileStore', () => {
  // 22 tests with 100% passing rate
  test('validates form data correctly', () => {
    // Store behavior testing
  });
});
```

## Change Impact Analysis

### **Risk Factors**

#### **High-Risk Areas**
1. **Authentication System**: Token security vulnerabilities
2. **Build Configuration**: TypeScript errors causing runtime issues
3. **Bundle Size**: Performance impact on load times
4. **WebSocket Connections**: Memory leaks and connection management
5. **Form Validation**: Data integrity and user experience

#### **Breaking Change Potential**
1. **API Contract Changes**: Backend changes affecting frontend integration
2. **Authentication Changes**: Token format or validation modifications
3. **Component Library Updates**: shadcn/ui or Radix updates
4. **State Management Changes**: Store interface modifications
5. **Route Structure Changes**: Next.js App Router modifications

### **Testing Requirements**

#### **Security Testing**
- **Authentication Flow**: Token handling and refresh mechanisms
- **XSS Prevention**: Input sanitization and output encoding
- **CSRF Protection**: State-changing operation validation
- **Data Storage Security**: localStorage and sessionStorage validation

#### **Performance Testing**
- **Bundle Analysis**: Webpack bundle analyzer for size optimization
- **Core Web Vitals**: LCP, FID, CLS measurement and optimization
- **Load Testing**: Component rendering under stress
- **Memory Profiling**: Memory leak detection and prevention

#### **Accessibility Testing**
- **Screen Reader**: NVDA, JAWS, VoiceOver compatibility
- **Keyboard Navigation**: Tab order and keyboard shortcuts
- **Color Contrast**: WCAG AA compliance validation
- **Focus Management**: Proper focus handling in dynamic content

## Current Status

### **Production Readiness Assessment**
- **Component Architecture**: ✅ Well-designed with modern patterns
- **State Management**: ✅ Comprehensive with Zustand + TanStack Query
- **UI Consistency**: ✅ Excellent with shadcn/ui integration
- **Critical Security Issues**: ❌ Authentication vulnerabilities block production
- **Build Configuration**: ⚠️ TypeScript errors need resolution
- **Performance**: ⚠️ Bundle optimization required

### **Completed Features**
- ✅ **Authentication Flow**: Login, registration, password management
- ✅ **Business Profile Management**: Complete CRUD with wizard interface
- ✅ **Dashboard**: Customizable widgets and analytics
- ✅ **UI Component Library**: 90+ components with consistent styling
- ✅ **Form Handling**: React Hook Form + Zod validation
- ✅ **Error Handling**: Error boundaries and user feedback
- ✅ **Real-time Features**: WebSocket chat and streaming

### **In Progress: Assessment Workflow**
- 🔄 **Assessment Wizard**: Multi-step assessment interface
- 🔄 **AI Integration**: Real-time guidance and recommendations
- 🔄 **Progress Tracking**: Assessment completion and validation
- 🔄 **Results Analysis**: Gap analysis and recommendation display

### **Required Actions Before Production**

#### **Phase 1: Critical Security Fixes (Week 1)**
1. **Implement secure token storage** - Use HTTP-only cookies
2. **Add CSRF protection** - Implement CSRF tokens for all mutations
3. **Encrypt sensitive localStorage data** - Add encryption layer
4. **Fix authentication vulnerabilities** - Comprehensive security review

#### **Phase 2: Build and Performance (Week 2)**
1. **Fix TypeScript errors** - Resolve all 26+ build errors
2. **Optimize bundle size** - Implement code splitting and lazy loading
3. **Performance optimization** - Core Web Vitals improvements
4. **Memory leak fixes** - WebSocket and event listener cleanup

#### **Phase 3: Feature Completion (Week 3)**
1. **Complete assessment workflow** - Finish wizard implementation
2. **Enhanced AI integration** - Real-time streaming and guidance
3. **Evidence management** - File upload and processing completion
4. **Comprehensive testing** - E2E workflow validation

### **Quality Metrics**

#### **Current Metrics**
- **Test Coverage**: 159 tests across all application areas
- **TypeScript Coverage**: ~85% (with build errors present)
- **Component Library**: 90+ reusable components
- **Accessibility**: Basic WCAG compliance implemented
- **Performance**: Needs optimization for production

#### **Target Metrics for Production**
- **Test Coverage**: >90% for critical user flows
- **TypeScript**: 100% error-free with strict mode
- **Performance**: <3s initial load, <1s navigation
- **Accessibility**: WCAG 2.2 AA compliance
- **Security**: Zero high-severity vulnerabilities

---

**Document Metadata**
- Created: 2025-01-07
- Version: 1.0.0
- Authors: AI Assistant
- Review Status: Initial Draft - CRITICAL SECURITY ISSUES IDENTIFIED
- Next Review: 2025-01-08 (Urgent - security fixes required)
- Dependencies: ARCHITECTURE_CONTEXT.md, AI_SERVICES_CONTEXT.md
- Change Impact: CRITICAL - security vulnerabilities require immediate attention
- Related Files: frontend/app/*, frontend/components/*, frontend/lib/*