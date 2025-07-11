#!/usr/bin/env node

/**
 * Script to fix failing frontend tests
 * Addresses validation errors, missing mock data, and configuration issues
 */

import fs from 'fs';
import path from 'path';

const FRONTEND_DIR = path.join(process.cwd());

// Fix 1: Update comprehensive store test with valid test data
function fixComprehensiveStoreTest() {
  const testFile = path.join(FRONTEND_DIR, 'tests/stores/comprehensive-store.test.ts');
  
  // Read the file
  let content = fs.readFileSync(testFile, 'utf-8');
  
  // Fix assessment mock data - add required fields
  content = content.replace(
    /const mockAssessments = \[\s*{\s*id:\s*'assess-1',\s*name:\s*'Test Assessment',\s*status:\s*'completed'\s*},\s*{\s*id:\s*'assess-2',\s*name:\s*'Test Assessment 2',\s*status:\s*'in_progress'\s*},?\s*\]/,
    `const mockAssessments = [
        {
          id: 'assess-1',
          name: 'Test Assessment',
          status: 'completed' as const,
          framework_id: 'gdpr',
          business_profile_id: 'profile-1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          total_questions: 20,
          answered_questions: 20,
          score: 85
        },
        {
          id: 'assess-2',
          name: 'Test Assessment 2',
          status: 'in_progress' as const,
          framework_id: 'iso27001',
          business_profile_id: 'profile-1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          total_questions: 30,
          answered_questions: 15,
          score: 50
        }
      ]`
  );
  
  // Fix new assessment data
  content = content.replace(
    /const newAssessment = \{\s*id:\s*'new-assess',\s*name:\s*'New Assessment',\s*status:\s*'draft',?\s*\}/,
    `const newAssessment = {
        id: 'new-assess',
        name: 'New Assessment',
        status: 'draft' as const,
        framework_id: 'gdpr',
        business_profile_id: 'profile-1',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }`
  );
  
  // Fix evidence mock data
  content = content.replace(
    /const mockEvidence = \[\s*{\s*id:\s*'ev-1',\s*name:\s*'Evidence 1',\s*status:\s*'collected'\s*},\s*{\s*id:\s*'ev-2',\s*name:\s*'Evidence 2',\s*status:\s*'pending'\s*},?\s*\]/,
    `const mockEvidence = [
        {
          id: 'ev-1',
          title: 'Evidence 1',
          status: 'collected' as const,
          evidence_type: 'document',
          framework_id: 'gdpr',
          business_profile_id: 'profile-1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 'ev-2',
          title: 'Evidence 2',
          status: 'pending' as const,
          evidence_type: 'screenshot',
          framework_id: 'iso27001',
          business_profile_id: 'profile-1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]`
  );
  
  // Fix widget mock data
  content = content.replace(
    /const mockWidgets = \[\s*{\s*id:\s*'widget-1',\s*type:\s*'compliance-score',\s*config:\s*{}\s*},\s*{\s*id:\s*'widget-2',\s*type:\s*'pending-tasks',\s*config:\s*{}\s*},?\s*\]/,
    `const mockWidgets = [
        {
          id: 'widget-1',
          type: 'compliance-score' as const,
          position: { x: 0, y: 0 },
          size: { w: 4, h: 2 },
          settings: {},
          isVisible: true
        },
        {
          id: 'widget-2',
          type: 'pending-tasks' as const,
          position: { x: 4, y: 0 },
          size: { w: 4, h: 2 },
          settings: {},
          isVisible: true
        }
      ]`
  );
  
  // Remove all 'as any' casts for these mock data
  content = content.replace(/store\.setAssessments\(mockAssessments as any\)/, 'store.setAssessments(mockAssessments)');
  content = content.replace(/store\.addAssessment\(newAssessment as any\)/, 'store.addAssessment(newAssessment)');
  content = content.replace(/store\.setEvidence\(mockEvidence as any\)/, 'store.setEvidence(mockEvidence)');
  content = content.replace(/store\.setWidgets\(mockWidgets as any\)/, 'store.setWidgets(mockWidgets)');
  
  fs.writeFileSync(testFile, content);
  console.log('✅ Fixed comprehensive store test');
}

// Fix 2: Add missing mock implementations for AI integration tests
function fixAIIntegrationTest() {
  const testFile = path.join(FRONTEND_DIR, 'tests/ai-integration.test.ts');
  
  // Read the file
  let content = fs.readFileSync(testFile, 'utf-8');
  
  // Ensure the test waits for the async operation
  content = content.replace(
    /engine\.answerQuestion\('q1', 'no'\);\s*\n\s*const hasMore = await engine\.nextQuestion\(\);/,
    `// Answer the question - this triggers shouldTriggerAIFollowUp check
      engine.answerQuestion('q1', 'no');
      
      // nextQuestion will trigger AI follow-up generation
      const hasMore = await engine.nextQuestion();
      
      // Wait a tick for the async operations to complete
      await new Promise(resolve => setTimeout(resolve, 0));`
  );
  
  fs.writeFileSync(testFile, content);
  console.log('✅ Fixed AI integration test');
}

