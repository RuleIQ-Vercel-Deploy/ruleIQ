import { FileText, MoreVertical } from "lucide-react"
import Image from "next/image"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { type Evidence, statuses } from "@/lib/data/evidence"

interface EvidenceListItemProps {
  evidence: Evidence
  isSelected: boolean
  onSelectionChange: (id: string) => void
}

export function EvidenceListItem({ evidence, isSelected, onSelectionChange }: EvidenceListItemProps) {
  const status = statuses.find((s) => s.value === evidence.status)

  return (
    <div className="grid grid-cols-[auto_1fr_1fr_1fr_1fr_auto] items-center gap-4 px-4 py-3 rounded-lg bg-oxford-blue/50 border border-transparent hover:border-gold/40 transition-colors duration-200">
      <Checkbox
        checked={isSelected}
        onCheckedChange={() => onSelectionChange(evidence.id)}
        aria-label={`Select ${evidence.name}`}
        className="ruleiq-checkbox"
      />
      <div className="flex items-center gap-3 font-medium text-eggshell-white">
        <FileText className="h-5 w-5 text-gold" />
        {evidence.name}
      </div>
      <div>
        <Badge variant={status?.value as any}>{status?.label}</Badge>
      </div>
      <div className="flex flex-wrap gap-1">
        {evidence.classification.map((tag) => (
          <Badge key={tag} variant="tag">
            {tag}
          </Badge>
        ))}
      </div>
      <div className="text-sm text-eggshell-white/60">{evidence.uploadDate}</div>
      <div className="flex items-center justify-end gap-2">
        <Image
          src={evidence.userAvatar || "/placeholder.svg"}
          alt={evidence.uploadedBy}
          width={24}
          height={24}
          className="rounded-full"
        />
        <span className="text-sm text-eggshell-white/60 hidden lg:inline">{evidence.uploadedBy}</span>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreVertical className="h-4 w-4" />
          <span className="sr-only">More actions</span>
        </Button>
      </div>
    </div>
  )
}
