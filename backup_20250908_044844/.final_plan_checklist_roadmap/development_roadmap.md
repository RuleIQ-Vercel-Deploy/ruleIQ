# ruleIQ Frontend Development Plan for AI Coding Agents

## 1. Core Project Foundation Documents

These documents must be included in **EVERY** prompt sent to AI coding agents to ensure consistency and adherence to project specifications.

### 1.1 Project Identity & Technical Stack Document

```markdown
# ruleIQ Project Foundation

## Project Identity
- **Name**: ruleIQ (ComplianceGPT)
- **Type**: AI-powered compliance automation platform for UK SMBs
- **Domain**: Regulatory compliance, risk management, evidence management

## Technical Stack (Non-negotiable)
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand (client state)
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod validation
- **Animations**: Framer Motion
- **Real-time**: Native WebSocket API
- **File Upload**: react-dropzone
- **Testing**: Vitest (unit), @testing-library/react (component), Playwright (E2E)

## Code Standards
- All components must be TypeScript with proper interfaces
- Use shadcn/ui components as base (no custom component libraries)
- Follow 8pt grid system for spacing
- Implement mobile-first responsive design
- Ensure WCAG 2.2 AA compliance
- Use semantic HTML structure
- Implement proper error boundaries and loading states
```

### 1.2 Design System Document

```markdown
# ruleIQ Design System

## Brand Attributes
- **Trustworthy & Secure**: Professional, reliable, fortress-like protection
- **Intelligent & Precise**: Clean, data-forward, analytical rigor
- **Professional & Authoritative**: Serious, expert-level credibility
- **Empowering & Clear**: Simplifies complexity, user mastery

## Color Palette
- **Primary Navy**: #103766 (primary-900)
- **Primary Teal**: #0B4F6C (primary-700)
- **Accent Orange**: #F28C28 (accent-600) - Use sparingly (≤10%)
- **Success**: #28A745
- **Warning**: #FFC107
- **Error**: #DC3545
- **Neutrals**: #333333 (text), #777777 (secondary), #F2F2F2 (bg)

## Typography
- **Font**: Inter (primary) or Roboto (fallback)
- **H1**: 32px Bold
- **H2**: 24px Bold
- **H3**: 18px Semi-Bold
- **Body**: 14px Regular
- **Small**: 12px Regular

## Spacing
- Use 8px grid system (4px half-step when necessary)
- All margins, paddings, gaps must be multiples of 8px

## Icons
- Use Lucide icon set exclusively
- Monochromatic line style only
```

### 1.3 User Persona Reference

```markdown
# ruleIQ Target User Personas

## Persona A: "Alex" - The Analytical Professional
- **Traits**: Data-driven, tech-savvy, efficiency-oriented
- **Needs**: Customizable dashboards, advanced filtering, data export, keyboard shortcuts
- **UI Preferences**: High information density, multiple data views, API access

## Persona B: "Ben" - The Cautious Professional  
- **Traits**: Risk-averse, meticulous, procedure-oriented
- **Needs**: Guided workflows, auto-save, confirmations, help documentation
- **UI Preferences**: Step-by-step wizards, progress indicators, trust signals

## Persona C: "Catherine" - The Principled Professional
- **Traits**: Ethics-focused, transparency-driven, accountability-oriented
- **Needs**: Immutable audit trails, version history, compliance certificates
- **UI Preferences**: Clear status indicators, user attribution, formal outputs

## Design Decisions
- Every feature must consider all three personas
- Default to "Ben" (cautious) for critical actions
- Provide customization for "Alex" (analytical)
- Ensure transparency for "Catherine" (principled)
```

### 1.4 API Integration Map

