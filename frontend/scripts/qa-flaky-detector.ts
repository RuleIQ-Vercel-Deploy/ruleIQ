#!/usr/bin/env node
/**
 * Ava's Flaky Test Detection & Management System
 * 
 * Automatically detects flaky tests, analyzes patterns, and suggests fixes
 * Maintains test stability by tracking failure rates and patterns
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

interface FlakyTestData {
  testName: string;
  filePath: string;
  failureRate: number;
  totalRuns: number;
  failures: number;
  lastFailures: TestFailure[];
  firstDetected: string;
  lastUpdated: string;
  suggestedFix: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  pattern: FlakyPattern;
}

interface TestFailure {
  timestamp: string;
  error: string;
  stackTrace: string;
  environment: string;
  duration: number;
}

interface FlakyPattern {
  type: 'TIMING' | 'ASYNC' | 'RACE_CONDITION' | 'ENVIRONMENT' | 'NETWORK' | 'UNKNOWN';
  confidence: number;
  description: string;
  commonErrors: string[];
}

interface FlakyReport {
  timestamp: string;
  totalTests: number;
  flakyTests: number;
  newFlakyTests: FlakyTestData[];
  improvedTests: FlakyTestData[];
  criticalTests: FlakyTestData[];
  recommendations: string[];
}

class AvaFlakyTestDetector {
  private readonly frontendPath = process.cwd();
  private readonly flakyDataPath = join(this.frontendPath, 'test-results', 'flaky-tests.json');
  private readonly reportsPath = join(this.frontendPath, 'test-results', 'flaky-reports');
  private flakyTests: Map<string, FlakyTestData> = new Map();

  constructor() {
    // TODO: Replace with proper logging
    this.ensureDirectories();
    this.loadExistingData();
  }

  private ensureDirectories(): void {
    const dirs = [
      join(this.frontendPath, 'test-results'),
      this.reportsPath
    ];

    dirs.forEach(dir => {
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }
    });
  }

  private loadExistingData(): void {
    if (existsSync(this.flakyDataPath)) {
      try {
        const data = JSON.parse(readFileSync(this.flakyDataPath, 'utf8'));
        this.flakyTests = new Map(Object.entries(data));
    // TODO: Replace with proper logging
      } catch {
        console.warn('⚠️ Could not load existing flaky test data');
      }
    }
  }

  async detectFlakyTests(runs: number = 10): Promise<FlakyReport> {
    // TODO: Replace with proper logging
    const testResults = await this.runMultipleTestSessions(runs);
    const flakyTests = this.analyzeFlakyPatterns(testResults);
    
    this.updateFlakyDatabase(flakyTests);
    
    const report = this.generateFlakyReport(flakyTests);
    await this.saveFlakyReport(report);
    
    return report;
  }

  private async runMultipleTestSessions(runs: number): Promise<Map<string, TestResult[]>> {
    const testResults = new Map<string, TestResult[]>();
    
    for (let i = 1; i <= runs; i++) {
    // TODO: Replace with proper logging
      try {
        const output = execSync('pnpm test --run --reporter=json', { 
          encoding: 'utf8',
          cwd: this.frontendPath 
        });
        
        const results = this.parseTestResults(output, i);
        
        results.forEach((result, testKey) => {
          if (!testResults.has(testKey)) {
            testResults.set(testKey, []);
          }
          testResults.get(testKey)!.push(result);
        });
        
      } catch (error: unknown) {
        console.warn(`⚠️ Test session ${i} had failures, parsing partial results...`);
        
        // Parse failed test results
        const failedResults = this.parseFailedTestResults(error.stdout || '', i);
        failedResults.forEach((result, testKey) => {
          if (!testResults.has(testKey)) {
            testResults.set(testKey, []);
          }
          testResults.get(testKey)!.push(result);
        });
      }
      
      // Small delay between runs to avoid resource contention
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    return testResults;
  }

  private parseTestResults(output: string, sessionNumber: number): Map<string, TestResult> {
    const results = new Map<string, TestResult>();
    
    try {
      const jsonOutput = JSON.parse(output);
      
      if (jsonOutput.testResults) {
        jsonOutput.testResults.forEach((fileResult: any) => {
          fileResult.assertionResults?.forEach((test: any) => {
            const testKey = `${fileResult.name}::${test.title}`;
            
            results.set(testKey, {
              testName: test.title,
              filePath: fileResult.name,
              status: test.status,
              duration: test.duration || 0,
              error: test.failureMessages?.[0] || null,
              sessionNumber
            });
          });
        });
      }
    } catch {
      console.warn('⚠️ Could not parse JSON test results, using fallback parsing');
    }
    
    return results;
  }

  private parseFailedTestResults(output: string, sessionNumber: number): Map<string, TestResult> {
    const results = new Map<string, TestResult>();
    
    // Parse failed test output using regex patterns
    const failurePattern = /FAIL\s+(.+?)\n.*?✕\s+(.+?)\n/gs;
    let match;
    
    while ((match = failurePattern.exec(output)) !== null) {
      const filePath = match[1].trim();
      const testName = match[2].trim();
      const testKey = `${filePath}::${testName}`;
      
      results.set(testKey, {
        testName,
        filePath,
        status: 'failed',
        duration: 0,
        error: 'Test failed during flaky detection run',
        sessionNumber
      });
    }
    
    return results;
  }

  private analyzeFlakyPatterns(testResults: Map<string, TestResult[]>): FlakyTestData[] {
    const flakyTests: FlakyTestData[] = [];
    
    testResults.forEach((results, testKey) => {
      const failures = results.filter(r => r.status === 'failed');
      const totalRuns = results.length;
      const failureRate = failures.length / totalRuns;
      
      // Consider a test flaky if it fails between 5% and 95% of the time
      if (failureRate > 0.05 && failureRate < 0.95 && totalRuns >= 5) {
        const [filePath, testName] = testKey.split('::');
        
        const pattern = this.identifyFlakyPattern(failures);
        const suggestedFix = this.generateSuggestedFix(pattern, failures);
        const severity = this.calculateSeverity(failureRate, failures.length);
        
        const flakyTest: FlakyTestData = {
          testName,
          filePath,
          failureRate,
          totalRuns,
          failures: failures.length,
          lastFailures: failures.slice(-3).map(f => ({
            timestamp: new Date().toISOString(),
            error: f.error || 'Unknown error',
            stackTrace: f.error || '',
            environment: 'local',
            duration: f.duration
          })),
          firstDetected: new Date().toISOString(),
          lastUpdated: new Date().toISOString(),
          suggestedFix,
          severity,
          pattern
        };
        
        flakyTests.push(flakyTest);
      }
    });
    
    return flakyTests;
  }

  private identifyFlakyPattern(failures: TestResult[]): FlakyPattern {
    const errors = failures.map(f => f.error || '').filter(e => e);
    const commonErrors = this.findCommonErrors(errors);
    
    // Analyze error patterns
    if (errors.some(e => e.includes('timeout') || e.includes('Timeout'))) {
      return {
        type: 'TIMING',
        confidence: 0.8,
        description: 'Test appears to have timing-related issues',
        commonErrors
      };
    }
    
    if (errors.some(e => e.includes('Promise') || e.includes('async') || e.includes('await'))) {
      return {
        type: 'ASYNC',
        confidence: 0.7,
        description: 'Test has asynchronous operation issues',
        commonErrors
      };
    }
    
    if (errors.some(e => e.includes('race') || e.includes('concurrent'))) {
      return {
        type: 'RACE_CONDITION',
        confidence: 0.9,
        description: 'Test has race condition issues',
        commonErrors
      };
    }
    
    if (errors.some(e => e.includes('network') || e.includes('fetch') || e.includes('request'))) {
      return {
        type: 'NETWORK',
        confidence: 0.6,
        description: 'Test has network-related issues',
        commonErrors
      };
    }
    
    return {
      type: 'UNKNOWN',
      confidence: 0.3,
      description: 'Flaky pattern could not be determined',
      commonErrors
    };
  }

  private findCommonErrors(errors: string[]): string[] {
    const errorCounts = new Map<string, number>();
    
    errors.forEach(error => {
      // Extract key phrases from errors
      const phrases = error.split(/[.!?]/).map(p => p.trim()).filter(p => p.length > 10);
      phrases.forEach(phrase => {
        errorCounts.set(phrase, (errorCounts.get(phrase) || 0) + 1);
      });
    });
    
    // Return phrases that appear in multiple errors
    return Array.from(errorCounts.entries())
      .filter(([_, count]) => count > 1)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([phrase, _]) => phrase);
  }

  private generateSuggestedFix(pattern: FlakyPattern, failures: TestResult[]): string {
    switch (pattern.type) {
      case 'TIMING':
        return 'Consider increasing timeouts, using waitFor() helpers, or adding proper async/await handling';
      
      case 'ASYNC':
        return 'Ensure all async operations are properly awaited and use proper async testing patterns';
      
      case 'RACE_CONDITION':
        return 'Add proper synchronization, use act() wrapper, or mock time-dependent operations';
      
      case 'NETWORK':
        return 'Mock network requests with MSW, add proper error handling, or use stable test data';
      
      case 'ENVIRONMENT':
        return 'Ensure test environment is properly isolated and reset between runs';
      
      default:
        return 'Review test for non-deterministic behavior, add proper cleanup, and ensure test isolation';
    }
  }

  private calculateSeverity(failureRate: number, failureCount: number): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
    if (failureRate > 0.5 || failureCount > 7) return 'CRITICAL';
    if (failureRate > 0.3 || failureCount > 5) return 'HIGH';
    if (failureRate > 0.15 || failureCount > 3) return 'MEDIUM';
    return 'LOW';
  }

  private updateFlakyDatabase(newFlakyTests: FlakyTestData[]): void {
    newFlakyTests.forEach(test => {
      const key = `${test.filePath}::${test.testName}`;
      
      if (this.flakyTests.has(key)) {
        // Update existing flaky test
        const existing = this.flakyTests.get(key)!;
        existing.failureRate = test.failureRate;
        existing.totalRuns += test.totalRuns;
        existing.failures += test.failures;
        existing.lastFailures = test.lastFailures;
        existing.lastUpdated = test.lastUpdated;
        existing.pattern = test.pattern;
        existing.suggestedFix = test.suggestedFix;
        existing.severity = test.severity;
      } else {
        // Add new flaky test
        this.flakyTests.set(key, test);
      }
    });
    
    // Save updated database
    const dataToSave = Object.fromEntries(this.flakyTests);
    writeFileSync(this.flakyDataPath, JSON.stringify(dataToSave, null, 2));
    // TODO: Replace with proper logging
  }

  private generateFlakyReport(newFlakyTests: FlakyTestData[]): FlakyReport {
    const allFlakyTests = Array.from(this.flakyTests.values());
    const criticalTests = allFlakyTests.filter(t => t.severity === 'CRITICAL');
    
    const recommendations = this.generateRecommendations(allFlakyTests);
    
    return {
      timestamp: new Date().toISOString(),
      totalTests: this.flakyTests.size,
      flakyTests: allFlakyTests.length,
      newFlakyTests,
      improvedTests: [], // TODO: Track improved tests
      criticalTests,
      recommendations
    };
  }

  private generateRecommendations(flakyTests: FlakyTestData[]): string[] {
    const recommendations: string[] = [];
    
    const criticalCount = flakyTests.filter(t => t.severity === 'CRITICAL').length;
    if (criticalCount > 0) {
      recommendations.push(`🚨 ${criticalCount} critical flaky tests need immediate attention`);
    }
    
    const timingIssues = flakyTests.filter(t => t.pattern.type === 'TIMING').length;
    if (timingIssues > 2) {
      recommendations.push(`⏱️ ${timingIssues} tests have timing issues - consider reviewing timeout configurations`);
    }
    
    const asyncIssues = flakyTests.filter(t => t.pattern.type === 'ASYNC').length;
    if (asyncIssues > 2) {
      recommendations.push(`🔄 ${asyncIssues} tests have async issues - review async/await patterns`);
    }
    
    if (flakyTests.length > 10) {
      recommendations.push('📊 High number of flaky tests detected - consider test environment review');
    }
    
    return recommendations;
  }

  private async saveFlakyReport(report: FlakyReport): Promise<void> {
    const reportPath = join(this.reportsPath, `flaky-report-${Date.now()}.json`);
    writeFileSync(reportPath, JSON.stringify(report, null, 2));
    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging
    if (report.recommendations.length > 0) {
    // TODO: Replace with proper logging
      report.recommendations.forEach(rec =>
    // TODO: Replace with proper logging
    }
  }

  async autoTagFlakyTests(): Promise<void> {
    // TODO: Replace with proper logging
    const flakyTests = Array.from(this.flakyTests.values());
    
    for (const test of flakyTests) {
      await this.addFlakyTestComment(test);
    }
    // TODO: Replace with proper logging
  }

  private async addFlakyTestComment(test: FlakyTestData): Promise<void> {
    try {
      const filePath = join(this.frontendPath, test.filePath);
      const content = readFileSync(filePath, 'utf8');
      
      const flakyComment = `
// 🔍 FLAKY TEST DETECTED by Ava
// Failure Rate: ${(test.failureRate * 100).toFixed(1)}%
// Pattern: ${test.pattern.type}
// Suggested Fix: ${test.suggestedFix}
// Last Updated: ${test.lastUpdated}
`;
      
      // Add comment before the test if not already present
      if (!content.includes('FLAKY TEST DETECTED by Ava')) {
        const testPattern = new RegExp(`(test|it)\\s*\\(\\s*['"\`]${test.testName}['"\`]`, 'g');
        const updatedContent = content.replace(testPattern, `${flakyComment}$&`);
        
        if (updatedContent !== content) {
          writeFileSync(filePath, updatedContent);
    // TODO: Replace with proper logging
        }
      }
    } catch {
      console.warn(`⚠️ Could not tag test ${test.testName}:`, _error);
    }
  }
}

interface TestResult {
  testName: string;
  filePath: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error: string | null;
  sessionNumber: number;
}

// CLI execution
async function main() {
  const runs = parseInt(process.argv[2]) || 10;
  
  const detector = new AvaFlakyTestDetector();
  
  try {
    const report = await detector.detectFlakyTests(runs);
    
    if (report.criticalTests.length > 0) {
    // TODO: Replace with proper logging
      await detector.autoTagFlakyTests();
    }
    // TODO: Replace with proper logging
  } catch {
    // Development logging - consider proper logger

    console.error('❌ Flaky test detection failed:', _error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { AvaFlakyTestDetector };
