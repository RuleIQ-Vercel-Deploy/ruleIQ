"use client";

import { Loader2, CheckCircle, XCircle, Play, Pause, RotateCcw } from 'lucide-react';
import React, { useState, useEffect } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

import type { StreamingChunk, StreamingMetadata } from '@/lib/api/assessments-ai.service';

interface StreamingResponseProps {
  title?: string;
  description?: string;
  className?: string;
  showProgress?: boolean;
  showControls?: boolean;
  onRetry?: () => void;
  onCancel?: () => void;
}

export interface StreamingResponseRef {
  addChunk: (chunk: StreamingChunk) => void;
  setMetadata: (metadata: StreamingMetadata) => void;
  setError: (error: string) => void;
  setComplete: () => void;
  reset: () => void;
  pause: () => void;
  resume: () => void;
}

export const StreamingResponse = React.forwardRef<StreamingResponseRef, StreamingResponseProps>(
  ({ title = "AI Analysis", description, className, showProgress = true, showControls = false, onRetry, onCancel }, ref) => {
    const [chunks, setChunks] = useState<StreamingChunk[]>([]);
    const [metadata, setMetadata] = useState<StreamingMetadata | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isComplete, setIsComplete] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [progress, setProgress] = useState(0);
    const [startTime, setStartTime] = useState<Date | null>(null);
    const [elapsedTime, setElapsedTime] = useState(0);

    // Timer for elapsed time
    useEffect(() => {
      let interval: NodeJS.Timeout;
      if (startTime && !isComplete && !isPaused) {
        interval = setInterval(() => {
          setElapsedTime(Math.floor((Date.now() - startTime.getTime()) / 1000));
        }, 1000);
      }
      return () => clearInterval(interval);
    }, [startTime, isComplete, isPaused]);

    // Expose methods via ref
    React.useImperativeHandle(ref, () => ({
      addChunk: (chunk: StreamingChunk) => {
        if (!isPaused) {
          setChunks(prev => [...prev, chunk]);
          // Estimate progress based on chunk count (rough estimate)
          setProgress(prev => Math.min(prev + 5, 90));
        }
      },
      setMetadata: (meta: StreamingMetadata) => {
        setMetadata(meta);
        setStartTime(new Date());
        setProgress(10);
      },
      setError: (errorMsg: string) => {
        setError(errorMsg);
        setIsComplete(true);
      },
      setComplete: () => {
        setIsComplete(true);
        setProgress(100);
      },
      reset: () => {
        setChunks([]);
        setMetadata(null);
        setError(null);
        setIsComplete(false);
        setIsPaused(false);
        setProgress(0);
        setStartTime(null);
        setElapsedTime(0);
      },
      pause: () => setIsPaused(true),
      resume: () => setIsPaused(false)
    }));

    const formatElapsedTime = (seconds: number) => {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const getStatusBadge = () => {
      if (error) {
        return <Badge variant="destructive" className="flex items-center gap-1">
          <XCircle className="h-3 w-3" />
          Error
        </Badge>;
      }
      if (isComplete) {
        return <Badge variant="default" className="flex items-center gap-1 bg-green-600">
          <CheckCircle className="h-3 w-3" />
          Complete
        </Badge>;
      }
      if (isPaused) {
        return <Badge variant="secondary" className="flex items-center gap-1">
          <Pause className="h-3 w-3" />
          Paused
        </Badge>;
      }
      return <Badge variant="outline" className="flex items-center gap-1">
        <Loader2 className="h-3 w-3 animate-spin" />
        Streaming
      </Badge>;
    };

    const contentText = chunks
      .filter(chunk => chunk.chunk_type === 'content')
      .map(chunk => chunk.content)
      .join('');

    return (
      <Card className={cn("w-full", className)}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">{title}</CardTitle>
              {description && (
                <p className="text-sm text-muted-foreground mt-1">{description}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {getStatusBadge()}
              {startTime && (
                <Badge variant="outline" className="text-xs">
                  {formatElapsedTime(elapsedTime)}
                </Badge>
              )}
            </div>
          </div>
          
          {showProgress && !error && (
            <div className="space-y-2">
              <Progress value={progress} className="h-2" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Progress: {progress}%</span>
                {metadata && (
                  <span>Type: {metadata.stream_type}</span>
                )}
              </div>
            </div>
          )}
        </CardHeader>

        <CardContent>
          {/* Error State */}
          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4">
              <div className="flex items-center gap-2 text-red-800">
                <XCircle className="h-4 w-4" />
                <span className="font-medium">Error occurred</span>
              </div>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              {showControls && onRetry && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onRetry}
                  className="mt-3"
                >
                  <RotateCcw className="h-3 w-3 mr-1" />
                  Retry
                </Button>
              )}
            </div>
          )}

          {/* Content Display */}
          {!error && (
            <div className="space-y-4">
              {/* Metadata Display */}
              {metadata && (
                <div className="text-xs text-muted-foreground border-l-2 border-blue-200 pl-3">
                  <div>Request ID: {metadata.request_id}</div>
                  <div>Framework: {metadata.framework_id}</div>
                  <div>Started: {new Date(metadata.started_at).toLocaleTimeString()}</div>
                </div>
              )}

              {/* Streaming Content */}
              <div className="min-h-[200px] max-h-[600px] overflow-y-auto">
                {chunks.length === 0 && !isComplete && !error ? (
                  <div className="flex items-center justify-center h-32 text-muted-foreground">
                    <Loader2 className="h-6 w-6 animate-spin mr-2" />
                    Waiting for response...
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      {contentText}
                      {!isComplete && !error && (
                        <span className="inline-block w-2 h-4 bg-blue-600 animate-pulse ml-1" />
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Controls */}
              {showControls && !error && (
                <div className="flex items-center gap-2 pt-3 border-t">
                  {!isComplete && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => isPaused ? setIsPaused(false) : setIsPaused(true)}
                      >
                        {isPaused ? (
                          <>
                            <Play className="h-3 w-3 mr-1" />
                            Resume
                          </>
                        ) : (
                          <>
                            <Pause className="h-3 w-3 mr-1" />
                            Pause
                          </>
                        )}
                      </Button>
                      {onCancel && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={onCancel}
                        >
                          Cancel
                        </Button>
                      )}
                    </>
                  )}
                  
                  {isComplete && (
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <CheckCircle className="h-4 w-4" />
                      Analysis completed in {formatElapsedTime(elapsedTime)}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }
);

StreamingResponse.displayName = "StreamingResponse";