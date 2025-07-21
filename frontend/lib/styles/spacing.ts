/**
 * Spacing system based on 8px grid
 * All values are in rem units for accessibility
 */
export const spacing = {
  // Core spacing scale (8px grid)
  '0': '0',
  px: '1px',
  '0.5': '0.125rem', // 2px
  '1': '0.25rem', // 4px
  '2': '0.5rem', // 8px (base unit)
  '3': '0.75rem', // 12px
  '4': '1rem', // 16px (2x base)
  '5': '1.25rem', // 20px
  '6': '1.5rem', // 24px (3x base)
  '8': '2rem', // 32px (4x base)
  '10': '2.5rem', // 40px
  '12': '3rem', // 48px (6x base)
  '16': '4rem', // 64px (8x base)
  '20': '5rem', // 80px
  '24': '6rem', // 96px (12x base)
  '32': '8rem', // 128px (16x base)
} as const;

// Semantic spacing tokens
export const semanticSpacing = {
  // Component padding
  'button-sm': spacing['3'], // 12px
  'button-md': spacing['4'], // 16px
  'button-lg': spacing['6'], // 24px

  // Card spacing
  'card-padding': spacing['6'], // 24px
  'card-gap': spacing['4'], // 16px

  // Layout spacing
  'section-gap': spacing['8'], // 32px
  'container-padding': spacing['6'], // 24px

  // Form spacing
  'form-gap': spacing['4'], // 16px
  'input-padding-x': spacing['3'], // 12px
  'input-padding-y': spacing['2'], // 8px
} as const;

// Grid helpers
export function grid(multiplier: number): string {
  return `${multiplier * 0.5}rem`; // 8px base unit
}

// Ensure spacing follows 8px grid
export function isOnGrid(value: string): boolean {
  const remValue = parseFloat(value);
  if (value.endsWith('rem')) {
    const pxValue = remValue * 16; // Assuming 16px base
    return pxValue % 8 === 0;
  }
  return false;
}

// Type helpers
export type SpacingScale = keyof typeof spacing;
export type SemanticSpacing = keyof typeof semanticSpacing;
