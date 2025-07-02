import { ShieldCheck, Lock } from "lucide-react"

import type React from "react"

const Badge = ({ icon, text }: { icon: React.ReactNode; text: string }) => (
  <div className="flex items-center gap-2">
    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10">{icon}</div>
    <span className="text-xs font-medium tracking-wider">{text}</span>
  </div>
)

export function TrustBadges() {
  return (
    <div
      className="flex flex-col items-center justify-center gap-4 rounded-lg border p-4 sm:flex-row sm:justify-between"
      style={{
        borderColor: "rgba(240, 234, 214, 0.2)",
        color: "#F0EAD6",
      }}
    >
      <Badge icon={<Lock className="h-4 w-4 text-success" />} text="256-bit SSL Encryption" />
      <Badge icon={<ShieldCheck className="h-4 w-4 text-eggshell-white" />} text="GDPR Compliant" />
      <Badge icon={<ShieldCheck className="h-4 w-4 text-eggshell-white" />} text="ISO 27001 Certified" />
    </div>
  )
}
