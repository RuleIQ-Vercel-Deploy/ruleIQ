# TestSprite Frontend Initialization - Automated Process

## Complete TestSprite Setup Commands
These commands should be run in sequence to avoid repetitive manual steps:

### 1. Bootstrap TestSprite
```bash
# Initialize TestSprite for frontend testing
testsprite_bootstrap_tests(
  localPort=3000,
  projectPath="/home/omar/Documents/ruleIQ", 
  testScope="codebase",
  type="frontend"
)
```

### 2. Generate Code Summary (AUTOMATED)
- TestSprite automatically requests code summary generation
- Creates `/home/omar/Documents/ruleIQ/testsprite_tests/code_summary.json`
- **IMPORTANT**: Use existing testsprite_tests directory, NOT tmp/

### 3. Generate PRD (AUTOMATED)
```bash
testsprite_generate_prd(projectPath="/home/omar/Documents/ruleIQ")
```

### 4. Generate Frontend Test Plan (AUTOMATED)
```bash  
testsprite_generate_frontend_test_plan(
  projectPath="/home/omar/Documents/ruleIQ",
  needLogin=true  # Always true for ruleIQ
)
```

### 5. Execute Tests (FINAL STEP)
```bash
testsprite_generate_code_and_execute(
  projectName="ruleIQ",
  projectPath="/home/omar/Documents/ruleIQ", 
  testIds=[],  # Empty = all tests
  additionalInstruction=""  # Usually empty
)
```

## Key Configuration Values
- **Local Port**: 3000 (frontend dev server)
- **Project Type**: frontend  
- **Test Scope**: codebase (not diff)
- **Need Login**: true (always for ruleIQ)
- **Project Name**: "ruleIQ" (root directory name)

## Code Summary Template (REFERENCE ONLY)
The code_summary.json should include these 13 core features:
1. Authentication System
2. Dashboard & Analytics  
3. Assessment Engine
4. Business Profile Management
5. Evidence Management
6. Policy Generation
7. AI Chat Interface
8. Team Management
9. UI Design System
10. Navigation & Layout
11. Integrations System
12. Payment & Billing
13. Testing Infrastructure

## Previous Issues Found
- Authentication token handling errors
- React duplicate key errors in assessments
- Missing grid.svg resource
- Performance optimization needs

## One-Command Future Setup
To avoid repetition, run these TestSprite tools in sequence without manual intervention between steps.