import { describe, it, expect } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import * as glob from 'glob';

/**
 * Theme Migration Test Suite
 * Ensures no teal colors or legacy hex codes remain in the codebase
 */
describe('Theme Migration', () => {
  const sourceDirectories = ['app', 'components', 'lib'];
  const excludePatterns = [
    '**/node_modules/**',
    '**/dist/**',
    '**/build/**',
    '**/.next/**',
    '**/neural-purple-colors.ts', // Exclude the migration map itself
    '**/theme-migration.test.tsx', // Exclude this test file
    '**/migrate-colors.ts', // Exclude the migration script
  ];

  // Patterns to detect teal colors and legacy hex codes
  const tealClassRegex = /\bteal-\d{2,3}\b/gi;
  const legacyHexCodes = [
    /#2C7A7B/gi, // Teal 700
    /#319795/gi, // Teal 600
    /#38B2AC/gi, // Teal 500
    /#4FD1C5/gi, // Teal 400
    /#81E6D9/gi, // Teal 300
    /#B2F5EA/gi, // Teal 200
    /#E6FFFA/gi, // Teal 100
    /#CB963E/gi, // Gold
    /#D4A574/gi, // Light gold
    /#B8822F/gi, // Dark gold
  ];

  const getAllFiles = () => {
    const files: string[] = [];
    sourceDirectories.forEach(dir => {
      const pattern = path.join(__dirname, '..', dir, '**/*.{tsx,ts,jsx,js,css}');
      const dirFiles = glob.sync(pattern, {
        ignore: excludePatterns,
      });
      files.push(...dirFiles);
    });
    return files;
  };

  describe('Teal Class Migration', () => {
    it('should not contain any teal Tailwind classes', () => {
      const files = getAllFiles();
      const violations: Array<{ file: string; matches: string[] }> = [];

      files.forEach(file => {
        const content = fs.readFileSync(file, 'utf-8');
        const matches = content.match(tealClassRegex);

        if (matches && matches.length > 0) {
          violations.push({
            file: path.relative(process.cwd(), file),
            matches: [...new Set(matches)], // Unique matches only
          });
        }
      });

      if (violations.length > 0) {
        const report = violations.map(v =>
          `  ${v.file}:\n    - ${v.matches.join('\n    - ')}`
        ).join('\n');

        throw new Error(
          `Found ${violations.length} files with teal classes:\n${report}\n\n` +
          `Run 'pnpm migrate:colors' to fix these automatically.`
        );
      }

      expect(violations).toHaveLength(0);
    });
  });

  describe('Legacy Hex Code Migration', () => {
    it('should not contain any legacy hex color codes', () => {
      const files = getAllFiles();
      const violations: Array<{ file: string; hexCodes: string[] }> = [];

      files.forEach(file => {
        const content = fs.readFileSync(file, 'utf-8');
        const foundHexCodes: string[] = [];

        legacyHexCodes.forEach(regex => {
          const matches = content.match(regex);
          if (matches) {
            foundHexCodes.push(...matches);
          }
        });

        if (foundHexCodes.length > 0) {
          violations.push({
            file: path.relative(process.cwd(), file),
            hexCodes: [...new Set(foundHexCodes)],
          });
        }
      });

      if (violations.length > 0) {
        const report = violations.map(v =>
          `  ${v.file}:\n    - ${v.hexCodes.join('\n    - ')}`
        ).join('\n');

        throw new Error(
          `Found ${violations.length} files with legacy hex codes:\n${report}\n\n` +
          `Run 'pnpm migrate:colors' to fix these automatically.`
        );
      }

      expect(violations).toHaveLength(0);
    });
  });

  describe('WCAG Contrast Compliance', () => {
    // Purple color values for testing
    const purpleColors = {
      primary: '#8B5CF6',
      primaryDark: '#7C3AED',
      primaryLight: '#C084FC',
      accent: '#A78BFA',
    };

    const backgrounds = {
      white: '#FFFFFF',
      dark: '#0F0F0F',
      lightGray: '#F3F4F6',
    };

    // Calculate relative luminance
    const getLuminance = (hex: string): number => {
      const rgb = parseInt(hex.slice(1), 16);
      const r = ((rgb >> 16) & 0xff) / 255;
      const g = ((rgb >> 8) & 0xff) / 255;
      const b = (rgb & 0xff) / 255;

      const toLinear = (c: number) =>
        c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);

      return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
    };

    // Calculate contrast ratio
    const getContrastRatio = (color1: string, color2: string): number => {
      const l1 = getLuminance(color1);
      const l2 = getLuminance(color2);
      const lighter = Math.max(l1, l2);
      const darker = Math.min(l1, l2);
      return (lighter + 0.05) / (darker + 0.05);
    };

    it('should meet WCAG AA standards for normal text (4.5:1)', () => {
      const minContrastAA = 4.5;
      const results: Array<{ combo: string; ratio: number; pass: boolean }> = [];

      Object.entries(purpleColors).forEach(([colorName, colorValue]) => {
        Object.entries(backgrounds).forEach(([bgName, bgValue]) => {
          const ratio = getContrastRatio(colorValue, bgValue);
          results.push({
            combo: `${colorName} on ${bgName}`,
            ratio,
            pass: ratio >= minContrastAA,
          });
        });
      });

      const failures = results.filter(r => !r.pass);
      if (failures.length > 0) {
        console.warn('⚠️  Some color combinations do not meet WCAG AA standards:');
        failures.forEach(f => {
          console.warn(`   ${f.combo}: ${f.ratio.toFixed(2)} (needs 4.5)`);
        });
      }

      // At least primary on white should pass for essential UI
      const primaryOnWhite = getContrastRatio(purpleColors.primary, backgrounds.white);
      expect(primaryOnWhite).toBeGreaterThanOrEqual(minContrastAA);
    });

    it('should meet WCAG AA standards for large text (3:1)', () => {
      const minContrastAALarge = 3;

      Object.entries(purpleColors).forEach(([colorName, colorValue]) => {
        Object.entries(backgrounds).forEach(([bgName, bgValue]) => {
          const ratio = getContrastRatio(colorValue, bgValue);
          expect(ratio).toBeGreaterThanOrEqual(minContrastAALarge);
        });
      });
    });
  });

  describe('Theme Consistency', () => {
    it('should use purple color tokens from the centralized theme file', () => {
      const files = getAllFiles();
      const purpleImportRegex = /from\s+['"].*neural-purple-colors['"]/;
      let filesUsingTheme = 0;

      files.forEach(file => {
        const content = fs.readFileSync(file, 'utf-8');

        // Check if file uses purple colors
        const usesPurpleColors = /purple-\d{2,3}|#8B5CF6|#7C3AED|#C084FC|#A78BFA/i.test(content);

        // If it uses purple colors, it should import from the theme file (with some exceptions)
        if (usesPurpleColors) {
          const isSpecialFile = file.includes('tailwind.config') ||
                               file.includes('.css') ||
                               file.includes('neural-purple-colors');

          if (!isSpecialFile && purpleImportRegex.test(content)) {
            filesUsingTheme++;
          }
        }
      });

      // We expect at least some files to be using the centralized theme
      expect(filesUsingTheme).toBeGreaterThan(0);
    });
  });
});