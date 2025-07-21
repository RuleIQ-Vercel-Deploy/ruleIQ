# Complete Frontend Pages Directory

This document contains all 37 frontend pages available in the ruleIQ application.

## 🎯 Migration Status Key

- ✅ = Fully migrated to new teal theme
- 🔄 = Partially migrated (some components updated)
- ❌ = Still using old dark theme
- 🎨 = Design system showcase pages

---

## 📋 All Pages List (37 Total)

### 🔐 Authentication Pages (4 pages)

1. **Login Page** - `/login` 🔄
   - http://localhost:3000/login
   - Status: Partially migrated with teal accents

2. **Signup Page** - `/signup` 🔄
   - http://localhost:3000/signup
   - Status: Partially migrated

3. **Register Page** - `/register` 🔄
   - http://localhost:3000/register
   - Status: Partially migrated

4. **Traditional Signup** - `/signup-traditional` 🔄
   - http://localhost:3000/signup-traditional
   - Status: Partially migrated

### 📊 Dashboard & Analytics (3 pages)

5. **Main Dashboard** - `/dashboard` 🔄
   - http://localhost:3000/dashboard
   - Status: Core components updated, charts need migration

6. **Custom Dashboard** - `/dashboard-custom` 🔄
   - http://localhost:3000/dashboard-custom
   - Status: Similar to main dashboard

7. **Analytics Page** - `/analytics` 🔄
   - http://localhost:3000/analytics
   - Status: Charts and data viz need color updates

### 📋 Assessment Pages (4 pages)

8. **Assessments List** - `/assessments` 🔄
   - http://localhost:3000/assessments
   - Status: DataTable partially updated

9. **New Assessment** - `/assessments/new` 🔄
   - http://localhost:3000/assessments/new
   - Status: Wizard needs styling updates

10. **Assessment Detail** - `/assessments/[id]` 🔄
    - http://localhost:3000/assessments/123 (example)
    - Status: Question renderer needs updates

11. **Assessment Results** - `/assessments/[id]/results` 🔄
    - http://localhost:3000/assessments/123/results (example)
    - Status: Charts and gauges need color migration

### 📄 Evidence & Document Management (1 page)

12. **Evidence Management** - `/evidence` 🔄
    - http://localhost:3000/evidence
    - Status: Cards and filters partially updated

### 📝 Policy Management (2 pages)

13. **Policies List** - `/policies` 🔄
    - http://localhost:3000/policies
    - Status: Policy cards need styling

14. **New Policy** - `/policies/new` 🔄
    - http://localhost:3000/policies/new
    - Status: Policy wizard needs updates

### ⚙️ Settings Pages (3 pages)

15. **Team Management** - `/settings/team` 🔄
    - http://localhost:3000/settings/team
    - Status: Tables and dialogs partially updated

16. **Integrations** - `/settings/integrations` 🔄
    - http://localhost:3000/settings/integrations
    - Status: Integration cards need styling

17. **Billing Settings** - `/settings/billing` 🔄
    - http://localhost:3000/settings/billing
    - Status: Pricing cards need updates

### 💬 Communication & Reports (2 pages)

18. **Chat Interface** - `/chat` 🔄
    - http://localhost:3000/chat
    - Status: Message styling needs updates

19. **Reports Page** - `/reports` 🔄
    - http://localhost:3000/reports
    - Status: Report cards and tables need styling

### 🎨 Design System & Component Showcases (3 pages)

20. **Design System** - `/design-system` 🎨 ✅
    - http://localhost:3000/design-system
    - Status: Fully shows new teal theme components

21. **Components Showcase** - `/components` 🎨 ✅
    - http://localhost:3000/components
    - Status: All components with new theme

22. **Forms Showcase** - `/forms` 🎨 ✅
    - http://localhost:3000/forms
    - Status: Form components with new styling

### 🔧 Demo & Testing Pages (7 pages)

23. **Loading States Demo** - `/loading-states` 🎨
    - http://localhost:3000/loading-states
    - Status: Loading animations showcase

24. **File Upload Demo** - `/demo/file-upload` 🎨
    - http://localhost:3000/demo/file-upload
    - Status: Upload component demo

25. **Error Boundary Demo** - `/demo/error-boundary` 🎨
    - http://localhost:3000/demo/error-boundary
    - Status: Error handling showcase

26. **Loading States (Demo)** - `/demo/loading-states` 🎨
    - http://localhost:3000/demo/loading-states
    - Status: Alternative loading showcase

27. **Modals Demo** - `/modals` 🎨
    - http://localhost:3000/modals
    - Status: Modal component showcase

28. **Quick Actions Test** - `/test-quick-actions` 🎨
    - http://localhost:3000/test-quick-actions
    - Status: Quick actions widget test

29. **Compliance Wizard** - `/compliance-wizard` 🔄
    - http://localhost:3000/compliance-wizard
    - Status: Wizard flow testing

### 💼 Business & Commerce Pages (4 pages)

30. **Business Profile** - `/business-profile` 🔄
    - http://localhost:3000/business-profile
    - Status: Profile forms need updates

31. **Pricing Page** - `/pricing` 🔄
    - http://localhost:3000/pricing
    - Status: Pricing cards need teal colors

32. **Checkout Flow** - `/checkout` 🔄
    - http://localhost:3000/checkout
    - Status: Payment forms need styling

33. **Data Export Demo** - `/data-export-demo` 🔄
    - http://localhost:3000/data-export-demo
    - Status: Export functionality demo

### 🔍 Monitoring & Development (3 pages)

34. **Error Testing** - `/monitoring/test-error` ❌
    - http://localhost:3000/monitoring/test-error
    - Status: Error monitoring test page

35. **Sentry Monitoring** - `/monitoring/sentry` ❌
    - http://localhost:3000/monitoring/sentry
    - Status: Sentry integration page

36. **Editor Page** - `/editor` 🔄
    - http://localhost:3000/editor
    - Status: Code editor interface

### 🏠 Public Pages (1 page)

37. **Landing Page** - `/` 🔄
    - http://localhost:3000/
    - Status: Hero section and features partially migrated

---

## 📊 Migration Summary

- **Total Pages**: 37
- **Fully Migrated**: ~3 pages (design system showcases)
- **Partially Migrated**: ~30 pages
- **Not Started**: ~4 pages

## 🚀 Quick Test Commands

```bash
# View design system (best to see new theme)
open http://localhost:3000/design-system

# View all auth pages
open http://localhost:3000/login
open http://localhost:3000/signup
open http://localhost:3000/register

# View main app pages
open http://localhost:3000/dashboard
open http://localhost:3000/assessments
open http://localhost:3000/policies
```

## 📝 Notes

- Pages marked with 🎨 are primarily for showcasing components and design patterns
- The `[id]` in URLs should be replaced with actual IDs (e.g., `/assessments/123`)
- All pages require the dev server running on port 3000
- Feature flag `NEXT_PUBLIC_USE_NEW_THEME=true` must be set in `.env.local`

---

_Last Updated: January 2025_
_Total Pages: 37_
