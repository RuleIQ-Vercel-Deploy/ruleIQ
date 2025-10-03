#!/usr/bin/env node
/**
 * Fix untokenized colors in components to use approved tokens from style_rules.json
 */

import fs from 'node:fs';
import path from 'node:path';
import { glob } from 'glob';

const cwd = process.cwd();

// Token mappings from style_rules.json
const colorMappings = {
  // Direct hex replacements
  '#6C757D': 'var(--silver-500)',  // Gray -> silver-500
  '#6c757d': 'var(--silver-500)',
  '#002147': 'var(--black)',       // Dark blue -> black
  '#002': 'var(--black)',
  '#FFD700': 'var(--purple-400)',  // Gold -> purple-400
  '#ffd700': 'var(--purple-400)',
  '#FFD': 'var(--purple-400)',
  '#F0EAD6': 'var(--purple-50)',   // Cream -> purple-50
  '#f0ead6': 'var(--purple-50)',
  '#F0E': 'var(--purple-50)',
  '#161e3a': 'var(--black)',       // Dark oxford -> black
  '#FF6F61': 'var(--purple-500)',  // Coral -> purple-500
  '#ff6f61': 'var(--purple-500)',
  '#FFFFFF': 'var(--white)',
  '#ffffff': 'var(--white)',
  '#fff': 'var(--white)',          // Short white
  '#FFF': 'var(--white)',
  '#6C7': 'var(--silver-400)',     // Short hex
  '#000000': 'var(--black)',       // Full black
  '#000': 'var(--black)',          // Short black
  '#ccc': 'var(--silver-light)',   // Light gray
  '#CCC': 'var(--silver-light)',
  '#8B5CF6': 'var(--purple-500)',  // Exact purple
  '#8b5cf6': 'var(--purple-500)',
  '#8B5': 'var(--purple-500)',     // Short purple
  '#10B981': 'var(--purple-400)',  // Green -> purple-400
  '#10b981': 'var(--purple-400)',
  '#10B': 'var(--purple-400)',
  '#F59E0B': 'var(--purple-600)',  // Orange -> purple-600
  '#f59e0b': 'var(--purple-600)',
  '#F59': 'var(--purple-600)',
  '#EF4444': 'var(--purple-500)',  // Red -> purple-500
  '#ef4444': 'var(--purple-500)',
  '#EF4': 'var(--purple-500)',
  // Additional colors found in components
  '#0A0': 'var(--purple-400)',     // Green
  '#1a1': 'var(--black)',          // Dark
  '#1F2937': 'var(--black)',       // Gray-800
  '#1F2': 'var(--black)',
  '#374151': 'var(--silver-500)',  // Gray-700  
  '#374': 'var(--silver-500)',
  '#4B5563': 'var(--silver-500)',  // Gray-600
  '#4B5': 'var(--silver-500)',
  '#9CA3AF': 'var(--silver-500)',  // Gray-400 (exact match)
  '#9CA': 'var(--silver-500)',
  '#9ca3af': 'var(--silver-500)',
  '#A855F7': 'var(--purple-500)',  // Purple
  '#A85': 'var(--purple-500)',
  '#a855f7': 'var(--purple-500)',
  '#C084FC': 'var(--purple-400)',  // Purple light
  '#C08': 'var(--purple-400)',
  '#c084fc': 'var(--purple-400)',
  '#C0C0C0': 'var(--silver-400)',  // Silver (exact match)
  '#C0C': 'var(--silver-400)',
  '#c0c0c0': 'var(--silver-400)',
  '#E9D5FF': 'var(--purple-50)',   // Purple lightest
  '#E9D': 'var(--purple-50)',
  '#e9d5ff': 'var(--purple-50)',
  '#F3F4F6': 'var(--purple-50)',   // Gray-100
  '#F3F': 'var(--purple-50)',
  '#f3f4f6': 'var(--purple-50)',
};

// Create CSS variables file
const cssVariables = `/* Token variables from style_rules.json */
:root {
  --purple-50: #faf5ff;
  --purple-400: #a78bfa;
  --purple-500: #8b5cf6;
  --purple-600: #7c3aed;
  --silver-400: #c0c0c0;
  --silver-500: #9ca3af;
  --silver-light: #e5e5e5;
  --white: #ffffff;
  --black: #000000;
}`;

async function fixComponentColors() {
  // Write CSS variables
  const cssPath = path.join(cwd, 'styles/tokens.css');
  fs.writeFileSync(cssPath, cssVariables);
  console.log('✓ Created styles/tokens.css');

  // Fix navigation components
  const patterns = [
    'components/navigation/**/*.tsx',
    'components/ui/**/*.tsx'
  ];

  let fixedCount = 0;
  
  for (const pattern of patterns) {
    const files = await glob(pattern, { cwd });
    
    for (const file of files) {
      const filePath = path.resolve(cwd, file);
      let content = fs.readFileSync(filePath, 'utf8');
      let modified = false;
      
      // Replace all color instances
      for (const [oldColor, newToken] of Object.entries(colorMappings)) {
        const regex = new RegExp(oldColor.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
        const before = content;
        content = content.replace(regex, newToken);
        if (before !== content) {
          modified = true;
        }
      }
      
      // Fix style prop patterns
      content = content.replace(/style=\{\{([^}]+)\}\}/g, (match, styles) => {
        let fixedStyles = styles;
        for (const [oldColor, newToken] of Object.entries(colorMappings)) {
          const regex = new RegExp(`(['"])${oldColor.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\1`, 'gi');
          fixedStyles = fixedStyles.replace(regex, `$1${newToken}$1`);
        }
        return `style={{${fixedStyles}}}`;
      });
      
      if (modified) {
        fs.writeFileSync(filePath, content);
        fixedCount++;
        console.log(`✓ Fixed ${file}`);
      }
    }
  }
  
  console.log(`\n✅ Fixed ${fixedCount} files with tokenized colors`);
  return fixedCount;
}

// Run the fix
fixComponentColors().catch(console.error);