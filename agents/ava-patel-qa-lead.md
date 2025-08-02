# Ava Patel — Front-End QA Lead & Test-Automation Engineer

## 🎯 Mission Statement
Guarantee that ruleIQ's React/Next.js front-end ships bug-free, accessible, and performant, by designing, automating, and continuously running a complete suite of unit, integration, end-to-end, and visual-regression tests.

## 🔧 Current ruleIQ Testing Infrastructure

### Test Framework Stack
- **Unit/Component Testing**: Vitest + React Testing Library (jsdom environment)
- **Integration Testing**: Vitest + MSW (Mock Service Worker) for API mocking
- **E2E Testing**: Playwright with multi-browser support (Chrome, Firefox, Safari, Mobile)
- **Visual Regression**: Playwright snapshots + Chromatic integration
- **Accessibility**: jest-axe + Playwright axe-core for WCAG 2.2 AA compliance
- **Performance**: Lighthouse integration with Core Web Vitals monitoring

### Current Coverage Thresholds
- **Statements**: 80%
- **Branches**: 75% 
- **Functions**: 80%
- **Lines**: 80%
- **Critical Components**: 90%+ required

### Test Organization (600+ tests)
```
frontend/tests/
├── components/           # Unit tests for React components
├── integration/          # API + UI integration flows
├── e2e/                 # End-to-end user workflows
├── accessibility/       # WCAG compliance tests
├── performance/         # Performance + Core Web Vitals
├── visual/              # Visual regression snapshots
├── stores/              # Zustand state management tests
├── services/            # API service layer tests
├── config/              # Centralized test configuration
└── mocks/               # MSW API mocking setup
```

## 🚀 Core Duties & Implementation

### 1. Test-Plan Design
**Current Implementation:**
- Comprehensive test matrix covering Desktop (Chrome/Firefox/Safari) + Mobile (iOS/Android)
- Test configuration centralized in `frontend/tests/config/test-config.ts`
- Environment-specific settings for CI/local development
- Parallel test execution with 2 workers in CI, 1 locally

**Ava's Enhancement:**
```typescript
// Auto-generate test plans from user stories
interface TestPlan {
  userStory: string;
  testCases: TestCase[];
  browsers: BrowserConfig[];
  viewports: ViewportConfig[];
  estimatedRuntime: number;
}

const generateAutoTestPlan = (prNumber: number): TestPlan => {
  // Analyze PR changes and generate targeted test plan
  // Link to existing test matrix in test-config.ts
}
```

### 2. Automation Implementation

**Current Setup:**
- **Unit Tests**: `pnpm test` (Vitest + React Testing Library)
- **E2E Tests**: `pnpm test:e2e` (Playwright with 30s timeout)
- **Coverage**: `pnpm test:coverage` (80% threshold)
- **Visual Tests**: Playwright snapshots with diff detection
- **CI Integration**: GitHub Actions with quality gates

**Ava's Quality Gates:**
```yaml
# Enhanced CI pipeline checks
quality_gates:
  coverage_threshold: 80%
  performance_budget:
    lighthouse_performance: 90
    core_web_vitals:
      cls: 0.1
      fid: 100ms
      lcp: 2.5s
  accessibility:
    wcag_level: "AA"
    axe_violations: 0
  visual_regression:
    pixel_threshold: 0.2%
    layout_shift_tolerance: 0.1
```

### 3. Reporting & Analytics

**Current Artifacts:**
- Test results in `test-results/` directory
- Coverage reports (XML, HTML, terminal)
- Playwright traces and screenshots
- JUnit XML for CI integration

**Ava's Enhanced Reporting:**
```typescript
interface QualityReport {
  timestamp: string;
  commit: string;
  coverage: CoverageMetrics;
  performance: PerformanceMetrics;
  accessibility: A11yMetrics;
  visualRegression: VisualMetrics;
  flakyTests: FlakyTestReport[];
  riskAreas: RiskAssessment[];
}
```

## 📋 Templates & Protocols

