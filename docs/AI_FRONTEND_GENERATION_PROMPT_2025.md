# RuleIQ AI Frontend Generation Prompt
## Master Prompt for AI-Driven Frontend Development Tools
### Version 1.0 - January 2025

---

## 🎯 COPY THIS ENTIRE PROMPT SECTION INTO YOUR AI TOOL

```markdown
# Create RuleIQ Compliance Automation Platform Frontend

## PROJECT CONTEXT & FOUNDATION

You are building the frontend for RuleIQ, an enterprise B2B SaaS platform that automates compliance management and risk assessment. The platform helps companies achieve and maintain compliance with frameworks like ISO 27001, SOC 2, GDPR, and HIPAA through AI-powered policy generation, automated assessments, and evidence collection.

### Tech Stack Requirements:
- **Framework**: Next.js 15.4.7 with App Router
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 3.4 with shadcn/ui components
- **State Management**: Zustand 4.x for global state
- **Forms**: React Hook Form with Zod validation
- **Data Fetching**: TanStack Query (React Query) v5
- **Icons**: Lucide React icons
- **Authentication**: NextAuth.js with JWT
- **Charts**: Recharts for data visualization
- **Tables**: TanStack Table for data grids
- **Date Handling**: date-fns
- **Animations**: Framer Motion for micro-interactions

### Design System & Brand Identity:
- **Primary Color**: Teal (#2C7A7B) - Professional trust
- **Secondary Color**: Dark Teal (#0F766E) - Authority
- **Accent Color**: Light Teal (#14B8A6) - Interactive elements
- **Success**: Green (#10B981)
- **Warning**: Amber (#F59E0B)
- **Error**: Red (#EF4444)
- **Typography**: Inter for body, Space Grotesk for headings
- **Border Radius**: 8px (rounded-lg)
- **Shadow**: Multi-layer for depth
- **Spacing**: 4px base unit

## HIGH-LEVEL GOAL

Create a responsive, accessible (WCAG 2.1 AA compliant), and performant compliance management dashboard with the following core modules:

1. Authentication flow with onboarding wizard
2. Main dashboard with compliance score visualization
3. Policy management interface
4. Assessment workflow system
5. Evidence collection and management
6. Risk register and mitigation tracking
7. User profile and team management
8. Settings and integrations panel

## DETAILED STEP-BY-STEP INSTRUCTIONS

### STEP 1: Project Setup and Configuration

1. Initialize a new Next.js project with TypeScript:
   ```bash
   npx create-next-app@latest ruleiq-frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
   ```

2. Install required dependencies:
   ```bash
   npm install @tanstack/react-query@5 zustand@4 react-hook-form@7 zod@3 
   npm install lucide-react recharts @tanstack/react-table date-fns framer-motion
   npm install next-auth@beta @auth/prisma-adapter
   ```

3. Configure `tailwind.config.ts` with the brand colors:
   ```typescript
   theme: {
     extend: {
       colors: {
         brand: {
           50: '#E6FFFA',
           100: '#B2F5EA',
           200: '#81E6D9',
           300: '#4FD1C5',
           400: '#14B8A6',
           500: '#319795',
           600: '#2C7A7B',
           700: '#0F766E',
           800: '#285E61',
           900: '#234E52',
         }
       }
     }
   }
   ```

### STEP 2: Create the Authentication Layout

Create `/app/(auth)/layout.tsx`:

```typescript
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-2">
            <Shield className="w-10 h-10 text-brand-600" />
            <span className="text-3xl font-bold text-gray-900">RuleIQ</span>
          </div>
          <p className="mt-2 text-gray-600">Compliance made simple</p>
        </div>
        {children}
      </div>
    </div>
  );
}
```

### STEP 3: Build the Login Component

Create `/app/(auth)/login/page.tsx` with these requirements:

1. Email and password fields with validation
2. "Remember me" checkbox
3. "Forgot password" link
4. Social login options (Google, Microsoft)
5. Loading states and error handling
6. Mobile-first responsive design
7. ARIA labels for accessibility

The form should:
- Validate email format
- Require minimum 8 character password
- Show inline validation errors
- Disable submit during loading
- Redirect to dashboard on success

### STEP 4: Create the Main Dashboard Layout

Create `/app/(dashboard)/layout.tsx` with:

1. **Sidebar Navigation** (collapsible on mobile):
   - Dashboard (home icon)
   - Policies (file-text icon)
   - Assessments (clipboard-check icon)
   - Evidence (folder-open icon)
   - Risks (alert-triangle icon)
   - Reports (bar-chart icon)
   - Settings (settings icon)

2. **Top Header Bar**:
   - Search bar (global search)
   - Notifications bell with badge
   - User avatar dropdown menu
   - Organization switcher

3. **Mobile Responsive Behavior**:
   - Hamburger menu for sidebar toggle
   - Bottom tab navigation for core features
   - Swipe gestures for navigation

### STEP 5: Build the Dashboard Home Page

Create `/app/(dashboard)/page.tsx` with these widgets:

1. **Compliance Score Card** (hero section):
   ```typescript
   // Visual: Large circular progress indicator
   // Score: 0-100 with color coding
   // Trend: Up/down arrow with percentage
   ```

2. **Framework Status Grid** (2x2 on desktop, stack on mobile):
   - ISO 27001: Progress bar, due date, action items
   - SOC 2: Progress bar, due date, action items
   - GDPR: Progress bar, due date, action items
   - HIPAA: Progress bar, due date, action items

3. **Recent Activity Timeline**:
   - Policy updates
   - Assessment completions
   - Evidence uploads
   - Team actions

4. **Quick Actions FAB** (floating action button on mobile):
   - Create policy
   - Start assessment
   - Upload evidence
   - Invite team member

### STEP 6: Create the Policy Management Interface

Create `/app/(dashboard)/policies/page.tsx`:

1. **Filter Bar**:
   - Search by policy name
   - Filter by framework
   - Filter by status (draft, active, archived)
   - Sort options (name, date, compliance)

2. **Policy Grid/List View Toggle**:
   - Grid view: Cards with preview
   - List view: Table with columns

3. **Policy Card Component**:
   ```typescript
   interface PolicyCard {
     title: string;
     framework: string;
     lastUpdated: Date;
     complianceScore: number;
     status: 'draft' | 'active' | 'review' | 'archived';
     owner: User;
     actions: ['edit', 'duplicate', 'archive', 'delete'];
   }
   ```

4. **Bulk Actions**:
   - Select multiple policies
   - Bulk approve/archive/delete
   - Export selected as PDF/CSV

### STEP 7: Build the Assessment Workflow

Create `/app/(dashboard)/assessments/[id]/page.tsx`:

1. **Progress Stepper**:
   - Step 1: Select framework
   - Step 2: Answer questions
   - Step 3: Upload evidence
   - Step 4: Review & submit
   - Step 5: Results & recommendations

2. **Question Interface**:
   - Question text with help tooltip
   - Answer options (Yes/No/Partial/NA)
   - Evidence attachment area
   - Notes/comments field
   - Save & continue button

3. **Mobile Optimizations**:
   - Swipe between questions
   - Progress bar at top
   - Quick save indicator
   - Offline mode support

### STEP 8: Implement Accessibility Features

1. **Keyboard Navigation**:
   ```typescript
   // Add skip links
   <a href="#main" className="sr-only focus:not-sr-only">
     Skip to main content
   </a>
   ```

2. **ARIA Labels**:
   ```typescript
   <button
     aria-label="Open navigation menu"
     aria-expanded={isOpen}
     aria-controls="navigation-menu"
   >
   ```

3. **Focus Management**:
   - Trap focus in modals
   - Restore focus on close
   - Visual focus indicators

4. **Color Contrast Fixes**:
   - Text: minimum 4.5:1 ratio
   - Large text: minimum 3:1 ratio
   - Use #14B8A6 instead of lighter teals

### STEP 9: Add Performance Optimizations

1. **Code Splitting**:
   ```typescript
   const PolicyEditor = dynamic(
     () => import('@/components/PolicyEditor'),
     { loading: () => <Skeleton /> }
   );
   ```

2. **Image Optimization**:
   ```typescript
   import Image from 'next/image';
   // Use Next.js Image component for all images
   ```

3. **Virtual Scrolling** for large lists:
   ```typescript
   import { VirtualList } from '@tanstack/react-virtual';
   // Implement for policy lists > 50 items
   ```

4. **Lazy Loading**:
   - Defer non-critical JavaScript
   - Lazy load below-fold content
   - Implement intersection observer

### STEP 10: Create Responsive Breakpoints

```css
/* Mobile First Approach */
/* Default: Mobile (320px - 639px) */
.container { padding: 1rem; }

