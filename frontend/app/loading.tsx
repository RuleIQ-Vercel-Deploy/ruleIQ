import { Loader2 } from "lucide-react"

export default function Loading() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center" style={{ backgroundColor: "#002147" }}>
      <div className="flex flex-col items-center gap-4">
        <div className="flex items-center space-x-2">
          <span className="text-3xl font-bold" style={{ color: "#F0EAD6" }}>
            rule
          </span>
          <span className="text-3xl font-bold" style={{ color: "#FFD700" }}>
            IQ
          </span>
        </div>
        <Loader2 className="h-8 w-8 animate-spin" style={{ color: "#F0EAD6" }} />
        <p className="text-lg" style={{ color: "#6C757D" }}>
          Loading your compliance dashboard...
        </p>
      </div>
    </div>
  )
}
