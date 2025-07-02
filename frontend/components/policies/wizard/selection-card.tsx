"use client"

import { CheckCircle2, type LucideIcon } from "lucide-react"

import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface SelectionCardProps {
  title: string
  description?: string
  icon?: LucideIcon
  isSelected: boolean
  onClick: () => void
  className?: string
}

export function SelectionCard({ title, description, icon: Icon, isSelected, onClick, className }: SelectionCardProps) {
  return (
    <Card
      onClick={onClick}
      className={cn(
        "ruleiq-card cursor-pointer transition-all duration-200 relative overflow-hidden",
        "hover:border-primary/80 hover:shadow-lg",
        isSelected ? "border-primary ring-2 ring-primary/50" : "border-border",
        className,
      )}
    >
      {isSelected && (
        <div className="absolute top-2 right-2 text-primary">
          <CheckCircle2 className="h-5 w-5" />
        </div>
      )}
      <CardHeader className="flex flex-row items-start gap-4 space-y-0">
        {Icon && <Icon className="h-8 w-8 text-primary mt-1" />}
        <div className="flex-1">
          <CardTitle className="text-lg">{title}</CardTitle>
          {description && <p className="text-muted-foreground text-sm mt-1">{description}</p>}
        </div>
      </CardHeader>
    </Card>
  )
}
