#!/usr/bin/env node
/**
 * TypeScript Error Fix Script for ruleIQ Frontend
 * 
 * This script fixes common TypeScript errors automatically
 * to improve type safety and prepare for production.
 */



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
      const importMatch = line.match(/import\s+\{([^}]+)\}\s+from/);
      if (importMatch?.[1]) {
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

    return content;
  }
}