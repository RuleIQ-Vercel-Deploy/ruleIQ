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
    <div
      className="overflow-hidden rounded-lg border"
      style={{
        backgroundColor: '#F0EAD6',
        borderColor: 'rgba(0, 33, 71, 0.2)',
      }}
    >
      <Table>
        <TableHeader>
          <TableRow
            style={{
              borderBottomColor: 'rgba(0, 33, 71, 0.2)',
              backgroundColor: 'rgba(0, 33, 71, 0.05)',
            }}
          >
            <TableHead className="px-6 py-4">
              <Skeleton className="bg-oxford-blue/10 h-5 w-24" />
            </TableHead>
            <TableHead className="px-6 py-4 text-center">
              <Skeleton className="bg-oxford-blue/10 mx-auto h-5 w-16" />
            </TableHead>
            <TableHead className="px-6 py-4 text-center">
              <Skeleton className="bg-oxford-blue/10 mx-auto h-5 w-20" />
            </TableHead>
            <TableHead className="px-6 py-4 text-right">
              <Skeleton className="bg-oxford-blue/10 ml-auto h-5 w-16" />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 5 }).map((_, index) => (
            <TableRow
              key={index}
              style={{
                borderBottomColor: 'rgba(0, 33, 71, 0.1)',
              }}
            >
              <TableCell className="px-6 py-4">
                <Skeleton className="bg-oxford-blue/10 h-5 w-3/4" />
              </TableCell>
              <TableCell className="px-6 py-4 text-center">
                <Skeleton className="bg-oxford-blue/10 mx-auto h-6 w-24" />
              </TableCell>
              <TableCell className="px-6 py-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Skeleton className="bg-oxford-blue/10 h-4 w-1/4" />
                    <Skeleton className="bg-oxford-blue/10 h-4 w-1/5" />
                  </div>
                  <Skeleton className="bg-oxford-blue/10 h-2 w-full" />
                </div>
              </TableCell>
              <TableCell className="px-6 py-4 text-right">
                <Skeleton className="bg-oxford-blue/10 ml-auto h-5 w-20" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
