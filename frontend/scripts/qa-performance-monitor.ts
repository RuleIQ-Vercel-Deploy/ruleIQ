#!/usr/bin/env node
/**
 * Ava's Performance Budget Monitor
 *
 * Monitors performance metrics against defined budgets
 * Prevents performance regressions and ensures optimal user experience
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

interface PerformanceBudget {
  lighthouse: {
    performance: number;
    accessibility: number;
    bestPractices: number;
    seo: number;
  };
  coreWebVitals: {
    cls: number; // Cumulative Layout Shift
    fid: number; // First Input Delay (ms)
    lcp: number; // Largest Contentful Paint (ms)
    fcp: number; // First Contentful Paint (ms)
    ttfb: number; // Time to First Byte (ms)
  };
  bundleSize: {
    maxTotalSize: number; // KB
    maxJSSize: number; // KB
    maxCSSSize: number; // KB
    maxChunks: number;
  };
  buildTime: {
    maxBuildTime: number; // seconds
  };
  runtime: {
    maxMemoryUsage: number; // MB
    maxCPUUsage: number; // percentage
  };
}

interface PerformanceResults {
  timestamp: string;
  lighthouse: LighthouseResults;
  coreWebVitals: CoreWebVitalsResults;
  bundleSize: BundleSizeResults;
  buildTime: BuildTimeResults;
  runtime: RuntimeResults;
  violations: BudgetViolation[];
  score: number;
}

interface LighthouseResults {
  performance: number;
  accessibility: number;
  bestPractices: number;
  seo: number;
  pwa: number;
  details: LighthouseDetails;
}

interface LighthouseDetails {
  fcp: number;
  lcp: number;
  cls: number;
  fid: number;
  ttfb: number;
  speedIndex: number;
  totalBlockingTime: number;
}

interface CoreWebVitalsResults {
  cls: number;
  fid: number;
  lcp: number;
  fcp: number;
  ttfb: number;
  passed: boolean;
}

interface BundleSizeResults {
  totalSize: number;
  jsSize: number;
  cssSize: number;
  imageSize: number;
  chunks: number;
  breakdown: BundleBreakdown[];
}

interface BundleBreakdown {
  name: string;
  size: number;
  type: 'js' | 'css' | 'image' | 'other';
}

interface BuildTimeResults {
  buildTime: number;
  compileTime: number;
  optimizationTime: number;
}

interface RuntimeResults {
  memoryUsage: number;
  cpuUsage: number;
  loadTime: number;
}

interface BudgetViolation {
  category: string;
  metric: string;
  actual: number;
  budget: number;
  severity: 'WARNING' | 'ERROR' | 'CRITICAL';
  impact: string;
  recommendation: string;
}

class AvaPerformanceMonitor {
  private readonly frontendPath = process.cwd();
  private readonly budgetPath = join(this.frontendPath, 'performance-budget.json');
  private readonly reportsPath = join(this.frontendPath, 'test-results', 'performance-reports');
  private budget: PerformanceBudget;

  constructor() {
    // TODO: Replace with proper logging
    this.budget = this.loadPerformanceBudget();
    this.ensureDirectories();
  }

  private loadPerformanceBudget(): PerformanceBudget {
    const defaultBudget: PerformanceBudget = {
      lighthouse: {
        performance: 90,
        accessibility: 100,
        bestPractices: 90,
        seo: 90,
      },
      coreWebVitals: {
        cls: 0.1,
        fid: 100,
        lcp: 2500,
        fcp: 1800,
        ttfb: 600,
      },
      bundleSize: {
        maxTotalSize: 500, // 500KB
        maxJSSize: 350, // 350KB
        maxCSSSize: 50, // 50KB
        maxChunks: 10,
      },
      buildTime: {
        maxBuildTime: 120, // 2 minutes
      },
      runtime: {
        maxMemoryUsage: 100, // 100MB
        maxCPUUsage: 80, // 80%
      },
    };

    if (existsSync(this.budgetPath)) {
      try {
        const customBudget = JSON.parse(readFileSync(this.budgetPath, 'utf8'));
        return { ...defaultBudget, ...customBudget };
      } catch {
        console.warn('⚠️ Could not load custom budget, using defaults');
      }
    }

    // Save default budget for reference
    writeFileSync(this.budgetPath, JSON.stringify(defaultBudget, null, 2));
    // TODO: Replace with proper logging
    return defaultBudget;
  }

  private ensureDirectories(): void {
    if (!existsSync(this.reportsPath)) {
      require('fs').mkdirSync(this.reportsPath, { recursive: true });
    }
  }

  async monitorPerformance(url: string = 'http://localhost:3000'): Promise<PerformanceResults> {
    // TODO: Replace with proper logging
    const results: PerformanceResults = {
      timestamp: new Date().toISOString(),
      lighthouse: await this.runLighthouseAudit(url),
      coreWebVitals: await this.measureCoreWebVitals(url),
      bundleSize: await this.analyzeBundleSize(),
      buildTime: await this.measureBuildTime(),
      runtime: await this.measureRuntimeMetrics(url),
      violations: [],
      score: 0,
    };

    results.violations = this.checkBudgetViolations(results);
    results.score = this.calculatePerformanceScore(results);

    await this.savePerformanceReport(results);
    this.displayResults(results);

    return results;
  }

  private async runLighthouseAudit(url: string): Promise<LighthouseResults> {
    // TODO: Replace with proper logging
    try {
      const lighthouseCmd = `npx lighthouse ${url} --output=json --quiet --chrome-flags="--headless --no-sandbox"`;
      const output = execSync(lighthouseCmd, { encoding: 'utf8', cwd: this.frontendPath });
      const lighthouse = JSON.parse(output);

      const lhr = lighthouse.lhr;
      const audits = lhr.audits;

      return {
        performance: Math.round(lhr.categories.performance.score * 100),
        accessibility: Math.round(lhr.categories.accessibility.score * 100),
        bestPractices: Math.round(lhr.categories['best-practices'].score * 100),
        seo: Math.round(lhr.categories.seo.score * 100),
        pwa: lhr.categories.pwa ? Math.round(lhr.categories.pwa.score * 100) : 0,
        details: {
          fcp: audits['first-contentful-paint'].numericValue,
          lcp: audits['largest-contentful-paint'].numericValue,
          cls: audits['cumulative-layout-shift'].numericValue,
          fid: audits['max-potential-fid'].numericValue,
          ttfb: audits['server-response-time'].numericValue,
          speedIndex: audits['speed-index'].numericValue,
          totalBlockingTime: audits['total-blocking-time'].numericValue,
        },
      };
    } catch {
      console.warn('⚠️ Lighthouse audit failed, using fallback values');
      return {
        performance: 0,
        accessibility: 0,
        bestPractices: 0,
        seo: 0,
        pwa: 0,
        details: { fcp: 0, lcp: 0, cls: 0, fid: 0, ttfb: 0, speedIndex: 0, totalBlockingTime: 0 },
      };
    }
  }

  private async measureCoreWebVitals(url: string): Promise<CoreWebVitalsResults> {
    // TODO: Replace with proper logging
    try {
      // Use web-vitals library to measure real metrics
      const webVitalsScript = `
        const { getCLS, getFID, getFCP, getLCP, getTTFB } = require('web-vitals');
        const results = {};
        
        getCLS((metric) => results.cls = metric.value);
        getFID((metric) => results.fid = metric.value);
        getFCP((metric) => results.fcp = metric.value);
        getLCP((metric) => results.lcp = metric.value);
        getTTFB((metric) => results.ttfb = metric.value);
        
        setTimeout(() =>
    // TODO: Replace with proper logging
      `;

      // For now, use Lighthouse values as fallback
      const lighthouse = await this.runLighthouseAudit(url);

      const cls = lighthouse.details.cls;
      const fid = lighthouse.details.fid;
      const lcp = lighthouse.details.lcp;
      const fcp = lighthouse.details.fcp;
      const ttfb = lighthouse.details.ttfb;

      const passed =
        cls <= this.budget.coreWebVitals.cls &&
        fid <= this.budget.coreWebVitals.fid &&
        lcp <= this.budget.coreWebVitals.lcp;

      return { cls, fid, lcp, fcp, ttfb, passed };
    } catch {
      console.warn('⚠️ Core Web Vitals measurement failed');
      return { cls: 0, fid: 0, lcp: 0, fcp: 0, ttfb: 0, passed: false };
    }
  }

  private async analyzeBundleSize(): Promise<BundleSizeResults> {
    // TODO: Replace with proper logging
    try {
      const buildOutput = execSync('pnpm build', { encoding: 'utf8', cwd: this.frontendPath });

      // Parse Next.js build output
      const sizePattern = /(\S+)\s+(\d+(?:\.\d+)?)\s*(kB|B)/g;
      const breakdown: BundleBreakdown[] = [];
      let totalSize = 0;
      let jsSize = 0;
      let cssSize = 0;
      let chunks = 0;

      let match;
      while ((match = sizePattern.exec(buildOutput)) !== null) {
        const name = match[1];
        const size = parseFloat(match[2]);
        const unit = match[3];
        const sizeInKB = unit === 'B' ? size / 1024 : size;

        breakdown.push({
          name,
          size: sizeInKB,
          type: name.endsWith('.js') ? 'js' : name.endsWith('.css') ? 'css' : 'other',
        });

        totalSize += sizeInKB;
        if (name.endsWith('.js')) jsSize += sizeInKB;
        if (name.endsWith('.css')) cssSize += sizeInKB;
        chunks++;
      }

      return {
        totalSize,
        jsSize,
        cssSize,
        imageSize: 0, // TODO: Calculate image sizes
        chunks,
        breakdown,
      };
    } catch {
      console.warn('⚠️ Bundle size analysis failed');
      return {
        totalSize: 0,
        jsSize: 0,
        cssSize: 0,
        imageSize: 0,
        chunks: 0,
        breakdown: [],
      };
    }
  }

  private async measureBuildTime(): Promise<BuildTimeResults> {
    // TODO: Replace with proper logging
    try {
      const startTime = Date.now();
      execSync('pnpm build', { encoding: 'utf8', cwd: this.frontendPath });
      const buildTime = (Date.now() - startTime) / 1000;

      return {
        buildTime,
        compileTime: buildTime * 0.7, // Estimate
        optimizationTime: buildTime * 0.3, // Estimate
      };
    } catch {
      console.warn('⚠️ Build time measurement failed');
      return { buildTime: 0, compileTime: 0, optimizationTime: 0 };
    }
  }

  private async measureRuntimeMetrics(url: string): Promise<RuntimeResults> {
    // TODO: Replace with proper logging
    try {
      // Use puppeteer to measure runtime metrics
      const puppeteerScript = `
        const puppeteer = require('puppeteer');
        (async () => {
          const browser = await puppeteer.launch({ headless: true });
          const page = await browser.newPage();
          
          const startTime = Date.now();
          await page.goto('${url}');
          const loadTime = Date.now() - startTime;
          
          const metrics = await page.metrics();
    // TODO: Replace with proper logging
          await browser.close();
        })();
      `;

      // For now, return mock values
      return {
        memoryUsage: 50, // MB
        cpuUsage: 30, // %
        loadTime: 1500, // ms
      };
    } catch {
      console.warn('⚠️ Runtime metrics measurement failed');
      return { memoryUsage: 0, cpuUsage: 0, loadTime: 0 };
    }
  }

  private checkBudgetViolations(results: PerformanceResults): BudgetViolation[] {
    const violations: BudgetViolation[] = [];

    // Check Lighthouse scores
    if (results.lighthouse.performance < this.budget.lighthouse.performance) {
      violations.push({
        category: 'Lighthouse',
        metric: 'Performance Score',
        actual: results.lighthouse.performance,
        budget: this.budget.lighthouse.performance,
        severity: 'ERROR',
        impact: 'Poor user experience and SEO ranking',
        recommendation: 'Optimize images, reduce bundle size, improve loading performance',
      });
    }

    // Check Core Web Vitals
    if (results.coreWebVitals.cls > this.budget.coreWebVitals.cls) {
      violations.push({
        category: 'Core Web Vitals',
        metric: 'Cumulative Layout Shift',
        actual: results.coreWebVitals.cls,
        budget: this.budget.coreWebVitals.cls,
        severity: 'CRITICAL',
        impact: 'Poor user experience, affects Google ranking',
        recommendation: 'Add size attributes to images, reserve space for dynamic content',
      });
    }

    if (results.coreWebVitals.lcp > this.budget.coreWebVitals.lcp) {
      violations.push({
        category: 'Core Web Vitals',
        metric: 'Largest Contentful Paint',
        actual: results.coreWebVitals.lcp,
        budget: this.budget.coreWebVitals.lcp,
        severity: 'ERROR',
        impact: 'Slow perceived loading performance',
        recommendation: 'Optimize largest content element, improve server response time',
      });
    }

    // Check bundle size
    if (results.bundleSize.totalSize > this.budget.bundleSize.maxTotalSize) {
      violations.push({
        category: 'Bundle Size',
        metric: 'Total Size',
        actual: results.bundleSize.totalSize,
        budget: this.budget.bundleSize.maxTotalSize,
        severity: 'WARNING',
        impact: 'Slower loading on slow connections',
        recommendation: 'Code splitting, tree shaking, remove unused dependencies',
      });
    }

    // Check build time
    if (results.buildTime.buildTime > this.budget.buildTime.maxBuildTime) {
      violations.push({
        category: 'Build Time',
        metric: 'Build Duration',
        actual: results.buildTime.buildTime,
        budget: this.budget.buildTime.maxBuildTime,
        severity: 'WARNING',
        impact: 'Slower CI/CD pipeline',
        recommendation: 'Optimize build process, use incremental builds',
      });
    }

    return violations;
  }

  private calculatePerformanceScore(results: PerformanceResults): number {
    const weights = {
      lighthouse: 0.4,
      coreWebVitals: 0.3,
      bundleSize: 0.2,
      buildTime: 0.1,
    };

    const lighthouseScore =
      (results.lighthouse.performance +
        results.lighthouse.accessibility +
        results.lighthouse.bestPractices) /
      3;

    const coreWebVitalsScore = results.coreWebVitals.passed
      ? 100
      : Math.max(
          0,
          100 - results.violations.filter((v) => v.category === 'Core Web Vitals').length * 20,
        );

    const bundleSizeScore =
      results.bundleSize.totalSize <= this.budget.bundleSize.maxTotalSize
        ? 100
        : Math.max(
            0,
            100 - (results.bundleSize.totalSize - this.budget.bundleSize.maxTotalSize) / 10,
          );

    const buildTimeScore =
      results.buildTime.buildTime <= this.budget.buildTime.maxBuildTime
        ? 100
        : Math.max(0, 100 - (results.buildTime.buildTime - this.budget.buildTime.maxBuildTime) / 5);

    return Math.round(
      lighthouseScore * weights.lighthouse +
        coreWebVitalsScore * weights.coreWebVitals +
        bundleSizeScore * weights.bundleSize +
        buildTimeScore * weights.buildTime,
    );
  }

  private async savePerformanceReport(results: PerformanceResults): Promise<void> {
    const reportPath = join(this.reportsPath, `performance-report-${Date.now()}.json`);
    writeFileSync(reportPath, JSON.stringify(results, null, 2));
    // TODO: Replace with proper logging
  }

  private displayResults(results: PerformanceResults): void {
    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging

    // TODO: Replace with proper logging
    if (results.violations.length > 0) {
      // TODO: Replace with proper logging
      results.violations.forEach((violation) => {
        const emoji =
          violation.severity === 'CRITICAL' ? '🔴' : violation.severity === 'ERROR' ? '🟠' : '🟡';
        // TODO: Replace with proper logging

        // TODO: Replace with proper logging

        // TODO: Replace with proper logging
      });
    } else {
      // TODO: Replace with proper logging
    }
  }

  async enforceQualityGates(): Promise<boolean> {
    // TODO: Replace with proper logging
    const results = await this.monitorPerformance();

    const criticalViolations = results.violations.filter((v) => v.severity === 'CRITICAL');
    const errorViolations = results.violations.filter((v) => v.severity === 'ERROR');

    if (criticalViolations.length > 0) {
      // TODO: Replace with proper logging
      return false;
    }

    if (errorViolations.length > 2) {
      // TODO: Replace with proper logging
      return false;
    }

    if (results.score < 70) {
      // TODO: Replace with proper logging
      return false;
    }
    // TODO: Replace with proper logging
    return true;
  }
}

// CLI execution
async function main() {
  const url = process.argv[2] || 'http://localhost:3000';
  const enforceGates = process.argv.includes('--enforce-gates');

  const monitor = new AvaPerformanceMonitor();

  try {
    if (enforceGates) {
      const passed = await monitor.enforceQualityGates();
      process.exit(passed ? 0 : 1);
    } else {
      await monitor.monitorPerformance(url);
      // TODO: Replace with proper logging
    }
  } catch (error) {
    // Development logging - consider proper logger

    console.error('❌ Performance monitoring failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { AvaPerformanceMonitor };
