/**
 * IQ Agent Page Object Model
 * 
 * Provides a high-level interface for interacting with IQ Agent components
 * during end-to-end testing.
 */

import { type Page, type Locator } from '@playwright/test';

export class IQAgentPage {
  readonly page: Page;
  
  // Main components
  readonly responseCard: Locator;
  readonly trustIndicator: Locator;
  readonly confidenceScore: Locator;
  readonly processingStages: Locator;
  
  // Response sections
  readonly evidenceSection: Locator;
  readonly actionPlanSection: Locator;
  readonly riskAssessmentSection: Locator;
  readonly graphAnalysisSection: Locator;
  readonly memorySection: Locator;
  
  // Trust indicators
  readonly trustProgressBar: Locator;
  readonly interactionCounter: Locator;
  
  // Processing indicators
  readonly processingProgress: Locator;
  readonly stageAnalyzing: Locator;
  readonly stageSearchingGraph: Locator;
  readonly stageEvaluatingEvidence: Locator;
  readonly stageGeneratingResponse: Locator;
  
  // Error handling
  readonly errorBoundary: Locator;
  readonly errorFallback: Locator;
  readonly errorRetryButton: Locator;
  
  constructor(page: Page) {
    this.page = page;
    
    // Main components
    this.responseCard = page.locator('[data-testid="iq-response-card"]');
    this.trustIndicator = page.locator('[data-testid="iq-trust-indicator"]');
    this.confidenceScore = page.locator('[data-testid="iq-confidence-score"]');
    this.processingStages = page.locator('[data-testid="iq-processing-stages"]');
    
    // Response sections
    this.evidenceSection = page.locator('[data-testid="evidence-section"]');
    this.actionPlanSection = page.locator('[data-testid="action-plan-section"]');
    this.riskAssessmentSection = page.locator('[data-testid="risk-assessment-section"]');
    this.graphAnalysisSection = page.locator('[data-testid="graph-analysis-section"]');
    this.memorySection = page.locator('[data-testid="memory-section"]');
    
    // Trust indicators
    this.trustProgressBar = page.locator('[data-testid="trust-progress-bar"]');
    this.interactionCounter = page.locator('[data-testid="interaction-counter"]');
    
    // Processing indicators
    this.processingProgress = page.locator('[data-testid="processing-progress"]');
    this.stageAnalyzing = page.locator('[data-testid="stage-analyzing"]');
    this.stageSearchingGraph = page.locator('[data-testid="stage-searching-graph"]');
    this.stageEvaluatingEvidence = page.locator('[data-testid="stage-evaluating-evidence"]');
    this.stageGeneratingResponse = page.locator('[data-testid="stage-generating-response"]');
    
    // Error handling
    this.errorBoundary = page.locator('[data-testid="iq-error-boundary"]');
    this.errorFallback = page.locator('[data-testid="iq-error-fallback"]');
    this.errorRetryButton = page.locator('[data-testid="error-retry-button"]');
  }
  
  /**
   * Wait for IQ Agent to be ready for queries
   */
  async waitForIQAgentReady(timeout = 10000) {
    await this.page.waitForFunction(
      () => {
        // Check if IQ Agent store indicates it's ready
        return window.localStorage.getItem('iq-agent-storage') !== null;
      },
      { timeout }
    );
    
    // Additional check for health status
    await this.page.waitForResponse(
      response => response.url().includes('/api/v1/iq/health') && response.status() === 200,
      { timeout: 5000 }
    ).catch(() => {
      // Health check failed, but continue - graceful degradation should handle this
      console.warn('IQ Agent health check failed, continuing with test');
    });
  }
  
  /**
   * Wait for processing indicator to appear
   */
  async waitForProcessingIndicator(timeout = 5000) {
    await this.processingStages.waitFor({ 
      state: 'visible', 
      timeout 
    });
  }
  
  /**
   * Wait for IQ Agent response to complete
   */
  async waitForResponse(timeout = 45000) {
    // Wait for processing to finish and response to appear
    await this.responseCard.waitFor({ 
      state: 'visible', 
      timeout 
    });
    
    // Ensure processing stages are no longer visible
    await this.processingStages.waitFor({ 
      state: 'hidden', 
      timeout: 5000 
    }).catch(() => {
      // Processing stages might still be visible if there's an error
    });
  }
  
  /**
   * Expand evidence section
   */
  async expandEvidenceSection() {
    const trigger = this.evidenceSection.locator('[data-testid="evidence-section-trigger"]');
    if (await trigger.isVisible()) {
      await trigger.click();
    }
  }
  
  /**
   * Expand action plan section
   */
  async expandActionPlanSection() {
    const trigger = this.actionPlanSection.locator('[data-testid="action-plan-section-trigger"]');
    if (await trigger.isVisible()) {
      await trigger.click();
    }
  }
  
  /**
   * Expand graph analysis section
   */
  async expandGraphAnalysisSection() {
    const trigger = this.graphAnalysisSection.locator('[data-testid="graph-analysis-section-trigger"]');
    if (await trigger.isVisible()) {
      await trigger.click();
    }
  }
  
  /**
   * Get current trust level
   */
  async getTrustLevel(): Promise<string> {
    const trustText = await this.trustIndicator.textContent();
    if (!trustText) return 'unknown';
    
    if (trustText.toLowerCase().includes('helper')) return 'helper';
    if (trustText.toLowerCase().includes('advisor')) return 'advisor';
    if (trustText.toLowerCase().includes('partner')) return 'partner';
    
    return 'unknown';
  }
  
