import { LoadingShowcase } from "@/components/loading/loading-showcase"
import { BreadcrumbNav } from "@/components/navigation/breadcrumb-nav"

export default function LoadingStatesPage() {
  return (
    <>
        <BreadcrumbNav items={[{ title: "Loading States" }]} />

        <main className="flex-1 space-y-6 p-6" style={{ backgroundColor: "#002147" }}>
          <div className="space-y-2">
            <h1 className="text-3xl font-bold" style={{ color: "#F0EAD6" }}>
              Loading & Skeleton States
            </h1>
            <p className="text-lg" style={{ color: "#6C757D" }}>
              Enhancing user experience with consistent loading indicators.
            </p>
          </div>

          <LoadingShowcase />
        </main>
    </>
  )
}