// Fix 3: Update auth flow test to handle form submission properly
function fixAuthFlowTest() {
  const testFile = path.join(FRONTEND_DIR, 'tests/components/auth/auth-flow.test.tsx');
  
  if (!fs.existsSync(testFile)) {
    console.log('⚠️  Auth flow test file not found, skipping');
    return;
  }
  
  // Read the file
  let content = fs.readFileSync(testFile, 'utf-8');
  
  // Fix form submission test - ensure the form is properly submitted
  content = content.replace(
    /fireEvent\.click\(screen\.getByRole\('button', { name: \/sign in\/i }\)\)/,
    `// Find and submit the form
    const form = screen.getByRole('button', { name: /sign in/i }).closest('form');
    if (form) {
      fireEvent.submit(form);
    } else {
      fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
    }`
  );
  
  fs.writeFileSync(testFile, content);
  console.log('✅ Fixed auth flow test');
}

// Fix 4: Create missing test utilities for assessment wizard
function createAssessmentWizardUtils() {
  const utilsFile = path.join(FRONTEND_DIR, 'tests/utils/assessment-test-utils.ts');
  
  const utilsContent = `import type { AssessmentFramework, Question } from '@/lib/assessment-engine/types';

export const createMockFramework = (overrides?: Partial<AssessmentFramework>): AssessmentFramework => ({
  id: 'test-framework',
  name: 'Test Framework',
  description: 'Test framework description',
  version: '1.0',
  scoringMethod: 'percentage',
  passingScore: 70,
  estimatedDuration: 30,
  tags: ['test'],
  sections: [
    {
      id: 'section-1',
      title: 'Test Section',
      description: 'Test section description',
      order: 1,
      questions: [
        {
          id: 'q1',
          type: 'radio',
          text: 'Test question 1?',
          options: [
            { value: 'yes', label: 'Yes' },
            { value: 'no', label: 'No' }
          ],
          validation: { required: true },
          weight: 1
        },
        {
          id: 'q2',
          type: 'textarea',
          text: 'Test question 2',
          validation: { required: true, minLength: 10 },
          weight: 1
        }
      ]
    }
  ],
  ...overrides
});

export const createMockAssessmentContext = () => ({
  assessmentId: 'test-assessment-id',
  frameworkId: 'test-framework',
  businessProfileId: 'test-profile-id',
  answers: new Map(),
  metadata: {}
});
`;
  
  // Ensure directory exists
  const utilsDir = path.dirname(utilsFile);
  if (!fs.existsSync(utilsDir)) {
    fs.mkdirSync(utilsDir, { recursive: true });
  }
  
  fs.writeFileSync(utilsFile, utilsContent);
  console.log('✅ Created assessment wizard test utilities');
}

// Fix 5: Update vitest config to handle long-running tests
function updateVitestConfig() {
  const configFile = path.join(FRONTEND_DIR, 'vitest.config.ts');
  
  let content = fs.readFileSync(configFile, 'utf-8');
  
  // Add pool configuration to prevent timeouts
  if (!content.includes('pool:')) {
    content = content.replace(
      /testTimeout: 10000,\s*\/\/ 10 seconds per test\s*\n\s*hookTimeout: 10000,\s*\/\/ 10 seconds for hooks/,
      `testTimeout: 10000, // 10 seconds per test
    hookTimeout: 10000, // 10 seconds for hooks
    pool: 'forks', // Use forks instead of threads for better isolation
    poolOptions: {
      forks: {
        singleFork: true // Run tests sequentially in a single fork
      }
    }`
    );
  }
  
  fs.writeFileSync(configFile, content);
  console.log('✅ Updated vitest config');
}

// Main execution
async function main() {
  console.log('🔧 Fixing frontend tests...\n');
  
  try {
    fixComprehensiveStoreTest();
    fixAIIntegrationTest();
    fixAuthFlowTest();
    createAssessmentWizardUtils();
    updateVitestConfig();
    
    console.log('\n✅ All fixes applied successfully!');
    console.log('\n📝 Next steps:');
    console.log('1. Run: pnpm test --run to verify fixes');
    console.log('2. For specific test files: pnpm test <filename>');
    console.log('3. For watch mode: pnpm test');
  } catch (error) {
    console.error('\n❌ Error applying fixes:', error);
    process.exit(1);
  }
}

main();