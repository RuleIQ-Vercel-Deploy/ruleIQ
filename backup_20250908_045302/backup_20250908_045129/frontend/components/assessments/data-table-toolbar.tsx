'use client';

import { Cross2Icon } from '@radix-ui/react-icons';
import { Search } from 'lucide-react';

import { DataTableFacetedFilter } from '@/components/assessments/data-table-faceted-filter';
import { DataTableViewOptions } from '@/components/assessments/data-table-view-options';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { frameworks, statuses } from '@/lib/data/assessments';

import type { Table } from '@tanstack/react-table';

interface DataTableToolbarProps<TData> {
  table: Table<TData>;
}

export function DataTableToolbar<TData>({ table }: DataTableToolbarProps<TData>) {
  const isFiltered = table.getState().columnFilters.length > 0;

  return (
    <div className="flex items-center justify-between">
      <div className="flex flex-1 items-center space-x-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Filter assessments..."
            value={(table.getColumn('name')?.getFilterValue() as string) ?? ''}
            onChange={(event) => table.getColumn('name')?.setFilterValue(event.target.value)}
            className="h-10 w-[150px] border-primary/30 bg-muted/20 pl-10 placeholder:text-muted-foreground focus:border-primary lg:w-[250px]"
          />
        </div>
        {table.getColumn('framework') && (
          <DataTableFacetedFilter
            column={table.getColumn('framework')!}
            title="Framework"
            options={frameworks}
          />
        )}
        {table.getColumn('status') && (
          <DataTableFacetedFilter
            column={table.getColumn('status')!}
            title="Status"
            options={statuses}
          />
        )}
        {isFiltered && (
          <Button
            variant="ghost"
            onClick={() => table.resetColumnFilters()}
            className="h-10 px-2 hover:bg-accent lg:px-3"
          >
            Reset
            <Cross2Icon className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>
      <DataTableViewOptions table={table} />
    </div>
  );
}
