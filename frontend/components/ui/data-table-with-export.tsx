"use client"

import {
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
  flexRender,
  getCoreRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { Download, FileSpreadsheet, FileJson, FileText } from "lucide-react"
import * as React from "react"
import { toast } from "sonner"

import { DataTablePagination } from "@/components/assessments/data-table-pagination"
import { DataTableToolbar } from "@/components/assessments/data-table-toolbar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"


interface DataTableWithExportProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  exportFilename?: string
  showToolbar?: boolean
  showPagination?: boolean
  showExport?: boolean
}

export function DataTableWithExport<TData, TValue>({
  columns,
  data,
  exportFilename = "data-export",
  showToolbar = true,
  showPagination = true,
  showExport = true,
}: DataTableWithExportProps<TData, TValue>) {
  const [rowSelection, setRowSelection] = React.useState({})
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [sorting, setSorting] = React.useState<SortingState>([])

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnVisibility,
      rowSelection,
      columnFilters,
    },
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
  })

  // Export functions
  const exportToCSV = () => {
    const {rows} = table.getFilteredRowModel()
    const headers = table.getAllColumns()
      .filter(col => col.getIsVisible())
      .map(col => col.id)
    
    // Create CSV content
    const csvContent = [
      headers.join(','),
      ...rows.map(row => 
        headers.map(header => {
          const value = row.getValue(header)
          // Handle different data types and escape commas
          if (value === null || value === undefined) return ''
          if (typeof value === 'string' && value.includes(',')) {
            return `"${value.replace(/"/g, '""')}"`
          }
          return String(value)
        }).join(',')
      )
    ].join('\n')

    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${exportFilename}-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    
    toast.success("Data exported to CSV successfully")
  }

  const exportToJSON = () => {
    const {rows} = table.getFilteredRowModel()
    const exportData = rows.map(row => {
      const rowData: Record<string, any> = {}
      table.getAllColumns()
        .filter(col => col.getIsVisible())
        .forEach(col => {
          rowData[col.id] = row.getValue(col.id)
        })
      return rowData
    })

    const jsonContent = JSON.stringify(exportData, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${exportFilename}-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    toast.success("Data exported to JSON successfully")
  }

  const exportToTXT = () => {
    const {rows} = table.getFilteredRowModel()
    const headers = table.getAllColumns()
      .filter(col => col.getIsVisible())
      .map(col => col.id)
    
    // Create text content with tab separation
    const txtContent = [
      headers.join('\t'),
      ...rows.map(row => 
        headers.map(header => {
          const value = row.getValue(header)
          return value === null || value === undefined ? '' : String(value)
        }).join('\t')
      )
    ].join('\n')

    const blob = new Blob([txtContent], { type: 'text/plain;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${exportFilename}-${new Date().toISOString().split('T')[0]}.txt`
    link.click()
    
    toast.success("Data exported to text file successfully")
  }

  const getSelectedRowsData = () => {
    const selectedRows = table.getFilteredSelectedRowModel().rows
    return selectedRows.length > 0 ? selectedRows : table.getFilteredRowModel().rows
  }

  const exportSelectedToCSV = () => {
    const rows = getSelectedRowsData()
    if (rows.length === 0) {
      toast.error("No rows selected for export")
      return
    }
    
    // Similar to exportToCSV but with selected rows
    const headers = table.getAllColumns()
      .filter(col => col.getIsVisible())
      .map(col => col.id)
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => 
        headers.map(header => {
          const value = row.getValue(header)
          if (value === null || value === undefined) return ''
          if (typeof value === 'string' && value.includes(',')) {
            return `"${value.replace(/"/g, '""')}"`
          }
          return String(value)
        }).join(',')
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${exportFilename}-selected-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    
    toast.success(`Exported ${rows.length} selected rows to CSV`)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        {showToolbar && <DataTableToolbar table={table} />}
        {showExport && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[200px]">
              <DropdownMenuLabel>Export all data</DropdownMenuLabel>
              <DropdownMenuItem onClick={exportToCSV}>
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                Export as CSV
              </DropdownMenuItem>
              <DropdownMenuItem onClick={exportToJSON}>
                <FileJson className="h-4 w-4 mr-2" />
                Export as JSON
              </DropdownMenuItem>
              <DropdownMenuItem onClick={exportToTXT}>
                <FileText className="h-4 w-4 mr-2" />
                Export as Text
              </DropdownMenuItem>
              {table.getFilteredSelectedRowModel().rows.length > 0 && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuLabel>Export selected</DropdownMenuLabel>
                  <DropdownMenuItem onClick={exportSelectedToCSV}>
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Export {table.getFilteredSelectedRowModel().rows.length} selected
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      <div className="rounded-lg border overflow-hidden">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      {showPagination && <DataTablePagination table={table} />}
    </div>
  )
}