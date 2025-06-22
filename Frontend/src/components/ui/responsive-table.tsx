"use client"

import type * as React from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useResponsive } from "@/hooks/use-responsive"
import { useSwipe } from "@/hooks/use-touch"
import { ChevronRight, MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"

interface Column<T> {
  key: keyof T
  label: string
  render?: (value: any, item: T) => React.ReactNode
  sortable?: boolean
  mobileHidden?: boolean
  mobileLabel?: string
}

interface ResponsiveTableProps<T> {
  data: T[]
  columns: Column<T>[]
  onRowClick?: (item: T) => void
  onRowAction?: (item: T) => void
  loading?: boolean
  emptyMessage?: string
  className?: string
}

export function ResponsiveTable<T extends Record<string, any>>({
  data,
  columns,
  onRowClick,
  onRowAction,
  loading = false,
  emptyMessage = "No data available",
  className,
}: ResponsiveTableProps<T>) {
  const { isMobile } = useResponsive()

  const swipeHandlers = useSwipe((swipe) => {
    // Handle swipe actions if needed
    console.log("Swiped:", swipe.direction)
  })

  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">{emptyMessage}</p>
        </CardContent>
      </Card>
    )
  }

  // Mobile card layout
  if (isMobile) {
    return (
      <div className={cn("space-y-2", className)}>
        {data.map((item, index) => (
          <Card
            key={index}
            className={cn(
              "transition-all duration-200 touch-manipulation",
              onRowClick && "cursor-pointer hover:shadow-md active:scale-[0.98]",
            )}
            onClick={() => onRowClick?.(item)}
            {...swipeHandlers}
          >
            <CardContent className="p-4">
              <div className="space-y-2">
                {columns
                  .filter((col) => !col.mobileHidden)
                  .map((column) => {
                    const value = item[column.key]
                    const displayValue = column.render ? column.render(value, item) : value

                    return (
                      <div key={String(column.key)} className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                          {column.mobileLabel || column.label}:
                        </span>
                        <div className="text-sm text-gray-900 dark:text-gray-100 text-right">{displayValue}</div>
                      </div>
                    )
                  })}
              </div>
              {(onRowClick || onRowAction) && (
                <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  {onRowClick && (
                    <Button variant="ghost" size="sm" className="text-blue-600 dark:text-blue-400">
                      View Details
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  )}
                  {onRowAction && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        onRowAction(item)
                      }}
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  // Desktop table layout
  return (
    <div className={cn("rounded-md border", className)}>
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead key={String(column.key)} className="font-medium">
                {column.label}
              </TableHead>
            ))}
            {(onRowClick || onRowAction) && <TableHead className="w-12" />}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item, index) => (
            <TableRow
              key={index}
              className={cn(
                "transition-colors",
                onRowClick && "cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800",
              )}
              onClick={() => onRowClick?.(item)}
            >
              {columns.map((column) => {
                const value = item[column.key]
                const displayValue = column.render ? column.render(value, item) : value

                return (
                  <TableCell key={String(column.key)} className="py-3">
                    {displayValue}
                  </TableCell>
                )
              })}
              {(onRowClick || onRowAction) && (
                <TableCell className="py-3">
                  {onRowAction && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        onRowAction(item)
                      }}
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  )}
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
