/**
 * Rate Limit Notice Component
 * Displays user-friendly rate limiting messages for AI endpoints
 */

import { AlertTriangle, Clock, Info } from 'lucide-react';
import React from 'react';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface RateLimitNoticeProps {
  operation: string;
  retryAfter: number;
  limit: number;
  window: string;
  suggestion?: string;
  onRetry?: () => void;
  className?: string;
}

export function RateLimitNotice({
  operation,
  retryAfter,
  limit,
  window,
  suggestion,
  onRetry,
  className
}: RateLimitNoticeProps) {
  const [countdown, setCountdown] = React.useState(retryAfter);
  const [canRetry, setCanRetry] = React.useState(false);

  React.useEffect(() => {
    if (countdown <= 0) {
      setCanRetry(true);
      return;
    }

    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          setCanRetry(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [countdown]);

  const formatTime = (seconds: number) => {
    if (seconds < 60) {
      return `${seconds} second${seconds !== 1 ? 's' : ''}`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getOperationDisplayName = (op: string) => {
    switch (op.toLowerCase()) {
      case 'help':
        return 'AI Help';
      case 'followup':
        return 'AI Follow-up Questions';
      case 'analysis':
        return 'AI Analysis';
      case 'recommendations':
        return 'AI Recommendations';
      default:
        return 'AI Service';
    }
  };

  return (
    <Alert className={`border-orange-200 bg-orange-50 ${className}`}>
      <AlertTriangle className="h-4 w-4 text-orange-600" />
      <AlertTitle className="text-orange-800 font-semibold">
        Rate Limit Reached
      </AlertTitle>
      <AlertDescription className="text-orange-700 space-y-3">
        <div>
          You've reached the rate limit for <strong>{getOperationDisplayName(operation)}</strong>.
        </div>
        
        <div className="flex items-center gap-2 text-sm">
          <Badge variant="outline" className="border-orange-300 text-orange-700">
            {limit} requests per {window}
          </Badge>
        </div>

        {!canRetry && (
          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4" />
            <span>
              Please wait <strong>{formatTime(countdown)}</strong> before trying again
            </span>
          </div>
        )}

        {suggestion && (
          <div className="text-sm bg-orange-100 p-3 rounded-md border border-orange-200">
            <div className="flex items-start gap-2">
              <Info className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
              <span>{suggestion}</span>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <div className="text-sm font-medium">While you wait, you can:</div>
          <ul className="text-sm space-y-1 ml-4">
            <li>• Review existing guidance and recommendations</li>
            <li>• Continue with other assessment questions</li>
            <li>• Check our knowledge base for immediate answers</li>
            {operation === 'help' && (
              <li>• Consult the framework documentation directly</li>
            )}
          </ul>
        </div>

        {canRetry && onRetry && (
          <div className="pt-2">
            <Button 
              onClick={onRetry}
              variant="outline"
              size="sm"
              className="border-orange-300 text-orange-700 hover:bg-orange-100"
            >
              Try Again
            </Button>
          </div>
        )}
      </AlertDescription>
    </Alert>
  );
}

interface RateLimitInfoProps {
  operation: string;
  remaining: number;
  limit: number;
  window: string;
  className?: string;
}

export function RateLimitInfo({
  operation,
  remaining,
  limit,
  window,
  className
}: RateLimitInfoProps) {
  const percentage = (remaining / limit) * 100;
  const isLow = percentage < 20;
  const isVeryLow = percentage < 10;

  if (remaining === limit) {
    return null; // Don't show when at full capacity
  }

  return (
    <div className={`text-xs text-gray-500 ${className}`}>
      <div className="flex items-center justify-between">
        <span>
          {remaining} of {limit} {operation} requests remaining
        </span>
        <Badge 
          variant={isVeryLow ? "destructive" : isLow ? "secondary" : "outline"}
          className="text-xs"
        >
          {Math.round(percentage)}%
        </Badge>
      </div>
      
      {isLow && (
        <div className="mt-1 text-orange-600">
          <Info className="h-3 w-3 inline mr-1" />
          Rate limit resets every {window}
        </div>
      )}
    </div>
  );
}

// Hook for managing rate limit state
export function useRateLimitState(_operation: string) {
  const [rateLimitInfo, setRateLimitInfo] = React.useState<{
    isRateLimited: boolean;
    retryAfter: number;
    limit: number;
    window: string;
    remaining: number;
    suggestion?: string;
  } | null>(null);

  const handleRateLimitError = React.useCallback((error: any) => {
    if (error.response?.status === 429) {
      const rateLimitError = error.response.data;
      setRateLimitInfo({
        isRateLimited: true,
        retryAfter: rateLimitError.error.retry_after,
        limit: rateLimitError.error.limit,
        window: rateLimitError.error.window,
        remaining: 0,
        suggestion: rateLimitError.suggestion
      });
      return true;
    }
    return false;
  }, []);

  const updateRateLimitHeaders = React.useCallback((headers: any) => {
    const limit = parseInt(headers['x-ratelimit-limit'] || '0');
    const remaining = parseInt(headers['x-ratelimit-remaining'] || '0');
    const window = '1 minute'; // Default window

    if (limit > 0) {
      setRateLimitInfo(prev => ({
        ...prev,
        isRateLimited: false,
        limit,
        remaining,
        window,
        retryAfter: 0
      }));
    }
  }, []);

  const clearRateLimit = React.useCallback(() => {
    setRateLimitInfo(null);
  }, []);

  return {
    rateLimitInfo,
    handleRateLimitError,
    updateRateLimitHeaders,
    clearRateLimit
  };
}
