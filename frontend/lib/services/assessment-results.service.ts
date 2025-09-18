/**
 * Assessment Results Service
 * Manages assessment results data including historical trends and export functionality
 */

import { freemiumService, type AssessmentResultsResponse } from '@/lib/api/freemium.service';
import type {
  AssessmentResult,
  AssessmentFramework,
  Gap,
  Recommendation
} from '@/lib/assessment-engine/types';
import type {
  FreemiumSession,
  ComplianceGap,
  ComplianceRecommendation
} from '@/types/freemium';
import type { BusinessProfile, Assessment } from '@/types/api';
import type { TrendDataPoint } from '@/types/assessment-results';

// ============================================================================
// TYPES
// ============================================================================

export interface HistoricalAssessment {
  id: string;
  sessionId: string;
  businessProfileId: string;
  frameworkId: string;
  frameworkName: string;
  overallScore: number;
  riskScore: number;
  completionPercentage: number;
  completedAt: string;
  sectionScores: Record<string, number>;
  gapsCount: number;
  recommendationsCount: number;
  metadata?: Record<string, any>;
}

export interface TrendAnalysisData {
  dataPoints: TrendDataPoint[];
  timePeriod: 'last_30_days' | 'last_3_months' | 'last_6_months' | 'last_year' | 'all_time';
  summary: {
    totalAssessments: number;
    averageScore: number;
    scoreImprovement: number;
    bestScore: number;
    worstScore: number;
    latestScore: number;
    trend: 'improving' | 'declining' | 'stable';
  };
  sectionTrends: Record<string, {
    average: number;
    improvement: number;
    trend: 'improving' | 'declining' | 'stable';
  }>;
}

export interface ExportData {
  assessment: {
    id: string;
    sessionId: string;
    frameworkName: string;
    businessProfile: Partial<BusinessProfile>;
    completedAt: string;
    overallScore: number;
    riskScore: number;
    completionPercentage: number;
  };
  sections: Array<{
    name: string;
    score: number;
    questionsTotal: number;
    questionsAnswered: number;
    completionRate: number;
  }>;
  gaps: Array<{
    category: string;
    severity: string;
    description: string;
    recommendation: string;
    estimatedEffort: string;
    regulatoryImpact: string;
  }>;
  recommendations: Array<{
    priority: string;
    category: string;
    title: string;
    description: string;
    implementationGuidance: string;
    estimatedCost: string;
    timeline: string;
    businessImpact: string;
  }>;
  summary: {
    strengths: string[];
    weaknesses: string[];
    criticalAreas: string[];
    nextSteps: string[];
  };
  metadata: {
    exportedAt: string;
    exportedBy?: string;
    reportVersion: string;
  };
}

export interface AssessmentResultsCache {
  [sessionToken: string]: {
    data: AssessmentResultsResponse;
    timestamp: number;
    expiresAt: number;
  };
}

export interface ServiceOptions {
  cacheEnabled?: boolean;
  cacheTTL?: number; // in milliseconds
  enableHistoricalData?: boolean;
  maxHistoricalRecords?: number;
}

// ============================================================================
// SERVICE CLASS
// ============================================================================

class AssessmentResultsService {
  private cache: AssessmentResultsCache = {};
  private historicalData: Map<string, HistoricalAssessment[]> = new Map();
  private options: ServiceOptions;

  constructor(options: ServiceOptions = {}) {
    this.options = {
      cacheEnabled: true,
      cacheTTL: 5 * 60 * 1000, // 5 minutes
      enableHistoricalData: true,
      maxHistoricalRecords: 50,
      ...options,
    };
  }

  // ============================================================================
  // CACHE MANAGEMENT
  // ============================================================================

  private getCachedResults(sessionToken: string): AssessmentResultsResponse | null {
    if (!this.options.cacheEnabled) return null;

    const cached = this.cache[sessionToken];
    if (!cached) return null;

    const now = Date.now();
    if (now > cached.expiresAt) {
      delete this.cache[sessionToken];
      return null;
    }

    return cached.data;
  }

  private setCachedResults(sessionToken: string, data: AssessmentResultsResponse): void {
    if (!this.options.cacheEnabled) return;

    const now = Date.now();
    this.cache[sessionToken] = {
      data,
      timestamp: now,
      expiresAt: now + (this.options.cacheTTL || 5 * 60 * 1000),
    };
  }

  private clearCache(): void {
    this.cache = {};
  }

