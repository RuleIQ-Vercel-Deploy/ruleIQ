# Policy Creation Page Specification

## Overview
**Route:** `/policies/new`  
**Status:** 🔴 NOT IMPLEMENTED  
**Priority:** HIGH - Core functionality missing  
**API Ready:** ✅ `generatePolicy` endpoint exists  

## Page Layout

### Header Section
```
[← Back to Policies]                           [Save Draft] [Preview] [Submit for Review]

# Create New Policy
Choose how you'd like to create your compliance policy
```

### Creation Method Selection (Step 1)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  How would you like to create your policy?                     │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │      🤖      │  │      ✍️      │  │      📤      │        │
│  │ AI Generate  │  │    Manual    │  │    Import    │        │
│  │              │  │              │  │              │        │
│  │ Use AI to    │  │ Start from   │  │ Upload an    │        │
│  │ generate a   │  │ a blank      │  │ existing     │        │
│  │ policy based │  │ template     │  │ policy       │        │
│  │ on your      │  │              │  │ document     │        │
│  │ framework    │  │              │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### AI Generation Flow (Step 2 - If AI Selected)

```
┌─────────────────────────────────────────────────────────────────┐
│ Select Compliance Framework                                     │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 🔍 Search frameworks...                                  │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ Popular Frameworks:                                            │
│ [ ] GDPR - General Data Protection Regulation                  │
│ [ ] ISO 27001 - Information Security Management                │
│ [ ] SOC 2 - Service Organization Control 2                     │
│ [ ] HIPAA - Health Insurance Portability Act                   │
│ [ ] PCI DSS - Payment Card Industry Data Security              │
│                                                                 │
│ Policy Type:                                                   │
│ (•) Comprehensive - Full detailed policy with all sections     │
│ ( ) Basic - Simplified version for small businesses            │
│ ( ) Custom - Specify your own requirements                     │
│                                                                 │
│ [Custom Requirements (if Custom selected)]                     │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ Enter specific requirements...                          │   │
│ │                                                         │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                              [Cancel] [Generate Policy →]       │
└─────────────────────────────────────────────────────────────────┘
```

### Policy Editor (Step 3)

```
┌─────────────────────────────────────────────────────────────────┐
│ Policy Details                                    [AI Enhance 🪄]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Title: [Data Protection and Privacy Policy                  ]  │
│                                                                 │
│ Framework: GDPR    Version: [1.0]    Status: [Draft      ▼]   │
│                                                                 │
│ Effective Date: [2024-09-15]    Review Date: [2025-09-15]     │
│                                                                 │
│ Owner: [Compliance Team        ▼]   Approver: [CTO        ▼]  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Sections                                      [+ Add Section]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ▼ 1. Introduction                              [⚙️] [🗑️]       │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ This policy outlines our commitment to protecting        │   │
│ │ personal data in accordance with GDPR requirements...    │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ▼ 2. Scope                                     [⚙️] [🗑️]       │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ This policy applies to all employees, contractors, and   │   │
│ │ third parties who process personal data...               │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ▼ 3. Data Protection Principles                [⚙️] [🗑️]       │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ • Lawfulness, fairness, and transparency                 │   │
│ │ • Purpose limitation                                     │   │
│ │ • Data minimization                                      │   │
│ │ • Accuracy                                               │   │
│ │ • Storage limitation                                     │   │
│ │ • Integrity and confidentiality                          │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ▶ 4. Roles and Responsibilities                [⚙️] [🗑️]       │
│ ▶ 5. Data Subject Rights                       [⚙️] [🗑️]       │
│ ▶ 6. Data Breach Response                      [⚙️] [🗑️]       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Section Editor Modal (When editing a section)

```
┌─────────────────────────────────────────────────────────────────┐
│ Edit Section: Data Protection Principles              [X Close] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Section Title: [Data Protection Principles                  ]  │
│                                                                 │
│ Content:                                   [AI Suggestions 🤖]  │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ [B] [I] [U] | [🔗] [📋] [📝] | [H1] [H2] [H3] | [⚫][1.]│   │
│ ├─────────────────────────────────────────────────────────┤   │
│ │                                                         │   │
│ │ We adhere to the following data protection principles: │   │
│ │                                                         │   │
│ │ 1. **Lawfulness, fairness, and transparency**         │   │
│ │    Personal data shall be processed lawfully...        │   │
│ │                                                         │   │
│ │ 2. **Purpose limitation**                              │   │
│ │    Data collected for specified, explicit purposes...  │   │
│ │                                                         │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ Tags: [GDPR] [Data Protection] [+]                            │
│                                                                 │
│ □ Mark as Critical Section                                     │
│ □ Requires Legal Review                                        │
│                                                                 │
│                                     [Cancel] [Save Section]    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. Creation Method Cards
- **Type:** Interactive cards with hover effects
- **States:** Default, Hover (elevation + teal border), Selected (teal background)
- **Icons:** Lucide icons (Bot, PenTool, Upload)

