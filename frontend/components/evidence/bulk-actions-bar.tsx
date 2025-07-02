"use client"

import { Trash2, Archive, ShieldCheck } from "lucide-react"

import { Button } from "@/components/ui/button"

interface BulkActionsBarProps {
  selectedCount: number
  onClearSelection: () => void
}

export function BulkActionsBar({ selectedCount, onClearSelection }: BulkActionsBarProps) {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-auto">
      <div className="flex items-center gap-4 rounded-lg bg-eggshell-white p-3 shadow-2xl border border-oxford-blue/20">
        <p className="text-sm font-medium text-oxford-blue">
          <span className="font-bold">{selectedCount}</span> item{selectedCount > 1 ? "s" : ""} selected
        </p>
        <div className="h-6 w-px bg-oxford-blue/20" />
        <div className="flex items-center gap-2">
          <Button variant="ghost-ruleiq" size="small">
            <ShieldCheck />
            Change Status
          </Button>
          <Button variant="ghost-ruleiq" size="small">
            <Archive />
            Archive
          </Button>
          <Button variant="ghost-ruleiq" size="small" className="text-error hover:bg-error/10 hover:text-error">
            <Trash2 />
            Delete
          </Button>
        </div>
        <div className="h-6 w-px bg-oxford-blue/20" />
        <Button variant="link" size="small" onClick={onClearSelection} className="text-oxford-blue">
          Clear
        </Button>
      </div>
    </div>
  )
}
