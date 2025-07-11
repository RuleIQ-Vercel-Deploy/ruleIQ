#!/usr/bin/env node

/**
 * Memory Leak Test Runner
 * 
 * This script runs all memory leak detection tests and generates a comprehensive report
 */

import { exec } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';

interface TestResult {
  file: string;
  passed: boolean;
  duration: number;
  memoryLeaks?: {
    eventListeners: number;
    timers: number;
    intervals: number;
    abortControllers: number;
  };
  error?: string;
}

async function findMemoryLeakTests(): Promise<string[]> {
  const testDir = path.join(__dirname);
  const files: string[] = [];
  
  async function walkDir(dir: string) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory() && !entry.name.startsWith('.')) {
        await walkDir(fullPath);
      } else if (
        entry.isFile() && 
        (entry.name.includes('memory-leak') || entry.name.includes('leak-detection')) &&
        entry.name.endsWith('.test.tsx')
      ) {
        files.push(fullPath);
      }
    }
  }
  
  await walkDir(testDir);
  return files;
}

function runTest(testFile: string): Promise<TestResult> {
  return new Promise((resolve) => {
    const startTime = Date.now();
    
    exec(
      `npx vitest run ${testFile} --reporter=json`,
      { cwd: path.join(__dirname, '..') },
      (error, stdout, stderr) => {
        const duration = Date.now() - startTime;
        
        if (error) {
          // Try to parse memory leak information from stderr
          const leakMatch = stderr.match(/Memory leaks detected:([\s\S]*?)$/m);
          let memoryLeaks;
          
          if (leakMatch) {
            const leakInfo = leakMatch[1];
            memoryLeaks = {
              eventListeners: (leakInfo.match(/Event Listeners: (\d+)/)?.[1] || '0'),
              timers: (leakInfo.match(/Timers: (\d+)/)?.[1] || '0'),
              intervals: (leakInfo.match(/Intervals: (\d+)/)?.[1] || '0'),
              abortControllers: (leakInfo.match(/AbortControllers: (\d+)/)?.[1] || '0'),
            };
          }
          
          resolve({
            file: testFile,
            passed: false,
            duration,
            memoryLeaks,
            error: error.message
          });
        } else {
          resolve({
            file: testFile,
            passed: true,
            duration
          });
        }
      }
    );
  });
}

async function generateReport(results: TestResult[]) {
  const totalTests = results.length;
  const passedTests = results.filter(r => r.passed).length;
  const failedTests = totalTests - passedTests;
  
  const report = `
# Memory Leak Test Report

## Summary
- **Total Tests**: ${totalTests}
- **Passed**: ${passedTests}
- **Failed**: ${failedTests}
- **Pass Rate**: ${((passedTests / totalTests) * 100).toFixed(2)}%

## Test Results

${results.map(result => {
  const status = result.passed ? '✅' : '❌';
  const fileName = path.basename(result.file);
  let details = `### ${status} ${fileName}
- **Duration**: ${result.duration}ms`;
  
  if (!result.passed && result.memoryLeaks) {
    details += `
- **Memory Leaks Detected**:
  - Event Listeners: ${result.memoryLeaks.eventListeners}
  - Timers: ${result.memoryLeaks.timers}
  - Intervals: ${result.memoryLeaks.intervals}
  - AbortControllers: ${result.memoryLeaks.abortControllers}`;
  }
  
  if (result.error) {
    details += `
- **Error**: ${result.error}`;
  }
  
  return details;
}).join('\n\n')}

## Recommendations

${failedTests > 0 ? `
### For Failed Tests:
1. Check component useEffect cleanup functions
2. Ensure all event listeners are removed on unmount
3. Clear all timers and intervals
4. Abort any ongoing fetch requests
5. Unsubscribe from any subscriptions
` : '✅ All tests passed! No memory leaks detected.'}

---
Generated: ${new Date().toISOString()}
`;

  const reportPath = path.join(__dirname, '..', 'memory-leak-test-report.md');
  await fs.writeFile(reportPath, report);
  console.log(`\nReport saved to: ${reportPath}`);
  
  return report;
}

async function main() {
  console.log('🔍 Finding memory leak tests...\n');
  
  const testFiles = await findMemoryLeakTests();
  console.log(`Found ${testFiles.length} memory leak test files\n`);
  
  console.log('🧪 Running tests...\n');
  
  const results: TestResult[] = [];
  
  for (const testFile of testFiles) {
    const fileName = path.basename(testFile);
    process.stdout.write(`Running ${fileName}... `);
    
    const result = await runTest(testFile);
    results.push(result);
    
    console.log(result.passed ? '✅' : '❌');
  }
  
  console.log('\n📊 Generating report...\n');
  const report = await generateReport(results);
  
  console.log('\n' + report);
  
  // Exit with error code if any tests failed
  process.exit(results.some(r => !r.passed) ? 1 : 0);
}

main().catch(console.error);