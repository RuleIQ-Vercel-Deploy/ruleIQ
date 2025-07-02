export const colors = {
  // Primary brand colors (from CLAUDE.md)
  primary: "#17255A",
  "primary-dark": "#0F1938",
  "primary-light": "#2B3A6A",
  
  // Accent colors
  gold: "#CB963E",
  "gold-dark": "#A67A2E",
  "gold-light": "#E0B567",
  
  cyan: "#34FEF7",
  "cyan-dark": "#1FD4E5",
  "cyan-light": "#6FFEFB",
  
  // Dark theme backgrounds
  "bg-dark": "#0A0F1B",
  "bg-card": "#111929",
  "bg-muted": "#1A2237",
  
  // Text colors
  "text-primary": "#F2F2F2",
  "text-secondary": "#B3B3B3",
  "text-muted": "#6B7280",
  
  // Semantic colors
  success: "#28A745",
  warning: "#CB963E",
  error: "#DC3545",
  info: "#34FEF7",
  
  // Neutral grays
  "neutral-light": "#D0D5E3",
  "neutral-medium": "#C2C2C2",
  "neutral-dark": "#6B7280",
} as const

export type ColorKey = keyof typeof colors
