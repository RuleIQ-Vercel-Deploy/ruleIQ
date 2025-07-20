"use client"

import * as React from "react"

import { cn } from "@/lib/utils"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./table"

interface ResponsiveTableColumn {
  key: string
  header: string | React.ReactNode
  accessor: (row: any) => React.ReactNode
  className?: string
  headerClassName?: string
  priority?: "high" | "medium" | "low" // for mobile visibility
}

interface ResponsiveTableProps {
  columns: ResponsiveTableColumn[]
  data: any[]
  className?: string
  mobileLayout?: "scroll" | "stack" // default is scroll
  emptyMessage?: string
}

const ResponsiveTable: React.FC<ResponsiveTableProps> = ({
  columns,
  data,
  className,
  mobileLayout = "scroll",
  emptyMessage = "No data available"
}) => {
  // For stacked mobile layout
  if (mobileLayout === "stack") {
    return (
      <>
        {/* Desktop view */}
        <div className={cn("hidden sm:block", className)}>
          <Table>
            <TableHeader>
              <TableRow>
                {columns.map((column) => (
                  <TableHead
                    key={column.key}
                    className={cn(column.headerClassName)}
                  >
                    {column.header}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="text-center py-8 text-neutral-500"
                  >
                    {emptyMessage}
                  </TableCell>
                </TableRow>
              ) : (
                data.map((row, rowIndex) => (
                  <TableRow key={rowIndex}>
                    {columns.map((column) => (
                      <TableCell
                        key={column.key}
                        className={cn(column.className)}
                      >
                        {column.accessor(row)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Mobile stacked view */}
        <div className="sm:hidden space-y-4">
          {data.length === 0 ? (
            <div className="text-center py-8 text-neutral-500">
              {emptyMessage}
            </div>
          ) : (
            data.map((row, rowIndex) => (
              <div
                key={rowIndex}
                className="bg-white rounded-lg border border-neutral-200 p-4 space-y-3 shadow-sm"
              >
                {columns
                  .filter(col => col.priority !== "low") // Hide low priority columns on mobile
                  .map((column) => (
                    <div
                      key={column.key}
                      className="flex flex-col sm:flex-row sm:items-center gap-1"
                    >
                      <div className="text-sm font-medium text-neutral-600">
                        {column.header}:
                      </div>
                      <div className="text-sm text-neutral-900">
                        {column.accessor(row)}
                      </div>
                    </div>
                  ))}
              </div>
            ))
          )}
        </div>
      </>
    )
  }

  // Default horizontal scroll layout
  return (
    <div className={className}>
      <Table responsive>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead
                key={column.key}
                className={cn(
                  column.headerClassName,
                  // Hide low priority columns on small screens
                  column.priority === "low" && "hidden lg:table-cell",
                  column.priority === "medium" && "hidden md:table-cell"
                )}
              >
                {column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={columns.length}
                className="text-center py-8 text-neutral-500"
              >
                {emptyMessage}
              </TableCell>
            </TableRow>
          ) : (
            data.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {columns.map((column) => (
                  <TableCell
                    key={column.key}
                    className={cn(
                      column.className,
                      // Hide low priority columns on small screens
                      column.priority === "low" && "hidden lg:table-cell",
                      column.priority === "medium" && "hidden md:table-cell"
                    )}
                  >
                    {column.accessor(row)}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}

export { ResponsiveTable, type ResponsiveTableColumn, type ResponsiveTableProps }