import { Badge } from "@/components/ui/badge"

interface RecommendationsListProps {
  recommendations: {
    id: string
    text: string
    priority: "High" | "Medium" | "Low"
  }[]
}

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "High":
        return "bg-destructive text-destructive-foreground border-destructive/50"
      case "Medium":
        return "bg-warning text-warning-foreground border-warning/50"
      case "Low":
        return "bg-muted text-muted-foreground border-muted-foreground/50"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  return (
    <div className="space-y-4">
      {recommendations.map((rec, index) => (
        <div
          key={rec.id}
          className="flex flex-col sm:flex-row items-start gap-4 p-4 rounded-lg border border-primary/20 bg-card/50"
        >
          <div className="flex items-center gap-4">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm">
              {index + 1}
            </span>
            <Badge variant="outline" className={`font-semibold ${getPriorityBadge(rec.priority)}`}>
              {rec.priority}
            </Badge>
          </div>
          <p className="flex-1 text-sm mt-1 sm:mt-0">{rec.text}</p>
        </div>
      ))}
    </div>
  )
}
