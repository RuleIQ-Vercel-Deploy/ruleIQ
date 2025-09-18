/**
 * WebSocket error handling utilities
 */

import { toast } from '@/components/ui/use-toast';

// Error categories
export enum WebSocketErrorType {
  CONNECTION_FAILED = 'CONNECTION_FAILED',
  AUTHENTICATION_FAILED = 'AUTHENTICATION_FAILED',
  RATE_LIMITED = 'RATE_LIMITED',
  SERVER_ERROR = 'SERVER_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  INVALID_MESSAGE = 'INVALID_MESSAGE',
  TIMEOUT = 'TIMEOUT',
  UNKNOWN = 'UNKNOWN'
}

export interface WebSocketError {
  type: WebSocketErrorType;
  code?: string;
  message: string;
  details?: any;
  recoverable: boolean;
  retryAfter?: number; // milliseconds
}

/**
 * Categorize WebSocket errors based on error details
 */
export function categorizeError(error: Error | Event | CloseEvent): WebSocketError {
  // Handle CloseEvent from WebSocket
  if ('code' in error && 'reason' in error) {
    const closeEvent = error as CloseEvent;

    switch (closeEvent.code) {
      case 1000:
        return {
          type: WebSocketErrorType.CONNECTION_FAILED,
          code: String(closeEvent.code),
          message: 'Connection closed normally',
          recoverable: false
        };

      case 1001:
        return {
          type: WebSocketErrorType.CONNECTION_FAILED,
          code: String(closeEvent.code),
          message: 'Endpoint is going away',
          recoverable: true,
          retryAfter: 5000
        };

      case 1002:
      case 1003:
        return {
          type: WebSocketErrorType.INVALID_MESSAGE,
          code: String(closeEvent.code),
          message: 'Protocol error',
          recoverable: false
        };

      case 1006:
        return {
          type: WebSocketErrorType.NETWORK_ERROR,
          code: String(closeEvent.code),
          message: 'Connection lost unexpectedly',
          recoverable: true,
          retryAfter: 2000
        };

      case 1008:
        return {
          type: WebSocketErrorType.SERVER_ERROR,
          code: String(closeEvent.code),
          message: 'Policy violation',
          recoverable: false
        };

      case 1009:
        return {
          type: WebSocketErrorType.INVALID_MESSAGE,
          code: String(closeEvent.code),
          message: 'Message too large',
          recoverable: false
        };

      case 1011:
        return {
          type: WebSocketErrorType.SERVER_ERROR,
          code: String(closeEvent.code),
          message: 'Server error',
          recoverable: true,
          retryAfter: 10000
        };

      case 4000:
        return {
          type: WebSocketErrorType.AUTHENTICATION_FAILED,
          code: String(closeEvent.code),
          message: closeEvent.reason || 'Authentication failed',
          recoverable: false
        };

      case 4429:
        return {
          type: WebSocketErrorType.RATE_LIMITED,
          code: String(closeEvent.code),
          message: closeEvent.reason || 'Too many requests',
          recoverable: true,
          retryAfter: 60000
        };

      default:
        return {
          type: WebSocketErrorType.UNKNOWN,
          code: String(closeEvent.code),
          message: closeEvent.reason || 'Unknown error',
          recoverable: true,
          retryAfter: 5000
        };
    }
  }

  // Handle regular Error objects
  const errorMessage = error instanceof Error ? error.message : String(error);

  // Check for specific error patterns
  if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError')) {
    return {
      type: WebSocketErrorType.NETWORK_ERROR,
      message: 'Network connection failed',
      recoverable: true,
      retryAfter: 2000
    };
  }

  if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
    return {
      type: WebSocketErrorType.AUTHENTICATION_FAILED,
      message: 'Authentication required',
      recoverable: false
    };
  }

  if (errorMessage.includes('429') || errorMessage.includes('rate limit')) {
    return {
      type: WebSocketErrorType.RATE_LIMITED,
      message: 'Rate limit exceeded',
      recoverable: true,
      retryAfter: 60000
    };
  }

  if (errorMessage.includes('500') || errorMessage.includes('503')) {
    return {
      type: WebSocketErrorType.SERVER_ERROR,
      message: 'Server error',
      recoverable: true,
      retryAfter: 10000
    };
  }

  if (errorMessage.includes('timeout')) {
    return {
      type: WebSocketErrorType.TIMEOUT,
      message: 'Connection timeout',
      recoverable: true,
      retryAfter: 3000
    };
  }

  return {
    type: WebSocketErrorType.UNKNOWN,
    message: errorMessage || 'Unknown error occurred',
    recoverable: true,
    retryAfter: 5000
  };
}

/**
 * Get user-friendly error message
 */
