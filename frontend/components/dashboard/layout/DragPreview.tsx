'use client';

import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  GripVertical,
  Layers,
  Move,
  ArrowRight,
} from 'lucide-react';

interface DragPreviewProps {
  type: 'widget' | 'rule' | 'group';
  title: string;
  subtitle?: string;
  metadata?: Record<string, any>;
  isValid?: boolean;
  isDragging?: boolean;
  dropZoneInfo?: {
    name: string;
    isValid: boolean;
    message?: string;
  };
  position?: { x: number; y: number };
  className?: string;
  reducedMotion?: boolean;
}

export function DragPreview({
  type,
  title,
  subtitle,
  metadata,
  isValid = true,
  isDragging = false,
  dropZoneInfo,
  position,
  className,
  reducedMotion = false,
}: DragPreviewProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !isDragging) {
    return null;
  }

  const getTypeIcon = () => {
    switch (type) {
      case 'widget':
        return <Layers className="h-4 w-4" />;
      case 'rule':
        return <Move className="h-4 w-4" />;
      case 'group':
        return <GripVertical className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const getValidityIcon = () => {
    if (dropZoneInfo?.isValid === false) {
      return <XCircle className="h-4 w-4 text-destructive" />;
    }
    if (dropZoneInfo?.isValid === true) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    if (!isValid) {
      return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
    return null;
  };

  const previewContent = (
    <AnimatePresence mode="wait">
      {isDragging && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{
            duration: reducedMotion ? 0 : 0.2,
            ease: 'easeOut',
          }}
          className={cn(
            'fixed pointer-events-none z-[9999]',
            className
          )}
          style={{
            left: position?.x ?? 0,
            top: position?.y ?? 0,
            transform: 'translate(-50%, -50%)',
          }}
        >
          <Card className={cn(
            'shadow-2xl border-2 backdrop-blur-sm',
            isValid ? 'border-primary bg-background/95' : 'border-destructive bg-destructive/5',
            dropZoneInfo?.isValid === false && 'border-destructive bg-destructive/10',
            dropZoneInfo?.isValid === true && 'border-green-500 bg-green-50/95'
          )}>
            <div className="p-4 min-w-[200px] max-w-[300px]">
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getTypeIcon()}
                  <span className="text-sm font-medium capitalize">{type}</span>
                </div>
                {getValidityIcon()}
              </div>

              {/* Content */}
              <div className="space-y-1">
                <h4 className="font-semibold text-sm line-clamp-1">{title}</h4>
                {subtitle && (
                  <p className="text-xs text-muted-foreground line-clamp-1">{subtitle}</p>
                )}
              </div>

              {/* Metadata */}
              {metadata && Object.keys(metadata).length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {Object.entries(metadata).slice(0, 3).map(([key, value]) => (
                    <Badge key={key} variant="secondary" className="text-xs px-1 py-0">
                      {key}: {value}
                    </Badge>
                  ))}
                </div>
              )}

              {/* Drop Zone Info */}
              {dropZoneInfo && (
                <div className={cn(
                  'mt-3 pt-3 border-t flex items-center gap-2',
                  dropZoneInfo.isValid ? 'border-green-200' : 'border-destructive/20'
                )}>
                  <ArrowRight className="h-3 w-3 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-xs font-medium">{dropZoneInfo.name}</p>
                    {dropZoneInfo.message && (
                      <p className={cn(
                        'text-xs mt-0.5',
                        dropZoneInfo.isValid ? 'text-green-600' : 'text-destructive'
                      )}>
                        {dropZoneInfo.message}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Visual Indicators */}
              {!reducedMotion && (
                <motion.div
                  className="absolute inset-0 rounded-lg pointer-events-none"
                  animate={{
                    boxShadow: [
                      '0 0 0 0 rgba(59, 130, 246, 0)',
                      '0 0 0 4px rgba(59, 130, 246, 0.1)',
                      '0 0 0 0 rgba(59, 130, 246, 0)',
                    ],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />
              )}
            </div>
          </Card>

          {/* Cursor Indicator */}
          <motion.div
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
            animate={reducedMotion ? {} : {
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            <div className={cn(
              'w-3 h-3 rounded-full',
              isValid ? 'bg-primary' : 'bg-destructive',
              'shadow-lg'
            )} />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );

  // Portal to render at root level
  if (typeof document !== 'undefined') {
    return createPortal(previewContent, document.body);
  }

  return null;
}

// Enhanced preview for complex drag operations
export function EnhancedDragPreview({
  items,
  operation,
  ...props
}: DragPreviewProps & {
  items?: Array<{ id: string; name: string }>;
  operation?: 'move' | 'copy' | 'swap' | 'merge';
}) {
  if (!items || items.length === 0) {
    return <DragPreview {...props} />;
  }

  const operationText = {
    move: 'Moving',
    copy: 'Copying',
    swap: 'Swapping',
    merge: 'Merging',
  }[operation || 'move'];

  const multiItemPreview = (
    <DragPreview
      {...props}
      title={`${operationText} ${items.length} items`}
      subtitle={items.map(i => i.name).join(', ')}
      metadata={{
        count: items.length,
        operation: operation || 'move',
      }}
    />
  );

  return multiItemPreview;
}

// Hook to manage drag preview state
export function useDragPreview() {
  const [previewState, setPreviewState] = useState<{
    isVisible: boolean;
    props: DragPreviewProps | null;
  }>({
    isVisible: false,
    props: null,
  });

  const showPreview = (props: DragPreviewProps) => {
    setPreviewState({
      isVisible: true,
      props: {
        ...props,
        isDragging: true,
      },
    });
  };

  const hidePreview = () => {
    setPreviewState({
      isVisible: false,
      props: null,
    });
  };

  const updatePreview = (updates: Partial<DragPreviewProps>) => {
    setPreviewState(prev => ({
      ...prev,
      props: prev.props ? { ...prev.props, ...updates } : null,
    }));
  };

  return {
    previewState,
    showPreview,
    hidePreview,
    updatePreview,
    DragPreviewComponent: previewState.props ? (
      <DragPreview {...previewState.props} />
    ) : null,
  };
}