  private cleanExpiredCache(): void {
    const now = Date.now();
    Object.keys(this.cache).forEach(key => {
      if (now > this.cache[key].expiresAt) {
        delete this.cache[key];
      }
    });
  }

  // ============================================================================
  // RESULTS FETCHING
  // ============================================================================

  /**
   * Get assessment results with caching
   */
  async getResults(sessionToken: string, forceRefresh = false): Promise<AssessmentResultsResponse> {
    try {
      // Check cache first
      if (!forceRefresh) {
        const cached = this.getCachedResults(sessionToken);
        if (cached) {
          return cached;
        }
      }

      // Fetch from API
      const results = await freemiumService.getResults(sessionToken);
      
      // Validate results
      this.validateResults(results);

      // Cache results
      this.setCachedResults(sessionToken, results);

      // Store in historical data if enabled
      if (this.options.enableHistoricalData) {
        await this.storeHistoricalData(sessionToken, results);
      }

      return results;
    } catch (error) {
      console.error('Failed to get assessment results:', error);
      throw new Error(
        error instanceof Error 
          ? `Failed to fetch results: ${error.message}`
          : 'Failed to fetch assessment results'
      );
    }
  }

  /**
   * Validate assessment results data
   */
  private validateResults(results: AssessmentResultsResponse): void {
    if (!results) {
      throw new Error('Results data is null or undefined');
    }

    if (typeof results.compliance_score !== 'number' || results.compliance_score < 0 || results.compliance_score > 100) {
      throw new Error('Invalid compliance score');
    }

    if (typeof results.risk_score !== 'number' || results.risk_score < 0 || results.risk_score > 100) {
      throw new Error('Invalid risk score');
    }

    if (!Array.isArray(results.compliance_gaps)) {
      throw new Error('Compliance gaps must be an array');
    }

    if (!Array.isArray(results.recommendations)) {
      throw new Error('Recommendations must be an array');
    }
  }

  // ============================================================================
  // HISTORICAL DATA MANAGEMENT
  // ============================================================================

  /**
   * Get assessment history for a business profile
   * Attempts to fetch from API first, falls back to local cache
   */
  // TypeScript overloads for getAssessmentHistory
  async getAssessmentHistory(
    businessProfileId: string,
    options?: { 
      limit?: number;
      includeArchived?: boolean;
    }
  ): Promise<HistoricalAssessment[]>;
  async getAssessmentHistory(
    businessProfileId: string,
    frameworkId?: string,
    limit?: number
  ): Promise<HistoricalAssessment[]>;
  
  // Single implementation handling both signatures
  async getAssessmentHistory(
    businessProfileId: string,
    optionsOrFrameworkId?: { limit?: number; includeArchived?: boolean } | string,
    limit?: number
  ): Promise<HistoricalAssessment[]> {
    try {
      // Handle overload signatures
      let frameworkId: string | undefined;
      let options: { limit?: number; includeArchived?: boolean } | undefined;
      
      if (typeof optionsOrFrameworkId === 'string') {
        // Second signature: (businessProfileId, frameworkId?, limit?)
        frameworkId = optionsOrFrameworkId;
        options = { limit };
      } else {
        // First signature: (businessProfileId, options?)
        options = optionsOrFrameworkId;
      }
      
      // First try to fetch from API if available
      try {
        const response = await freemiumService.getAssessmentHistory?.(businessProfileId);
        if (response && Array.isArray(response)) {
          // Store in local cache for offline access
          const historicalRecords = response.map((item: any) => ({
            id: item.id || `${item.session_id}_${Date.now()}`,
            sessionId: item.session_id,
            businessProfileId: businessProfileId,
            frameworkId: item.framework_id || 'freemium_framework',
            frameworkName: item.framework_name || 'Freemium Assessment',
            overallScore: item.compliance_score,
            riskScore: item.risk_score,
            completionPercentage: item.completion_percentage,
            completedAt: item.results_generated_at || item.created_at,
            sectionScores: item.section_scores || {},
            gapsCount: item.gaps_count || 0,
            recommendationsCount: item.recommendations_count || 0,
            metadata: item.metadata || {}
          }));

          // Sort by completedAt descending to ensure consistent ordering
          historicalRecords.sort((a, b) =>
            new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime()
          );

          // Update local cache
          this.historicalData.set(businessProfileId, historicalRecords);

          // Apply filters and limits
          let filtered = historicalRecords;
          
          // Filter by framework if specified
          if (frameworkId) {
            filtered = filtered.filter(h => h.frameworkId === frameworkId);
          }
          
          if (!options?.includeArchived) {
            filtered = filtered.filter(record => !record.metadata?.archived);
          }
          if (options?.limit) {
            filtered = filtered.slice(0, options.limit);
          }
          
          return filtered;
        }
      } catch (apiError) {
        console.warn('Failed to fetch from API, using local cache:', apiError);
      }

      // Fallback to local cache
      const localHistory = this.historicalData.get(businessProfileId) || [];
      
      // Apply filters and limits
      let filtered = [...localHistory];
      
      // Filter by framework if specified
      if (frameworkId) {
        filtered = filtered.filter(h => h.frameworkId === frameworkId);
      }
      
      if (!options?.includeArchived) {
        filtered = filtered.filter(record => !record.metadata?.archived);
      }
      if (options?.limit) {
        filtered = filtered.slice(0, options.limit);
      }
      
      // Sort by date (newest first)
      filtered.sort((a, b) => new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime());
      
      return filtered;
    } catch (error) {
      console.error('Failed to get assessment history:', error);
      // Return empty array instead of throwing to allow graceful degradation
      return [];
    }
  }