/* Tablet (640px - 1023px) */
@media (min-width: 640px) {
  .container { padding: 2rem; }
}

/* Desktop (1024px - 1279px) */
@media (min-width: 1024px) {
  .container { padding: 3rem; }
}

/* Large Desktop (1280px+) */
@media (min-width: 1280px) {
  .container { padding: 4rem; }
}
```

## API CONTRACTS & INTEGRATION POINTS

### Authentication Endpoints:
```typescript
POST /api/auth/login
Body: { email: string, password: string }
Response: { token: string, user: User }

POST /api/auth/refresh
Headers: { Authorization: "Bearer <refresh_token>" }
Response: { token: string }

POST /api/auth/logout
Headers: { Authorization: "Bearer <token>" }
Response: { success: boolean }
```

### Dashboard Data:
```typescript
GET /api/dashboard/summary
Response: {
  complianceScore: number;
  frameworks: Framework[];
  recentActivity: Activity[];
  upcomingDeadlines: Deadline[];
}
```

### Policy Management:
```typescript
GET /api/policies
Query: { page: number, limit: number, search?: string, framework?: string }
Response: { policies: Policy[], total: number }

POST /api/policies
Body: { title: string, framework: string, content: string }
Response: { policy: Policy }

PUT /api/policies/:id
Body: { title?: string, content?: string, status?: string }
Response: { policy: Policy }
```

## CONSTRAINTS & BOUNDARIES

### DO:
- Use shadcn/ui components as the base component library
- Implement proper loading states for all async operations
- Add error boundaries for graceful error handling
- Use Zustand for global state management
- Implement proper TypeScript types for all components
- Follow mobile-first responsive design
- Ensure WCAG 2.1 AA compliance
- Use Tailwind CSS for all styling
- Implement proper form validation with Zod
- Add animations with Framer Motion

### DO NOT:
- Use any UI library other than shadcn/ui
- Create custom CSS files (use Tailwind only)
- Implement authentication logic (use NextAuth.js)
- Make direct API calls (use TanStack Query)
- Use class components (functional only)
- Ignore TypeScript errors
- Skip accessibility requirements
- Use inline styles except for dynamic values
- Modify the core Next.js configuration
- Use client-side routing (use Next.js App Router)

### FILES TO CREATE:
- /app/(auth)/layout.tsx
- /app/(auth)/login/page.tsx
- /app/(auth)/register/page.tsx
- /app/(auth)/forgot-password/page.tsx
- /app/(dashboard)/layout.tsx
- /app/(dashboard)/page.tsx
- /app/(dashboard)/policies/page.tsx
- /app/(dashboard)/assessments/page.tsx
- /app/(dashboard)/evidence/page.tsx
- /app/(dashboard)/risks/page.tsx
- /components/ui/* (shadcn components)
- /components/features/* (feature components)
- /lib/api/* (API client functions)
- /lib/stores/* (Zustand stores)
- /types/* (TypeScript definitions)

### FILES NOT TO MODIFY:
- package.json (except for dependencies)
- next.config.js (unless absolutely necessary)
- .env files (security sensitive)
- Any files outside the specified directories

## MOBILE-FIRST RESPONSIVE INSTRUCTIONS

### Mobile Layout (320px - 639px):
1. Single column layout
2. Hamburger menu for navigation
3. Bottom tab bar for quick access
4. Full-width cards and buttons
5. Larger touch targets (minimum 44x44px)
6. Simplified data tables (key info only)
7. Stacked form fields
8. Modal dialogs take full screen

### Tablet Layout (640px - 1023px):
1. Two column grid where appropriate
2. Collapsible sidebar (closed by default)
3. Floating action buttons
4. Cards in 2-column grid
5. Show more table columns
6. Side-by-side form fields where logical
7. Modal dialogs centered with margin

### Desktop Layout (1024px+):
1. Full sidebar always visible
2. Multi-column dashboards (3-4 columns)
3. Advanced data tables with all columns
4. Inline editing capabilities
5. Hover states for interactive elements
6. Keyboard shortcuts enabled
7. Right-side panels for details

## FINAL NOTES

This prompt provides the complete specification for building the RuleIQ frontend. Start with Step 1 and proceed sequentially. Each component should be fully functional and tested before moving to the next. Remember to:

1. Test on real devices, not just browser dev tools
2. Validate accessibility with screen readers
3. Check performance metrics (Core Web Vitals)
4. Ensure cross-browser compatibility
5. Implement proper error handling
6. Add loading skeletons for better UX
7. Document component props with TypeScript
8. Write unit tests for critical paths

The generated code will require human review, testing, and refinement before production deployment. Focus on creating one component at a time, testing it thoroughly, then building upon that foundation.
```

