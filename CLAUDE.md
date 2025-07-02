I can see there are some formatting issues in the file. Here's the corrected version with proper formatting:

```markdown
# CLAUDE.md - ruleIQ Frontend Development Guide

This file provides guidance to Claude Code (claude.ai/code) when working with the ruleIQ compliance automation platform frontend.

## 🎉 PRODUCTION STATUS: READY FOR DEPLOYMENT

**Build Status**: ✅ Successful (36 static pages generated)
**Critical Issues**: ✅ All Resolved
**Environment Config**: ✅ Complete
**Testing**: ✅ 26 tests passing
**Production Readiness**: ✅ 95% Complete

### Latest Updates (2025-07-02)
- **Build Failures Fixed**: SSR issues, sidebar provider context, team page data structure
- **Environment Variables**: Stripe keys added to all environments
- **Production Config**: Docker, CI/CD, Next.js optimization complete
- **Code Quality**: ESLint auto-fixes applied, remaining issues non-blocking

## Project Context

**ruleIQ** (formerly ComplianceGPT) is an AI-powered compliance automation platform for UK SMBs. This is the frontend codebase, separated from the backend API.

### Target Users (Personas)
- **Alex (Analytical)**: Data-driven, wants customization and control
- **Ben (Cautious)**: Risk-averse, needs guidance and reassurance  
- **Catherine (Principled)**: Ethics-focused, values transparency and audit trails

## Development Commands

```bash
# Install dependencies (using pnpm - required)
pnpm install

# Start development server (runs on http://localhost:3000)
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run linting
pnpm lint

# Type checking (run manually as build ignores TS errors)
pnpm tsc --noEmit
```

**⚠️ Important Build Configuration:**
- TypeScript errors are ignored during build (`ignoreBuildErrors: true`) - Build succeeds despite TS errors
- ESLint errors are ignored during build (`ignoreDuringBuilds: true`) - 200+ linting errors exist but don't block builds
- Production build verified: `pnpm build` generates 36 static pages successfully
- Run type checking manually: `pnpm typecheck` (shows errors but doesn't block deployment)

## Architecture Overview

### Tech Stack (Non-Negotiable)
- **Framework**: Next.js 15.2.4 with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: 
  - Client: Zustand (to be implemented)
  - Server: TanStack Query (React Query) 
- **Forms**: React Hook Form + Zod validation
- **Animations**: Framer Motion
- **Real-time**: Native WebSocket API
- **File Upload**: react-dropzone
- **Rich Text**: TipTap editor

### Project Structure

```
/app                    # Next.js App Router pages
├── (auth)             # Auth pages (login, register)
├── (dashboard)        # Authenticated app pages
│   ├── dashboard/     # Main dashboard
│   ├── assessments/   # Compliance assessments
│   ├── evidence/      # Evidence management
│   ├── policies/      # Policy generation/management
│   └── chat/          # AI assistant
└── (public)           # Marketing pages

/components            
├── ui/                # Base shadcn/ui components
│   └── aceternity/    # Animation-focused components
├── features/          # Feature-specific components
│   ├── assessments/   
│   ├── evidence/      
│   ├── policies/      
│   └── chat/          
├── layouts/           # Layout components
└── shared/            # Shared components

/lib                   
├── api/               # API client (to be implemented)
├── data/              # Mock data (temporary)
├── hooks/             # Custom React hooks
├── stores/            # Zustand stores (to be implemented)
├── utils/             # Utilities
└── validations/       # Zod schemas
```

## Design System

### Brand Attributes
- **Trustworthy & Secure**: Professional, reliable, fortress-like protection
- **Intelligent & Precise**: Clean, data-forward, analytical rigor
- **Professional & Authoritative**: Serious, expert-level credibility
- **Empowering & Clear**: Simplifies complexity, user mastery

### Color Palette
```css
/* Primary Colors */
--primary-navy: #17255A;     /* Deep navy blue - primary brand color */
--primary-gold: #CB963E;     /* Gold - accent color for CTAs and highlights */
--primary-cyan: #34FEF7;     /* Bright cyan - energetic accent */

/* Neutral Colors */
--neutral-light: #D0D5E3;    /* Light gray - backgrounds, borders */
--neutral-medium: #C2C2C2;   /* Medium gray - secondary text, dividers */

/* Extended Palette (derived from primary) */
--navy-dark: #0F1938;        /* Darker variant for headers */
--navy-light: #2B3A6A;       /* Lighter variant for hover states */
--gold-dark: #A67A2E;        /* Darker gold for hover states */
--gold-light: #E0B567;       /* Lighter gold for backgrounds */

/* Semantic Colors */
--success: #28A745;          /* Keep existing for consistency */
--warning: #CB963E;          /* Use gold for warnings */
--error: #DC3545;            /* Keep existing for consistency */
--info: #34FEF7;             /* Use cyan for info states */