  /**
   * Store assessment results in historical data
   */
  private async storeHistoricalData(
    sessionToken: string,
    results: AssessmentResultsResponse
  ): Promise<void> {
    try {
      // Use lead_id if available, otherwise fall back to session token
      // This provides better continuity for returning users
      const businessProfileKey = results.lead_id || sessionToken;

      const historicalRecord: HistoricalAssessment = {
        id: `${results.session_id}_${Date.now()}`,
        sessionId: results.session_id,
        businessProfileId: businessProfileKey,
        frameworkId: 'freemium_framework',
        frameworkName: 'Freemium Assessment',
        overallScore: results.compliance_score,
        riskScore: results.risk_score,
        completionPercentage: results.completion_percentage,
        completedAt: results.results_generated_at,
        sectionScores: this.extractSectionScores(results),
        gapsCount: results.compliance_gaps.length,
        recommendationsCount: results.recommendations.length,
        metadata: {
          sessionToken,
          resultsSummary: results.results_summary,
        },
      };

      // Get existing historical data
      const existing = this.historicalData.get(businessProfileKey) || [];

      // Check for duplicate session_id to prevent storing the same result multiple times
      const isDuplicate = existing.some(record => record.sessionId === results.session_id);

      if (!isDuplicate) {
        // Add new record only if not a duplicate
        existing.push(historicalRecord);

        // Sort by completion date (newest first)
        existing.sort((a, b) => new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime());

        // Limit records if configured
        if (this.options.maxHistoricalRecords && existing.length > this.options.maxHistoricalRecords) {
          existing.splice(this.options.maxHistoricalRecords);
        }

        // Store back
        this.historicalData.set(businessProfileKey, existing);
      } else {
        // Update existing record with the same session_id if needed
        const recordIndex = existing.findIndex(record => record.sessionId === results.session_id);
        if (recordIndex !== -1) {
          existing[recordIndex] = historicalRecord;
          this.historicalData.set(businessProfileKey, existing);
        }
      }

    } catch (error) {
      console.error('Failed to store historical data:', error);
      // Don't throw - this is not critical for the main flow
    }
  }

  /**
   * Extract section scores from results (mock implementation for freemium)
   */
  private extractSectionScores(results: AssessmentResultsResponse): Record<string, number> {
    // For freemium assessments, we'll create mock section scores based on gaps
    const sections: Record<string, number> = {};
    
    // Group gaps by category to create section scores
    const gapsByCategory = results.compliance_gaps.reduce((acc, gap) => {
      if (!acc[gap.category]) {
        acc[gap.category] = [];
      }
      acc[gap.category].push(gap);
      return acc;
    }, {} as Record<string, ComplianceGap[]>);

    // Calculate section scores based on gap severity
    Object.entries(gapsByCategory).forEach(([category, gaps]) => {
      const severityWeights = { critical: 0, high: 25, medium: 50, low: 75 };
      const avgSeverityScore = gaps.reduce((sum, gap) => {
        return sum + (severityWeights[gap.severity] || 50);
      }, 0) / gaps.length;
      
      sections[category] = Math.round(avgSeverityScore);
    });

    // Ensure we have some default sections
    if (Object.keys(sections).length === 0) {
      sections['Data Protection'] = results.compliance_score;
      sections['Security Controls'] = Math.max(0, results.compliance_score - 10);
      sections['Access Management'] = Math.max(0, results.compliance_score - 5);
      sections['Documentation'] = Math.max(0, results.compliance_score + 5);
    }

    return sections;
  }



