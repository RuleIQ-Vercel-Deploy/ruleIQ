#!/usr/bin/env tsx

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// Define cleanup levels
type CleanupLevel = 'dev' | 'staging' | 'prod';

// Files to remove for production
const FILES_TO_REMOVE = [
  'debug-trace.html',
  'manual-auth-test-script.js',
  'validate-auth-flow.py',
  'screenshot-pages.js',
  'fix-eslint-comprehensive.js',
  'verify-visual-refresh.sh',
  'public/debug-trace.html',
];

// Directories to remove for production
const DIRS_TO_REMOVE = [
  'logs',
  'NEEDS SORTING coverage',
  '.serena',
];

// Parse command line arguments
const args = process.argv.slice(2);
const level: CleanupLevel = (args[0] as CleanupLevel) || 'prod';

console.log(`🧹 Running cleanup for ${level} environment...`);

// Function to safely remove file
function removeFile(filePath: string): void {
  const fullPath = path.join(rootDir, filePath);
  if (fs.existsSync(fullPath)) {
    try {
      fs.unlinkSync(fullPath);
      console.log(`✅ Removed file: ${filePath}`);
    } catch (error) {
      console.error(`❌ Failed to remove file ${filePath}:`, error);
    }
  } else {
    console.log(`⚠️  File not found: ${filePath}`);
  }
}

// Function to safely remove directory
function removeDirectory(dirPath: string): void {
  const fullPath = path.join(rootDir, dirPath);
  if (fs.existsSync(fullPath)) {
    try {
      fs.rmSync(fullPath, { recursive: true, force: true });
      console.log(`✅ Removed directory: ${dirPath}`);
    } catch (error) {
      console.error(`❌ Failed to remove directory ${dirPath}:`, error);
    }
  } else {
    console.log(`⚠️  Directory not found: ${dirPath}`);
  }
}

// Main cleanup function
function cleanup(): void {
  console.log('\n📁 Cleaning up development artifacts...\n');

  // Remove files
  if (level === 'prod' || level === 'staging') {
    console.log('Removing development files...');
    FILES_TO_REMOVE.forEach(removeFile);
  }

  // Remove directories
  if (level === 'prod') {
    console.log('\nRemoving development directories...');
    DIRS_TO_REMOVE.forEach(removeDirectory);
  }

  // Update .gitignore if needed
  updateGitignore();

  console.log('\n✨ Cleanup complete!\n');
}

// Function to update .gitignore
function updateGitignore(): void {
  const gitignorePath = path.join(rootDir, '.gitignore');
  const entriesToAdd = [
    '\n# Development artifacts (auto-added by cleanup script)',
    ...FILES_TO_REMOVE,
    ...DIRS_TO_REMOVE,
  ].filter(entry => !entry.includes('/'));

  try {
    let content = '';
    if (fs.existsSync(gitignorePath)) {
      content = fs.readFileSync(gitignorePath, 'utf-8');
    }

    const linesToAdd: string[] = [];
    entriesToAdd.forEach(entry => {
      if (!content.includes(entry)) {
        linesToAdd.push(entry);
      }
    });

    if (linesToAdd.length > 0) {
      fs.appendFileSync(gitignorePath, '\n' + linesToAdd.join('\n'));
      console.log('✅ Updated .gitignore with cleanup entries');
    }
  } catch (error) {
    console.error('❌ Failed to update .gitignore:', error);
  }
}

// Run cleanup
cleanup();

export { cleanup, removeFile, removeDirectory };