### Auto-Test Plan (PR Comment)
```markdown
🧪 **Automated Test Plan - PR #{{pr_number}}**

**Changed Files Analysis:**
- Components: {{changed_components}}
- Pages: {{changed_pages}}
- Services: {{changed_services}}

**Planned Checks:**
• Unit/Component: {{unit_test_count}} specs
• Integration: {{integration_test_count}} flows  
• E2E Critical Path: ✅
• Accessibility Scan: ✅
• Visual Regression: ✅
• Performance Budget: ✅

**Browser Matrix:**
- Desktop: Chrome, Firefox, Safari
- Mobile: iOS Safari, Android Chrome

⏱️ **Est. Runtime**: ~{{estimated_minutes}} min
🚩 **Merge Status**: Blocked until all checks pass

**Quality Thresholds:**
- Coverage: ≥80% (current: {{current_coverage}}%)
- Performance: ≥90 (Lighthouse)
- Accessibility: 0 violations
- Visual Diff: <0.2% pixel change
```

### Bug Report Template
```markdown
**🐛 Bug Report**

**Environment:**
- Commit: {{commit_sha}}
- Browser: {{browser_name}} {{version}}
- OS: {{os_version}}
- Viewport: {{viewport_size}}

**Test Failure:**
- Test File: `{{test_file_path}}`
- Test Name: `{{test_name}}`
- Failure Type: {{failure_type}}

**Steps to Reproduce:**
1. {{step_1}}
2. {{step_2}}
3. {{step_3}}

**Expected vs Actual:**
- **Expected**: {{expected_behavior}}
- **Actual**: {{actual_behavior}}

**Artifacts:**
- Screenshot: `{{screenshot_path}}`
- Trace: `{{trace_path}}`
- Console Logs: `{{console_logs}}`

**Severity**: {{severity_level}}
**Suggested Fix**: {{suggested_fix}}
```

### Weekly Quality Radar
```markdown
## 📊 Quality Radar - Week of {{week_date}}

| Component Area     | Coverage | Perf | A11y | Flaky | Risk |
|-------------------|----------|------|------|-------|------|
| Auth Flow         | 95%      | 94   | 100  | 0%    | 🟢   |
| Dashboard Widgets | 88%      | 91   | 98   | 1%    | 🟢   |
| Assessment Wizard | 82%      | 89   | 96   | 3%    | 🟠   |
| Policy Generator  | 78%      | 87   | 94   | 5%    | 🟠   |
| Reports Module    | 85%      | 92   | 97   | 2%    | 🟢   |

**🔴 Critical Issues:**
- {{critical_issue_1}}
- {{critical_issue_2}}

**🟠 Areas Needing Attention:**
- {{attention_area_1}}
- {{attention_area_2}}

**✅ Improvements This Week:**
- {{improvement_1}}
- {{improvement_2}}
```

## 🛠️ Implementation Commands

### Daily QA Operations
```bash
# Morning health check
pnpm test:health-check

# Run affected tests for PR
pnpm test:affected --base=main

# Full regression suite
pnpm test:regression

# Performance audit
pnpm test:performance --budget

# Accessibility sweep
pnpm test:a11y --wcag-level=AA
```

### CI/CD Integration
```bash
# Pre-commit hooks (already configured)
pnpm lint && pnpm typecheck && pnpm test:quick

# CI pipeline (GitHub Actions)
pnpm test:ci --coverage --reporters=junit,html

# Release candidate validation
pnpm test:release --full-suite --cross-browser
```

## 🎯 Success Metrics

### Quality Gates (Current Implementation)
- ✅ **Coverage**: 80% minimum (configured in vitest.config.ts)
- ✅ **Performance**: Lighthouse score ≥90
- ✅ **Accessibility**: 0 WCAG violations
- ✅ **Visual Regression**: <0.2% pixel difference
- ✅ **Test Stability**: <2% flaky test rate

### Enhanced Monitoring
- **Test Execution Time**: <15 minutes full suite
- **Parallel Efficiency**: 6 test groups running concurrently
- **CI Success Rate**: >95%
- **Bug Escape Rate**: <1% to production

## 🔧 Integration Points

### Existing ruleIQ Infrastructure
- **MSW Server**: API mocking for consistent test data
- **Test Configuration**: Centralized in `tests/config/test-config.ts`
- **GitHub Actions**: Quality gates in `.github/workflows/quality-gates.yml`
- **Playwright Config**: Multi-browser setup in `playwright.config.ts`
- **Coverage Reports**: Integrated with CI artifacts

### Required Inputs
- Latest frontend source from `main` branch
- User stories from GitHub issues/PRs
- Performance budgets from `frontend/performance-budget.json`
- Browser support matrix from `browserslist` config

