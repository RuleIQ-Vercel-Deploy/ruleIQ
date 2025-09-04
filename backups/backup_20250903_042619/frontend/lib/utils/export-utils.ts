import * as XLSX from '@e965/xlsx';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

export interface ExportOptions {
  filename: string;
  format: 'csv' | 'json' | 'txt' | 'pdf' | 'xlsx';
  headers?: string[];
  customFormatter?: (value: any) => string;
}

export class DataExporter {
  static exportToCSV(data: unknown[], options: Partial<ExportOptions> = {}) {
    const { filename = 'export', headers } = options;

    // Extract headers from data if not provided
    const columnHeaders = headers || (data.length > 0 ? Object.keys(data[0]) : []);

    // Create CSV content
    const csvContent = [
      columnHeaders.join(','),
      ...data.map((row) =>
        columnHeaders
          .map((header) => {
            const value = row[header];
            if (value === null || value === undefined) return '';
            if (typeof value === 'string' && value.includes(',')) {
              return `"${value.replace(/"/g, '""')}"`;
            }
            return String(value);
          })
          .join(','),
      ),
    ].join('\n');

    this.downloadFile(csvContent, `${filename}.csv`, 'text/csv;charset=utf-8;');
  }

  static exportToJSON(data: unknown[], options: Partial<ExportOptions> = {}) {
    const { filename = 'export' } = options;
    const jsonContent = JSON.stringify(data, null, 2);
    this.downloadFile(jsonContent, `${filename}.json`, 'application/json');
  }

  static exportToExcel(data: unknown[], options: Partial<ExportOptions> = {}) {
    const { filename = 'export', headers } = options;

    // Create workbook and worksheet
    const ws = XLSX.utils.json_to_sheet(data, { header: headers });
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Data');

    // Style the header row
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1');
    for (let C = range.s.c; C <= range.e.c; ++C) {
      const address = `${XLSX.utils.encode_col(C)}1`;
      if (!ws[address]) continue;
      ws[address].s = {
        font: { bold: true, color: { rgb: 'FFFFFF' } },
        fill: { fgColor: { rgb: '17255A' } },
      };
    }

    // Generate and download file
    XLSX.writeFile(wb, `${filename}.xlsx`);
  }

  static exportToPDF(data: unknown[], options: Partial<ExportOptions> = {}) {
    const { filename = 'export', headers } = options;

    // Create PDF document
    const doc = new jsPDF();

    // Add title
    doc.setFontSize(16);
    doc.setTextColor(23, 37, 90); // Navy color
    doc.text('Data Export', 14, 15);

    // Add timestamp
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 25);

    // Prepare table data
    const columnHeaders = headers || (data.length > 0 ? Object.keys(data[0]) : []);
    const tableData = data.map((row) =>
      columnHeaders.map((header) => {
        const value = row[header];
        return value === null || value === undefined ? '' : String(value);
      }),
    );

    // Add table
    autoTable(doc, {
      head: [columnHeaders],
      body: tableData,
      startY: 35,
      headStyles: {
        fillColor: [23, 37, 90], // Navy
        textColor: 255,
        fontStyle: 'bold',
      },
      alternateRowStyles: {
        fillColor: [248, 249, 251], // Light gray
      },
      margin: { horizontal: 14 },
      styles: {
        fontSize: 9,
        cellPadding: 3,
      },
    });

    // Save the PDF
    doc.save(`${filename}.pdf`);
  }

  static async exportWithProgress(
    data: unknown[],
    format: ExportOptions['format'],
    onProgress?: (progress: number) => void,
  ) {
    const chunkSize = 1000;
    const chunks = [];

    for (let i = 0; i < data.length; i += chunkSize) {
      chunks.push(data.slice(i, i + chunkSize));
      if (onProgress) {
        onProgress((i / data.length) * 100);
      }
      // Allow UI to update
      await new Promise((resolve) => setTimeout(resolve, 0));
    }

    // Export based on format
    switch (format) {
      case 'csv':
        this.exportToCSV(data);
        break;
      case 'json':
        this.exportToJSON(data);
        break;
      case 'xlsx':
        this.exportToExcel(data);
        break;
      case 'pdf':
        this.exportToPDF(data);
        break;
      default:
        throw new Error(`Unsupported format: ${format}`);
    }

    if (onProgress) {
      onProgress(100);
    }
  }

  private static downloadFile(content: string | Blob, filename: string, mimeType: string) {
    const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  }
}

// Utility functions for data transformation
export const transformDataForExport = (
  data: unknown[],
  columnMapping?: Record<string, string>,
  valueFormatters?: Record<string, (value: any) => string>,
) => {
  return data.map((row) => {
    const transformedRow: Record<string, any> = {};

    Object.entries(row).forEach(([key, value]) => {
      const mappedKey = columnMapping?.[key] || key;
      const formatter = valueFormatters?.[key];
      transformedRow[mappedKey] = formatter ? formatter(value) : value;
    });

    return transformedRow;
  });
};

// Export presets for common data types
export const exportPresets = {
  compliance: {
    columnMapping: {
      compliance_score: 'Compliance Score (%)',
      last_assessed: 'Last Assessment Date',
      framework_name: 'Framework',
      status: 'Status',
    },
    valueFormatters: {
      last_assessed: (value: string) => new Date(value).toLocaleDateString(),
      compliance_score: (value: number) => `${value}%`,
      status: (value: string) => value.charAt(0).toUpperCase() + value.slice(1),
    },
  },

  policies: {
    columnMapping: {
      policy_name: 'Policy Name',
      last_updated: 'Last Updated',
      version: 'Version',
      approval_status: 'Approval Status',
    },
    valueFormatters: {
      last_updated: (value: string) => new Date(value).toLocaleDateString(),
      version: (value: string) => `v${value}`,
    },
  },

  evidence: {
    columnMapping: {
      file_name: 'File Name',
      upload_date: 'Upload Date',
      file_size: 'Size',
      status: 'Status',
    },
    valueFormatters: {
      upload_date: (value: string) => new Date(value).toLocaleDateString(),
      file_size: (value: number) => {
        const mb = value / (1024 * 1024);
        return mb > 1 ? `${mb.toFixed(1)} MB` : `${(value / 1024).toFixed(1)} KB`;
      },
    },
  },
};
