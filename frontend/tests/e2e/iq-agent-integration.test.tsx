/**
 * IQ Agent Integration - End-to-End Test
 * 
 * This test verifies the complete IQ Agent flow from frontend to backend,
 * including GraphRAG processing, trust gradient progression, and error handling.
 */

import { test, expect, type Page } from '@playwright/test';
import { LoginPage } from '../page-objects/login.page';
import { ChatPage } from '../page-objects/chat.page';
import { IQAgentPage } from '../page-objects/iq-agent.page';

// Test data
const TEST_QUERIES = {
  gdpr_breach: "We discovered a data breach involving 500 customer email addresses. What are our GDPR obligations?",
  iso27001_access: "We're a fintech startup with 50 employees. How do we implement ISO 27001 access management controls?",
  multi_framework: "Create a compliance roadmap for SOC 2 Type II while maintaining GDPR compliance",
  invalid_query: "What's the weather like today?",
  complex_gdpr: "Explain the relationship between GDPR Article 33 breach notification and Article 34 data subject notification requirements"
};

const DEMO_USER = {
  email: 'demo@ruleiq.com',
  password: 'DemoPass123!'
};

test.describe('IQ Agent Integration - Complete Flow', () => {
  let loginPage: LoginPage;
  let chatPage: ChatPage;
  let iqAgentPage: IQAgentPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    chatPage = new ChatPage(page);
    iqAgentPage = new IQAgentPage(page);

    // Navigate to application and login
    await loginPage.goto();
    await loginPage.login(DEMO_USER.email, DEMO_USER.password);
    
    // Navigate to chat
    await chatPage.navigateToChat();
    
    // Wait for IQ Agent to be ready
    await iqAgentPage.waitForIQAgentReady();
  });

  test.describe('Core IQ Agent Functionality', () => {
    test('should detect compliance query and route to IQ Agent', async ({ page }) => {
      // Send GDPR compliance query
      await chatPage.sendMessage(TEST_QUERIES.gdpr_breach);
      
      // Verify IQ Agent processing starts
      await iqAgentPage.waitForProcessingIndicator();
      await expect(iqAgentPage.processingStages).toBeVisible();
      
      // Verify processing stages appear
      await expect(page.locator('[data-testid="stage-analyzing"]')).toBeVisible();
      await expect(page.locator('[data-testid="stage-searching-graph"]')).toBeVisible();
      
      // Wait for response
      await iqAgentPage.waitForResponse();
      
      // Verify IQ Agent response structure
      await expect(iqAgentPage.responseCard).toBeVisible();
      await expect(iqAgentPage.trustIndicator).toBeVisible();
      await expect(iqAgentPage.confidenceScore).toContainText('%');
      
      // Verify GraphRAG evidence
      await expect(iqAgentPage.evidenceSection).toBeVisible();
      await iqAgentPage.expandEvidenceSection();
      
      const evidenceItems = page.locator('[data-testid="evidence-item"]');
      await expect(evidenceItems).toHaveCountGreaterThan(2);
      
      // Verify action plan
      await iqAgentPage.expandActionPlanSection();
      await expect(iqAgentPage.actionPlanSection).toBeVisible();
      await expect(page.locator('[data-testid="immediate-action"]')).toHaveCountGreaterThan(0);
    });

    test('should show trust gradient progression through multiple interactions', async ({ page }) => {
      // First interaction - should be in Helper mode
      await chatPage.sendMessage(TEST_QUERIES.gdpr_breach);
      await iqAgentPage.waitForResponse();
      
      const initialTrustLevel = await iqAgentPage.getTrustLevel();
      expect(initialTrustLevel).toBe('helper');
      
      // Second interaction - check for progression
      await chatPage.sendMessage(TEST_QUERIES.iso27001_access);
      await iqAgentPage.waitForResponse();
      
      const secondTrustLevel = await iqAgentPage.getTrustLevel();
      const confidenceScore = await iqAgentPage.getConfidenceScore();
      
      // Trust should remain helper but confidence might improve
      expect(secondTrustLevel).toBe('helper');
      expect(confidenceScore).toBeGreaterThan(70);
      
      // Third interaction - potential progression to advisor
      await chatPage.sendMessage(TEST_QUERIES.complex_gdpr);
      await iqAgentPage.waitForResponse();
      
      // Verify trust progression indicators are working
      await expect(iqAgentPage.trustProgressBar).toBeVisible();
      await expect(iqAgentPage.interactionCounter).toContainText('3');
    });

    test('should handle multi-framework compliance queries', async ({ page }) => {
      // Send complex multi-framework query
      await chatPage.sendMessage(TEST_QUERIES.multi_framework);
      await iqAgentPage.waitForResponse();
      
      // Verify expanded response format
      await expect(iqAgentPage.responseCard).toBeVisible();
      
      // Check for graph analysis section
      await iqAgentPage.expandGraphAnalysisSection();
      await expect(iqAgentPage.graphAnalysisSection).toBeVisible();
      
      // Verify multiple frameworks are referenced
      const frameworkBadges = page.locator('[data-testid="framework-badge"]');
      await expect(frameworkBadges).toHaveCountGreaterThanOrEqual(2);
      
      // Check for cross-framework analysis
      const analysisMetrics = page.locator('[data-testid="graph-metric"]');
      await expect(analysisMetrics).toHaveCountGreaterThan(3);
      
      // Verify relationship traversal data
      await expect(page.locator('[data-testid="nodes-analyzed"]')).toContainText(/\d+/);
      await expect(page.locator('[data-testid="relationships-traversed"]')).toContainText(/\d+/);
    });
  });

  test.describe('Error Handling & Fallback Mechanisms', () => {
    test('should gracefully fallback to regular chat for non-compliance queries', async ({ page }) => {
      // Send non-compliance query
      await chatPage.sendMessage(TEST_QUERIES.invalid_query);
      
      // Should not trigger IQ Agent processing
      await expect(iqAgentPage.processingStages).not.toBeVisible({ timeout: 3000 });
      
      // Should get regular chat response
      const response = await chatPage.waitForLastMessage();
      await expect(response).not.toHaveClass(/iq-agent-response/);
      
      // Should not show IQ Agent indicators
      await expect(iqAgentPage.trustIndicator).not.toBeVisible();
      await expect(iqAgentPage.confidenceScore).not.toBeVisible();
    });

    test('should handle IQ Agent service failures gracefully', async ({ page }) => {
      // Mock IQ Agent service failure
      await page.route('/api/v1/iq/health', route => {
        route.fulfill({
          status: 503,
          body: JSON.stringify({
            status: 'unhealthy',
            neo4j_connected: false,
            message: 'Service temporarily unavailable'
          })
        });
      });

      // Send compliance query
      await chatPage.sendMessage(TEST_QUERIES.gdpr_breach);
      
      // Should show error state
      await expect(page.locator('[data-testid="iq-error-fallback"]')).toBeVisible();
      await expect(page.locator('text=IQ Agent is temporarily unavailable')).toBeVisible();
      
      // Should still get regular chat response as fallback
      const response = await chatPage.waitForLastMessage();
      expect(response).toBeTruthy();
    });

    test('should show error boundary for IQ Agent component failures', async ({ page }) => {
      // Simulate component error by corrupting data
      await page.evaluate(() => {
        window.localStorage.setItem('iq-agent-storage', 'invalid-json');
      });
      
      // Reload page to trigger error
      await page.reload();
      await loginPage.login(DEMO_USER.email, DEMO_USER.password);
      await chatPage.navigateToChat();
      
      // Should show error boundary
      await expect(page.locator('[data-testid="iq-error-boundary"]')).toBeVisible();
      await expect(page.locator('text=IQ Agent Error')).toBeVisible();
      
      // Should provide recovery options
      await expect(page.locator('[data-testid="error-retry-button"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-fallback-button"]')).toBeVisible();
    });
  });

  test.describe('Performance & Metrics', () => {
    test('should meet response time SLOs', async ({ page }) => {
      const startTime = Date.now();
      
      // Send compliance query
      await chatPage.sendMessage(TEST_QUERIES.gdpr_breach);
      await iqAgentPage.waitForResponse();
      
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      // Verify response time is within acceptable bounds (45s max for comprehensive)
      expect(responseTime).toBeLessThan(45000);
      
      // Check response time display
      const responseTimeDisplay = await iqAgentPage.getResponseTime();
      expect(responseTimeDisplay).toMatch(/\d+ms/);
    });

    test('should track confidence scores and evidence quality', async ({ page }) => {
      await chatPage.sendMessage(TEST_QUERIES.complex_gdpr);
      await iqAgentPage.waitForResponse();
      
      // Check confidence score
      const confidenceScore = await iqAgentPage.getConfidenceScore();
      expect(confidenceScore).toBeGreaterThan(70); // Minimum threshold
      expect(confidenceScore).toBeLessThanOrEqual(100);
      
      // Check evidence count
      await iqAgentPage.expandEvidenceSection();
      const evidenceCount = await iqAgentPage.getEvidenceCount();
      expect(evidenceCount).toBeGreaterThanOrEqual(3); // Minimum evidence requirement
      
      // Verify source quality (should have legislation.gov.uk or EUR-Lex)
      const evidenceSources = await page.locator('[data-testid="evidence-source"]').allTextContents();
      const hasPrimarySources = evidenceSources.some(source => 
        source.includes('legislation.gov.uk') || 
        source.includes('eur-lex.europa.eu')
      );
      expect(hasPrimarySources).toBeTruthy();
    });
  });

  test.describe('Memory & Context Awareness', () => {
    test('should remember context across conversation', async ({ page }) => {
      // First query establishing context
      await chatPage.sendMessage("We are a fintech startup with 50 employees.");
      await iqAgentPage.waitForResponse();
      
      // Second query should use previous context
      await chatPage.sendMessage("What ISO 27001 controls should we prioritize?");
      await iqAgentPage.waitForResponse();
      
      // Response should reference fintech context
      const response = await chatPage.getLastMessageContent();
      expect(response.toLowerCase()).toMatch(/fintech|financial|startup/);
      
      // Check memory section if available
      if (await iqAgentPage.memorySection.isVisible()) {
        await expect(iqAgentPage.memorySection).toContainText('fintech');
        await expect(iqAgentPage.memorySection).toContainText('50 employees');
      }
    });

    test('should export conversation history with IQ Agent metadata', async ({ page }) => {
      // Conduct multiple IQ Agent interactions
      for (const query of [TEST_QUERIES.gdpr_breach, TEST_QUERIES.iso27001_access]) {
        await chatPage.sendMessage(query);
        await iqAgentPage.waitForResponse();
      }
      
      // Export conversation history
      await chatPage.openExportDialog();
      await chatPage.exportConversation();
      
      // Verify download includes IQ Agent metadata
      // Note: In real test, you'd verify the downloaded file contains:
      // - Trust levels
      // - Confidence scores  
      // - Evidence sources
      // - Response times
      // - Graph analysis data
      
      await expect(page.locator('[data-testid="export-success"]')).toBeVisible();
    });
  });

  test.describe('UI/UX Verification', () => {
    test('should display all IQ Agent UI components correctly', async ({ page }) => {
      await chatPage.sendMessage(TEST_QUERIES.gdpr_breach);
      await iqAgentPage.waitForResponse();
      
      // Verify main response card
      await expect(iqAgentPage.responseCard).toBeVisible();
      await expect(iqAgentPage.responseCard).toHaveClass(/border-l-4.*border-l-blue-500/);
      
      // Verify trust indicator
      await expect(iqAgentPage.trustIndicator).toBeVisible();
      await expect(iqAgentPage.trustIndicator).toContainText('Helper');
      
      // Verify collapsible sections
      const sections = [
        'evidence-section',
        'action-plan-section',
        'risk-assessment-section',
        'graph-analysis-section'
      ];
      
      for (const section of sections) {
        const sectionElement = page.locator(`[data-testid="${section}"]`);
        if (await sectionElement.isVisible()) {
          // Test expand/collapse functionality
          await sectionElement.click();
          await expect(sectionElement).toHaveAttribute('data-expanded', 'true');
          
          await sectionElement.click();
          await expect(sectionElement).toHaveAttribute('data-expanded', 'false');
        }
      }
      
      // Verify responsive design
      await page.setViewportSize({ width: 768, height: 1024 }); // Mobile
      await expect(iqAgentPage.responseCard).toBeVisible();
      
      await page.setViewportSize({ width: 1920, height: 1080 }); // Desktop
      await expect(iqAgentPage.responseCard).toBeVisible();
    });

    test('should handle streaming updates correctly', async ({ page }) => {
      // Note: This test requires backend streaming support
      await chatPage.sendMessage(TEST_QUERIES.multi_framework);
      
      // Verify streaming indicators appear
      await expect(iqAgentPage.processingStages).toBeVisible();
      
      // Check that stages update progressively
      await expect(page.locator('[data-testid="stage-analyzing"]')).toHaveClass(/active/);
      
      // Wait for stage progression
      await page.waitForTimeout(2000);
      await expect(page.locator('[data-testid="stage-searching-graph"]')).toHaveClass(/active/);
      
      // Verify progress bar updates
      const progressBar = page.locator('[data-testid="processing-progress"]');
      await expect(progressBar).toBeVisible();
      
      const initialProgress = await progressBar.getAttribute('value');
      await page.waitForTimeout(2000);
      const updatedProgress = await progressBar.getAttribute('value');
      
      expect(parseInt(updatedProgress || '0')).toBeGreaterThan(parseInt(initialProgress || '0'));
    });
  });
});