/* Text Colors */
--text-primary: #17255A;     /* Primary text in navy */
--text-secondary: #6B7280;   /* Secondary text */
--text-on-dark: #FFFFFF;     /* Text on dark backgrounds */
--text-on-gold: #17255A;     /* Navy text on gold backgrounds */

/* Background Colors */
--bg-primary: #FFFFFF;       /* White backgrounds */
--bg-secondary: #F8F9FB;     /* Slight blue tint */
--bg-tertiary: #D0D5E3;      /* Light gray sections */
```

### Color Usage Guidelines
- **Navy (#17255A)**: Primary brand color for headers, primary buttons, and key UI elements
- **Gold (#CB963E)**: Accent color for CTAs, highlights, and important actions (use sparingly ~10-15%)
- **Cyan (#34FEF7)**: Energy accent for interactive elements, notifications, and modern touches (use very sparingly ~5%)
- **Light Gray (#D0D5E3)**: Backgrounds, cards, section dividers
- **Medium Gray (#C2C2C2)**: Borders, disabled states, secondary elements

### Updated Tailwind Config Reference
```javascript
// tailwind.config.ts color extensions
colors: {
  primary: {
    DEFAULT: '#17255A',
    dark: '#0F1938',
    light: '#2B3A6A',
  },
  gold: {
    DEFAULT: '#CB963E',
    dark: '#A67A2E',
    light: '#E0B567',
  },
  cyan: {
    DEFAULT: '#34FEF7',
    dark: '#1FD4E5',
    light: '#6FFEFB',
  },
  neutral: {
    light: '#D0D5E3',
    medium: '#C2C2C2',
  }
}
```

### Component Color Applications
- **Primary Buttons**: `bg-primary hover:bg-primary-dark text-white`
- **Secondary Buttons**: `border-2 border-primary text-primary hover:bg-primary hover:text-white`
- **Accent Buttons**: `bg-gold hover:bg-gold-dark text-primary`
- **Cards**: `bg-white border border-neutral-light`
- **Sections**: `bg-neutral-light/20`
- **Interactive Elements**: `hover:text-cyan focus:ring-cyan/20`

### Typography
- **Font**: Inter (primary) or Roboto (fallback)
- **Scale**: H1: 32px Bold, H2: 24px Bold, H3: 18px Semi-Bold, Body: 14px, Small: 12px

### Spacing
- Use 8px grid system (4px half-step when necessary)
- All margins, paddings, gaps must be multiples of 8px

### Icons
- Use Lucide icon set exclusively
- Monochromatic line style only

## API Integration (Backend)

### Base Configuration
```typescript
// API URL: http://localhost:8000/api (development)
// All requests require Bearer token authentication
```

### Response Formats
```typescript
// Success Response
{
  "data": {...},
  "message": "Success",
  "status": 200
}

// Error Response  
{
  "detail": "Error message",
  "status": 400
}

// Paginated Response
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20
}
```

### Key API Endpoints
- **Auth**: `/api/auth/register`, `/api/auth/login`, `/api/auth/refresh`
- **Business Profiles**: `/api/business-profiles/*`
- **Assessments**: `/api/assessments/*`, `/api/assessments/quick`
- **Evidence**: `/api/evidence/*`, `/api/evidence/upload`
- **Policies**: `/api/policies/generate`, `/api/policies/*`
- **Chat**: `/api/chat/conversations`, WebSocket: `/api/chat/ws/{id}`

## Critical Integrations

### Business Profile Field Mapper
Located at `/lib/api/business-profile/field-mapper.ts`
- Handles backend field name truncation (e.g., `handles_personal_data` → `handles_persona`)
- Automatically applied in all business profile API calls
- Use `BusinessProfileFieldMapper.toAPI()` and `.fromAPI()` for manual transformations

### Advanced Error Handling
Located at `/lib/api/error-handler.ts` and `/lib/hooks/use-error-handler.ts`
- Automatic retry with exponential backoff for network/server errors
- User-friendly error messages based on context
- React hooks: `useErrorHandler()`, `useAsyncError()`, `useFormError()`

### UI Utilities
Located at `/lib/ui-utils.ts`
- Use `ruleIQStyles` for consistent styling
- `getComplianceScoreStyle(score)` for compliance-based styling
- `getButtonClassName(variant, size)` for button styling
- Persona-specific styles available

## Component Development Guidelines

### Component Patterns
```typescript
// Always use this pattern for new components
interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
  // Component-specific props
}

export function Component({ className, ...props }: ComponentProps) {
  return (
    <div className={cn("default-styles", className)} {...props}>
      {/* Component content */}
    </div>
  );
}
```

### Form Validation Pattern
```typescript
// Define schema in /lib/validations/
const schema = z.object({
  field: z.string().min(1, "Required"),
  // ... other fields
});

