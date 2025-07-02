import { Skeleton } from "@/components/ui/skeleton"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export function DataTableSkeleton() {
  return (
    <div
      className="rounded-lg border overflow-hidden"
      style={{
        backgroundColor: "#F0EAD6",
        borderColor: "rgba(0, 33, 71, 0.2)",
      }}
    >
      <Table>
        <TableHeader>
          <TableRow
            style={{
              borderBottomColor: "rgba(0, 33, 71, 0.2)",
              backgroundColor: "rgba(0, 33, 71, 0.05)",
            }}
          >
            <TableHead className="px-6 py-4">
              <Skeleton className="h-5 w-24 bg-oxford-blue/10" />
            </TableHead>
            <TableHead className="px-6 py-4 text-center">
              <Skeleton className="h-5 w-16 mx-auto bg-oxford-blue/10" />
            </TableHead>
            <TableHead className="px-6 py-4 text-center">
              <Skeleton className="h-5 w-20 mx-auto bg-oxford-blue/10" />
            </TableHead>
            <TableHead className="px-6 py-4 text-right">
              <Skeleton className="h-5 w-16 ml-auto bg-oxford-blue/10" />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 5 }).map((_, index) => (
            <TableRow
              key={index}
              style={{
                borderBottomColor: "rgba(0, 33, 71, 0.1)",
              }}
            >
              <TableCell className="px-6 py-4">
                <Skeleton className="h-5 w-3/4 bg-oxford-blue/10" />
              </TableCell>
              <TableCell className="px-6 py-4 text-center">
                <Skeleton className="h-6 w-24 mx-auto bg-oxford-blue/10" />
              </TableCell>
              <TableCell className="px-6 py-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Skeleton className="h-4 w-1/4 bg-oxford-blue/10" />
                    <Skeleton className="h-4 w-1/5 bg-oxford-blue/10" />
                  </div>
                  <Skeleton className="h-2 w-full bg-oxford-blue/10" />
                </div>
              </TableCell>
              <TableCell className="px-6 py-4 text-right">
                <Skeleton className="h-5 w-20 ml-auto bg-oxford-blue/10" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