  /**
   * Get confidence score percentage
   */
  async getConfidenceScore(): Promise<number> {
    const scoreText = await this.confidenceScore.textContent();
    if (!scoreText) return 0;
    
    const match = scoreText.match(/(\d+)%/);
    return match ? parseInt(match[1]) : 0;
  }
  
  /**
   * Get interaction count
   */
  async getInteractionCount(): Promise<number> {
    const counterText = await this.interactionCounter.textContent();
    if (!counterText) return 0;
    
    const match = counterText.match(/(\d+)/);
    return match ? parseInt(match[1]) : 0;
  }
  
  /**
   * Get evidence count
   */
  async getEvidenceCount(): Promise<number> {
    await this.expandEvidenceSection();
    const evidenceItems = this.page.locator('[data-testid="evidence-item"]');
    return await evidenceItems.count();
  }
  
  /**
   * Get response time from metadata
   */
  async getResponseTime(): Promise<string> {
    const responseTimeElement = this.page.locator('[data-testid="response-time"]');
    const text = await responseTimeElement.textContent();
    return text || '0ms';
  }
  
  /**
   * Get number of graph nodes analyzed
   */
  async getGraphNodesCount(): Promise<number> {
    await this.expandGraphAnalysisSection();
    const nodesElement = this.page.locator('[data-testid="nodes-analyzed"]');
    const text = await nodesElement.textContent();
    
    if (!text) return 0;
    const match = text.match(/(\d+)/);
    return match ? parseInt(match[1]) : 0;
  }
  
  /**
   * Check if IQ Agent is in error state
   */
  async isInErrorState(): Promise<boolean> {
    return await this.errorFallback.isVisible() || await this.errorBoundary.isVisible();
  }
  
  /**
   * Retry after error
   */
  async retryAfterError() {
    if (await this.errorRetryButton.isVisible()) {
      await this.errorRetryButton.click();
    }
  }
  
  /**
   * Get all evidence sources
   */
  async getEvidenceSources(): Promise<string[]> {
    await this.expandEvidenceSection();
    const sourceElements = this.page.locator('[data-testid="evidence-source"]');
    return await sourceElements.allTextContents();
  }
  
  /**
   * Get immediate actions from action plan
   */
  async getImmediateActions(): Promise<string[]> {
    await this.expandActionPlanSection();
    const actionElements = this.page.locator('[data-testid="immediate-action"]');
    return await actionElements.allTextContents();
  }
  
  /**
   * Get risk assessment level
   */
  async getRiskLevel(): Promise<string> {
    const riskElement = this.page.locator('[data-testid="risk-level"]');
    const text = await riskElement.textContent();
    return text?.toLowerCase() || 'unknown';
  }
  
  /**
   * Check if processing stage is active
   */
  async isStageActive(stage: 'analyzing' | 'searching-graph' | 'evaluating-evidence' | 'generating-response'): Promise<boolean> {
    const stageElement = this.page.locator(`[data-testid="stage-${stage}"]`);
    const classes = await stageElement.getAttribute('class');
    return classes?.includes('active') || false;
  }
  
  /**
   * Get processing progress percentage
   */
  async getProcessingProgress(): Promise<number> {
    const progressValue = await this.processingProgress.getAttribute('value');
    return progressValue ? parseInt(progressValue) : 0;
  }
  
  /**
   * Wait for specific processing stage
   */
  async waitForStage(stage: 'analyzing' | 'searching-graph' | 'evaluating-evidence' | 'generating-response', timeout = 10000) {
    const stageElement = this.page.locator(`[data-testid="stage-${stage}"]`);
    
    await this.page.waitForFunction(
      (stageSelector) => {
        const element = document.querySelector(stageSelector);
        return element?.classList.contains('active') || false;
      },
      `[data-testid="stage-${stage}"]`,
      { timeout }
    );
  }
  
  /**
   * Get full response summary text
   */
  async getResponseSummary(): Promise<string> {
    const summaryElement = this.responseCard.locator('[data-testid="response-summary"]');
    return await summaryElement.textContent() || '';
  }
  
  /**
   * Check if response indicates high confidence
   */
  async isHighConfidenceResponse(): Promise<boolean> {
    const confidence = await this.getConfidenceScore();
    return confidence >= 85;
  }
  
  /**
   * Verify IQ Agent branding is present
   */
  async verifyIQBranding(): Promise<boolean> {
    const brandingElements = [
      this.page.locator('text="IQ Agent"'),
      this.page.locator('[data-testid="iq-brain-icon"]'),
      this.page.locator('[data-testid="graphrag-indicator"]')
    ];
    
    for (const element of brandingElements) {
      if (await element.isVisible()) {
        return true;
      }
    }
    
    return false;
  }
  
  /**
   * Get processing stage timeline
   */
  async getStageTimeline(): Promise<{ stage: string; active: boolean }[]> {
    const stages = ['analyzing', 'searching-graph', 'evaluating-evidence', 'generating-response'];
    const timeline = [];
    
    for (const stage of stages) {
      const isActive = await this.isStageActive(stage);
      timeline.push({ stage, active: isActive });
    }
    
    return timeline;
  }
}