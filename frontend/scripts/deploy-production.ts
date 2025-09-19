#!/usr/bin/env ts-node

/**
 * Production Deployment Script
 * Handles environment validation, build checks, deployment, and smoke tests
 */

import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import chalk from 'chalk';
import axios from 'axios';

// Load environment variables
dotenv.config({ path: '.env.production.local' });

interface DeploymentConfig {
  dryRun: boolean;
  skipTests: boolean;
  skipBuild: boolean;
  environment: 'staging' | 'production';
  rollbackOnFailure: boolean;
}

class ProductionDeployment {
  private config: DeploymentConfig;
  private deploymentUrl: string | null = null;
  private previousDeploymentUrl: string | null = null;

  constructor(config: DeploymentConfig) {
    this.config = config;
  }

  /**
   * Main deployment flow
   */
  async deploy() {
    console.log(chalk.blue.bold('🚀 RuleIQ Production Deployment'));
    console.log(chalk.gray('================================'));
    console.log(chalk.gray(`Environment: ${this.config.environment}`));
    console.log(chalk.gray(`Dry Run: ${this.config.dryRun}`));
    console.log('');

    try {
      // Step 1: Validate environment
      this.validateEnvironment();

      // Step 2: Run pre-deployment checks
      if (!this.config.skipTests) {
        await this.runPreDeploymentChecks();
      }

      // Step 3: Build the application
      if (!this.config.skipBuild) {
        await this.buildApplication();
      }

      // Step 4: Deploy to Vercel
      if (!this.config.dryRun) {
        await this.deployToVercel();
      }

      // Step 5: Run smoke tests
      await this.runSmokeTests();

      // Step 6: Health check
      await this.performHealthCheck();

      console.log('');
      console.log(chalk.green.bold('✅ Deployment successful!'));
      if (this.deploymentUrl) {
        console.log(chalk.green(`🌐 URL: ${this.deploymentUrl}`));
      }
    } catch (error) {
      console.error(chalk.red.bold('❌ Deployment failed!'));
      console.error(error);

      if (this.config.rollbackOnFailure && this.previousDeploymentUrl) {
        await this.rollback();
      }

      process.exit(1);
    }
  }

  /**
   * Validate required environment variables
   */
  private validateEnvironment() {
    console.log(chalk.blue('📋 Validating environment variables...'));

    const requiredVars = [
      'NEXT_PUBLIC_API_URL',
      'NEXT_PUBLIC_APP_URL',
      'NEO4J_URI',
      'NEO4J_PASSWORD',
    ];

    const optionalVars = [
      'NEXT_PUBLIC_PUSHER_KEY',
      'NEXT_PUBLIC_PUSHER_CLUSTER',
      'PUSHER_APP_ID',
      'PUSHER_SECRET',
      'VERCEL_KV_REST_API_URL',
      'VERCEL_KV_REST_API_TOKEN',
    ];

    const missing: string[] = [];
    const warnings: string[] = [];

    // Check required variables
    requiredVars.forEach(varName => {
      if (!process.env[varName]) {
        missing.push(varName);
      }
    });

    // Check optional variables
    optionalVars.forEach(varName => {
      if (!process.env[varName]) {
        warnings.push(varName);
      }
    });

    if (missing.length > 0) {
      console.error(chalk.red('❌ Missing required environment variables:'));
      missing.forEach(v => console.error(chalk.red(`   - ${v}`)));
      throw new Error('Environment validation failed');
    }

    if (warnings.length > 0) {
      console.warn(chalk.yellow('⚠️  Missing optional environment variables:'));
      warnings.forEach(v => console.warn(chalk.yellow(`   - ${v}`)));
    }

    console.log(chalk.green('✅ Environment variables validated'));
  }

  /**
   * Run pre-deployment checks
   */
  private async runPreDeploymentChecks() {
    console.log('');
    console.log(chalk.blue('🧪 Running pre-deployment checks...'));

    const checks = [
      { name: 'Type checking', command: 'pnpm typecheck' },
      { name: 'Linting', command: 'pnpm lint' },
      { name: 'Tests', command: 'pnpm test --run' },
      { name: 'Theme migration test', command: 'pnpm test:theme' },
    ];

    for (const check of checks) {
      try {
        console.log(chalk.gray(`   Running ${check.name}...`));
        if (!this.config.dryRun) {
          execSync(check.command, { stdio: 'pipe' });
        }
        console.log(chalk.green(`   ✅ ${check.name} passed`));
      } catch (error) {
        console.error(chalk.red(`   ❌ ${check.name} failed`));
        throw error;
      }
    }
  }

  /**
   * Build the application
   */
  private async buildApplication() {
    console.log('');
    console.log(chalk.blue('🔨 Building application...'));

    try {
      if (!this.config.dryRun) {
        execSync('pnpm build:production', { stdio: 'inherit' });
      }
      console.log(chalk.green('✅ Build completed successfully'));
    } catch (error) {
      console.error(chalk.red('❌ Build failed'));
      throw error;
    }
  }