### 2. Framework Selector
- **Type:** Searchable checkbox list
- **Features:** 
  - Fuzzy search
  - Popular frameworks pinned to top
  - Custom framework input option
  - Multiple selection support

### 3. Rich Text Editor
- **Library:** TipTap or Lexical
- **Features:**
  - Basic formatting (bold, italic, underline)
  - Headers (H1-H3)
  - Lists (ordered, unordered)
  - Links
  - Tables
  - Code blocks for technical policies
  - Auto-save every 30 seconds
  - Version history

### 4. AI Enhancement Panel
- **Trigger:** "AI Enhance 🪄" button
- **Options:**
  - Improve clarity
  - Add missing sections
  - Check compliance gaps
  - Simplify language
  - Generate summary

### 5. Status Management
- **States:** 
  - Draft (gray badge)
  - Under Review (yellow badge)
  - Approved (green badge)
  - Active (blue badge)
  - Archived (gray badge, strikethrough)

## API Integration

### Generate Policy
```typescript
// When user clicks "Generate Policy"
const generatePolicy = async () => {
  const response = await policyService.generatePolicy({
    framework_id: selectedFramework,
    policy_type: policyType, // 'comprehensive' | 'basic' | 'custom'
    custom_requirements: customRequirements // if custom
  });
  
  // Navigate to editor with generated content
  router.push(`/policies/edit/${response.id}`);
};
```

### Save Draft
```typescript
// Auto-save and manual save
const saveDraft = async () => {
  await policyService.updatePolicy(policyId, {
    title,
    content: sections,
    status: 'draft',
    metadata: {
      framework_id,
      effective_date,
      review_date,
      owner,
      approver
    }
  });
};
```

## Validation Rules

1. **Title:** Required, 5-200 characters
2. **Framework:** At least one must be selected
3. **Effective Date:** Cannot be in the past
4. **Review Date:** Must be after effective date
5. **Content:** At least 3 sections required
6. **Each Section:** Minimum 50 characters

## Error States

- **Generation Failed:** "Unable to generate policy. Please try again or create manually."
- **Save Failed:** "Failed to save changes. Your work has been preserved locally."
- **Network Error:** "Connection lost. Changes will sync when reconnected."

## Success States

- **Policy Generated:** "Policy successfully generated! Review and customize as needed."
- **Draft Saved:** "Draft saved successfully" (toast, 3 seconds)
- **Submitted for Review:** "Policy submitted for review. You'll be notified once approved."

## Mobile Responsiveness

- Creation method cards stack vertically
- Editor switches to full-screen mode
- Section accordion for better navigation
- Floating action button for save/submit
- Simplified toolbar in rich text editor

## Accessibility

- All form fields have labels
- Error messages linked to fields
- Keyboard navigation through all elements
- Screen reader announcements for status changes
- High contrast mode support

## Performance Considerations

- Lazy load rich text editor
- Debounced auto-save (30 seconds)
- Virtual scrolling for long policies
- Optimistic UI updates
- Offline support with local storage

---

**Priority Implementation Steps:**
1. Create route and basic page structure
2. Implement creation method selection
3. Add framework selector with API integration
4. Build rich text editor with sections
5. Add save/submit functionality
6. Implement AI enhancement features
7. Add validation and error handling
8. Mobile optimization
9. Accessibility audit