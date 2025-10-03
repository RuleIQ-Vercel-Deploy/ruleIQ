# Agent 1: STYLE-CORE Tasks

## Primary Responsibility
Parse canonical style source and extract design tokens for system-wide consistency.

## Prerequisites
- None (dependency-free; runs first)

## Tasks

### 1. Parse Canonical Style Source
- **Primary Source**: `/home/omar/Documents/ruleIQ/frontend/styles/globals.css`
- **Secondary**: `tailwind.config.ts` (if present, but globals.css wins on conflicts)

### 2. Extract Design Tokens
Parse and categorize:
- **Colors**: CSS variables, Tailwind color scales
- **Spacing**: margin, padding scales
- **Typography**: font families, sizes, weights, line heights
- **Border Radius**: rounding scales
- **Shadows**: box-shadow definitions  
- **Motion**: transition durations, easing functions
- **Z-index**: stacking contexts

### 3. Generate Token Registry
**Output**: `_index_ops/quality_gate/style_rules.json`

```json
{
  "colors": {
    "primary": {"50": "#...", "500": "#...", "900": "#..."},
    "background": {"DEFAULT": "#...", "secondary": "#..."}
  },
  "spacing": {"xs": "4px", "sm": "8px", "md": "16px"},
  "typography": {
    "fontFamily": {"sans": ["Inter", "sans-serif"]},
    "fontSize": {"sm": "14px", "base": "16px"}
  },
  "borderRadius": {"sm": "4px", "md": "8px"},
  "shadows": {"sm": "0 1px 2px...", "md": "0 4px 6px..."},
  "motion": {"duration": {"fast": "150ms", "normal": "300ms"}},
  "zIndex": {"dropdown": "1000", "modal": "1050"}
}
```

### 4. Scaffold Lint Configuration
Create placeholder `_index_ops/quality_gate/lint-config-base.mjs` that other agents can import.

## Success Criteria
- `style_rules.json` exists and contains comprehensive token registry
- File validates as proper JSON
- All tokens extracted from globals.css (with Tailwind config as fallback)
- No hardcoded values; everything derives from canonical source

## Next Agent Dependencies
- Agent 2 & 3 wait for `style_rules.json` to exist
- Token registry becomes single source of truth for all component generation/validation

## Commands to Execute in Tmux Pane
```bash
cd /home/omar/Documents/ruleIQ/frontend
echo "🎯 Agent 1: Style Core Parser Starting..."

# Parse globals.css and tailwind config
# Extract tokens to style_rules.json
# Create lint config base
# Signal completion

echo "✅ Agent 1: Style tokens extracted to _index_ops/quality_gate/style_rules.json"
```