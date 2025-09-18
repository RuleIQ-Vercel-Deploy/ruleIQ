'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { useLayoutStore } from '@/lib/stores/layout.store';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Undo2,
  Redo2,
  RotateCcw,
  History,
  Save,
  ChevronDown,
  Clock,
  Layers,
  Move,
  Trash2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

interface UndoRedoControlsProps {
  className?: string;
  showHistory?: boolean;
  showSaveButton?: boolean;
  showResetButton?: boolean;
  compact?: boolean;
  onSave?: () => void;
  onReset?: () => void;
}

const operationIcons: Record<string, React.ReactNode> = {
  'widget-reorder': <Move className="h-3 w-3" />,
  'widget-resize': <Layers className="h-3 w-3" />,
  'rule-reorder': <Move className="h-3 w-3" />,
  'batch-operation': <Layers className="h-3 w-3" />,
  'layout-reset': <RotateCcw className="h-3 w-3" />,
};

export function UndoRedoControls({
  className,
  showHistory = true,
  showSaveButton = true,
  showResetButton = true,
  compact = false,
  onSave,
  onReset,
}: UndoRedoControlsProps) {
  const {
    history,
    historyIndex,
    undo,
    redo,
    clearHistory,
    resetLayout,
    isDirty,
    isSaving,
  } = useLayoutStore();

  const [showHistoryDropdown, setShowHistoryDropdown] = useState(false);
  const [isResetDialogOpen, setIsResetDialogOpen] = useState(false);

  // Determine platform for keyboard shortcuts
  const [isMac, setIsMac] = useState(false);
  useEffect(() => {
    setIsMac(navigator.platform.toUpperCase().indexOf('MAC') >= 0);
  }, []);

  const canUndo = historyIndex >= 0 && history.length > 0;
  const canRedo = historyIndex < history.length - 1;

  const undoShortcut = isMac ? '⌘Z' : 'Ctrl+Z';
  const redoShortcut = isMac ? '⌘⇧Z' : 'Ctrl+Shift+Z';
  const saveShortcut = isMac ? '⌘S' : 'Ctrl+S';
  const resetShortcut = isMac ? '⌘R' : 'Ctrl+R';

  const handleUndo = useCallback(() => {
    if (canUndo) {
      undo();
    }
  }, [canUndo, undo]);

  const handleRedo = useCallback(() => {
    if (canRedo) {
      redo();
    }
  }, [canRedo, redo]);

  const handleSave = useCallback(() => {
    onSave?.();
  }, [onSave]);

  const handleReset = useCallback(() => {
    resetLayout();
    clearHistory();
    onReset?.();
    setIsResetDialogOpen(false);
  }, [resetLayout, clearHistory, onReset]);

  const handleJumpToHistory = useCallback((targetIndex: number) => {
    const currentIndex = historyIndex;

    if (targetIndex < currentIndex) {
      // Undo to target
      for (let i = currentIndex; i > targetIndex; i--) {
        undo();
      }
    } else if (targetIndex > currentIndex) {
      // Redo to target
      for (let i = currentIndex; i < targetIndex; i++) {
        redo();
      }
    }

    setShowHistoryDropdown(false);
  }, [historyIndex, undo, redo]);

  const getOperationColor = (type: string) => {
    switch (type) {
      case 'widget-reorder':
      case 'rule-reorder':
        return 'bg-blue-100 text-blue-800';
      case 'widget-resize':
        return 'bg-green-100 text-green-800';
      case 'batch-operation':
        return 'bg-purple-100 text-purple-800';
      case 'layout-reset':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (compact) {
    return (
      <div className={cn('flex items-center gap-1', className)}>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleUndo}
                disabled={!canUndo}
                className="h-8 w-8"
              >
                <Undo2 className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Undo {undoShortcut}</p>
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleRedo}
                disabled={!canRedo}
                className="h-8 w-8"
              >
                <Redo2 className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Redo {redoShortcut}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    );
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <TooltipProvider>
        <div className="flex items-center rounded-md border">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleUndo}
                disabled={!canUndo}
                className="rounded-r-none"
                aria-label="Undo last action"
              >
                <Undo2 className="mr-2 h-4 w-4" />
                Undo
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Undo last action</p>
              <p className="text-xs text-muted-foreground">{undoShortcut}</p>
            </TooltipContent>
          </Tooltip>

          <div className="h-8 w-px bg-border" />

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRedo}
                disabled={!canRedo}
                className="rounded-l-none"
                aria-label="Redo last action"
              >
                <Redo2 className="mr-2 h-4 w-4" />
                Redo
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Redo last action</p>
              <p className="text-xs text-muted-foreground">{redoShortcut}</p>
            </TooltipContent>
          </Tooltip>
        </div>

        {showHistory && history.length > 0 && (
          <DropdownMenu open={showHistoryDropdown} onOpenChange={setShowHistoryDropdown}>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="gap-1"
                aria-label="View history"
              >
                <History className="h-4 w-4" />
                History
                <Badge variant="secondary" className="ml-1 px-1 py-0 text-xs">
                  {history.length}
                </Badge>
                <ChevronDown className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <ScrollArea className="h-72">
                <div className="p-2">
                  <h4 className="mb-2 text-sm font-medium">Action History</h4>
                  {history.map((item, index) => (
                    <DropdownMenuItem
                      key={item.id}
                      onClick={() => handleJumpToHistory(index)}
                      className={cn(
                        'flex items-start gap-2 p-2 cursor-pointer',
                        index === historyIndex && 'bg-accent',
                        index > historyIndex && 'opacity-50'
                      )}
                    >
                      <div className="mt-0.5">
                        {operationIcons[item.operation.type] || <Clock className="h-3 w-3" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{item.description}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge
                            variant="secondary"
                            className={cn('text-xs px-1 py-0', getOperationColor(item.operation.type))}
                          >
                            {item.operation.type.replace('-', ' ')}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(item.timestamp, { addSuffix: true })}
                          </span>
                        </div>
                      </div>
                      {index === historyIndex && (
                        <Badge variant="default" className="text-xs px-1 py-0">
                          Current
                        </Badge>
                      )}
                    </DropdownMenuItem>
                  ))}
                  {history.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      No history yet
                    </p>
                  )}
                </div>
              </ScrollArea>
              {history.length > 0 && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => {
                      clearHistory();
                      setShowHistoryDropdown(false);
                    }}
                    className="text-destructive"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Clear History
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {showSaveButton && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={isDirty ? 'default' : 'outline'}
                size="sm"
                onClick={handleSave}
                disabled={isSaving || !isDirty}
                aria-label="Save layout"
              >
                <Save className="mr-2 h-4 w-4" />
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Save current layout</p>
              <p className="text-xs text-muted-foreground">{saveShortcut}</p>
            </TooltipContent>
          </Tooltip>
        )}

        {showResetButton && (
          <AlertDialog open={isResetDialogOpen} onOpenChange={setIsResetDialogOpen}>
            <Tooltip>
              <TooltipTrigger asChild>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    aria-label="Reset layout"
                  >
                    <RotateCcw className="mr-2 h-4 w-4" />
                    Reset
                  </Button>
                </AlertDialogTrigger>
              </TooltipTrigger>
              <TooltipContent>
                <p>Reset to default layout</p>
                <p className="text-xs text-muted-foreground">{resetShortcut}</p>
              </TooltipContent>
            </Tooltip>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Reset Layout?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will reset your dashboard to the default layout and clear all history.
                  This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleReset}>
                  Reset Layout
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )}
      </TooltipProvider>

      {/* Status Indicators */}
      {isDirty && (
        <Badge variant="outline" className="text-xs">
          <span className="mr-1 h-2 w-2 rounded-full bg-yellow-500" />
          Unsaved changes
        </Badge>
      )}

      {isSaving && (
        <Badge variant="outline" className="text-xs">
          <span className="mr-1 h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
          Saving...
        </Badge>
      )}
    </div>
  );
}