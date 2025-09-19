#!/usr/bin/env ts-node

/**
 * Color Migration Script
 * Replaces Tailwind teal classes and hex codes with Neural Purple tokens
 */

import * as fs from 'fs';
import * as path from 'path';
import * as glob from 'glob';
import { neuralPurple, tailwindColorMap, legacyToNeuralPurpleMap } from '../lib/theme/neural-purple-colors';

interface MigrationOptions {
  dryRun: boolean;
  verbose: boolean;
  pattern?: string;
}

interface MigrationResult {
  file: string;
  changes: number;
  errors?: string[];
}

class ColorMigrationTool {
  private results: MigrationResult[] = [];
  private totalChanges = 0;

  constructor(private options: MigrationOptions) {}

  async run() {
    console.log('🎨 Neural Purple Migration Tool');
    console.log('================================');
    console.log(`Mode: ${this.options.dryRun ? 'DRY RUN' : 'LIVE'}`);
    console.log('');

    const pattern = this.options.pattern || '{app,components,lib}/**/*.{tsx,ts,jsx,js,css}';
    const files = glob.sync(pattern, {
      cwd: path.join(__dirname, '..'),
      ignore: ['**/node_modules/**', '**/scripts/**', '**/neural-purple-colors.ts'],
      absolute: true,
    });

    console.log(`Found ${files.length} files to scan...`);
    console.log('');

    for (const file of files) {
      await this.processFile(file);
    }

    this.printReport();
  }

  private async processFile(filePath: string) {
    try {
      let content = fs.readFileSync(filePath, 'utf-8');
      const originalContent = content;
      let changeCount = 0;

      // Replace Tailwind classes
      for (const [oldClass, newClass] of Object.entries(tailwindColorMap)) {
        const regex = new RegExp(`\\b${oldClass}\\b`, 'g');
        const matches = content.match(regex);
        if (matches) {
          changeCount += matches.length;
          content = content.replace(regex, newClass);
        }
      }

      // Replace hex colors
      for (const [oldHex, newValue] of Object.entries(legacyToNeuralPurpleMap)) {
        const regex = new RegExp(oldHex.replace('#', '#?'), 'gi');
        const matches = content.match(regex);
        if (matches) {
          changeCount += matches.length;
          // For hex replacements, use the actual hex value from neuralPurple
          const newHex = typeof newValue === 'string' ? newValue : newValue.toString();
          content = content.replace(regex, newHex);
        }
      }

      // Check for remaining teal references that might have been missed
      const remainingTeal = content.match(/\bteal-\d{2,3}\b/g);
      if (remainingTeal && remainingTeal.length > 0) {
        console.warn(`⚠️  ${path.basename(filePath)}: Found ${remainingTeal.length} unmigrated teal classes`);
      }

      if (changeCount > 0) {
        if (!this.options.dryRun) {
          fs.writeFileSync(filePath, content, 'utf-8');
        }

        this.results.push({
          file: path.relative(process.cwd(), filePath),
          changes: changeCount,
        });

        this.totalChanges += changeCount;

        if (this.options.verbose) {
          console.log(`✅ ${path.basename(filePath)}: ${changeCount} replacements`);
        }
      }
    } catch (error) {
      this.results.push({
        file: path.relative(process.cwd(), filePath),
        changes: 0,
        errors: [(error as Error).message],
      });
    }
  }

  private printReport() {
    console.log('');
    console.log('Migration Report');
    console.log('================');
    console.log(`Total files processed: ${this.results.length}`);
    console.log(`Total changes: ${this.totalChanges}`);

    if (this.results.length > 0) {
      console.log('');
      console.log('Files changed:');
      this.results
        .filter(r => r.changes > 0)
        .sort((a, b) => b.changes - a.changes)
        .forEach(result => {
          console.log(`  ${result.file}: ${result.changes} changes`);
        });
    }

    const errors = this.results.filter(r => r.errors && r.errors.length > 0);
    if (errors.length > 0) {
      console.log('');
      console.log('❌ Errors encountered:');
      errors.forEach(result => {
        console.log(`  ${result.file}: ${result.errors?.join(', ')}`);
      });
    }

    if (this.options.dryRun) {
      console.log('');
      console.log('ℹ️  This was a dry run. No files were modified.');
      console.log('   Run with --live to apply changes.');
    } else {
      console.log('');
      console.log('✨ Migration complete! All teal colors have been replaced with Neural Purple.');
    }
  }
}

// CLI interface
const args = process.argv.slice(2);
const options: MigrationOptions = {
  dryRun: !args.includes('--live'),
  verbose: args.includes('--verbose') || args.includes('-v'),
  pattern: args.find(arg => !arg.startsWith('-')),
};

// Run the migration
const migrator = new ColorMigrationTool(options);
migrator.run().catch(console.error);