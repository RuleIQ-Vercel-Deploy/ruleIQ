# Refactor & Rationalization Plan

This plan consolidates primitives, enforces token usage, and provides codemods to migrate non-conforming styles.

## Targets
- Ensure all Button/Card/Input/Textarea/Select/Table/Badge/Alert/Dialog/Sheet/Tabs/Tooltip/Sidebar use only tokens from `_index_ops/quality_gate/style_rules.json`.
- Remove inline hex colors and arbitrary Tailwind colors.

## Actions
1) Static Scan (Iron-Fist)
   - Use `_index_ops/quality_gate/lint-components.mjs` to detect FAIL/WARN.

2) Codemods
   - `_index_ops/codemods/enforce-tokenized-colors.ts` – replaces inline hex and `bg-[#...]` with mapped tokens.

3) Merge/Replace
   - Prefer a single Button component `components/ui/button.tsx`.
   - Remove ad-hoc button variants with inline colors.

4) Verification
   - Storybook visual snapshots for kept components.
   - A11y checks via addon-a11y.

## Rollout
- Phase 1: Flag + codemod dry run
- Phase 2: Apply codemod to selected components
- Phase 3: Visual + a11y verification in Storybook
