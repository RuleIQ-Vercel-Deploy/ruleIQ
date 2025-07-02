import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { SidebarTrigger } from "@/components/ui/sidebar"

interface BreadcrumbNavProps {
  items: Array<{
    title: string
    href?: string
  }>
}

export function BreadcrumbNav({ items }: BreadcrumbNavProps) {
  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b border-white/20 bg-midnight-blue/95 px-4 backdrop-blur-sm">
      <SidebarTrigger className="text-eggshell-white hover:bg-white/10" />
      <Separator orientation="vertical" className="mr-2 h-4 bg-white/20" />
      <Breadcrumb>
        <BreadcrumbList>
          {items.map((item, index) => (
            <div key={item.title} className="flex items-center">
              {index > 0 && <BreadcrumbSeparator />}
              <BreadcrumbItem>
                {item.href && index < items.length - 1 ? (
                  <BreadcrumbLink
                    href={item.href}
                    className="text-muted-foreground transition-colors hover:text-eggshell-white"
                  >
                    {item.title}
                  </BreadcrumbLink>
                ) : (
                  <BreadcrumbPage className="font-medium text-eggshell-white">{item.title}</BreadcrumbPage>
                )}
              </BreadcrumbItem>
            </div>
          ))}
        </BreadcrumbList>
      </Breadcrumb>
    </header>
  )
}
