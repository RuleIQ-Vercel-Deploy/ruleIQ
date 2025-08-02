'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface EvidenceFiltersProps {
  filters?: {
    search?: string;
    status?: string;
    framework?: string;
    fileType?: string;
    dateRange?: {
      from?: Date;
      to?: Date;
    };
  };
  onFiltersChange?: (filters: any) => void;
}

export function EvidenceFilters({ filters = {}, onFiltersChange }: EvidenceFiltersProps) {
  const [searchTerm, setSearchTerm] = useState(filters.search || '');
  const [statusFilter, setStatusFilter] = useState(filters.status || '');
  const [frameworkFilter, setFrameworkFilter] = useState(filters.framework || '');
  const [fileTypeFilter, setFileTypeFilter] = useState(filters.fileType || '');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');

  const activeFiltersCount = [
    searchTerm,
    statusFilter,
    frameworkFilter,
    fileTypeFilter,
    fromDate,
    toDate
  ].filter(Boolean).length;

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStatus = e.target.value;
    setStatusFilter(newStatus);
    onFiltersChange?.({
      ...filters,
      status: newStatus
    });
  };

  const handleFrameworkChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newFramework = e.target.value;
    setFrameworkFilter(newFramework);
    onFiltersChange?.({
      ...filters,
      framework: newFramework
    });
  };

  const handleFromDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFromDate = e.target.value;
    setFromDate(newFromDate);
    onFiltersChange?.({
      ...filters,
      dateRange: {
        from: newFromDate ? new Date(newFromDate) : undefined,
        to: toDate ? new Date(toDate) : undefined
      }
    });
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
    setFrameworkFilter('');
    setFileTypeFilter('');
    setFromDate('');
    setToDate('');
    onFiltersChange?.({
      status: '',
      framework: '',
      fileType: '',
      dateRange: {
        from: undefined,
        to: undefined
      }
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Filters
          {activeFiltersCount > 0 && (
            <span className="ml-2 text-sm text-gray-500">
              {activeFiltersCount} filters active
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <label htmlFor="search" className="text-sm font-medium">
              Search
            </label>
            <Input
              id="search"
              placeholder="Search evidence..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="status" className="text-sm font-medium">
              Status
            </label>
            <select
              id="status"
              className="w-full p-2 border rounded"
              value={statusFilter}
              onChange={handleStatusChange}
            >
              <option value="">All</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div>
            <label htmlFor="framework" className="text-sm font-medium">
              Framework
            </label>
            <select
              id="framework"
              className="w-full p-2 border rounded"
              value={frameworkFilter}
              onChange={handleFrameworkChange}
            >
              <option value="">All Frameworks</option>
              <option value="gdpr">GDPR</option>
              <option value="iso27001">ISO 27001</option>
              <option value="sox">SOX</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label htmlFor="fromDate" className="text-sm font-medium">
                From Date
              </label>
              <Input
                id="fromDate"
                type="date"
                value={fromDate}
                onChange={handleFromDateChange}
              />
            </div>
            <div>
              <label htmlFor="toDate" className="text-sm font-medium">
                To Date
              </label>
              <Input
                id="toDate"
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button className="flex-1">
              Apply Filters
            </Button>
            {activeFiltersCount > 0 && (
              <Button
                variant="outline"
                onClick={handleClearFilters}
                className="flex-1"
              >
                Clear Filters
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