---

## 📋 HOW TO USE THIS PROMPT

### For Vercel v0:
1. Copy the entire prompt above (everything in the code block)
2. Go to [v0.dev](https://v0.dev)
3. Paste the prompt
4. v0 will generate the initial components
5. Iterate on specific components by asking for refinements

### For Lovable.ai / Bolt.new:
1. Create a new project
2. Paste the prompt as your initial specification
3. Let the AI scaffold the project structure
4. Use follow-up prompts to refine individual features

### For Claude/ChatGPT Code Generation:
1. Start a new conversation
2. Paste the prompt
3. Ask for specific file generation one at a time
4. Example: "Generate the complete code for /app/(auth)/login/page.tsx"

## 🔄 ITERATION STRATEGY

After initial generation, use these follow-up prompts for refinement:

### Refining Components:
```
"Make the PolicyCard component more visually appealing with a gradient border on hover and add a preview modal when clicking the preview button"
```

### Adding Features:
```
"Add real-time search to the policies page that filters as the user types, with debouncing and loading states"
```

### Fixing Issues:
```
"The sidebar navigation is not closing on mobile when a link is clicked. Fix this and add a smooth transition animation"
```

### Enhancing UX:
```
"Add skeleton loaders to all data-fetching components and implement optimistic updates for better perceived performance"
```

## ⚠️ IMPORTANT REMINDERS

1. **Generated Code Requires Review**: All AI-generated code must be:
   - Tested thoroughly
   - Reviewed for security vulnerabilities
   - Validated for accessibility
   - Optimized for performance
   - Checked for proper error handling

2. **Incremental Development**: Don't try to generate the entire application at once:
   - Start with authentication flow
   - Build the layout structure
   - Add one feature at a time
   - Test each component before proceeding

3. **Security Considerations**:
   - Never expose API keys in frontend code
   - Implement proper CORS policies
   - Validate all user inputs
   - Use HTTPS for all API calls
   - Implement rate limiting

4. **Performance Monitoring**:
   - Use Lighthouse for performance audits
   - Monitor bundle sizes
   - Implement proper caching strategies
   - Optimize images and assets

## 🎯 SUCCESS CRITERIA

Your generated frontend is successful when:

✅ All WCAG 2.1 AA requirements are met
✅ Core Web Vitals scores are in the green
✅ Mobile responsiveness works on all devices
✅ All forms have proper validation
✅ Loading states are present for all async operations
✅ Error handling provides clear user feedback
✅ The design matches the brand guidelines
✅ Navigation is intuitive and consistent
✅ The code is properly typed with TypeScript
✅ All API integrations work correctly

---

*Generated by RuleIQ Frontend Architecture Team - January 2025*
*This prompt is optimized for AI code generation tools and follows industry best practices for frontend development.*