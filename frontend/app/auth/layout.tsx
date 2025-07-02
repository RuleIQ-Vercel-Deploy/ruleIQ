import { AuthLayout } from "@/components/layouts/auth-layout"

import type React from "react"

export default function AuthPagesLayout({ children }: { children: React.ReactNode }) {
  return <AuthLayout>{children}</AuthLayout>
}
