import { 
  type Question, 
  type AssessmentFramework, 
  type AssessmentSection,
  type AssessmentResult,
  type Gap
} from './types';

export class AssessmentUtils {
  /**
   * Generate a unique assessment ID
   */
  static generateAssessmentId(): string {
    const timestamp = Date.now().toString(36);
    const randomStr = Math.random().toString(36).substring(2, 9);
    return `ASM-${timestamp}-${randomStr}`.toUpperCase();
  }

  /**
   * Calculate estimated time to complete assessment
   */
  static calculateEstimatedTime(framework: AssessmentFramework): number {
    if (framework.estimatedDuration) {
      return framework.estimatedDuration;
    }

    let totalTime = 0;
    framework.sections.forEach(section => {
      section.questions.forEach(question => {
        // Estimate based on question type
        switch (question.type) {
          case 'radio':
          case 'checkbox':
          case 'select':
            totalTime += 0.5; // 30 seconds
            break;
          case 'text':
          case 'number':
          case 'date':
            totalTime += 1; // 1 minute
            break;
          case 'textarea':
            totalTime += 2; // 2 minutes
            break;
          case 'matrix':
            totalTime += 3; // 3 minutes
            break;
          case 'file_upload':
            totalTime += 2; // 2 minutes
            break;
          default:
            totalTime += 1;
        }
      });
    });

    return Math.ceil(totalTime);
  }

  /**
   * Format time duration for display
   */
  static formatDuration(minutes: number): string {
    if (minutes < 60) {
      return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
    }
    
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (remainingMinutes === 0) {
      return `${hours} hour${hours !== 1 ? 's' : ''}`;
    }
    
    return `${hours} hour${hours !== 1 ? 's' : ''} ${remainingMinutes} minute${remainingMinutes !== 1 ? 's' : ''}`;
  }

  /**
   * Get question by ID from framework
   */
  static getQuestionById(
    framework: AssessmentFramework, 
    questionId: string
  ): Question | null {
    for (const section of framework.sections) {
      const question = section.questions.find(q => q.id === questionId);
      if (question) return question;
    }
    return null;
  }

  /**
   * Get section containing a specific question
   */
  static getSectionByQuestionId(
    framework: AssessmentFramework,
    questionId: string
  ): AssessmentSection | null {
    return framework.sections.find(section =>
      section.questions.some(q => q.id === questionId)
    ) || null;
  }

  /**
   * Export assessment result to JSON
   */
  static exportToJSON(result: AssessmentResult): string {
    return JSON.stringify(result, null, 2);
  }

  /**
   * Generate compliance certificate data
   */
  static generateCertificateData(result: AssessmentResult): {
    title: string;
    score: number;
    level: string;
    date: string;
    validUntil: string;
  } {
    const validityPeriod = result.overallScore >= 80 ? 12 : 6; // months
    const validUntil = new Date();
    validUntil.setMonth(validUntil.getMonth() + validityPeriod);

    return {
      title: `${result.frameworkId} Compliance Certificate`,
      score: result.overallScore,
      level: result.maturityLevel || 'initial',
      date: result.completedAt.toLocaleDateString(),
      validUntil: validUntil.toLocaleDateString()
    };
  }

  /**
   * Group gaps by section
   */
  static groupGapsBySection(gaps: Gap[]): Record<string, Gap[]> {
    return gaps.reduce((acc, gap) => {
      if (!acc[gap.section]) {
        acc[gap.section] = [];
      }
      acc[gap.section]!.push(gap);
      return acc;
    }, {} as Record<string, Gap[]>);
  }

  /**
   * Calculate section completion percentage
   */
  static calculateSectionCompletion(
    section: AssessmentSection,
    answers: Map<string, any>
  ): number {
    const totalQuestions = section.questions.length;
    if (totalQuestions === 0) return 100;

    const answeredQuestions = section.questions.filter(
      question => answers.has(question.id)
    ).length;

    return Math.round((answeredQuestions / totalQuestions) * 100);
  }

  /**
   * Get unanswered required questions
   */
  static getUnansweredRequiredQuestions(
    framework: AssessmentFramework,
    answers: Map<string, any>
  ): Question[] {
    const unanswered: Question[] = [];

    framework.sections.forEach(section => {
      section.questions.forEach(question => {
        if (
          question.validation?.required &&
          !answers.has(question.id)
        ) {
          unanswered.push(question);
        }
      });
    });

    return unanswered;
  }

  /**
   * Sanitize user input
   */
  static sanitizeInput(input: string): string {
    // Basic XSS prevention
    return input
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
  }

  /**
   * Parse file size to human readable format
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))  } ${  sizes[i]}`;
  }

  /**
   * Check if assessment is expired
   */
  static isAssessmentExpired(completedDate: Date, validityMonths: number = 12): boolean {
    const expiryDate = new Date(completedDate);
    expiryDate.setMonth(expiryDate.getMonth() + validityMonths);
    return new Date() > expiryDate;
  }

  /**
   * Get color class based on score
   */
  static getScoreColorClass(score: number): string {
    if (score >= 90) return 'text-green-600 bg-green-50';
    if (score >= 75) return 'text-blue-600 bg-blue-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    if (score >= 40) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  }

  /**
   * Get maturity level label
   */
  static getMaturityLevelLabel(level: string): {
    label: string;
    description: string;
    color: string;
  } {
    const levels = {
      initial: {
        label: 'Initial',
        description: 'Ad-hoc processes, reactive approach',
        color: 'red'
      },
      developing: {
        label: 'Developing',
        description: 'Some documented processes, inconsistent implementation',
        color: 'orange'
      },
      defined: {
        label: 'Defined',
        description: 'Standardized processes, regular reviews',
        color: 'yellow'
      },
      managed: {
        label: 'Managed',
        description: 'Measured and controlled processes, proactive approach',
        color: 'blue'
      },
      optimized: {
        label: 'Optimized',
        description: 'Continuous improvement, industry best practices',
        color: 'green'
      }
    };

    return levels[level as keyof typeof levels] || levels.initial;
  }
}