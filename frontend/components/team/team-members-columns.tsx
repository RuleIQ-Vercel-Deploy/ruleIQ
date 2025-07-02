"use client"

import { MoreHorizontal, Edit, Trash2 } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { roles } from "@/lib/data/team-data"
import { cn } from "@/lib/utils"

import type { TeamMember, Role } from "@/lib/data/team-data"
import type { ColumnDef } from "@tanstack/react-table"

export const columns: ColumnDef<TeamMember>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => {
      const { name, email, avatar } = row.original
      return (
        <div className="flex items-center gap-3">
          <img src={avatar || "/placeholder.svg"} alt={name} className="h-10 w-10 rounded-full object-cover" />
          <div className="flex flex-col">
            <span className="font-medium text-oxford-blue">{name}</span>
            <span className="text-sm text-oxford-blue/70">{email}</span>
          </div>
        </div>
      )
    },
  },
  {
    accessorKey: "role",
    header: "Role",
    cell: ({ row }) => {
      const role = row.getValue("role") as Role
      const roleInfo = roles.find((r) => r.value === role)

      return (
        <Select defaultValue={role}>
          <SelectTrigger className="w-40 h-9 bg-eggshell-white/50 border-oxford-blue/30 focus:ring-gold">
            <SelectValue>
              <div className="flex items-center gap-2">
                {roleInfo && <roleInfo.icon className="h-4 w-4" />}
                <span>{role}</span>
              </div>
            </SelectValue>
          </SelectTrigger>
          <SelectContent className="bg-oxford-blue text-eggshell-white border-gold/50">
            {roles.map((r) => (
              <SelectItem key={r.value} value={r.value} className="focus:bg-gold/20 data-[highlighted]:bg-gold/20">
                <div className="flex items-center gap-2">
                  <r.icon className="h-4 w-4" />
                  <span>{r.label}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string
      return (
        <Badge
          variant={status === "Active" ? "approved" : "pending"}
          className={cn(
            "capitalize",
            status === "Active" ? "bg-success/10 text-success-foreground" : "bg-warning/10 text-warning-foreground",
          )}
        >
          {status}
        </Badge>
      )
    },
  },
  {
    accessorKey: "lastActive",
    header: "Last Active",
    cell: ({ row }) => <div className="text-oxford-blue/90">{row.getValue("lastActive")}</div>,
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const member = row.original
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost-ruleiq" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-eggshell-white text-oxford-blue border-oxford-blue/20">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem onClick={() => navigator.clipboard.writeText(member.email)}>Copy email</DropdownMenuItem>
            <DropdownMenuSeparator className="bg-oxford-blue/10" />
            <DropdownMenuItem>
              <Edit className="mr-2 h-4 w-4" />
              Edit Member
            </DropdownMenuItem>
            <DropdownMenuItem className="text-error focus:text-error focus:bg-error/10">
              <Trash2 className="mr-2 h-4 w-4" />
              Remove Member
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]
