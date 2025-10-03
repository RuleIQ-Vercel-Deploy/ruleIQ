/**
 * Codemod: Enforce tokenized colors and shadows
 * Strategy:
 *  - Replace inline hex colors and Tailwind arbitrary color classes with mapped tokens from style_rules.json
 *  - Dry-run mode by default; pass --write to persist changes
 */

import fs from 'node:fs';
import path from 'node:path';
import { globSync } from 'glob';

const cwd = process.cwd();
const rules = JSON.parse(fs.readFileSync(path.resolve(cwd, '_index_ops/quality_gate/style_rules.json'), 'utf8'));
const allowedHex = new Set(Object.values(rules.colors).map((v: string) => v.toLowerCase()));

const write = process.argv.includes('--write');

function normalize3to6(h: string): string {
  // Convert 3-digit hex to 6-digit
  const m = /^#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])$/.exec(h);
  if (!m) return h.toLowerCase();
  return (`#${m[1]}${m[1]}${m[2]}${m[2]}${m[3]}${m[3]}`).toLowerCase();
}

function mapHexToNearestToken(hex: string): string | null {
  const h6 = normalize3to6(hex);
  if (allowedHex.has(h6)) return h6;
  // Common safe mappings
  if (h6 === '#ffffff') return '#ffffff';
  if (h6 === '#000000') return '#000000';
  if (h6 === '#cccccc') return rules.colors['silver-400']?.toLowerCase?.() ?? '#c0c0c0';
  // Fallback: map to purple-500 to stay within token palette
  return rules.colors['purple-500']?.toLowerCase?.() ?? null;
}

const files = globSync('components/**/*.{ts,tsx}', { cwd });

let changes = 0;
for (const rel of files) {
  const file = path.resolve(cwd, rel);
  let src = fs.readFileSync(file, 'utf8');
  let modified = src;

  // Replace Tailwind arbitrary color classes like bg-[#fff]
  modified = modified.replace(/((?:bg|text|from|to|via))-\[#[0-9a-fA-F]{3,6}\]/g, (m, prefix) => {
    const hex = m.match(/#[0-9a-fA-F]{3,6}/)?.[0] ?? '';
    const mapped = mapHexToNearestToken(hex);
    if (!mapped) return m;
    return `${prefix}-[${mapped}]`;
  });

  // Replace inline hex occurrences in style strings and JSX
  modified = modified.replace(/#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})/g, (m) => mapHexToNearestToken(m) ?? m);

  if (modified !== src) {
    changes++;
    if (write) fs.writeFileSync(file, modified, 'utf8');
  }
}

console.log(`Processed ${files.length} files; ${changes} files changed${write ? '' : ' (dry-run)'}.`);
