"use client"

import React, { useCallback, useState } from 'react'
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core'
import { arrayMove, SortableContext, sortableKeyboardCoordinates, rectSortingStrategy } from '@dnd-kit/sortable'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, X, Settings, Maximize2, Minimize2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export interface WidgetConfig {
  id: string
  type: string
  title: string
  content: React.ReactNode
  minWidth?: number
  minHeight?: number
  defaultWidth?: number
  defaultHeight?: number
  canResize?: boolean
  canRemove?: boolean
  settings?: Record<string, any>
}

interface WidgetContainerProps {
  widgets: WidgetConfig[]
  onWidgetOrderChange?: (widgets: WidgetConfig[]) => void
  onWidgetRemove?: (widgetId: string) => void
  onWidgetSettings?: (widgetId: string) => void
  columns?: number
  gap?: number
  className?: string
}

interface SortableWidgetProps {
  widget: WidgetConfig
  onRemove?: (id: string) => void
  onSettings?: (id: string) => void
  isExpanded: boolean
  onToggleExpand: (id: string) => void
}

function SortableWidget({ widget, onRemove, onSettings, isExpanded, onToggleExpand }: SortableWidgetProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: widget.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "relative group",
        isDragging && "z-50 opacity-50",
        isExpanded && "md:col-span-2 lg:col-span-3"
      )}
    >
      <Card className="h-full overflow-hidden bg-white border-neutral-200 hover:shadow-lg transition-all duration-300">
        {/* Widget Header */}
        <div className="flex items-center justify-between p-4 border-b border-neutral-100">
          <div className="flex items-center gap-2">
            <button
              className="cursor-move touch-none p-1 rounded hover:bg-neutral-100 transition-colors"
              {...attributes}
              {...listeners}
            >
              <GripVertical className="h-4 w-4 text-neutral-400" />
            </button>
            <h3 className="font-semibold text-neutral-900">{widget.title}</h3>
          </div>
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onToggleExpand(widget.id)}
              className="h-8 w-8 p-0"
            >
              {isExpanded ? (
                <Minimize2 className="h-3.5 w-3.5 text-neutral-600" />
              ) : (
                <Maximize2 className="h-3.5 w-3.5 text-neutral-600" />
              )}
            </Button>
            {onSettings && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onSettings(widget.id)}
                className="h-8 w-8 p-0"
              >
                <Settings className="h-3.5 w-3.5 text-neutral-600" />
              </Button>
            )}
            {widget.canRemove !== false && onRemove && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onRemove(widget.id)}
                className="h-8 w-8 p-0 hover:bg-red-50"
              >
                <X className="h-3.5 w-3.5 text-neutral-600 hover:text-red-600" />
              </Button>
            )}
          </div>
        </div>
        {/* Widget Content */}
        <div className="p-4">
          {widget.content}
        </div>
      </Card>
    </div>
  )
}

export function WidgetContainer({
  widgets: initialWidgets,
  onWidgetOrderChange,
  onWidgetRemove,
  onWidgetSettings,
  columns = 3,
  gap = 6,
  className,
}: WidgetContainerProps) {
  const [widgets, setWidgets] = useState(initialWidgets)
  const [expandedWidgets, setExpandedWidgets] = useState<Set<string>>(new Set())

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event

    if (over && active.id !== over.id) {
      setWidgets((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id)
        const newIndex = items.findIndex((item) => item.id === over.id)
        const newOrder = arrayMove(items, oldIndex, newIndex)
        
        onWidgetOrderChange?.(newOrder)
        return newOrder
      })
    }
  }, [onWidgetOrderChange])

  const handleRemoveWidget = useCallback((widgetId: string) => {
    setWidgets((items) => items.filter((item) => item.id !== widgetId))
    onWidgetRemove?.(widgetId)
  }, [onWidgetRemove])

  const handleToggleExpand = useCallback((widgetId: string) => {
    setExpandedWidgets((prev) => {
      const next = new Set(prev)
      if (next.has(widgetId)) {
        next.delete(widgetId)
      } else {
        next.add(widgetId)
      }
      return next
    })
  }, [])

  const gridClassName = cn(
    "grid gap-6",
    columns === 1 && "grid-cols-1",
    columns === 2 && "grid-cols-1 md:grid-cols-2",
    columns === 3 && "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
    columns === 4 && "grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
    className
  )

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext
        items={widgets.map(w => w.id)}
        strategy={rectSortingStrategy}
      >
        <div className={gridClassName} style={{ gap: `${gap * 0.25}rem` }}>
          {widgets.map((widget) => (
            <SortableWidget
              key={widget.id}
              widget={widget}
              onRemove={handleRemoveWidget}
              onSettings={onWidgetSettings}
              isExpanded={expandedWidgets.has(widget.id)}
              onToggleExpand={handleToggleExpand}
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  )
}