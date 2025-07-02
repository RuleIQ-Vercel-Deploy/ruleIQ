"use client"
import { Home, ClipboardCheck, FileText, Shield, BarChart3, X } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"

interface MobileNavProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const navigationItems = [
  {
    title: "Dashboard",
    href: "/",
    icon: Home,
  },
  {
    title: "Assessments",
    href: "/assessments",
    icon: ClipboardCheck,
  },
  {
    title: "Evidence",
    href: "/evidence",
    icon: FileText,
  },
  {
    title: "Policies",
    href: "/policies",
    icon: Shield,
  },
  {
    title: "Reports",
    href: "/reports",
    icon: BarChart3,
  },
]

export function MobileNav({ open, onOpenChange }: MobileNavProps) {
  const pathname = usePathname()

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="left"
        className="w-[300px] sm:w-[400px] p-0"
        style={{
          backgroundColor: "#002147",
          borderRightColor: "rgba(233, 236, 239, 0.2)",
        }}
      >
        <SheetHeader className="border-b px-6 py-4" style={{ borderBottomColor: "rgba(233, 236, 239, 0.2)" }}>
          <div className="flex items-center justify-between">
            <SheetTitle className="flex items-center space-x-1">
              <span className="text-xl font-bold" style={{ color: "#F0EAD6" }}>
                rule
              </span>
              <span className="text-xl font-bold" style={{ color: "#FFD700" }}>
                IQ
              </span>
            </SheetTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onOpenChange(false)}
              className="hover:bg-white/10"
              style={{ color: "#F0EAD6" }}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </SheetHeader>
        <div className="flex flex-col space-y-2 p-6">
          {navigationItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => onOpenChange(false)}
                className={`flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive ? "shadow-sm" : "hover:bg-white/10"
                }`}
                style={{
                  backgroundColor: isActive ? "#F0EAD6" : "transparent",
                  color: isActive ? "#002147" : "#F0EAD6",
                }}
              >
                <item.icon
                  className="h-5 w-5"
                  style={{
                    color: isActive ? "#002147" : "#6C757D",
                  }}
                />
                <span>{item.title}</span>
              </Link>
            )
          })}
        </div>
      </SheetContent>
    </Sheet>
  )
}
