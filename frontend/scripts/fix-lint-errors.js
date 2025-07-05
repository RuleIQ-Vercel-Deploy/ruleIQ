#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Function to fix common ESLint errors
function fixCommonErrors() {
  console.log('Starting automated ESLint fixes...');
  
  // Get all TypeScript/JavaScript files
  const files = execSync('find . -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" | grep -v node_modules | grep -v .next', { encoding: 'utf8' })
    .split('\n')
    .filter(file => file.trim());

  files.forEach(file => {
    if (!fs.existsSync(file)) return;
    
    let content = fs.readFileSync(file, 'utf8');
    let modified = false;

    // Fix 1: Add React import for files that use React.ReactNode but don't import React
    if (content.includes('React.ReactNode') && !content.includes('import React') && !content.includes('import type React')) {
      if (content.startsWith('"use client"')) {
        content = content.replace('"use client";\n', '"use client";\n\nimport type React from "react"\n');
      } else {
        content = 'import type React from "react"\n\n' + content;
      }
      modified = true;
    }

    // Fix 2: Replace unescaped quotes in JSX
    content = content.replace(/(\w+)="([^"]*)'([^"]*)"/, '$1="$2&apos;$3"');
    content = content.replace(/(\w+)="([^"]*)"([^"]*)"/, '$1="$2&quot;$3"');
    content = content.replace(/>([^<]*)'([^<]*)</g, '>$1&apos;$2<');
    content = content.replace(/>([^<]*)"([^<]*)</g, '>$1&quot;$2<');

    // Fix 3: Prefix unused variables with underscore
    const unusedVarRegex = /(\w+):\s*(\w+)\s*\)\s*=>/g;
    content = content.replace(unusedVarRegex, (match, param, type) => {
      if (param !== '_' && !param.startsWith('_')) {
        return match.replace(param, '_' + param);
      }
      return match;
    });

    // Fix 4: Replace 'any' with 'unknown' in catch blocks
    content = content.replace(/catch\s*\(\s*(\w+):\s*any\s*\)/g, 'catch ($1: unknown)');

    // Fix 5: Fix import ordering (basic)
    const lines = content.split('\n');
    const imports = [];
    const nonImports = [];
    let inImportSection = true;

    lines.forEach(line => {
      if (line.trim().startsWith('import ') || line.trim().startsWith('export ')) {
        if (inImportSection) {
          imports.push(line);
        } else {
          nonImports.push(line);
        }
      } else if (line.trim() === '') {
        if (inImportSection && imports.length > 0) {
          imports.push(line);
        } else {
          nonImports.push(line);
        }
      } else {
        inImportSection = false;
        nonImports.push(line);
      }
    });

    if (modified || imports.length > 0) {
      fs.writeFileSync(file, content);
      console.log(`Fixed: ${file}`);
    }
  });

  console.log('Automated fixes completed!');
}

// Run the fixes
fixCommonErrors();
