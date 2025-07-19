# Descriptive Variable Names Best Practices

## Principle
Always use descriptive, meaningful variable names that clearly indicate their purpose, content, or behavior. Avoid abbreviations, single letters, or ambiguous terms.

## Examples

### Good Descriptive Names
```typescript
// Clear purpose and scope
const userAuthenticationToken = getAuthToken();
const complianceAssessmentResults = await fetchAssessmentData();
const navigationMenuItems = generateMenuStructure();
const primaryBrandColorTeal = '#2C7A7B';
const maximumFileUploadSizeInBytes = 10 * 1024 * 1024;

// State management
const [isUserDataLoading, setIsUserDataLoading] = useState(false);
const [selectedComplianceFramework, setSelectedComplianceFramework] = useState(null);
const [assessmentWizardCurrentStep, setAssessmentWizardCurrentStep] = useState(1);

// Component props
interface UserProfileCardProps {
  currentUserData: User;
  onUserProfileUpdate: (updatedUserData: User) => void;
  shouldShowEditButton: boolean;
  profileImageUploadHandler: (imageFile: File) => Promise<void>;
}

// Function names
function validateUserInputAndShowErrors(inputValue: string): ValidationResult {
  // Implementation
}

function generateComplianceReportForFramework(frameworkId: string): Promise<Report> {
  // Implementation
}
```

### Poor Names to Avoid
```typescript
// Avoid these patterns
const data = getData(); // What kind of data?
const temp = calculateSomething(); // Temporary what?
const flag = true; // Flag for what?
const i = 0; // Use descriptive loop variables
const btn = document.querySelector('button'); // Button for what?
const arr = []; // Array of what?
const obj = {}; // Object representing what?
const res = await fetch(); // Response from what?
const fn = () => {}; // Function doing what?
```

## Context-Specific Guidelines

### React Components
```typescript
// Component names
const ComplianceAssessmentWizard = () => {};
const UserProfileEditForm = () => {};
const NavigationSidebarMenu = () => {};

// Props and state
const [complianceScoreValue, setComplianceScoreValue] = useState(0);
const [isAssessmentDataLoading, setIsAssessmentDataLoading] = useState(false);
const [userSelectedFrameworks, setUserSelectedFrameworks] = useState([]);
```

### API and Data Handling
```typescript
// Service functions
async function fetchUserComplianceAssessments(userId: string): Promise<Assessment[]> {}
async function submitComplianceFrameworkAssessment(assessmentData: AssessmentSubmission): Promise<void> {}
async function uploadEvidenceDocumentFile(evidenceFile: File, frameworkId: string): Promise<UploadResult> {}

// Data structures
interface ComplianceFrameworkAssessmentResult {
  frameworkIdentifier: string;
  overallComplianceScore: number;
  individualRequirementScores: RequirementScore[];
  assessmentCompletionTimestamp: Date;
  recommendedImprovementActions: RecommendationItem[];
}
```

### CSS and Styling
```css
/* Descriptive CSS variable names */
:root {
  --primary-brand-color-teal: #2C7A7B;
  --secondary-text-color-gray: #6B7280;
  --button-hover-background-color: #285E61;
  --form-input-border-color-default: #E5E7EB;
  --form-input-border-color-focused: #2C7A7B;
  --navigation-sidebar-background-color: #FFFFFF;
  --compliance-score-gauge-success-color: #10B981;
}

/* Descriptive class names */
.compliance-assessment-wizard-container {}
.user-profile-edit-form-section {}
.navigation-sidebar-menu-item-active {}
.evidence-upload-dropzone-highlighted {}
```

## Benefits
1. **Self-Documenting Code**: Code explains itself without comments
2. **Easier Debugging**: Clear variable names help identify issues quickly
3. **Better Collaboration**: Team members understand code purpose immediately
4. **Reduced Cognitive Load**: No mental mapping of abbreviations to meanings
5. **Maintenance**: Future developers (including yourself) understand code faster

## When to Use Shorter Names
- **Well-established conventions**: `id`, `url`, `api`
- **Very limited scope**: Loop variables in simple, short loops
- **Standard abbreviations**: `html`, `css`, `json`, `http`
- **Mathematical contexts**: `x`, `y` for coordinates, `i`, `j` for indices in mathematical operations

## Team Agreement
- Establish team conventions for common patterns
- Use linting rules to enforce naming standards
- Document domain-specific abbreviations if unavoidable
- Regular code reviews to catch and improve naming