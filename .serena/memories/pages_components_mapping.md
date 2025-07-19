# Pages and Components Mapping

## Overview
Comprehensive mapping of all frontend pages and their component dependencies in the ruleIQ application.

## Page Categories

### Authentication Pages (4 pages)
- `/login`, `/signup`, `/register`, `/signup-traditional`
- **Key Components**: SecurityBadges, TrustSignals, authentication forms
- **Common UI**: Alert, Button, Card, Input, Label, Checkbox
- **Icons**: Shield, Eye, EyeOff, Loader2, AlertCircle, UserPlus

### Dashboard Pages (3 pages)
- `/dashboard`, `/dashboard-custom`, `/analytics`
- **Key Components**: DashboardHeader, EnhancedStatsCard, DataTable, QuickActionsWidget, AIInsightsWidget, ComplianceScoreWidget
- **Charts**: ComplianceTrendChart, FrameworkBreakdownChart, ActivityHeatmap, RiskMatrix, TaskProgressChart
- **UI**: Alert, Button, Card, Skeleton

### Assessment Pages (4 pages)
- `/assessments`, `/assessments/new`, `/assessments/[id]`, `/assessments/[id]/results`
- **Key Components**: AssessmentWizard, QuestionRenderer, ProgressTracker, ComplianceGauge, RadarChart, GapAnalysisCard
- **Specialized**: FrameworkSelector, RecommendationCard, ActionItemsList
- **Icons**: ClipboardCheck, Shield, Clock, CheckCircle, AlertCircle

### Evidence Pages (2 pages)
- `/evidence`, `/evidence/upload`
- **Key Components**: EvidenceCard, FilterSidebar, BulkActionsBar, FileUploader, FilePreviewCard
- **UI**: Badge, Checkbox, DropdownMenu, Select
- **Icons**: Search, Upload, FileText, Download, Trash2, Eye

### Policy Pages (2 pages)
- `/policies`, `/policies/new`
- **Key Components**: Policy cards, SelectionCard, GenerationProgress
- **UI**: Badge, Button, Card, Stepper, Textarea
- **Icons**: Shield, Plus, Edit, Eye, FileText, Download

### Chat Pages (1 page)
- `/chat`
- **Key Components**: ChatHeader, ChatInput, ChatMessage, ConversationSidebar, TypingIndicator
- **UI**: Alert, Button, Skeleton
- **Icons**: Plus, MessageSquare

### Settings Pages (3 pages)
- `/settings/team`, `/settings/integrations`, `/settings/billing`
- **Key Components**: TeamMembersTable, IntegrationCard, PricingCard, CheckoutForm
- **UI**: Table, Dialog, Button, Card, Badge
- **Icons**: Users, Plug, payment icons

### Reports Pages (1 page)
- `/reports`
- **Key Components**: Report cards, data tables
- **UI**: Card, Button, Table, DataTable
- **Icons**: BarChart3, FileText, Download

## Universal Components (Used Across All Pages)

### Navigation
- **AppSidebar**: All dashboard pages
- **TopNavigation**: All dashboard pages  
- **BreadcrumbNav**: Selected pages
- **MobileNav**: Mobile responsive

### Common Patterns
- **Data Tables**: DataTable + columns + pagination + filters
- **Form Handling**: Form + Input + Button + validation
- **Loading States**: Skeleton + LoadingSpinner + PageLoader
- **Error Handling**: Alert + ErrorBoundary
- **Modal Dialogs**: Dialog + AlertDialog + Sheet

## Migration Priority for Theme Update

### High Priority (Core Infrastructure)
1. **Navigation Components**: AppSidebar, TopNavigation
2. **Basic UI**: Button, Card, Input, Alert
3. **Typography**: All text components

### Medium Priority (Feature Components)
1. **Dashboard**: Charts, widgets, data tables
2. **Forms**: All form components and validation
3. **Authentication**: Login/signup flows

### Low Priority (Specialized)
1. **Demo Pages**: Component showcases, testing pages
2. **Advanced Features**: Complex charts, specialized widgets

## Component Dependencies
- **Most Used**: Button (all pages), Card (all pages), Alert (error handling)
- **Charts**: Heavy usage in dashboard and analytics
- **Forms**: Authentication, settings, assessment creation
- **Tables**: Assessments, evidence, team management, reports