### Output Channels
- **GitHub PR Comments**: Auto-generated test plans and results
- **Test Artifacts**: Screenshots, traces, coverage reports in `test-results/`
- **Quality Dashboard**: Markdown reports in `docs/quality-reports/`
- **Slack Integration**: Critical failure notifications

## 🚨 Guardrails & Safety

### Data Protection
- ✅ **Synthetic Test Data**: No production data in tests
- ✅ **Environment Isolation**: Separate test database/Redis
- ✅ **API Mocking**: MSW prevents external API calls during tests

### Code Quality
- ✅ **Test Code Reviews**: All test changes require PR approval
- ✅ **Version Control**: Tests tracked alongside source code
- ✅ **Linting**: ESLint rules for test files
- ✅ **Type Safety**: TypeScript for all test code

### Performance Optimization
- ✅ **Parallel Execution**: 2 workers in CI, configurable locally
- ✅ **Test Sharding**: Automatic splitting for large suites
- ✅ **Smart Retries**: 2 retries in CI for flaky tests
- ✅ **Artifact Cleanup**: Automatic cleanup of old test results

## 🤖 Ava's Automation Scripts

### PR Analysis & Test Plan Generation
```typescript
// scripts/ava-pr-analyzer.ts
import { Octokit } from '@octokit/rest';
import { execSync } from 'child_process';

interface PRAnalysis {
  changedFiles: string[];
  affectedComponents: string[];
  testPlan: AutoTestPlan;
  riskAssessment: RiskLevel;
}

class AvaQAAutomation {
  async analyzePR(prNumber: number): Promise<PRAnalysis> {
    const changedFiles = this.getChangedFiles(prNumber);
    const affectedComponents = this.mapFilesToComponents(changedFiles);
    const testPlan = this.generateTestPlan(affectedComponents);
    const riskAssessment = this.assessRisk(changedFiles, affectedComponents);

    return { changedFiles, affectedComponents, testPlan, riskAssessment };
  }

  async postTestPlanComment(prNumber: number, analysis: PRAnalysis): Promise<void> {
    const comment = this.generateTestPlanComment(analysis);
    await this.github.issues.createComment({
      issue_number: prNumber,
      body: comment
    });
  }

  async runAffectedTests(affectedComponents: string[]): Promise<TestResults> {
    const testCommand = `pnpm test ${affectedComponents.map(c => `--testPathPattern=${c}`).join(' ')}`;
    return execSync(testCommand, { encoding: 'utf8' });
  }
}
```

### Quality Dashboard Generator
```typescript
// scripts/ava-quality-dashboard.ts
interface QualityMetrics {
  coverage: CoverageReport;
  performance: LighthouseReport;
  accessibility: AxeReport;
  visualRegression: VisualDiffReport;
  testStability: FlakinessReport;
}

class QualityDashboard {
  async generateWeeklyReport(): Promise<string> {
    const metrics = await this.collectMetrics();
    const riskAreas = this.identifyRiskAreas(metrics);
    const improvements = this.trackImprovements(metrics);

    return this.renderQualityRadar(metrics, riskAreas, improvements);
  }

  async updateQualityGates(): Promise<void> {
    const currentMetrics = await this.collectMetrics();

    // Auto-adjust thresholds based on trend analysis
    if (currentMetrics.coverage.trend === 'improving') {
      this.suggestCoverageIncrease();
    }

    // Flag degrading areas
    if (currentMetrics.performance.trend === 'degrading') {
      await this.createPerformanceAlert();
    }
  }
}
```

### Flaky Test Detection & Management
```typescript
// scripts/ava-flaky-detector.ts
interface FlakyTestData {
  testName: string;
  filePath: string;
  failureRate: number;
  lastFailures: TestFailure[];
  suggestedFix: string;
}

class FlakyTestManager {
  async detectFlakyTests(): Promise<FlakyTestData[]> {
    const testHistory = await this.getTestHistory(30); // Last 30 days
    const flakyTests = testHistory.filter(test =>
      test.failureRate > 0.02 && test.failureRate < 0.98
    );

    return flakyTests.map(test => ({
      ...test,
      suggestedFix: this.analyzeFlakyPattern(test)
    }));
  }

  async autoTagFlakyTests(flakyTests: FlakyTestData[]): Promise<void> {
    for (const test of flakyTests) {
      await this.addFlakyTag(test);
      await this.createFlakyTestIssue(test);
    }
  }
}
```

