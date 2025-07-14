#!/usr/bin/env node

/**
 * Image Optimization Audit Script
 * Analyzes all images in the frontend directory and provides optimization recommendations
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const FRONTEND_DIR = path.join(__dirname, "..", "frontend");
const PUBLIC_DIR = path.join(FRONTEND_DIR, "public");
const RESULTS_FILE = path.join(
  __dirname,
  "..",
  "frontend",
  "image-audit-results.json"
);

class ImageAudit {
  constructor() {
    this.results = {
      totalImages: 0,
      optimizedImages: 0,
      unoptimizedImages: 0,
      recommendations: [],
      summary: {
        totalSize: 0,
        potentialSavings: 0,
        averageSize: 0,
      },
    };
  }

  async run() {
    console.log("🔍 Starting image optimization audit...");

    const images = this.findImages(PUBLIC_DIR);
    console.log(`📊 Found ${images.length} images to analyze`);

    for (const imagePath of images) {
      await this.analyzeImage(imagePath);
    }

    this.generateReport();
    this.saveResults();

    console.log("✅ Image audit complete!");
    console.log(`📋 Report saved to: ${RESULTS_FILE}`);
  }

  findImages(dir) {
    const images = [];
    const extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"];

    if (!fs.existsSync(dir)) {
      console.log(`⚠️ Directory not found: ${dir}`);
      return images;
    }

    const files = fs.readdirSync(dir, { recursive: true });

    for (const file of files) {
      const filePath = path.join(dir, file);
      const ext = path.extname(file).toLowerCase();

      if (extensions.includes(ext) && fs.statSync(filePath).isFile()) {
        images.push(filePath);
      }
    }

    return images;
  }

  async analyzeImage(imagePath) {
    const stats = fs.statSync(imagePath);
    const sizeInKB = stats.size / 1024;
    const ext = path.extname(imagePath).toLowerCase();

    this.results.totalImages++;
    this.results.summary.totalSize += sizeInKB;

    const analysis = {
      path: path.relative(FRONTEND_DIR, imagePath),
      size: sizeInKB,
      extension: ext,
      optimized: false,
      recommendations: [],
    };

    // Check for optimization opportunities
    if (ext === ".png" && sizeInKB > 100) {
      analysis.recommendations.push({
        type: "compression",
        message: "Convert to WebP for better compression",
        potentialSavings: Math.round(sizeInKB * 0.3),
      });
    }

    if (ext === ".jpg" && sizeInKB > 200) {
      analysis.recommendations.push({
        type: "compression",
        message: "Consider WebP format with quality optimization",
        potentialSavings: Math.round(sizeInKB * 0.25),
      });
    }

    if (sizeInKB > 500) {
      analysis.recommendations.push({
        type: "resize",
        message: "Image is very large, consider resizing for web use",
        potentialSavings: Math.round(sizeInKB * 0.5),
      });
    }

    if (ext === ".gif" && sizeInKB > 100) {
      analysis.recommendations.push({
        type: "format",
        message: "Consider converting animated GIF to MP4/WebM",
        potentialSavings: Math.round(sizeInKB * 0.8),
      });
    }

    if (analysis.recommendations.length === 0) {
      analysis.optimized = true;
      this.results.optimizedImages++;
    } else {
      this.results.unoptimizedImages++;
      const totalSavings = analysis.recommendations.reduce(
        (sum, rec) => sum + rec.potentialSavings,
        0
      );
      this.results.summary.potentialSavings += totalSavings;
    }

    this.results.recommendations.push(analysis);
  }

  generateReport() {
    console.log("\n📊 Image Optimization Report");
    console.log("================================");
    console.log(`Total Images: ${this.results.totalImages}`);
    console.log(`Optimized: ${this.results.optimizedImages}`);
    console.log(`Need Optimization: ${this.results.unoptimizedImages}`);
    console.log(
      `Total Size: ${(this.results.summary.totalSize / 1024).toFixed(2)} MB`
    );
    console.log(
      `Potential Savings: ${(
        this.results.summary.potentialSavings / 1024
      ).toFixed(2)} MB`
    );

    if (this.results.unoptimizedImages > 0) {
      console.log("\n🎯 Priority Optimizations:");
      const priorityImages = this.results.recommendations
        .filter((img) => !img.optimized)
        .sort((a, b) => b.size - a.size)
        .slice(0, 10);

      priorityImages.forEach((img) => {
        console.log(`\n📸 ${img.path} (${img.size.toFixed(1)} KB)`);
        img.recommendations.forEach((rec) => {
          console.log(`   - ${rec.message} (save ~${rec.potentialSavings} KB)`);
        });
      });
    }
  }

  saveResults() {
    fs.writeFileSync(RESULTS_FILE, JSON.stringify(this.results, null, 2));
  }
}

// Run the audit
if (require.main === module) {
  const audit = new ImageAudit();
  audit.run().catch(console.error);
}

module.exports = ImageAudit;
