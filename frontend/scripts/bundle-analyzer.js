#!/usr/bin/env node

/**
 * Bundle Size Analyzer for ruleIQ Frontend
 *
 * This script analyzes the production build bundle sizes and generates reports
 * to help monitor and optimize the application's performance.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk');

// Bundle size thresholds (in KB)
const THRESHOLDS = {
  // Individual chunk thresholds
  MAIN_CHUNK: 250, // Main application bundle
  VENDOR_CHUNK: 500, // Third-party libraries
  PAGE_CHUNK: 100, // Individual page chunks
  COMPONENT_CHUNK: 50, // Component chunks

  // Total bundle thresholds
  TOTAL_JS: 800, // Total JavaScript
  TOTAL_CSS: 100, // Total CSS
  TOTAL_ASSETS: 1000, // Total assets

  // Critical thresholds
  FIRST_LOAD_JS: 300, // First load JS (critical)
  GZIP_RATIO: 0.3, // Minimum gzip compression ratio
};

// File patterns to analyze
const PATTERNS = {
  JS_FILES: /\.js$/,
  CSS_FILES: /\.css$/,
  CHUNK_FILES: /chunk\./,
  PAGE_FILES: /pages\//,
  VENDOR_FILES: /(vendor|node_modules)/,
};

class BundleAnalyzer {
  constructor() {
    this.buildDir = path.join(process.cwd(), '.next');
    this.staticDir = path.join(this.buildDir, 'static');
    this.results = {
      chunks: [],
      totals: {},
      violations: [],
      recommendations: [],
    };
  }

  async analyze() {
    console.log(chalk.blue('🔍 Analyzing bundle sizes...\n'));

    try {
      // Ensure build exists
      if (!fs.existsSync(this.buildDir)) {
        throw new Error('Build directory not found. Run "pnpm build" first.');
      }

      // Analyze chunks
      await this.analyzeChunks();

      // Calculate totals
      this.calculateTotals();

      // Check thresholds
      this.checkThresholds();

      // Generate recommendations
      this.generateRecommendations();

      // Generate reports
      this.generateReport();
      this.generateJSONReport();

      // Exit with appropriate code
      process.exit(this.results.violations.length > 0 ? 1 : 0);
    } catch (error) {
      console.error(chalk.red('❌ Bundle analysis failed:'), error.message);
      process.exit(1);
    }
  }

  async analyzeChunks() {
    const chunks = [];

    // Analyze JavaScript chunks
    const jsDir = path.join(this.staticDir, 'chunks');
    if (fs.existsSync(jsDir)) {
      const jsFiles = this.getFilesRecursively(jsDir, PATTERNS.JS_FILES);
      chunks.push(...this.analyzeFiles(jsFiles, 'js'));
    }

    // Analyze CSS chunks
    const cssDir = path.join(this.staticDir, 'css');
    if (fs.existsSync(cssDir)) {
      const cssFiles = this.getFilesRecursively(cssDir, PATTERNS.CSS_FILES);
      chunks.push(...this.analyzeFiles(cssFiles, 'css'));
    }

    // Analyze page chunks
    const pagesDir = path.join(this.staticDir, 'chunks', 'pages');
    if (fs.existsSync(pagesDir)) {
      const pageFiles = this.getFilesRecursively(pagesDir, PATTERNS.JS_FILES);
      chunks.push(...this.analyzeFiles(pageFiles, 'page'));
    }

    this.results.chunks = chunks.sort((a, b) => b.size - a.size);
  }

  getFilesRecursively(dir, pattern) {
    const files = [];

    if (!fs.existsSync(dir)) return files;

    const items = fs.readdirSync(dir);

    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        files.push(...this.getFilesRecursively(fullPath, pattern));
      } else if (pattern.test(item)) {
        files.push(fullPath);
      }
    }

    return files;
  }

  analyzeFiles(files, type) {
    return files.map((filePath) => {
      const stat = fs.statSync(filePath);
      const relativePath = path.relative(this.buildDir, filePath);
      const name = path.basename(filePath);

      // Get gzipped size if possible
      let gzipSize = null;
      try {
        const gzipCommand = `gzip -c "${filePath}" | wc -c`;
        gzipSize = parseInt(execSync(gzipCommand, { encoding: 'utf8' }).trim());
      } catch (error) {
        // Gzip not available or failed
      }

      return {
        name,
        path: relativePath,
        size: stat.size,
        sizeKB: Math.round((stat.size / 1024) * 100) / 100,
        gzipSize,
        gzipSizeKB: gzipSize ? Math.round((gzipSize / 1024) * 100) / 100 : null,
        compressionRatio: gzipSize ? gzipSize / stat.size : null,
        type,
        isVendor: PATTERNS.VENDOR_FILES.test(relativePath),
        isPage: PATTERNS.PAGE_FILES.test(relativePath),
        isChunk: PATTERNS.CHUNK_FILES.test(name),
      };
    });
  }

  calculateTotals() {
    const totals = {
      totalJS: 0,
      totalCSS: 0,
      totalAssets: 0,
      totalGzipJS: 0,
      totalGzipCSS: 0,
      chunkCount: 0,
      vendorSize: 0,
      pageSize: 0,
      firstLoadJS: 0,
    };

    for (const chunk of this.results.chunks) {
      if (chunk.type === 'js') {
        totals.totalJS += chunk.size;
        totals.totalGzipJS += chunk.gzipSize || 0;

        if (chunk.isVendor) {
          totals.vendorSize += chunk.size;
        }

        if (chunk.isPage) {
          totals.pageSize += chunk.size;
        }

        // Estimate first load JS (main + vendor chunks)
        if (chunk.name.includes('main') || chunk.name.includes('vendor')) {
          totals.firstLoadJS += chunk.size;
        }
      } else if (chunk.type === 'css') {
        totals.totalCSS += chunk.size;
        totals.totalGzipCSS += chunk.gzipSize || 0;
      }

      totals.totalAssets += chunk.size;
      totals.chunkCount++;
    }

    // Convert to KB
    Object.keys(totals).forEach((key) => {
      if (key !== 'chunkCount') {
        totals[key + 'KB'] = Math.round((totals[key] / 1024) * 100) / 100;
      }
    });

    this.results.totals = totals;
  }

  checkThresholds() {
    const { totals, chunks } = this.results;
    const violations = [];

    // Check total thresholds
    if (totals.totalJSKB > THRESHOLDS.TOTAL_JS) {
      violations.push({
        type: 'total_js',
        message: `Total JavaScript size (${totals.totalJSKB}KB) exceeds threshold (${THRESHOLDS.TOTAL_JS}KB)`,
        severity: 'error',
        actual: totals.totalJSKB,
        threshold: THRESHOLDS.TOTAL_JS,
      });
    }

    if (totals.totalCSSKB > THRESHOLDS.TOTAL_CSS) {
      violations.push({
        type: 'total_css',
        message: `Total CSS size (${totals.totalCSSKB}KB) exceeds threshold (${THRESHOLDS.TOTAL_CSS}KB)`,
        severity: 'warning',
        actual: totals.totalCSSKB,
        threshold: THRESHOLDS.TOTAL_CSS,
      });
    }

    if (totals.firstLoadJSKB > THRESHOLDS.FIRST_LOAD_JS) {
      violations.push({
        type: 'first_load_js',
        message: `First load JavaScript (${totals.firstLoadJSKB}KB) exceeds threshold (${THRESHOLDS.FIRST_LOAD_JS}KB)`,
        severity: 'error',
        actual: totals.firstLoadJSKB,
        threshold: THRESHOLDS.FIRST_LOAD_JS,
      });
    }

    // Check individual chunk thresholds
    for (const chunk of chunks) {
      let threshold;

      if (chunk.isVendor) {
        threshold = THRESHOLDS.VENDOR_CHUNK;
      } else if (chunk.isPage) {
        threshold = THRESHOLDS.PAGE_CHUNK;
      } else if (chunk.name.includes('main')) {
        threshold = THRESHOLDS.MAIN_CHUNK;
      } else {
        threshold = THRESHOLDS.COMPONENT_CHUNK;
      }

      if (chunk.sizeKB > threshold) {
        violations.push({
          type: 'chunk_size',
          message: `Chunk "${chunk.name}" (${chunk.sizeKB}KB) exceeds threshold (${threshold}KB)`,
          severity: 'warning',
          actual: chunk.sizeKB,
          threshold,
          chunk: chunk.name,
        });
      }

      // Check compression ratio
      if (chunk.compressionRatio && chunk.compressionRatio > THRESHOLDS.GZIP_RATIO) {
        violations.push({
          type: 'compression',
          message: `Chunk "${chunk.name}" has poor compression ratio (${Math.round(chunk.compressionRatio * 100)}%)`,
          severity: 'info',
          actual: chunk.compressionRatio,
          threshold: THRESHOLDS.GZIP_RATIO,
          chunk: chunk.name,
        });
      }
    }

    this.results.violations = violations;
  }

  generateRecommendations() {
    const { totals, chunks, violations } = this.results;
    const recommendations = [];

    // Large vendor chunks
    const largeVendorChunks = chunks.filter((c) => c.isVendor && c.sizeKB > 200);
    if (largeVendorChunks.length > 0) {
      recommendations.push({
        type: 'vendor_optimization',
        message: 'Consider code splitting large vendor libraries',
        details: largeVendorChunks.map((c) => `${c.name}: ${c.sizeKB}KB`),
      });
    }

    // Many small chunks
    const smallChunks = chunks.filter((c) => c.sizeKB < 10);
    if (smallChunks.length > 10) {
      recommendations.push({
        type: 'chunk_consolidation',
        message: `Consider consolidating ${smallChunks.length} small chunks`,
        details: ['Small chunks increase HTTP overhead'],
      });
    }

    // Poor compression
    const poorlyCompressed = chunks.filter((c) => c.compressionRatio > 0.7);
    if (poorlyCompressed.length > 0) {
      recommendations.push({
        type: 'compression_optimization',
        message: 'Some files have poor compression ratios',
        details: poorlyCompressed.map((c) => `${c.name}: ${Math.round(c.compressionRatio * 100)}%`),
      });
    }

    // High first load JS
    if (totals.firstLoadJSKB > 200) {
      recommendations.push({
        type: 'first_load_optimization',
        message: 'Consider reducing first load JavaScript',
        details: [
          'Use dynamic imports for non-critical code',
          'Implement route-based code splitting',
          'Defer non-essential libraries',
        ],
      });
    }

    this.results.recommendations = recommendations;
  }

  generateReport() {
    const { totals, chunks, violations, recommendations } = this.results;

    console.log(chalk.bold('📊 Bundle Analysis Report\n'));

    // Summary
    console.log(chalk.bold('Summary:'));
    console.log(
      `  Total JavaScript: ${chalk.cyan(totals.totalJSKB + 'KB')} (gzipped: ${totals.totalGzipJSKB}KB)`,
    );
    console.log(
      `  Total CSS: ${chalk.cyan(totals.totalCSSKB + 'KB')} (gzipped: ${totals.totalGzipCSSKB}KB)`,
    );
    console.log(`  First Load JS: ${chalk.cyan(totals.firstLoadJSKB + 'KB')}`);
    console.log(`  Total Chunks: ${chalk.cyan(totals.chunkCount)}\n`);

    // Largest chunks
    console.log(chalk.bold('Largest Chunks:'));
    chunks.slice(0, 10).forEach((chunk) => {
      const sizeColor =
        chunk.sizeKB > 100 ? chalk.red : chunk.sizeKB > 50 ? chalk.yellow : chalk.green;
      console.log(
        `  ${chunk.name}: ${sizeColor(chunk.sizeKB + 'KB')} ${chunk.gzipSizeKB ? `(${chunk.gzipSizeKB}KB gzipped)` : ''}`,
      );
    });
    console.log();

    // Violations
    if (violations.length > 0) {
      console.log(chalk.bold('⚠️  Threshold Violations:'));
      violations.forEach((violation) => {
        const color =
          violation.severity === 'error'
            ? chalk.red
            : violation.severity === 'warning'
              ? chalk.yellow
              : chalk.blue;
        console.log(`  ${color('●')} ${violation.message}`);
      });
      console.log();
    }

    // Recommendations
    if (recommendations.length > 0) {
      console.log(chalk.bold('💡 Recommendations:'));
      recommendations.forEach((rec) => {
        console.log(`  ${chalk.blue('●')} ${rec.message}`);
        if (rec.details) {
          rec.details.forEach((detail) => {
            console.log(`    - ${detail}`);
          });
        }
      });
      console.log();
    }

    // Status
    if (violations.filter((v) => v.severity === 'error').length > 0) {
      console.log(chalk.red('❌ Bundle analysis failed - critical thresholds exceeded'));
    } else if (violations.length > 0) {
      console.log(chalk.yellow('⚠️  Bundle analysis completed with warnings'));
    } else {
      console.log(chalk.green('✅ Bundle analysis passed - all thresholds met'));
    }
  }

  generateJSONReport() {
    const reportPath = path.join(process.cwd(), 'bundle-analysis.json');

    const report = {
      timestamp: new Date().toISOString(),
      thresholds: THRESHOLDS,
      results: this.results,
      status:
        this.results.violations.filter((v) => v.severity === 'error').length > 0
          ? 'failed'
          : 'passed',
    };

    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📄 Detailed report saved to: ${reportPath}`);
  }
}

// Run analyzer if called directly
if (require.main === module) {
  const analyzer = new BundleAnalyzer();
  analyzer.analyze();
}

module.exports = BundleAnalyzer;
