// Comprehensive type definitions for layout management

export interface Position {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface WidgetPosition {
  id: string;
  gridX: number;
  gridY: number;
  width: number;
  height: number;
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
  static?: boolean;
}

export interface DashboardLayout {
  id: string;
  userId: string;
  name: string;
  widgets: WidgetPosition[];
  ruleOrder: string[];
  gridCols?: number;
  rowHeight?: number;
  compactType?: 'vertical' | 'horizontal' | null;
  preventCollision?: boolean;
  metadata: {
    createdAt: string;
    updatedAt: string;
    version: number;
    isDefault?: boolean;
    isShared?: boolean;
  };
}

export interface LayoutHistoryItem {
  id: string;
  timestamp: number;
  operation: DragOperation;
  previousState: Partial<DashboardLayout>;
  currentState: Partial<DashboardLayout>;
  description: string;
  canUndo: boolean;
  canRedo: boolean;
}

export type DragOperationType =
  | 'widget-reorder'
  | 'widget-resize'
  | 'rule-reorder'
  | 'cross-container-move'
  | 'batch-operation'
  | 'layout-reset';

export interface DragOperation {
  type: DragOperationType;
  source: {
    containerId?: string;
    index?: number;
    id: string;
    position?: Position;
  };
  destination: {
    containerId?: string;
    index?: number;
    position?: Position;
  };
  item: {
    id: string;
    type: 'widget' | 'rule' | 'group';
    data?: any;
  };
  timestamp: number;
  userId: string;
}

export interface RuleOrderConfig {
  ruleId: string;
  order: number;
  priority: 'P0' | 'P1' | 'P2' | 'P3' | 'P4' | 'P5' | 'P6' | 'P7';
  framework: string;
  groupId?: string;
  dependencies?: string[];
}

export interface LayoutPersistencePayload {
  layout: DashboardLayout;
  timestamp: string;
  checksum?: string;
  compressed?: boolean;
}

export interface LayoutPreferences {
  enableAutoSave: boolean;
  autoSaveInterval: number; // milliseconds
  maxHistorySize: number;
  enableAnimations: boolean;
  snapToGrid: boolean;
  gridSize: number;
  showGridLines: boolean;
  enableKeyboardShortcuts: boolean;
  compactMode: boolean;
  dragHandleSelector?: string;
  resizeHandleSelector?: string;
  announceMovements: boolean;
  highContrastMode: boolean;
}

export interface AccessibilityAnnouncement {
  id: string;
  message: string;
  severity: 'info' | 'success' | 'warning' | 'error';
  timestamp: number;
  duration?: number;
  politeness?: 'polite' | 'assertive' | 'off';
}

export interface LayoutValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning';
  suggestion?: string;
}

export interface LayoutConflictResolution {
  strategy: 'last-write-wins' | 'merge' | 'user-choice';
  localVersion: DashboardLayout;
  remoteVersion: DashboardLayout;
  resolvedVersion?: DashboardLayout;
  conflicts: Array<{
    path: string;
    localValue: any;
    remoteValue: any;
  }>;
}

export interface LayoutExportOptions {
  format: 'json' | 'yaml' | 'csv';
  includeMetadata: boolean;
  includeHistory: boolean;
  compress: boolean;
}

export interface LayoutImportResult {
  success: boolean;
  layout?: DashboardLayout;
  errors?: LayoutValidationError[];
  warnings?: LayoutValidationError[];
  migratedFrom?: number;
}

export interface DragConstraints {
  minX?: number;
  maxX?: number;
  minY?: number;
  maxY?: number;
  snapToGrid?: boolean;
  snapSize?: number;
}

export interface DropZone {
  id: string;
  accepts: Array<'widget' | 'rule' | 'group'>;
  isActive: boolean;
  isOver: boolean;
  canDrop: boolean;
  rect: DOMRect | null;
}

export interface DragState {
  isDragging: boolean;
  draggedItem: DragOperation['item'] | null;
  activeDropZone: string | null;
  dragOffset: Position;
  initialPosition: Position;
  currentPosition: Position;
  preview: HTMLElement | null;
}

export interface LayoutSnapshot {
  id: string;
  name: string;
  description?: string;
  layout: DashboardLayout;
  createdAt: string;
  tags?: string[];
  thumbnail?: string;
}

export interface LayoutTemplate {
  id: string;
  name: string;
  description: string;
  category: 'default' | 'compact' | 'focus' | 'custom';
  layout: Partial<DashboardLayout>;
  preview?: string;
  isPremium?: boolean;
}