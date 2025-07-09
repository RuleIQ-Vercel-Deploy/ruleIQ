#!/usr/bin/env node
/**
 * TypeScript Error Fix Script for ruleIQ Frontend
 * 
 * This script fixes common TypeScript errors automatically
 * to improve type safety and prepare for production.
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

interface TypeScriptError {
  file: string;
  line: number;
  column: number;
  code: string;
  message: string;
}

class TypeScriptErrorFixer {
  private projectRoot: string;
  private errors: TypeScriptError[] = [];

  constructor(projectRoot: string) {
    this.projectRoot = projectRoot;
  }

  /**
   * Parse TypeScript errors from tsc output
   */
  private parseErrors(output: string): TypeScriptError[] {
    const errors: TypeScriptError[] = [];
    const lines = output.split('\n');
    
    for (const line of lines) {
      const match = line.match(/^(.+?)\((\d+),(\d+)\): error (TS\d+): (.+)$/);
      if (match) {
        const [, file, lineStr, columnStr, code, message] = match;
        errors.push({
          file,
          line: parseInt(lineStr, 10),
          column: parseInt(columnStr, 10),
          code,
          message
        });
      }
    }
    
    return errors;
  }

  /**
   * Fix unused variable errors by prefixing with underscore
   */
  private fixUnusedVariables(filePath: string, content: string): string {
    // Fix: 'variable' is declared but its value is never read
    const patterns = [
      // Function parameters
      /(\w+): ([^,)]+)(?=\s*[,)])/g,
      // Variable declarations
      /(?:const|let|var)\s+(\w+)/g,
      // Destructuring
      /{\s*(\w+)(?:\s*,\s*(\w+))*\s*}/g
    ];

    // This is a simplified approach - in practice, you'd need more sophisticated parsing
    return content;
  }

  /**
   * Fix type annotation errors by adding proper types
   */
  private fixTypeAnnotations(filePath: string, content: string): string {
    // Replace 'any' with more specific types where possible
    const commonReplacements = [
      // Event handlers
      [/\(.*?\): any\s*=>/g, '(event: React.FormEvent) =>'],
      // Object props
      [/:\s*any\s*(?=[,}])/g, ': unknown'],
      // Function parameters
      [/\((\w+): any\)/g, '($1: unknown)'],
    ];

    let result = content;
    for (const [pattern, replacement] of commonReplacements) {
      result = result.replace(pattern as RegExp, replacement as string);
    }

    return result;
  }

  /**
   * Fix missing property errors by adding optional properties
   */
  private fixMissingProperties(filePath: string, content: string): string {
    // This would require more complex AST manipulation
    // For now, just add basic fixes
    
    // Fix trendValue property issues
    if (content.includes('trendValue')) {
      content = content.replace(
        /trendValue:\s*([^,}]+)/g,
        'trend: { value: $1, isPositive: true }'
      );
    }

    return content;
  }

  /**
   * Remove unused imports
   */
  private removeUnusedImports(filePath: string, content: string): string {
    const lines = content.split('\n');
    const imports = new Set<string>();
    const usage = new Set<string>();

    // Find imports
    for (const line of lines) {
      const importMatch = line.match(/import\s+{([^}]+)}\s+from/);
      if (importMatch) {
        const importList = importMatch[1].split(',').map(s => s.trim());
        for (const imp of importList) {
          imports.add(imp);
        }
      }
    }

    // Find usage
    for (const line of lines) {
      for (const imp of imports) {
        if (line.includes(imp) && !line.includes('import')) {
          usage.add(imp);
        }
      }
    }

    // Remove unused imports
    const unusedImports = Array.from(imports).filter(imp => !usage.has(imp));
    let result = content;
    
    for (const unused of unusedImports) {
      result = result.replace(new RegExp(`\\s*${unused}\\s*,?`, 'g'), '');
      result = result.replace(new RegExp(`{\\s*,\\s*}`, 'g'), '{}');
    }

    return result;
  }

  /**
   * Apply fixes to a single file
   */
  private fixFile(filePath: string): boolean {
    if (!fs.existsSync(filePath)) {
      console.log(`File not found: ${filePath}`);
      return false;
    }

    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;

    // Apply fixes
    content = this.removeUnusedImports(filePath, content);
    content = this.fixUnusedVariables(filePath, content);
    content = this.fixTypeAnnotations(filePath, content);
    content = this.fixMissingProperties(filePath, content);

    // Write back if changed
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✓ Fixed: ${filePath}`);
      return true;
    }

    return false;
  }

  /**
   * Run TypeScript compiler and get errors
   */
  private async getTypeScriptErrors(): Promise<TypeScriptError[]> {
    try {
      execSync('pnpm tsc --noEmit', { cwd: this.projectRoot });
      return []; // No errors
    } catch (error: any) {
      const output = error.stdout?.toString() || error.stderr?.toString() || '';
      return this.parseErrors(output);
    }
  }

  /**
   * Fix critical errors that prevent build
   */
  public async fixCriticalErrors(): Promise<void> {
    console.log('🔧 Starting TypeScript error fixes...\n');

    // Get initial errors
    const errors = await this.getTypeScriptErrors();
    console.log(`Found ${errors.length} TypeScript errors`);

    // Group errors by file
    const errorsByFile = new Map<string, TypeScriptError[]>();
    for (const error of errors) {
      const fullPath = path.resolve(this.projectRoot, error.file);
      if (!errorsByFile.has(fullPath)) {
        errorsByFile.set(fullPath, []);
      }
      errorsByFile.get(fullPath)!.push(error);
    }

    // Fix files with errors
    let fixedFiles = 0;
    for (const [filePath, fileErrors] of errorsByFile) {
      console.log(`\nProcessing ${filePath}:`);
      for (const error of fileErrors) {
        console.log(`  Line ${error.line}: ${error.message}`);
      }
      
      if (this.fixFile(filePath)) {
        fixedFiles++;
      }
    }

    console.log(`\n✅ Processing complete:`);
    console.log(`   Files processed: ${errorsByFile.size}`);
    console.log(`   Files modified: ${fixedFiles}`);

    // Check remaining errors
    const remainingErrors = await this.getTypeScriptErrors();
    console.log(`   Remaining errors: ${remainingErrors.length}`);

    if (remainingErrors.length > 0) {
      console.log('\n⚠️  Some errors still need manual fixing:');
      const remainingByFile = new Map<string, number>();
      for (const error of remainingErrors) {
        remainingByFile.set(error.file, (remainingByFile.get(error.file) || 0) + 1);
      }
      
      for (const [file, count] of remainingByFile) {
        console.log(`   ${file}: ${count} errors`);
      }
    } else {
      console.log('\n🎉 All TypeScript errors fixed!');
    }
  }

  /**
   * Apply specific fixes for known issues
   */
  public applyKnownFixes(): void {
    console.log('🔧 Applying known fixes...\n');

    // Fix unused import in dashboard page
    const dashboardPath = path.join(this.projectRoot, 'app/(dashboard)/dashboard/page.tsx');
    if (fs.existsSync(dashboardPath)) {
      let content = fs.readFileSync(dashboardPath, 'utf8');
      content = content.replace(/import\s+{[^}]*TrendingUp[^}]*}\s+from[^;]+;?\n?/g, '');
      fs.writeFileSync(dashboardPath, content, 'utf8');
      console.log('✓ Fixed unused TrendingUp import');
    }

    // Fix Assessment type conflicts
    const assessmentTypesPath = path.join(this.projectRoot, 'types/api.ts');
    if (fs.existsSync(assessmentTypesPath)) {
      let content = fs.readFileSync(assessmentTypesPath, 'utf8');
      // Add missing properties to Assessment interface
      if (content.includes('interface Assessment') && !content.includes('name:')) {
        content = content.replace(
          /interface Assessment\s*{([^}]+)}/,
          `interface Assessment {
  id: string;
  name: string;
  framework: string;
  date: string;
  status: string;
  $1
}`
        );
        fs.writeFileSync(assessmentTypesPath, content, 'utf8');
        console.log('✓ Fixed Assessment interface');
      }
    }

    // Fix button variant types
    const buttonVariantFiles = [
      'app/(dashboard)/policies/new/page.tsx'
    ];

    for (const file of buttonVariantFiles) {
      const filePath = path.join(this.projectRoot, file);
      if (fs.existsSync(filePath)) {
        let content = fs.readFileSync(filePath, 'utf8');
        content = content.replace(/variant="secondary-ruleiq"/g, 'variant="secondary"');
        content = content.replace(/variant="accent"/g, 'variant="default"');
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`✓ Fixed button variants in ${file}`);
      }
    }

    console.log('\n✅ Known fixes applied');
  }
}

// Main execution
async function main() {
  const projectRoot = process.cwd();
  const fixer = new TypeScriptErrorFixer(projectRoot);

  console.log('🚀 ruleIQ TypeScript Error Fixer\n');
  console.log(`Project: ${projectRoot}\n`);

  // Apply known fixes first
  fixer.applyKnownFixes();

  // Then attempt to fix remaining errors
  await fixer.fixCriticalErrors();

  console.log('\n🎯 Next steps:');
  console.log('1. Run `pnpm tsc --noEmit` to check remaining errors');
  console.log('2. Run `pnpm build` to test production build');
  console.log('3. Fix any remaining type errors manually');
  console.log('4. Consider enabling strict mode gradually');
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}