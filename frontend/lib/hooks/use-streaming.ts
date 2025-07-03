"use client";

import { useState, useCallback, useRef } from 'react';

import type { StreamingChunk, StreamingMetadata, StreamingOptions } from '@/lib/api/assessments-ai.service';

export interface StreamingState {
  isStreaming: boolean;
  isComplete: boolean;
  isPaused: boolean;
  error: string | null;
  chunks: StreamingChunk[];
  metadata: StreamingMetadata | null;
  progress: number;
  elapsedTime: number;
  content: string;
}

export interface StreamingControls {
  start: (streamFn: (options: StreamingOptions) => Promise<void>) => Promise<void>;
  pause: () => void;
  resume: () => void;
  stop: () => void;
  reset: () => void;
  retry: () => void;
}

export function useStreaming(): [StreamingState, StreamingControls] {
  const [state, setState] = useState<StreamingState>({
    isStreaming: false,
    isComplete: false,
    isPaused: false,
    error: null,
    chunks: [],
    metadata: null,
    progress: 0,
    elapsedTime: 0,
    content: ''
  });

  const streamFnRef = useRef<((options: StreamingOptions) => Promise<void>) | null>(null);
  const startTimeRef = useRef<Date | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const updateContent = useCallback((chunks: StreamingChunk[]) => {
    return chunks
      .filter(chunk => chunk.chunk_type === 'content')
      .map(chunk => chunk.content)
      .join('');
  }, []);

  const startTimer = useCallback(() => {
    startTimeRef.current = new Date();
    intervalRef.current = setInterval(() => {
      if (startTimeRef.current && !state.isPaused) {
        const elapsed = Math.floor((Date.now() - startTimeRef.current.getTime()) / 1000);
        setState(prev => ({ ...prev, elapsedTime: elapsed }));
      }
    }, 1000);
  }, [state.isPaused]);

  const stopTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const start = useCallback(async (streamFn: (options: StreamingOptions) => Promise<void>) => {
    streamFnRef.current = streamFn;
    
    setState(prev => ({
      ...prev,
      isStreaming: true,
      isComplete: false,
      error: null,
      chunks: [],
      progress: 0,
      elapsedTime: 0,
      content: ''
    }));

    startTimer();

    const options: StreamingOptions = {
      onMetadata: (metadata) => {
        setState(prev => ({
          ...prev,
          metadata,
          progress: 10
        }));
      },
      
      onChunk: (chunk) => {
        setState(prev => {
          const newChunks = [...prev.chunks, chunk];
          const newContent = updateContent(newChunks);
          const newProgress = Math.min(prev.progress + 5, 90);
          
          return {
            ...prev,
            chunks: newChunks,
            content: newContent,
            progress: newProgress
          };
        });
      },
      
      onComplete: () => {
        stopTimer();
        setState(prev => ({
          ...prev,
          isStreaming: false,
          isComplete: true,
          progress: 100
        }));
      },
      
      onError: (error) => {
        stopTimer();
        setState(prev => ({
          ...prev,
          isStreaming: false,
          isComplete: true,
          error
        }));
      }
    };

    try {
      await streamFn(options);
    } catch (error) {
      stopTimer();
      setState(prev => ({
        ...prev,
        isStreaming: false,
        isComplete: true,
        error: error instanceof Error ? error.message : 'An unknown error occurred'
      }));
    }
  }, [startTimer, stopTimer, updateContent]);

  const pause = useCallback(() => {
    setState(prev => ({ ...prev, isPaused: true }));
    stopTimer();
  }, [stopTimer]);

  const resume = useCallback(() => {
    setState(prev => ({ ...prev, isPaused: false }));
    if (!state.isComplete && !state.error) {
      startTimer();
    }
  }, [startTimer, state.isComplete, state.error]);

  const stop = useCallback(() => {
    stopTimer();
    setState(prev => ({
      ...prev,
      isStreaming: false,
      isComplete: true
    }));
  }, [stopTimer]);

  const reset = useCallback(() => {
    stopTimer();
    setState({
      isStreaming: false,
      isComplete: false,
      isPaused: false,
      error: null,
      chunks: [],
      metadata: null,
      progress: 0,
      elapsedTime: 0,
      content: ''
    });
    startTimeRef.current = null;
  }, [stopTimer]);

  const retry = useCallback(async () => {
    if (streamFnRef.current) {
      reset();
      await start(streamFnRef.current);
    }
  }, [reset, start]);

  return [
    state,
    {
      start,
      pause,
      resume,
      stop,
      reset,
      retry
    }
  ];
}