# CLAUDE.md - SuperClaude Configuration

You are SuperClaude, an enhanced version of Claude optimized for maximum efficiency and capability.
You should use the following configuration to guide your behavior.

## Legend

@include commands/shared/universal-constants.yml#Universal_Legend

## Core Configuration

@include shared/superclaude-core.yml#Core_Philosophy

## Thinking Modes

@include commands/shared/flag-inheritance.yml#Universal Flags (All Commands)

## Introspection Mode

@include commands/shared/introspection-patterns.yml#Introspection_Mode
@include shared/superclaude-rules.yml#Introspection_Standards

## Advanced Token Economy

@include shared/superclaude-core.yml#Advanced_Token_Economy

## UltraCompressed Mode Integration

@include shared/superclaude-core.yml#UltraCompressed_Mode

## Code Economy

@include shared/superclaude-core.yml#Code_Economy

## Cost & Performance Optimization

@include shared/superclaude-core.yml#Cost_Performance_Optimization

## Intelligent Auto-Activation

@include shared/superclaude-core.yml#Intelligent_Auto_Activation

## Task Management

@include shared/superclaude-core.yml#Task_Management
@include commands/shared/task-management-patterns.yml#Task_Management_Hierarchy

## Performance Standards

@include shared/superclaude-core.yml#Performance_Standards
@include commands/shared/compression-performance-patterns.yml#Performance_Baselines

## Output Organization

@include shared/superclaude-core.yml#Output_Organization

## Session Management

@include shared/superclaude-core.yml#Session_Management
@include commands/shared/system-config.yml#Session_Settings

## Rules & Standards

### Evidence-Based Standards

@include shared/superclaude-core.yml#Evidence_Based_Standards

### Standards

@include shared/superclaude-core.yml#Standards

### Severity System

@include commands/shared/quality-patterns.yml#Severity_Levels
@include commands/shared/quality-patterns.yml#Validation_Sequence

### Smart Defaults & Handling

@include shared/superclaude-rules.yml#Smart_Defaults

### Ambiguity Resolution

@include shared/superclaude-rules.yml#Ambiguity_Resolution

### Development Practices

@include shared/superclaude-rules.yml#Development_Practices

### Code Generation

@include shared/superclaude-rules.yml#Code_Generation

### Session Awareness

@include shared/superclaude-rules.yml#Session_Awareness

### Action & Command Efficiency

@include shared/superclaude-rules.yml#Action_Command_Efficiency

### Project Quality

@include shared/superclaude-rules.yml#Project_Quality

### Security Standards

@include shared/superclaude-rules.yml#Security_Standards
@include commands/shared/security-patterns.yml#OWASP_Top_10
@include commands/shared/security-patterns.yml#Validation_Levels

### Efficiency Management

@include shared/superclaude-rules.yml#Efficiency_Management

### Operations Standards

@include shared/superclaude-rules.yml#Operations_Standards

## Model Context Protocol (MCP) Integration

### MCP Architecture

@include commands/shared/flag-inheritance.yml#Universal Flags (All Commands)
@include commands/shared/execution-patterns.yml#Servers

### Server Capabilities Extended

@include shared/superclaude-mcp.yml#Server_Capabilities_Extended

### Token Economics

@include shared/superclaude-mcp.yml#Token_Economics

### Workflows

@include shared/superclaude-mcp.yml#Workflows

### Quality Control

@include shared/superclaude-mcp.yml#Quality_Control

### Command Integration

@include shared/superclaude-mcp.yml#Command_Integration

### Error Recovery

@include shared/superclaude-mcp.yml#Error_Recovery

### Best Practices

@include shared/superclaude-mcp.yml#Best_Practices

### Session Management

@include shared/superclaude-mcp.yml#Session_Management

## Cognitive Archetypes (Personas)

### Persona Architecture

@include commands/shared/flag-inheritance.yml#Universal Flags (All Commands)

### All Personas

@include shared/superclaude-personas.yml#All_Personas

### Collaboration Patterns

@include shared/superclaude-personas.yml#Collaboration_Patterns

### Intelligent Activation Patterns

@include shared/superclaude-personas.yml#Intelligent_Activation_Patterns

### Command Specialization

@include shared/superclaude-personas.yml#Command_Specialization

### Integration Examples

@include shared/superclaude-personas.yml#Integration_Examples

### Advanced Features

@include shared/superclaude-personas.yml#Advanced_Features

### MCP + Persona Integration

@include shared/superclaude-personas.yml#MCP_Persona_Integration

---

_SuperClaude v2.0.1 | Development framework | Evidence-based methodology | Advanced Claude Code configuration_

````markdown
ruleIQ Frontend Development Guide

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
````

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
--primary-navy: #17255a; /* Deep navy blue - primary brand color */
--primary-gold: #cb963e; /* Gold - accent color for CTAs and highlights */
--primary-cyan: #34fef7; /* Bright cyan - energetic accent */

/* Neutral Colors */
--neutral-light: #d0d5e3; /* Light gray - backgrounds, borders */
--neutral-medium: #c2c2c2; /* Medium gray - secondary text, dividers */

/* Extended Palette (derived from primary) */
--navy-dark: #0f1938; /* Darker variant for headers */
--navy-light: #2b3a6a; /* Lighter variant for hover states */
--gold-dark: #a67a2e; /* Darker gold for hover states */
--gold-light: #e0b567; /* Lighter gold for backgrounds */

/* Semantic Colors */
--success: #28a745; /* Keep existing for consistency */
--warning: #cb963e; /* Use gold for warnings */
--error: #dc3545; /* Keep existing for consistency */
--info: #34fef7; /* Use cyan for info states */

/* Text Colors */
--text-primary: #17255a; /* Primary text in navy */
--text-secondary: #6b7280; /* Secondary text */
--text-on-dark: #ffffff; /* Text on dark backgrounds */
--text-on-gold: #17255a; /* Navy text on gold backgrounds */

/* Background Colors */
--bg-primary: #ffffff; /* White backgrounds */
--bg-secondary: #f8f9fb; /* Slight blue tint */
--bg-tertiary: #d0d5e3; /* Light gray sections */
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