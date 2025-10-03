# Agent 3: QUALITY-GATE + STORYBOOK Tasks

## Primary Responsibility
Implement Iron-Fist Quality Gate and scaffold production-ready Storybook with dark theme.

## Prerequisites
- `_index_ops/quality_gate/style_rules.json` must exist (from Agent 1)
- `_index_ops/components_ready.flag` must exist (from Agent 2)

## Tasks

### 1. Storybook Setup (Dark Theme)
Scaffold complete Storybook configuration:

**Files to create:**
- `frontend/.storybook/main.ts` - Core configuration
- `frontend/.storybook/preview.ts` - Global decorators, dark theme
- `frontend/.storybook/manager.ts` - Manager UI configuration  
- `frontend/.storybook/theming.ts` - Theme mapping to globals.css tokens
- `frontend/.storybook/tsconfig.json` - TypeScript configuration

**Package.json scripts to add:**
```json
{
  "storybook": "storybook dev -p 6006",
  "build-storybook": "storybook build", 
  "test-storybook": "test-storybook",
  "lint:ui": "eslint src/components/**/*.{ts,tsx}",
  "fix:ui": "eslint src/components/**/*.{ts,tsx} --fix"
}
```

### 2. Iron-Fist Quality Gate Implementation

#### Static Scanner: `lint-components.mjs`
Create comprehensive static analysis tool that:
- Allows **only** tokens/vars/classes from `style_rules.json`
- Bans inline non-token colors (e.g., `color: #ff0000`)
- Enforces type-safe props
- Detects dead/unused variants
- Reports violations with precise fixes

#### Visual Testing Harness
- Playwright visual tests: `playwright.visual.spec.ts`
- Capture canonical component stories
- Settings: DPR=1, 1440×900, dark mode
- Compare against baseline screenshots

### 3. Build & Test Automation
**Create**: `frontend/_index_ops/rebuild_storybook.sh`

Pipeline:
```bash
#!/bin/bash
set -e  # Exit on any error

cd /home/omar/Documents/ruleIQ/frontend

echo "🏗️ Installing dependencies..."
pnpm install

echo "🔍 Linting UI components..."
pnpm lint:ui

echo "🧪 Running Storybook tests..."
pnpm test-storybook

echo "📦 Building Storybook..."
pnpm build-storybook

echo "✅ Storybook build complete: frontend/storybook-static/"
```

### 4. Quality Gate Reports
**Output**: `_index_ops/quality_gate/report.json` and `report.md`

Report structure:
```json
{
  "timestamp": "2025-01-28T22:20:52Z",
  "components": [
    {
      "name": "Button",
      "path": "src/components/ui/button.tsx", 
      "status": "PASS|WARN|FAIL",
      "violations": [],
      "fixes": []
    }
  ],
  "summary": {
    "total": 12,
    "pass": 10,
    "warn": 2, 
    "fail": 0
  }
}
```

### 5. Quality Gate Execution
Run comprehensive quality checks:
- Static analysis with `lint-components.mjs`
- Visual regression testing
- Component story validation  
- Token conformance verification

**Success Criteria for PASS:**
- All components use only approved tokens from `style_rules.json`
- No hardcoded styling values
- All stories render without errors
- Visual tests match baselines
- WCAG AA compliance (focus rings, keyboard nav, reduced motion)

### 6. Completion Signaling
If all components achieve **PASS** status:
```bash
echo "PASS" > _index_ops/quality_gate/PASS.flag
git add -A && git commit -m "Agent3: Quality Gate PASS - components vetted"
```

If any **FAIL** status:
```bash
echo "Quality Gate FAILED - see report.json for details" 
exit 1
```

## Commands to Execute in Tmux Pane
```bash
cd /home/omar/Documents/ruleIQ/frontend

echo "🎯 Agent 3: Quality Gate + Storybook Starting..."
echo "⏳ Waiting for prerequisites..."

# Wait for Agent 1 & 2 completion
while [ ! -f "_index_ops/quality_gate/style_rules.json" ] || [ ! -f "_index_ops/components_ready.flag" ]; do
  sleep 2
done

echo "✅ Prerequisites ready, scaffolding Storybook..."

# Scaffold Storybook configuration
# Implement static scanner and visual tests  
# Run Quality Gate
# Generate reports
# Signal completion or failure

echo "🏁 Agent 3: Quality Gate complete"
```

## Iron-Fist Quality Standards
- **Zero tolerance** for drift from `style_rules.json`
- **Dark mode** as default rendering context
- **WCAG AA** accessibility compliance
- **No emojis** in any component code or stories
- **Deterministic** and **idempotent** build process
- **Fail fast** on any violation