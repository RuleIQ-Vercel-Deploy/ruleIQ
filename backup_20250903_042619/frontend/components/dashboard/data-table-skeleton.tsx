import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export function DataTableSkeleton() {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow className="border-b border-border bg-muted/50">
            <TableHead className="px-6 py-4">
              <Skeleton className="h-5 w-24" />
            </TableHead>
            <TableHead className="px-6 py-4 text-center">
              <Skeleton className="mx-auto h-5 w-16" />
            </TableHead>
            <TableHead className="px-6 py-4 text-center">
              <Skeleton className="mx-auto h-5 w-20" />
            </TableHead>
            <TableHead className="px-6 py-4 text-right">
              <Skeleton className="ml-auto h-5 w-16" />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 5 }).map((_, index) => (
            <TableRow key={index} className="border-b border-border">
              <TableCell className="px-6 py-4">
                <Skeleton className="h-5 w-3/4" />
              </TableCell>
              <TableCell className="px-6 py-4 text-center">
                <Skeleton className="mx-auto h-6 w-24" />
              </TableCell>
              <TableCell className="px-6 py-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Skeleton className="h-4 w-1/4" />
                    <Skeleton className="h-4 w-1/5" />
                  </div>
                  <Skeleton className="h-2 w-full" />
                </div>
              </TableCell>
              <TableCell className="px-6 py-4 text-right">
                <Skeleton className="ml-auto h-5 w-20" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