export function getUserMessage(error: WebSocketError): string {
  switch (error.type) {
    case WebSocketErrorType.CONNECTION_FAILED:
      return 'Unable to connect to the server. Please check your internet connection.';

    case WebSocketErrorType.AUTHENTICATION_FAILED:
      return 'Authentication failed. Please sign in again.';

    case WebSocketErrorType.RATE_LIMITED:
      return 'Too many requests. Please wait a moment before trying again.';

    case WebSocketErrorType.SERVER_ERROR:
      return 'Server error occurred. Our team has been notified.';

    case WebSocketErrorType.NETWORK_ERROR:
      return 'Network connection lost. Attempting to reconnect...';

    case WebSocketErrorType.INVALID_MESSAGE:
      return 'Invalid message format. Please refresh the page.';

    case WebSocketErrorType.TIMEOUT:
      return 'Connection timeout. Retrying...';

    default:
      return error.message || 'An unexpected error occurred.';
  }
}

/**
 * Get recovery suggestion for error
 */
export function getRecoverySuggestion(error: WebSocketError): string {
  switch (error.type) {
    case WebSocketErrorType.CONNECTION_FAILED:
    case WebSocketErrorType.NETWORK_ERROR:
      return 'Check your internet connection and try again.';

    case WebSocketErrorType.AUTHENTICATION_FAILED:
      return 'Please sign in again to continue.';

    case WebSocketErrorType.RATE_LIMITED:
      return `Please wait ${Math.ceil((error.retryAfter || 60000) / 1000)} seconds before trying again.`;

    case WebSocketErrorType.SERVER_ERROR:
      return 'The issue has been logged. Please try again later.';

    case WebSocketErrorType.INVALID_MESSAGE:
      return 'Refresh the page to resolve this issue.';

    default:
      return error.recoverable ? 'The system will retry automatically.' : 'Please refresh the page.';
  }
}

/**
 * Exponential backoff retry delay calculator
 */
export function calculateRetryDelay(
  attempt: number,
  baseDelay: number = 1000,
  maxDelay: number = 30000,
  jitter: boolean = true
): number {
  const exponentialDelay = Math.min(baseDelay * Math.pow(2, attempt - 1), maxDelay);

  if (jitter) {
    // Add random jitter to prevent thundering herd
    const jitterAmount = exponentialDelay * 0.1 * Math.random();
    return Math.floor(exponentialDelay + jitterAmount);
  }

  return exponentialDelay;
}

/**
 * Message queue for persisting messages during disconnection
 */
export class MessageQueue {
  private queue: any[] = [];
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.maxSize = maxSize;
  }

  enqueue(message: any): boolean {
    if (this.queue.length >= this.maxSize) {
      // Remove oldest message if queue is full
      this.queue.shift();
    }
    this.queue.push(message);
    return true;
  }

  dequeue(): any | undefined {
    return this.queue.shift();
  }

  peek(): any | undefined {
    return this.queue[0];
  }

  size(): number {
    return this.queue.length;
  }

  clear(): void {
    this.queue = [];
  }

  getAll(): any[] {
    return [...this.queue];
  }
}

/**
 * Show error toast notification
 */
export function showErrorToast(error: WebSocketError): void {
  const message = getUserMessage(error);
  const suggestion = getRecoverySuggestion(error);

  toast({
    title: 'Connection Error',
    description: `${message} ${suggestion}`,
    variant: 'destructive',
    duration: error.recoverable ? 5000 : undefined
  });
}

/**
 * Log WebSocket error for debugging
 */
export function logError(error: WebSocketError, context?: any): void {
  const logLevel = error.recoverable ? 'warn' : 'error';
  const logData = {
    type: error.type,
    code: error.code,
    message: error.message,
    recoverable: error.recoverable,
    retryAfter: error.retryAfter,
    timestamp: new Date().toISOString(),
    ...context
  };

  console[logLevel]('WebSocket Error:', logData);

  // In production, send to error tracking service
  if (process.env.NODE_ENV === 'production') {
    // Send to error tracking service (e.g., Sentry)
    // Sentry.captureException(error, { extra: logData });
  }
}

/**
 * Create error recovery strategy
 */
export interface RecoveryStrategy {
  shouldRetry: (error: WebSocketError, attempt: number) => boolean;
  getDelay: (error: WebSocketError, attempt: number) => number;
  onRetry: (error: WebSocketError, attempt: number) => void;
  onGiveUp: (error: WebSocketError, attempts: number) => void;
}

export function createRecoveryStrategy(options?: Partial<RecoveryStrategy>): RecoveryStrategy {
  return {
    shouldRetry: options?.shouldRetry || ((error, attempt) => {
      return error.recoverable && attempt < 5;
    }),

    getDelay: options?.getDelay || ((error, attempt) => {
      const baseDelay = error.retryAfter || 1000;
      return calculateRetryDelay(attempt, baseDelay);
    }),

    onRetry: options?.onRetry || ((error, attempt) => {
      console.log(`Retrying connection (attempt ${attempt})...`);
    }),

    onGiveUp: options?.onGiveUp || ((error, attempts) => {
      showErrorToast({
        ...error,
        message: `Failed to connect after ${attempts} attempts`,
        recoverable: false
      });
    })
  };
}