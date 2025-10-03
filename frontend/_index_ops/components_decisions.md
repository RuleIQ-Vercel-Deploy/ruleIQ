# Component Decisions (Iron-Fist Rationalization)

Status legend: keep | merge | deprecate | delete

| Component | Import Path | Status | Replacement | Notes |
|---|---|---|---|---|
| Button | components/ui/button.tsx | keep | — | Core CTA; enforce globals.css tokens |
| Card | components/ui/card.tsx | keep | — | Elevation via --shadow-purple-* |
| Input | components/ui/input.tsx | keep | — | Dark defaults + focus ring tokens |
| Textarea | components/ui/textarea.tsx | keep | — | Tokenized borders/background |
| Select | components/ui/select.tsx | keep | — | Radix wrapper; theme mapped |
| Table | components/ui/table.tsx | keep | — | Hover/zebra via tokens |
| Badge | components/ui/badge.tsx | keep | — | No inline hex |
| Alert | components/ui/alert.tsx | keep | — | a11y roles + tokens |
| Sheet | components/ui/sheet.tsx | keep | — | Overlay tokens |
| Drawer | components/ui/drawer.tsx | keep | — | Same as Sheet |
| Dialog | components/ui/dialog.tsx | keep | — | Focus trap + reduced motion |
| Tabs | components/ui/tabs.tsx | keep | — | Indicator color tokens |
| Tooltip | components/ui/tooltip.tsx | keep | — | Content tokens |
| Sidebar | components/ui/sidebar.tsx | keep | — | Keyboard nav |
| Navbar | components/navigation/navbar.tsx | keep | — | Theming compliance |