  /**
   * Deploy to Vercel
   */
  private async deployToVercel() {
    console.log('');
    console.log(chalk.blue('☁️  Deploying to Vercel...'));

    // Get current deployment for rollback
    try {
      const currentDeployment = execSync('vercel inspect --token=$VERCEL_TOKEN', {
        encoding: 'utf-8',
      });
      const urlMatch = currentDeployment.match(/https:\/\/[^\s]+\.vercel\.app/);
      if (urlMatch) {
        this.previousDeploymentUrl = urlMatch[0];
      }
    } catch (error) {
      console.warn(chalk.yellow('⚠️  Could not get current deployment URL'));
    }

    try {
      const command = this.config.environment === 'production'
        ? 'vercel --prod --yes'
        : 'vercel --yes';

      const output = execSync(command, { encoding: 'utf-8', stdio: 'pipe' });

      // Extract deployment URL
      const urlMatch = output.match(/https:\/\/[^\s]+\.vercel\.app/);
      if (urlMatch) {
        this.deploymentUrl = urlMatch[0];
      }

      console.log(chalk.green('✅ Deployment initiated'));
    } catch (error) {
      console.error(chalk.red('❌ Deployment failed'));
      throw error;
    }
  }

  /**
   * Run smoke tests
   */
  private async runSmokeTests() {
    console.log('');
    console.log(chalk.blue('🔥 Running smoke tests...'));

    const baseUrl = this.deploymentUrl || process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

    const tests = [
      { name: 'Health Check', path: '/api/health', expectedStatus: 200 },
      { name: 'Homepage', path: '/', expectedStatus: 200 },
      { name: 'Dashboard', path: '/dashboard', expectedStatus: 200 },
      { name: 'Assessment', path: '/assessment', expectedStatus: 200 },
      { name: 'Pusher Auth (no auth)', path: '/api/pusher/auth', expectedStatus: 401, method: 'POST' },
    ];

    let failures = 0;

    for (const test of tests) {
      try {
        console.log(chalk.gray(`   Testing ${test.name}...`));

        if (!this.config.dryRun) {
          const response = await axios({
            url: `${baseUrl}${test.path}`,
            method: test.method || 'GET',
            validateStatus: () => true,
            timeout: 10000,
          });

          if (response.status !== test.expectedStatus) {
            console.error(chalk.red(`   ❌ ${test.name}: Expected ${test.expectedStatus}, got ${response.status}`));
            failures++;
          } else {
            console.log(chalk.green(`   ✅ ${test.name}: OK`));
          }
        } else {
          console.log(chalk.gray(`   [DRY RUN] Would test ${test.name}`));
        }
      } catch (error: any) {
        console.error(chalk.red(`   ❌ ${test.name}: ${error.message}`));
        failures++;
      }
    }

    if (failures > 0) {
      throw new Error(`${failures} smoke test(s) failed`);
    }
  }

  /**
   * Perform health check
   */
  private async performHealthCheck() {
    console.log('');
    console.log(chalk.blue('💓 Performing health check...'));

    const baseUrl = this.deploymentUrl || process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

    try {
      if (!this.config.dryRun) {
        const response = await axios.get(`${baseUrl}/api/health`, {
          timeout: 5000,
        });

        if (response.data.status === 'healthy') {
          console.log(chalk.green('✅ Application is healthy'));
        } else {
          throw new Error('Health check returned unhealthy status');
        }
      } else {
        console.log(chalk.gray('[DRY RUN] Would perform health check'));
      }
    } catch (error) {
      console.error(chalk.red('❌ Health check failed'));
      throw error;
    }
  }

  /**
   * Rollback deployment
   */
  private async rollback() {
    console.log('');
    console.log(chalk.yellow('⏮️  Rolling back to previous deployment...'));

    if (!this.previousDeploymentUrl) {
      console.error(chalk.red('❌ No previous deployment URL available'));
      return;
    }

    try {
      execSync(`vercel rollback ${this.previousDeploymentUrl} --yes`, {
        stdio: 'inherit',
      });
      console.log(chalk.green('✅ Rollback completed'));
    } catch (error) {
      console.error(chalk.red('❌ Rollback failed'));
    }
  }
}

// Parse command line arguments
const args = process.argv.slice(2);
const config: DeploymentConfig = {
  dryRun: args.includes('--dry-run'),
  skipTests: args.includes('--skip-tests'),
  skipBuild: args.includes('--skip-build'),
  environment: args.includes('--staging') ? 'staging' : 'production',
  rollbackOnFailure: !args.includes('--no-rollback'),
};

// Help text
if (args.includes('--help')) {
  console.log(`
${chalk.bold('RuleIQ Production Deployment Script')}

${chalk.gray('Usage:')}
  pnpm deploy:prod [options]

${chalk.gray('Options:')}
  --dry-run         Run without actually deploying
  --skip-tests      Skip pre-deployment tests
  --skip-build      Skip build step (use existing build)
  --staging         Deploy to staging instead of production
  --no-rollback     Don't rollback on failure
  --help            Show this help message

${chalk.gray('Examples:')}
  pnpm deploy:prod                    # Full production deployment
  pnpm deploy:prod --dry-run          # Test deployment process
  pnpm deploy:prod --staging          # Deploy to staging
  pnpm deploy:prod --skip-tests       # Deploy without running tests
`);
  process.exit(0);
}

// Run deployment
const deployment = new ProductionDeployment(config);
deployment.deploy().catch(() => process.exit(1));