// Use with React Hook Form
const form = useForm<z.infer<typeof schema>>({
  resolver: zodResolver(schema),
});
```

### Persona-Specific UI Considerations
- **For Alex (Analytical)**:
  - Provide data-rich interfaces with customization
  - Include advanced filtering and export options
  - Show detailed metrics and analytics
  
- **For Ben (Cautious)**:
  - Use step-by-step wizards with progress indicators
  - Add confirmation dialogs and auto-save features
  - Provide extensive help text and tooltips
  
- **For Catherine (Principled)**:
  - Emphasize audit trails and version history
  - Show compliance status prominently
  - Include policy documentation links

## Implementation Status

### Phase 1: Foundation ✅ COMPLETED
- [x] Basic setup and authentication UI
- [x] Component library integration
- [x] API client setup with advanced error handling
- [x] State management implementation (Zustand)
- [x] Error boundaries and loading states
- [x] Business Profile Field Mapper
- [x] Advanced UI Utilities
- [x] WebSocket real-time features

### Phase 2: Business Profile & Dashboard ✅ COMPLETED
- [x] Multi-step profile wizard
- [x] Dashboard with widgets (AI Insights, Compliance Score, Pending Tasks)
- [x] Real API integration
- [x] Stripe payment integration

### Phase 3: Enhanced Features ✅ COMPLETED
- [x] Data visualization charts ✅ COMPLETED
- [x] Analytics dashboard for data-driven users ✅ COMPLETED
- [x] Export functionality for all data tables ✅ COMPLETED
- [x] Customizable dashboard widgets ✅ COMPLETED

### Phase 4: Production Readiness ✅ COMPLETED
- [x] Critical build issues fixed (SSR, sidebar provider, data structure errors)
- [x] Environment variables configured (development, staging, production)
- [x] Production build verification (36 static pages generated successfully)
- [x] Code quality improvements (ESLint auto-fixes applied)
- [x] Production configuration complete (Docker, CI/CD, Next.js optimization)
- [x] Testing infrastructure (26 tests passing)

### Future Enhancements (Optional)
- [ ] Quick actions panel
- [ ] Notification center
- [ ] Assessment framework selection
- [ ] Dynamic questionnaire
- [ ] Address remaining TypeScript strict mode issues
- [ ] Fix remaining ESLint code quality issues

### 🚀 PRODUCTION READY
The frontend is now **95% production ready** with all critical issues resolved. Build succeeds, environment is configured, and the application is ready for deployment. Remaining items are optional enhancements that don't block production deployment.

## Code Standards

### TypeScript
- Use strict mode
- Define interfaces for all props
- Avoid `any` type
- Use proper return types

### Component Standards
- All components must be accessible (WCAG 2.2 AA)
- Use semantic HTML
- Include proper ARIA labels
- Support keyboard navigation

### Performance
- Lazy load routes with dynamic imports
- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Optimize images with Next.js Image

### Git Workflow
- Branch naming: `feature/`, `fix/`, `chore/`
- Commit messages: conventional commits format
- PR required for main branch

## Development Checkpoints

Latest checkpoint: `frontend/.checkpoint-2025-01-07.md` - Quick Actions & Productivity planning

## Common Tasks

### Adding a New Page
1. Create route in `/app/(dashboard)/[feature]/page.tsx`
2. Add navigation item to sidebar
3. Create feature components in `/components/features/[feature]/`
4. Add Zod schema for forms in `/lib/validations/`

### Creating a Data Table
```typescript
// Use the existing DataTable component pattern
import { DataTable } from "@/components/ui/data-table";

// Define columns
const columns: ColumnDef<DataType>[] = [
  // ... column definitions
];

// Use in component
<DataTable data={data} columns={columns} />
```

### Implementing File Upload
```typescript
// Use existing Dropzone pattern
import { FileUpload } from "@/components/shared/file-upload";

<FileUpload
  onUpload={handleUpload}
  acceptedTypes={["pdf", "docx"]}
  maxSize={10 * 1024 * 1024} // 10MB
/>
```

## Debugging Tips

1. **Mock Data**: All data is currently mocked in `/lib/data/`
2. **No Auth**: Authentication is UI-only, no actual auth logic
3. **Type Errors**: Run `pnpm tsc --noEmit` to check types
4. **Build Issues**: Check console for suppressed TS/ESLint errors

## Resources

- [Backend API Documentation](../backend_full_breakdown.odt)
- [Design System Spec](../ruleIQ_complete_frontend_design_specification.md)
- [shadcn/ui Docs](https://ui.shadcn.com)
- [Tailwind CSS Docs](https://tailwindcss.com)
```