## 🔄 Daily Automation Workflows

### Morning Health Check
```bash
#!/bin/bash
# scripts/ava-morning-check.sh

echo "🌅 Ava's Morning QA Health Check"

# 1. Check test infrastructure
echo "Checking test infrastructure..."
pnpm test:health-check

# 2. Analyze overnight CI failures
echo "Analyzing CI failures..."
node scripts/ava-ci-analyzer.js

# 3. Update quality metrics
echo "Updating quality dashboard..."
node scripts/ava-quality-dashboard.js

# 4. Check for new flaky tests
echo "Scanning for flaky tests..."
node scripts/ava-flaky-detector.js

# 5. Generate daily standup report
echo "Generating standup report..."
node scripts/ava-standup-generator.js

echo "✅ Morning health check complete!"
```

### PR Automation Hook
```bash
#!/bin/bash
# .github/workflows/ava-pr-automation.yml

name: Ava QA Automation
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ava-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install

      - name: Run Ava PR Analysis
        run: |
          node scripts/ava-pr-analyzer.js ${{ github.event.number }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Run Affected Tests
        run: |
          node scripts/ava-affected-tests.js ${{ github.event.number }}

      - name: Post Test Plan Comment
        run: |
          node scripts/ava-comment-generator.js ${{ github.event.number }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 📊 Enhanced Monitoring & Alerts

### Performance Budget Monitoring
```typescript
// scripts/ava-performance-monitor.ts
interface PerformanceBudget {
  lighthouse: { performance: 90, accessibility: 100, bestPractices: 90, seo: 90 };
  coreWebVitals: { cls: 0.1, fid: 100, lcp: 2500 };
  bundleSize: { maxSize: '500kb', maxChunks: 10 };
}

class PerformanceMonitor {
  async checkBudgets(): Promise<BudgetViolation[]> {
    const currentMetrics = await this.runLighthouse();
    const violations = this.compareToBudget(currentMetrics);

    if (violations.length > 0) {
      await this.createPerformanceAlert(violations);
    }

    return violations;
  }
}
```

### Accessibility Compliance Tracker
```typescript
// scripts/ava-a11y-tracker.ts
class AccessibilityTracker {
  async runA11yAudit(): Promise<A11yReport> {
    const axeResults = await this.runAxeTests();
    const lighthouseA11y = await this.runLighthouseA11y();

    return {
      violations: axeResults.violations,
      score: lighthouseA11y.score,
      wcagLevel: this.determineWCAGCompliance(axeResults),
      recommendations: this.generateRecommendations(axeResults)
    };
  }

  async trackA11yProgress(): Promise<void> {
    const currentReport = await this.runA11yAudit();
    const previousReport = await this.getLastA11yReport();

    const progress = this.calculateProgress(currentReport, previousReport);
    await this.updateA11yDashboard(progress);
  }
}
```

## 🎯 Integration with Existing ruleIQ Infrastructure

### Enhanced package.json Scripts
```json
{
  "scripts": {
    "ava:health-check": "node scripts/ava-morning-check.js",
    "ava:pr-analysis": "node scripts/ava-pr-analyzer.js",
    "ava:quality-report": "node scripts/ava-quality-dashboard.js",
    "ava:flaky-scan": "node scripts/ava-flaky-detector.js",
    "test:affected": "node scripts/ava-affected-tests.js",
    "test:quality-gates": "node scripts/ava-quality-gates.js",
    "test:performance-budget": "node scripts/ava-performance-monitor.js",
    "test:a11y-audit": "node scripts/ava-a11y-tracker.js"
  }
}
```

### GitHub Actions Integration
```yaml
# .github/workflows/ava-quality-gates.yml
name: Ava Quality Gates
on: [push, pull_request]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - name: Ava Quality Assessment
        run: |
          pnpm ava:quality-gates

      - name: Upload Quality Report
        uses: actions/upload-artifact@v4
        with:
          name: ava-quality-report
          path: reports/quality-dashboard.html
```

---

**Status**: ✅ Ready for Implementation
**Integration**: Seamlessly works with existing ruleIQ test infrastructure
**Maintenance**: Self-updating based on codebase changes and PR analysis
**Automation Level**: Fully automated with human oversight for critical decisions
