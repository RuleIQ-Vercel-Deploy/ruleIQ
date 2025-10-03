# Agent 2: COMPONENT-AUDIT Tasks

## Primary Responsibility
Inventory existing components, rationalize the set, and generate/normalize components using MCP servers.

## Prerequisites  
- `_index_ops/quality_gate/style_rules.json` must exist (from Agent 1)

## Tasks

### 1. Component Inventory
Scan existing components and create comprehensive inventory.

**Output**: `_index_ops/components_inventory.json`
```json
[
  {
    "name": "Button", 
    "importPath": "src/components/ui/button.tsx",
    "usages": ["app/dashboard/page.tsx", "components/header.tsx"],
    "status": "keep|merge|deprecate|delete",
    "replacement": "Optional path if merging/deprecating",
    "notes": ["Primary CTA component", "Uses custom styling"]
  }
]
```

### 2. Rationalization Decisions
Analyze inventory and make keep/merge/deprecate/delete decisions.

**Output**: `_index_ops/components_decisions.md` (table format with crisp rationale)

### 3. MCP Component Generation
Use available MCP servers to generate/normalize components:

#### shadcn MCP Usage
- Search & generate components: button, card, input, textarea, select, table, badge, alert, sheet/drawer, dialog, tabs, tooltip, navbar, sidebar
- Ensure all generated components consume **only** tokens from `style_rules.json`

#### Aceternity Integration (if available)
- Import components via MCP or package
- **Wrap/normalize** to conform to `style_rules.json` tokens
- Reject any components that cannot be normalized

### 4. Component Implementation
- Write/overwrite components in `src/components/**`
- Generate Storybook stories/MDX for each component
- Ensure all variants: default/hover/focus/disabled/error/loading/dense

### 5. Refactoring Plan
**Output**: `_index_ops/refactor_plan.md` + codemods in `_index_ops/codemods/*.ts`
- Document replacement/merge mappings
- Create automated migration scripts (ts-morph/jscodeshift)

## MCP Server Integration

### Expected MCP Calls
```bash
# shadcn component generation
call_mcp_tool component-builder --components '[{"name": "button", "necessity": "critical"}]'

# Or if shadcn MCP is available:
# shadcn.search { query: "button" }
# shadcn.generate { name: "button", variants: ["primary","ghost"], tokensFrom: "globals.css" }
```

### Token Conformance Rule
Every generated component MUST:
- Use only tokens from `style_rules.json`  
- Pass static analysis for token compliance
- Have no hardcoded colors/spacing/typography

## Success Criteria
- `components_inventory.json` contains complete component inventory
- `components_decisions.md` provides clear keep/merge/deprecate/delete decisions
- All components in `src/components/**` use only approved tokens
- Storybook stories generated for each kept component
- `components_ready.flag` created to signal Agent 3

## Signaling Completion
```bash
touch _index_ops/components_ready.flag
git add -A && git commit -m "Agent2: Component audit and normalization complete"
```

## Commands to Execute in Tmux Pane
```bash
cd /home/omar/Documents/ruleIQ/frontend

echo "🎯 Agent 2: Component Audit Starting..."
echo "⏳ Waiting for style_rules.json..."

# Wait for Agent 1 completion
while [ ! -f "_index_ops/quality_gate/style_rules.json" ]; do
  sleep 2
done

echo "✅ Style tokens available, proceeding with component audit..."

# Execute component inventory, decisions, and MCP generation
# Create Storybook stories
# Signal completion with flag

echo "✅ Agent 2: Component audit complete, ready for Quality Gate"
```