```markdown
# ruleIQ API Endpoints Reference

## Authentication
- POST /api/auth/register
- POST /api/auth/token
- POST /api/auth/login
- POST /api/auth/refresh
- GET /api/users/me

## Core Features
- Business Profiles: /api/business-profiles/*
- Assessments: /api/assessments/*
- Evidence: /api/evidence/*
- Policies: /api/policies/*
- Chat: /api/chat/*
- Integrations: /api/integrations/*

## Response Format
Success: { data: {...}, message: "Success", status: 200 }
Error: { detail: "Error message", status: 400 }
Paginated: { items: [...], total: 100, page: 1, size: 20 }

## Authentication
- Use Bearer token in Authorization header
- Store tokens securely (httpOnly cookies preferred)
- Implement token refresh logic
```

## 2. Staged Development Roadmap

### Phase 1: Foundation & Authentication (Week 1)
**Priority: CRITICAL**

#### Stage 1.1: Project Setup & Configuration
- Initialize Next.js 15 with TypeScript
- Configure Tailwind CSS with custom theme
- Set up shadcn/ui components
- Configure ESLint, Prettier, and Git hooks
- Set up folder structure per specifications

#### Stage 1.2: Authentication System
- Implement login/register pages with forms
- Create authentication context with Zustand
- Set up protected route middleware
- Implement token management and refresh
- Create user session handling

#### Stage 1.3: Base Layouts & Navigation
- Create DashboardLayout with collapsible sidebar
- Implement responsive navigation
- Create loading states and error boundaries
- Set up toast notification system
- Implement breadcrumb navigation

### Phase 2: Business Profile & Dashboard (Week 1-2)
**Priority: HIGH**

#### Stage 2.1: Dashboard Implementation
- Create customizable dashboard grid
- Implement compliance score widget (gauge/donut)
- Build activity feed component
- Create pending tasks widget
- Implement quick actions panel

#### Stage 2.2: Business Profile Wizard
- Create multi-step form wizard component
- Implement company information step
- Build compliance questionnaire step
- Create integration setup step
- Add progress saving and validation

### Phase 3: Assessment System (Week 2-3)
**Priority: HIGH**

#### Stage 3.1: Framework Selection
- Build framework comparison interface
- Create AI recommendation component
- Implement framework cards with details
- Add selection persistence

#### Stage 3.2: Assessment Wizard
- Create dynamic questionnaire renderer
- Implement question type components
- Build progress tracking system
- Add save/resume functionality
- Create response validation

#### Stage 3.3: Results & Reporting
- Build score visualization components
- Create gap analysis display
- Implement export functionality
- Add report generation UI

### Phase 4: Evidence Management (Week 3-4)
**Priority: HIGH**

#### Stage 4.1: Evidence Upload
- Implement drag-drop file upload
- Create bulk upload interface
- Add file validation and preview
- Build upload progress tracking

#### Stage 4.2: Evidence Library
- Create data table with filtering
- Implement grid/list view toggle
- Add bulk action capabilities
- Create evidence detail modal

#### Stage 4.3: AI Processing & Approval
- Build AI classification display
- Create quality score visualization
- Implement approval workflow UI
- Add control mapping interface

### Phase 5: AI Features (Week 4)
**Priority: MEDIUM-HIGH**

#### Stage 5.1: Policy Generator
- Create policy generation wizard
- Build template selection interface
- Implement customization options
- Add generation progress display

#### Stage 5.2: Chat Assistant
- Build chat message interface
- Implement real-time updates
- Create typing indicators
- Add follow-up suggestions

### Phase 6: Advanced Features (Week 5)
**Priority: MEDIUM**

#### Stage 6.1: Implementation Planning
- Create timeline/Gantt chart views
- Build task management interface
- Implement resource planning

#### Stage 6.2: Advanced Reporting
- Create report builder interface
- Implement analytics dashboard
- Build export center

### Phase 7: Polish & Optimization (Week 5-6)
**Priority: LOW-MEDIUM**

#### Stage 7.1: Performance Optimization
- Implement code splitting
- Add image optimization
- Configure caching strategies

#### Stage 7.2: Testing & Accessibility
- Write comprehensive tests
- Conduct accessibility audit
- Fix identified issues

