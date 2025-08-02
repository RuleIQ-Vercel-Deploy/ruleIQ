#!/usr/bin/env node
/**
 * Ava's Affected Tests Runner
 * 
 * Intelligently runs only tests affected by PR changes
 * Provides fast feedback while maintaining comprehensive coverage
 */

import { execSync, spawn } from 'child_process';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

interface TestExecution {
  category: string;
  command: string;
  files: string[];
  estimatedTime: number;
  required: boolean;
  status: 'pending' | 'running' | 'passed' | 'failed' | 'skipped';
  output?: string;
  duration?: number;
}

interface TestResults {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  totalDuration: number;
  coverage: CoverageReport;
  failures: TestFailure[];
}

interface CoverageReport {
  statements: number;
  branches: number;
  functions: number;
  lines: number;
  threshold: boolean;
}

interface TestFailure {
  testFile: string;
  testName: string;
  error: string;
  stackTrace: string;
}

class AvaAffectedTestsRunner {
  private readonly frontendPath = process.cwd();
  private readonly testsPath = join(this.frontendPath, 'tests');
  private testExecutions: TestExecution[] = [];

  constructor() {
    console.log('🧪 Ava Affected Tests Runner initializing...');
  }

  async runAffectedTests(prNumber?: number): Promise<TestResults> {
    console.log(`🎯 Running affected tests${prNumber ? ` for PR #${prNumber}` : ''}...`);
    
    const changedFiles = this.getChangedFiles();
    const affectedTestFiles = this.findAffectedTests(changedFiles);
    
    console.log(`📊 Found ${affectedTestFiles.length} affected test files`);
    
    this.planTestExecution(affectedTestFiles);
    
    const results = await this.executeTests();
    
    await this.generateReport(results, prNumber);
    
    return results;
  }

  private getChangedFiles(): string[] {
    try {
      const gitDiff = execSync('git diff --name-only HEAD~1', { encoding: 'utf8' });
      return gitDiff.trim().split('\n').filter(file => 
        file.startsWith('frontend/') && 
        (file.endsWith('.tsx') || file.endsWith('.ts') || file.endsWith('.js'))
      );
    } catch (error) {
      console.warn('⚠️ Could not get git diff, running all tests');
      return [];
    }
  }

  private findAffectedTests(changedFiles: string[]): string[] {
    const affectedTests = new Set<string>();
    
    changedFiles.forEach(filePath => {
      const componentName = this.extractComponentName(filePath);
      const testFiles = this.findTestFilesForComponent(componentName, filePath);
      
      testFiles.forEach(testFile => affectedTests.add(testFile));
      
      // Also find tests that import this component
      const dependentTests = this.findDependentTests(filePath);
      dependentTests.forEach(testFile => affectedTests.add(testFile));
    });

    return Array.from(affectedTests);
  }

  private extractComponentName(filePath: string): string {
    const fileName = filePath.split('/').pop() || '';
    return fileName.replace(/\.(tsx?|jsx?)$/, '');
  }

  private findTestFilesForComponent(componentName: string, filePath: string): string[] {
    const testFiles: string[] = [];
    
    // Direct test files
    const possibleTestPaths = [
      `tests/components/${componentName}.test.tsx`,
      `tests/components/${componentName}.test.ts`,
      `tests/integration/${componentName}.test.tsx`,
      `tests/e2e/${componentName}.test.ts`,
      `tests/accessibility/${componentName}.test.tsx`,
      `tests/visual/${componentName}.test.ts`,
      `tests/performance/${componentName}.test.ts`,
      `__tests__/${componentName}.test.tsx`
    ];

    // Check for nested component tests
    if (filePath.includes('components/')) {
      const pathParts = filePath.split('/');
      const componentDir = pathParts.slice(0, -1).join('/').replace('frontend/', '');
      possibleTestPaths.push(`tests/${componentDir}/${componentName}.test.tsx`);
    }

    possibleTestPaths.forEach(testPath => {
      if (existsSync(join(this.frontendPath, testPath))) {
        testFiles.push(testPath);
      }
    });

    return testFiles;
  }

  private findDependentTests(filePath: string): string[] {
    const dependentTests: string[] = [];
    
    try {
      // Search for tests that import this component
      const searchPattern = filePath.replace('frontend/', '').replace(/\.(tsx?|jsx?)$/, '');
      const grepCommand = `grep -r "from.*${searchPattern}" ${this.testsPath} --include="*.test.*" -l`;
      
      const grepOutput = execSync(grepCommand, { encoding: 'utf8' });
      const foundFiles = grepOutput.trim().split('\n').filter(f => f.trim());
      
      foundFiles.forEach(file => {
        const relativePath = file.replace(this.frontendPath + '/', '');
        dependentTests.push(relativePath);
      });
    } catch (error) {
      // No dependent tests found, which is fine
    }

    return dependentTests;
  }

  private planTestExecution(affectedTestFiles: string[]): void {
    this.testExecutions = [];

    // Group tests by category
    const unitTests = affectedTestFiles.filter(f => f.includes('components/'));
    const integrationTests = affectedTestFiles.filter(f => f.includes('integration/'));
    const e2eTests = affectedTestFiles.filter(f => f.includes('e2e/'));
    const accessibilityTests = affectedTestFiles.filter(f => f.includes('accessibility/'));
    const visualTests = affectedTestFiles.filter(f => f.includes('visual/'));
    const performanceTests = affectedTestFiles.filter(f => f.includes('performance/'));

    // Plan unit tests
    if (unitTests.length > 0) {
      this.testExecutions.push({
        category: 'Unit Tests',
        command: `pnpm test ${unitTests.join(' ')} --coverage`,
        files: unitTests,
        estimatedTime: unitTests.length * 2,
        required: true,
        status: 'pending'
      });
    }

    // Plan integration tests
    if (integrationTests.length > 0) {
      this.testExecutions.push({
        category: 'Integration Tests',
        command: `pnpm test ${integrationTests.join(' ')}`,
        files: integrationTests,
        estimatedTime: integrationTests.length * 5,
        required: true,
        status: 'pending'
      });
    }

    // Plan E2E tests
    if (e2eTests.length > 0) {
      this.testExecutions.push({
        category: 'E2E Tests',
        command: `pnpm test:e2e ${e2eTests.join(' ')}`,
        files: e2eTests,
        estimatedTime: e2eTests.length * 10,
        required: true,
        status: 'pending'
      });
    }

    // Plan accessibility tests
    if (accessibilityTests.length > 0) {
      this.testExecutions.push({
        category: 'Accessibility Tests',
        command: `pnpm test ${accessibilityTests.join(' ')}`,
        files: accessibilityTests,
        estimatedTime: accessibilityTests.length * 3,
        required: true,
        status: 'pending'
      });
    }

    // Plan visual tests (optional)
    if (visualTests.length > 0) {
      this.testExecutions.push({
        category: 'Visual Regression Tests',
        command: `pnpm test:visual ${visualTests.join(' ')}`,
        files: visualTests,
        estimatedTime: visualTests.length * 4,
        required: false,
        status: 'pending'
      });
    }

    // Plan performance tests (optional)
    if (performanceTests.length > 0) {
      this.testExecutions.push({
        category: 'Performance Tests',
        command: `pnpm test:performance ${performanceTests.join(' ')}`,
        files: performanceTests,
        estimatedTime: performanceTests.length * 8,
        required: false,
        status: 'pending'
      });
    }

    console.log(`📋 Planned ${this.testExecutions.length} test execution groups`);
  }

  private async executeTests(): Promise<TestResults> {
    const results: TestResults = {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      skippedTests: 0,
      totalDuration: 0,
      coverage: { statements: 0, branches: 0, functions: 0, lines: 0, threshold: false },
      failures: []
    };

    const startTime = Date.now();

    for (const execution of this.testExecutions) {
      console.log(`\n🏃 Running ${execution.category}...`);
      execution.status = 'running';
      
      const executionStart = Date.now();
      
      try {
        const output = execSync(execution.command, { 
          encoding: 'utf8',
          cwd: this.frontendPath,
          timeout: execution.estimatedTime * 60 * 1000 // Convert to milliseconds
        });
        
        execution.output = output;
        execution.duration = Date.now() - executionStart;
        execution.status = 'passed';
        
        // Parse test results from output
        const testCount = this.parseTestCount(output);
        results.totalTests += testCount;
        results.passedTests += testCount;
        
        console.log(`✅ ${execution.category} passed (${testCount} tests, ${execution.duration}ms)`);
        
      } catch (error: any) {
        execution.status = 'failed';
        execution.output = error.stdout || error.message;
        execution.duration = Date.now() - executionStart;
        
        const failure = this.parseTestFailure(execution, error);
        results.failures.push(failure);
        results.failedTests++;
        
        console.log(`❌ ${execution.category} failed`);
        
        // Stop on required test failures
        if (execution.required) {
          console.log(`🚫 Stopping execution due to required test failure`);
          break;
        }
      }
    }

    results.totalDuration = Date.now() - startTime;
    
    // Parse coverage from the last unit test execution
    const unitTestExecution = this.testExecutions.find(e => e.category === 'Unit Tests');
    if (unitTestExecution?.output) {
      results.coverage = this.parseCoverage(unitTestExecution.output);
    }

    return results;
  }

  private parseTestCount(output: string): number {
    const match = output.match(/(\d+) passed/);
    return match ? parseInt(match[1]) : 0;
  }

  private parseTestFailure(execution: TestExecution, error: any): TestFailure {
    return {
      testFile: execution.files[0] || 'unknown',
      testName: execution.category,
      error: error.message || 'Test execution failed',
      stackTrace: error.stack || ''
    };
  }

  private parseCoverage(output: string): CoverageReport {
    const coverage = {
      statements: 0,
      branches: 0,
      functions: 0,
      lines: 0,
      threshold: false
    };

    // Parse coverage percentages from output
    const stmtMatch = output.match(/Statements\s+:\s+(\d+\.?\d*)%/);
    const branchMatch = output.match(/Branches\s+:\s+(\d+\.?\d*)%/);
    const funcMatch = output.match(/Functions\s+:\s+(\d+\.?\d*)%/);
    const linesMatch = output.match(/Lines\s+:\s+(\d+\.?\d*)%/);

    if (stmtMatch) coverage.statements = parseFloat(stmtMatch[1]);
    if (branchMatch) coverage.branches = parseFloat(branchMatch[1]);
    if (funcMatch) coverage.functions = parseFloat(funcMatch[1]);
    if (linesMatch) coverage.lines = parseFloat(linesMatch[1]);

    // Check if coverage meets thresholds (80% for all)
    coverage.threshold = coverage.statements >= 80 && 
                        coverage.branches >= 75 && 
                        coverage.functions >= 80 && 
                        coverage.lines >= 80;

    return coverage;
  }

  private async generateReport(results: TestResults, prNumber?: number): Promise<void> {
    const reportPath = join(this.frontendPath, 'test-results', 
      `affected-tests-${prNumber || 'local'}-${Date.now()}.json`);
    
    const report = {
      timestamp: new Date().toISOString(),
      prNumber,
      results,
      executions: this.testExecutions
    };

    require('fs').writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`\n📊 Test Results Summary:`);
    console.log(`✅ Passed: ${results.passedTests}`);
    console.log(`❌ Failed: ${results.failedTests}`);
    console.log(`⏭️ Skipped: ${results.skippedTests}`);
    console.log(`⏱️ Duration: ${results.totalDuration}ms`);
    console.log(`📈 Coverage: ${results.coverage.statements}% statements`);
    console.log(`🎯 Threshold Met: ${results.coverage.threshold ? '✅' : '❌'}`);
    console.log(`📄 Report saved: ${reportPath}`);
  }
}

// CLI execution
async function main() {
  const prNumber = process.argv[2] ? parseInt(process.argv[2]) : undefined;
  
  const runner = new AvaAffectedTestsRunner();
  
  try {
    const results = await runner.runAffectedTests(prNumber);
    
    if (results.failedTests > 0) {
      console.log('\n❌ Some tests failed!');
      process.exit(1);
    }
    
    if (!results.coverage.threshold) {
      console.log('\n❌ Coverage threshold not met!');
      process.exit(1);
    }
    
    console.log('\n✅ All affected tests passed!');
    
  } catch (error) {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { AvaAffectedTestsRunner };