  // ============================================================================
  // TREND ANALYSIS
  // ============================================================================

  /**
   * Generate trend analysis data from historical assessments
   */
  async generateTrendData(
    businessProfileId: string,
    timePeriod: TrendAnalysisData['timePeriod'] = 'last_3_months',
    frameworkId?: string
  ): Promise<TrendAnalysisData> {
    try {
      const historical = await this.getAssessmentHistory(businessProfileId, frameworkId);
      
      // Filter by time period
      const filteredData = this.filterByTimePeriod(historical, timePeriod);

      if (filteredData.length === 0) {
        return this.createEmptyTrendData(timePeriod);
      }

      // Defensively sort by completedAt descending before summary calculations
      filteredData.sort((a, b) =>
        new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime()
      );

      // Convert to trend data points
      const dataPoints = this.convertToTrendDataPoints(filteredData);
      
      // Calculate summary statistics
      const summary = this.calculateTrendSummary(dataPoints);
      
      // Calculate section trends
      const sectionTrends = this.calculateSectionTrends(dataPoints);

      return {
        dataPoints,
        timePeriod,
        summary,
        sectionTrends,
      };
    } catch (error) {
      console.error('Failed to generate trend data:', error);
      return this.createEmptyTrendData(timePeriod);
    }
  }

  /**
   * Filter historical data by time period
   */
  private filterByTimePeriod(
    historical: HistoricalAssessment[],
    timePeriod: TrendAnalysisData['timePeriod']
  ): HistoricalAssessment[] {
    if (timePeriod === 'all_time') {
      return historical;
    }

    const now = new Date();
    const cutoffDate = new Date();

    switch (timePeriod) {
      case 'last_30_days':
        cutoffDate.setDate(now.getDate() - 30);
        break;
      case 'last_3_months':
        cutoffDate.setMonth(now.getMonth() - 3);
        break;
      case 'last_6_months':
        cutoffDate.setMonth(now.getMonth() - 6);
        break;
      case 'last_year':
        cutoffDate.setFullYear(now.getFullYear() - 1);
        break;
    }

    return historical.filter(h => new Date(h.completedAt) >= cutoffDate);
  }

  /**
   * Convert historical assessments to trend data points
   */
  private convertToTrendDataPoints(historical: HistoricalAssessment[]): TrendDataPoint[] {
    return historical.map((assessment, index) => {
      const dataPoint: TrendDataPoint = {
        date: assessment.completedAt,
        overallScore: assessment.overallScore,
        riskScore: assessment.riskScore,
        completionPercentage: assessment.completionPercentage,
        sectionScores: assessment.sectionScores,
        assessmentId: assessment.id,
      };

      // Calculate change from previous assessment
      if (index < historical.length - 1) {
        const previous = historical[index + 1];
        dataPoint.changeFromPrevious = {
          overallScore: assessment.overallScore - previous.overallScore,
          riskScore: assessment.riskScore - previous.riskScore,
          completionPercentage: assessment.completionPercentage - previous.completionPercentage,
        };
      }

      return dataPoint;
    });
  }

  /**
   * Calculate trend summary statistics
   */
  private calculateTrendSummary(dataPoints: TrendDataPoint[]): TrendAnalysisData['summary'] {
    if (dataPoints.length === 0) {
      return {
        totalAssessments: 0,
        averageScore: 0,
        scoreImprovement: 0,
        bestScore: 0,
        worstScore: 0,
        latestScore: 0,
        trend: 'stable',
      };
    }

    const scores = dataPoints.map(dp => dp.overallScore);
    const totalAssessments = dataPoints.length;
    const averageScore = scores.reduce((sum, score) => sum + score, 0) / totalAssessments;
    const bestScore = Math.max(...scores);
    const worstScore = Math.min(...scores);
    const latestScore = scores[0]; // First item is latest (sorted desc)
    
    // Calculate improvement (latest vs oldest)
    const oldestScore = scores[scores.length - 1];
    const scoreImprovement = latestScore - oldestScore;
    
    // Determine trend
    let trend: 'improving' | 'declining' | 'stable' = 'stable';
    if (scoreImprovement > 5) {
      trend = 'improving';
    } else if (scoreImprovement < -5) {
      trend = 'declining';
    }

    return {
      totalAssessments,
      averageScore: Math.round(averageScore * 100) / 100,
      scoreImprovement: Math.round(scoreImprovement * 100) / 100,
      bestScore,
      worstScore,
      latestScore,
      trend,
    };
  }