// Page Object Models for IQ Agent testing
test.describe('Demo Flow Verification', () => {
  test('should execute complete founder demo scenario', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const chatPage = new ChatPage(page);
    const iqAgentPage = new IQAgentPage(page);

    // Setup demo environment
    await loginPage.goto();
    await loginPage.login(DEMO_USER.email, DEMO_USER.password);
    await chatPage.navigateToChat();
    await iqAgentPage.waitForIQAgentReady();

    // Demo Scenario 1: GDPR Data Breach
    console.log('Executing Demo Scenario 1: GDPR Data Breach');
    const scenario1Start = Date.now();
    
    await chatPage.sendMessage(TEST_QUERIES.gdpr_breach);
    await iqAgentPage.waitForResponse();
    
    const scenario1Time = Date.now() - scenario1Start;
    console.log(`Scenario 1 completed in ${scenario1Time}ms`);
    
    // Verify expected demo elements
    await expect(iqAgentPage.trustIndicator).toContainText('Helper');
    await expect(iqAgentPage.confidenceScore).toContainText('%');
    
    const evidenceCount = await iqAgentPage.getEvidenceCount();
    expect(evidenceCount).toBeGreaterThanOrEqual(3);
    
    // Demo Scenario 2: ISO 27001 Implementation
    console.log('Executing Demo Scenario 2: ISO 27001');
    const scenario2Start = Date.now();
    
    await chatPage.sendMessage(TEST_QUERIES.iso27001_access);
    await iqAgentPage.waitForResponse();
    
    const scenario2Time = Date.now() - scenario2Start;
    console.log(`Scenario 2 completed in ${scenario2Time}ms`);
    
    // Verify trust progression
    const trustLevel = await iqAgentPage.getTrustLevel();
    const interactionCount = await iqAgentPage.getInteractionCount();
    expect(interactionCount).toBe(2);
    
    // Demo Scenario 3: Multi-Framework Analysis
    console.log('Executing Demo Scenario 3: Multi-Framework');
    const scenario3Start = Date.now();
    
    await chatPage.sendMessage(TEST_QUERIES.multi_framework);
    await iqAgentPage.waitForResponse();
    
    const scenario3Time = Date.now() - scenario3Start;
    console.log(`Scenario 3 completed in ${scenario3Time}ms`);
    
    // Verify advanced features
    await iqAgentPage.expandGraphAnalysisSection();
    const nodesAnalyzed = await iqAgentPage.getGraphNodesCount();
    expect(nodesAnalyzed).toBeGreaterThan(10);
    
    // Summary metrics for demo
    console.log('Demo Summary:');
    console.log(`- Total scenarios: 3`);
    console.log(`- Average response time: ${(scenario1Time + scenario2Time + scenario3Time) / 3}ms`);
    console.log(`- Trust level progression: Helper → ${trustLevel}`);
    console.log(`- Evidence sources: ${evidenceCount}`);
    console.log(`- Graph nodes analyzed: ${nodesAnalyzed}`);
    
    // All demo scenarios completed successfully
    expect(scenario1Time).toBeLessThan(45000);
    expect(scenario2Time).toBeLessThan(45000);
    expect(scenario3Time).toBeLessThan(45000);
  });
});