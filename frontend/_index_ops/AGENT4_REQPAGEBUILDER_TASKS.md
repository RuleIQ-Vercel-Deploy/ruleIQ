# Agent 4: REQ-PAGE BUILDER Tasks

## Primary Responsibility
Build "Create Wireframe" requirement page using only PASS components, with Excalidraw MCP wireframing.

## Prerequisites
- `_index_ops/quality_gate/PASS.flag` must exist (from Agent 3)

## Tasks

### 1. Wireframe Creation with Excalidraw MCP
Use Excalidraw MCP to create comprehensive wireframe:

**MCP Calls:**
```bash
# Create canvas and wireframe elements
call_mcp_tool create_element --type rectangle --x 50 --y 50 --width 1200 --height 800 --text "App Shell"
call_mcp_tool create_element --type rectangle --x 100 --y 150 --width 1100 --height 100 --text "Hero Section"
call_mcp_tool create_element --type rectangle --x 100 --y 280 --width 530 --height 200 --text "Primary CTA Block" 
call_mcp_tool create_element --type rectangle --x 670 --y 280 --width 530 --height 200 --text "Secondary CTA Block"
call_mcp_tool create_element --type rectangle --x 100 --y 520 --width 360 --height 250 --text "Card List Region"
call_mcp_tool create_element --type rectangle --x 500 --y 520 --width 350 --height 250 --text "Form Section"  
call_mcp_tool create_element --type rectangle --x 890 --y 520 --width 310 --height 250 --text "Data Table"

# Export wireframe assets
call_mcp_tool get_resource --resource scene  # Export to PNG/SVG
```

**Output Files:**
- `_req_pages/wireframes/create-wireframe.png`
- `_req_pages/wireframes/create-wireframe.svg`

### 2. Requirements Configuration
**Create**: `_req_pages/requirements.json`
```json
[
  {
    "key": "create-wireframe",
    "title": "Create Wireframe", 
    "status": "planned",
    "priority": "P1",
    "owner": "UI Guild",
    "notes": [
      "High-level wireframe view rendered with vetted layout primitives.",
      "Zero business logic; interaction stubs only.", 
      "Demonstrate grid, typography scale, spacing tokens from globals.css."
    ]
  }
]
```

### 3. Next.js Route Implementation
**Preferred**: Next.js App Router structure
```
frontend/app/(requirements)/layout.tsx      # Dark theme layout
frontend/app/(requirements)/create-wireframe/page.tsx  # Main page
```

**Alternative**: React Router at `/requirements/create-wireframe`

#### Layout Component (`layout.tsx`)
- Import `styles/globals.css`
- Apply dark theme by default
- Ensure WCAG AA compliance baseline

#### Page Component (`page.tsx`)  
- Use **only** PASS components from Agent 3
- Implement wireframe structure:
  - App shell (header/nav)
  - Hero section with H1/H2 typography
  - Primary & Secondary CTA blocks
  - Card list region (placeholder data)
  - Form section (interaction stubs)
  - Data table region (mock data)

### 4. Page-Level Conformance Check
**Create**: Static analysis for the requirement page

**Tools:**
- Reuse `lint-components.mjs` from Agent 3
- Verify only `style_rules.json` tokens used
- Check WCAG AA compliance

**Output Reports:**
- `_req_pages/reports/create-wireframe.json`
- `_req_pages/reports/create-wireframe.md`

### 5. Screenshot Generation
Use Playwright to capture full-page screenshot:

**Settings:**
- Dark mode rendering
- DPR=1, viewport 1440×900
- Wait for network idle
- Full page capture

**Output**: `_req_pages/screenshots/create-wireframe.png`

### 6. Index Management
**Create/Update:**
- `_req_pages/INDEX.md` (human-readable)
- `_req_pages/req_index.json` (machine-readable)

**Entry Schema:**
```json
{
  "key": "create-wireframe",
  "route": "/requirements/create-wireframe", 
  "title": "Create Wireframe",
  "last_commit_iso": "2025-01-28T22:20:52Z",
  "screenshot": "screenshots/create-wireframe.png",
  "wireframe": "wireframes/create-wireframe.svg",
  "conformance": {
    "status": "PASS",
    "notes": ["All components vetted", "Dark mode compliant", "WCAG AA passed"]
  }
}
```

### 7. Build Automation
**Create**: `_req_pages/rebuild_req_pages.sh`

```bash
#!/bin/bash
set -e

cd /home/omar/Documents/ruleIQ/frontend

echo "🎯 Validating requirements.json..."
# JSON validation

echo "🏗️ Ensuring route scaffolds..."
# Generate missing routes from requirements.json

echo "🔍 Running page conformance checks..."
# Use style_rules.json for validation

echo "📸 Launching app and capturing screenshots..."
# Start Next.js dev server (port 3000→4000 fallback)
# Run Playwright screenshot capture

echo "📋 Updating index..."
# Regenerate INDEX.md and req_index.json

echo "✅ Requirement pages rebuild complete"
```

### 8. Documentation  
**Create**: `_req_pages/README.md`

Content:
- Prerequisites and setup
- How to add new requirements
- Conformance checking process
- Wireframe workflow with Excalidraw MCP
- Report interpretation guide

## Hard Constraints
- **Exactly one page** per requirement in `requirements.json`
- Use **only** PASS components from Quality Gate
- **Dark mode** as default rendering context
- **No emojis** anywhere in code or content
- **WCAG AA** compliance mandatory
- Git commit timestamps for sorting (fallback to mtime)

## Success Criteria
- `/requirements/create-wireframe` route accessible and functional
- Wireframe assets exported via Excalidraw MCP
- Screenshot captured successfully  
- Page passes conformance checks (PASS status only)
- Index files updated with single requirement entry
- Rebuild script is idempotent

## Commands to Execute in Tmux Pane
```bash
cd /home/omar/Documents/ruleIQ/frontend

echo "🎯 Agent 4: Requirement Page Builder Starting..."
echo "⏳ Waiting for Quality Gate PASS..."

# Wait for Agent 3 completion
while [ ! -f "_index_ops/quality_gate/PASS.flag" ]; do
  sleep 2
done

echo "✅ Quality Gate passed, building requirement page..."

# Create wireframe with Excalidraw MCP
# Scaffold Next.js routes  
# Implement page with PASS components
# Run conformance checks
# Generate screenshot
# Update indexes
# Create rebuild script

echo "🏁 Agent 4: Create Wireframe page complete"
```

## MCP Integration Priority
1. **Excalidraw MCP** - Essential for wireframe creation/export
2. **Playwright integration** - For screenshot automation  
3. **Shell/Git MCP** - For commit timestamp extraction