  /**
   * Calculate section-specific trends
   */
  private calculateSectionTrends(dataPoints: TrendDataPoint[]): TrendAnalysisData['sectionTrends'] {
    const sectionTrends: Record<string, any> = {};
    
    if (dataPoints.length === 0) {
      return sectionTrends;
    }

    // Get all unique section names
    const allSections = new Set<string>();
    dataPoints.forEach(dp => {
      Object.keys(dp.sectionScores).forEach(section => allSections.add(section));
    });

    // Calculate trends for each section
    allSections.forEach(sectionName => {
      const sectionScores = dataPoints
        .map(dp => dp.sectionScores[sectionName])
        .filter(score => score !== undefined);

      if (sectionScores.length > 0) {
        const average = sectionScores.reduce((sum, score) => sum + score, 0) / sectionScores.length;
        const latest = sectionScores[0];
        const oldest = sectionScores[sectionScores.length - 1];
        const improvement = latest - oldest;

        let trend: 'improving' | 'declining' | 'stable' = 'stable';
        if (improvement > 5) {
          trend = 'improving';
        } else if (improvement < -5) {
          trend = 'declining';
        }

        sectionTrends[sectionName] = {
          average: Math.round(average * 100) / 100,
          improvement: Math.round(improvement * 100) / 100,
          trend,
        };
      }
    });

    return sectionTrends;
  }

  /**
   * Create empty trend data for cases with no historical data
   */
  private createEmptyTrendData(timePeriod: TrendAnalysisData['timePeriod']): TrendAnalysisData {
    return {
      dataPoints: [],
      timePeriod,
      summary: {
        totalAssessments: 0,
        averageScore: 0,
        scoreImprovement: 0,
        bestScore: 0,
        worstScore: 0,
        latestScore: 0,
        trend: 'stable',
      },
      sectionTrends: {},
    };
  }

  // ============================================================================
  // EXPORT DATA PREPARATION
  // ============================================================================

  /**
   * Prepare assessment data for export
   */
  async prepareExportData(
    sessionToken: string,
    businessProfile?: Partial<BusinessProfile>
  ): Promise<ExportData> {
    try {
      const results = await this.getResults(sessionToken);
      
      return {
        assessment: {
          id: results.session_id,
          sessionId: results.session_id,
          frameworkName: 'Freemium Compliance Assessment',
          businessProfile: businessProfile || {
            company_name: results.lead_id ? `Company ${results.lead_id.slice(0, 8)}` : 'Unknown Company',
            industry: 'Unknown',
            id: results.lead_id || results.session_id,
          },
          completedAt: results.results_generated_at,
          overallScore: results.compliance_score,
          riskScore: results.risk_score,
          completionPercentage: results.completion_percentage,
        },
        sections: this.prepareSectionData(results),
        gaps: this.prepareGapsData(results.compliance_gaps),
        recommendations: this.prepareRecommendationsData(results.recommendations),
        summary: {
          strengths: results.detailed_analysis?.strengths || [],
          weaknesses: results.detailed_analysis?.weaknesses || [],
          criticalAreas: results.detailed_analysis?.critical_areas || [],
          nextSteps: results.detailed_analysis?.next_steps || [],
        },
        metadata: {
          exportedAt: new Date().toISOString(),
          reportVersion: '1.0',
        },
      };
    } catch (error) {
      console.error('Failed to prepare export data:', error);
      throw new Error(
        error instanceof Error 
          ? `Failed to prepare export data: ${error.message}`
          : 'Failed to prepare export data'
      );
    }
  }

  /**
   * Prepare section data for export
   */
  private prepareSectionData(results: AssessmentResultsResponse): ExportData['sections'] {
    const sectionScores = this.extractSectionScores(results);
    
    return Object.entries(sectionScores).map(([name, score]) => ({
      name,
      score,
      questionsTotal: 10, // Mock data for freemium
      questionsAnswered: Math.round((results.completion_percentage / 100) * 10),
      completionRate: results.completion_percentage,
    }));
  }

