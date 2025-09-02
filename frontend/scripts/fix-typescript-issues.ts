#!/usr/bin/env node

/**
 * TypeScript Issues Fix Script for ruleIQ Frontend
 *
 * This script identifies and fixes common TypeScript issues that affect test reliability.
 * It focuses on type safety improvements and test compatibility.
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

interface TypeScriptIssue {
  file: string;
  line: number;
  column: number;
  code: string;
  message: string;
  severity: 'error' | 'warning';
}

class TypeScriptFixer {
  private issues: TypeScriptIssue[] = [];
  private fixedFiles: Set<string> = new Set();

  constructor() {
    // TODO: Replace with proper logging
  }

  async run() {
    try {
      // Analyze TypeScript issues
      await this.analyzeIssues();

      // Apply automated fixes
      await this.applyAutomatedFixes();

      // Generate report
      this.generateReport();
      // TODO: Replace with proper logging
    } catch {
      // Development logging - consider proper logger

      console.error('❌ TypeScript fixing failed:', _error);
      process.exit(1);
    }
  }

  private async analyzeIssues() {
    // TODO: Replace with proper logging
    try {
      // Run TypeScript compiler to get issues
      const output = execSync('pnpm typecheck', {
        encoding: 'utf8',
        stdio: 'pipe',
      });
    } catch (error: unknown) {
      // Parse TypeScript errors from output
      this.parseTypeScriptErrors(error.stdout || error.message);
    }
    // TODO: Replace with proper logging
  }

  private parseTypeScriptErrors(output: string) {
    const lines = output.split('\n');

    for (const line of lines) {
      // Parse TypeScript error format: file.ts:line:column - error TSxxxx: message
      const match = line.match(/^(.+):(\d+):(\d+) - (error|warning) (TS\d+): (.+)$/);

      if (match) {
        const [, file, lineStr, columnStr, severity, code, message] = match;

        this.issues.push({
          file: file.trim(),
          line: parseInt(lineStr),
          column: parseInt(columnStr),
          code,
          message,
          severity: severity as 'error' | 'warning',
        });
      }
    }
  }

  private async applyAutomatedFixes() {
    // TODO: Replace with proper logging
    // Group issues by file for efficient processing
    const issuesByFile = this.groupIssuesByFile();

    for (const [filePath, fileIssues] of issuesByFile.entries()) {
      await this.fixFileIssues(filePath, fileIssues);
    }
  }

  private groupIssuesByFile(): Map<string, TypeScriptIssue[]> {
    const grouped = new Map<string, TypeScriptIssue[]>();

    for (const issue of this.issues) {
      if (!grouped.has(issue.file)) {
        grouped.set(issue.file, []);
      }
      grouped.get(issue.file)!.push(issue);
    }

    return grouped;
  }

  private async fixFileIssues(filePath: string, issues: TypeScriptIssue[]) {
    if (!fs.existsSync(filePath)) {
      // TODO: Replace with proper logging
      return;
    }

    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;

    // Sort issues by line number (descending) to avoid line number shifts
    const sortedIssues = issues.sort((a, b) => b.line - a.line);

    for (const issue of sortedIssues) {
      const fix = this.getAutomatedFix(issue, content);

      if (fix) {
        content = this.applyFix(content, issue, fix);
        modified = true;
        // TODO: Replace with proper logging
      }
    }

    if (modified) {
      fs.writeFileSync(filePath, content);
      this.fixedFiles.add(filePath);
    }
  }

  private getAutomatedFix(issue: TypeScriptIssue, content: string): string | null {
    const { code, message } = issue;

    // Fix unused variable declarations
    if (code === 'TS6133' && message.includes('is declared but its value is never read')) {
      const variableName = this.extractVariableName(message);
      if (variableName) {
        return `// eslint-disable-next-line @typescript-eslint/no-unused-vars\n`;
      }
    }

    // Fix missing properties in type assignments
    if (code === 'TS2322' && message.includes('is not assignable to type')) {
      return this.fixTypeAssignmentIssue(issue, content);
    }

    // Fix possibly undefined issues
    if (code === 'TS18048' && message.includes("is possibly 'undefined'")) {
      return this.fixPossiblyUndefinedIssue(issue, content);
    }

    // Fix missing properties
    if (code === 'TS2339' && message.includes('Property') && message.includes('does not exist')) {
      return this.fixMissingPropertyIssue(issue, content);
    }

    // Fix index signature access
    if (code === 'TS4111' && message.includes('comes from an index signature')) {
      return this.fixIndexSignatureIssue(issue, content);
    }

    // Fix argument count mismatches
    if (code === 'TS2554' && message.includes('Expected') && message.includes('arguments')) {
      return this.fixArgumentCountIssue(issue, content);
    }

    return null;
  }

  private extractVariableName(message: string): string | null {
    const match = message.match(/'([^']+)' is declared but its value is never read/);
    return match ? match[1] : null;
  }

  private fixTypeAssignmentIssue(issue: TypeScriptIssue, content: string): string | null {
    // Add type assertion or optional chaining based on context
    if (issue.message.includes('undefined')) {
      return " || ''"; // Add fallback for string types
    }
    return null;
  }

  private fixPossiblyUndefinedIssue(issue: TypeScriptIssue, content: string): string | null {
    // Add optional chaining or null check
    return '?.'; // Add optional chaining
  }

  private fixMissingPropertyIssue(issue: TypeScriptIssue, content: string): string | null {
    // This usually requires manual intervention
    return null;
  }

  private fixIndexSignatureIssue(issue: TypeScriptIssue, content: string): string | null {
    const lines = content.split('\n');
    const line = lines[issue.line - 1];

    // Convert dot notation to bracket notation
    const match = line.match(/(\w+)\.(\w+)/);
    if (match) {
      const [, object, property] = match;
      return `${object}['${property}']`;
    }

    return null;
  }

  private fixArgumentCountIssue(issue: TypeScriptIssue, content: string): string | null {
    // This usually requires manual intervention to understand the correct signature
    return null;
  }

  private applyFix(content: string, issue: TypeScriptIssue, fix: string): string {
    const lines = content.split('\n');
    const lineIndex = issue.line - 1;

    if (lineIndex >= 0 && lineIndex < lines.length) {
      const line = lines[lineIndex];

      // Apply fix based on type
      if (fix.startsWith('// eslint-disable-next-line')) {
        // Add comment above the line
        lines.splice(lineIndex, 0, fix);
      } else if (fix === '?.') {
        // Add optional chaining
        lines[lineIndex] = line.replace(/\.(\w+)/, '?.$1');
      } else if (fix.includes('||')) {
        // Add fallback value
        lines[lineIndex] = line.replace(/;$/, `${fix};`);
      } else if (fix.includes('[') && fix.includes(']')) {
        // Replace dot notation with bracket notation
        lines[lineIndex] = line.replace(/\.(\w+)/, `['$1']`);
      }
    }

    return lines.join('\n');
  }

  private generateReport() {
    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging
    // Group issues by type
    const issuesByCode = new Map<string, number>();
    for (const issue of this.issues) {
      issuesByCode.set(issue.code, (issuesByCode.get(issue.code) || 0) + 1);
    }
    // TODO: Replace with proper logging
    for (const [code, count] of issuesByCode.entries()) {
      // TODO: Replace with proper logging
    }

    if (this.fixedFiles.size > 0) {
      // TODO: Replace with proper logging
      for (const file of this.fixedFiles) {
        // TODO: Replace with proper logging
      }
    }

    // Recommendations for manual fixes
    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging
  }
}

// Run the fixer if called directly
if (require.main === module) {
  const fixer = new TypeScriptFixer();
  fixer.run();
}

export default TypeScriptFixer;
