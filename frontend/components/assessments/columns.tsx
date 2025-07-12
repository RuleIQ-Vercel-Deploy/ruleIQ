"use client"

import { DataTableColumnHeader } from "@/components/assessments/data-table-column-header"
import { DataTableRowActions } from "@/components/assessments/data-table-row-actions"
import { Badge } from "@/components/ui/badge"
import { ProgressBar } from "@/components/ui/progress-bar"
import { frameworks, statuses, type Assessment } from "@/lib/data/assessments"

import type { ColumnDef } from "@tanstack/react-table"

export const columns: ColumnDef<Assessment>[] = [
  {
    accessorKey: "title",
    header: ({ column }) => <DataTableColumnHeader column={column} title="Assessment" />,
    cell: ({ row }) => <div className="w-[250px] font-medium truncate">{row.getValue("title")}</div>,
    enableSorting: true,
    enableHiding: false,
  },
  {
    accessorKey: "framework_name",
    header: ({ column }) => <DataTableColumnHeader column={column} title="Framework" />,
    cell: ({ row }) => {
      const framework = frameworks.find((f) => f.value === row.original.framework_name)
      return <div className="w-[120px] capitalize">{framework?.label || row.original.framework_name}</div>
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    accessorKey: "status",
    header: ({ column }) => <DataTableColumnHeader column={column} title="Status" />,
    cell: ({ row }) => {
      const status = statuses.find((s) => s.value === row.getValue("status"))
      if (!status) return null
      return (
        <Badge className={`capitalize border ${status.color}`} variant="outline">
          {status.label}
        </Badge>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    accessorKey: "progress",
    header: ({ column }) => <DataTableColumnHeader column={column} title="Progress" />,
    cell: ({ row }) => {
      const status = statuses.find((s) => s.value === row.original.status)
      return (
        <div className="w-[150px]">
          <ProgressBar value={row.getValue("progress")} color={status?.progressColor || "blue"} />
        </div>
      )
    },
  },
  {
    accessorKey: "created_at",
    header: ({ column }) => <DataTableColumnHeader column={column} title="Date" />,
    cell: ({ row }) => (
      <div className="w-[100px]">
        {new Date(row.getValue("created_at")).toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        })}
      </div>
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => <DataTableRowActions row={row} />,
  },
]