  /**
   * Prepare gaps data for export
   */
  private prepareGapsData(gaps: ComplianceGap[]): ExportData['gaps'] {
    return gaps.map(gap => ({
      category: gap.category,
      severity: gap.severity,
      description: gap.description,
      recommendation: gap.recommendation,
      estimatedEffort: gap.estimated_effort,
      regulatoryImpact: gap.regulatory_impact,
    }));
  }

  /**
   * Prepare recommendations data for export
   */
  private prepareRecommendationsData(recommendations: ComplianceRecommendation[]): ExportData['recommendations'] {
    return recommendations.map(rec => ({
      priority: rec.priority,
      category: rec.category,
      title: rec.title,
      description: rec.description,
      implementationGuidance: rec.implementation_guidance,
      estimatedCost: rec.estimated_cost,
      timeline: rec.timeline,
      businessImpact: rec.business_impact,
    }));
  }

  // ============================================================================
  // DATA TRANSFORMATION
  // ============================================================================

  /**
   * Transform freemium results to assessment engine format
   */
  transformToAssessmentResult(
    results: AssessmentResultsResponse,
    frameworkId: string = 'freemium_framework'
  ): AssessmentResult {
    return {
      assessmentId: results.session_id,
      frameworkId,
      overallScore: results.compliance_score,
      sectionScores: this.extractSectionScores(results),
      gaps: this.transformGaps(results.compliance_gaps),
      recommendations: this.transformRecommendations(results.recommendations),
      completedAt: new Date(results.results_generated_at),
    };
  }

  /**
   * Transform compliance gaps to assessment engine format
   */
  private transformGaps(gaps: ComplianceGap[]): Gap[] {
    return gaps.map((gap, index) => ({
      id: `gap_${index}`,
      questionId: `question_${gap.category.toLowerCase().replace(/\s+/g, '_')}`,
      questionText: `${gap.category} compliance question`,
      section: gap.category,
      category: gap.category,
      severity: gap.severity,
      description: gap.description,
      impact: gap.regulatory_impact,
      currentState: 'Non-compliant',
      targetState: 'Compliant',
      expectedAnswer: 'Yes',
      actualAnswer: 'No',
    }));
  }

  /**
   * Transform compliance recommendations to assessment engine format
   */
  private transformRecommendations(recommendations: ComplianceRecommendation[]): Recommendation[] {
    return recommendations.map((rec, index) => ({
      id: `rec_${index}`,
      gapId: `gap_${index}`,
      priority: this.mapPriorityToTimeframe(rec.priority),
      title: rec.title,
      description: rec.description,
      estimatedEffort: rec.estimated_cost,
      category: rec.category,
      impact: rec.business_impact,
      effort: rec.estimated_cost,
      estimatedTime: rec.timeline,
    }));
  }

  /**
   * Map priority levels to timeframes
   */
  private mapPriorityToTimeframe(priority: string): 'immediate' | 'short_term' | 'medium_term' | 'long_term' {
    switch (priority.toLowerCase()) {
      case 'critical':
        return 'immediate';
      case 'high':
        return 'short_term';
      case 'medium':
        return 'medium_term';
      case 'low':
      default:
        return 'long_term';
    }
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  /**
   * Clear all cached data
   */
  clearAllCache(): void {
    this.clearCache();
    this.historicalData.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): {
    cachedResults: number;
    historicalProfiles: number;
    totalHistoricalRecords: number;
  } {
    const totalHistoricalRecords = Array.from(this.historicalData.values())
      .reduce((sum, records) => sum + records.length, 0);

    return {
      cachedResults: Object.keys(this.cache).length,
      historicalProfiles: this.historicalData.size,
      totalHistoricalRecords,
    };
  }

  /**
   * Health check for the service
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    details: Record<string, any>;
  }> {
    try {
      // Clean expired cache
      this.cleanExpiredCache();

      // Check freemium service
      await freemiumService.healthCheck();

      const stats = this.getCacheStats();

      return {
        status: 'healthy',
        details: {
          cacheEnabled: this.options.cacheEnabled,
          historicalDataEnabled: this.options.enableHistoricalData,
          ...stats,
          lastCheck: new Date().toISOString(),
        },
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        details: {
          error: error instanceof Error ? error.message : 'Unknown error',
          lastCheck: new Date().toISOString(),
        },
      };
    }
  }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

export const assessmentResultsService = new AssessmentResultsService();

// ============================================================================
// EXPORTS
// ============================================================================

export default AssessmentResultsService;
export type {
  HistoricalAssessment,
  TrendDataPoint,
  TrendAnalysisData,
  ExportData,
  ServiceOptions,
};